import hashlib
import inspect
import json
import time
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
from annotated_dict import AnnotatedDict
from . import JSONResource
from . import Job, Resource, Jobs, Executor, Response, Message
from . import log, MessageQueue, Response

REQUEST_DEFAULTS = {
    "params": {},
    "json": {},
    "headers": {}
}

class RequestHash(AnnotatedDict):
    method: str
    url: str
    params: dict
    json: dict
    headers: dict

    @classmethod
    def from_request(cls, **kwargs) -> 'RequestHash':
        if (not kwargs.get('method')) or (not kwargs.get('url')): raise KeyError(f'Missing either method or url, got {kwargs} instead')
        kwargs = REQUEST_DEFAULTS.copy() | kwargs
        instance = cls(**kwargs)
        return instance

    @property
    def hash_key(self) -> str:
        hash_data = {
            'method': self.method,
            'url': self.url,
            'params': self.params,
            'json': self.json,
            'headers': self.headers
        }
        json_str = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()


class CacheEntry(AnnotatedDict):
    entry_time: int  # in the whatever second thingy
    ttl: int  = 604800
    method: str
    url: str
    params: dict = {}
    json: dict = {}
    headers: dict = {}
    response: dict

    @property
    def hash_key(self):
        if self.get("method", None) is None: raise KeyError("Can't hash without method attribute!")
        if self.get("url", None) is None: raise KeyError("Can't hash without url attribute!")
        request_hash = RequestHash(**self)
        return request_hash.hash_key

    @classmethod
    def fetch(cls, hash: str, cache: dict):
        if not cls.is_in_cache(hash, cache): return None
        else: return cls(**cache[hash])

    @staticmethod
    def is_in_cache(hash: str, cache: dict) -> bool:
        if not cache.get(hash): return False
        return True

    def commit(self, cache: dict):
        if not self.response: raise KeyError("Can't commit without a response field!")
        cache[self.hash_key] = {**self}

    @classmethod
    def from_kwargs(cls, **kwargs):
        if not kwargs.get("response"): raise KeyError("Can't construct a cache entry without a response field!")
        instance = cls()
        instance.ttl = kwargs.get("ttl", cls.ttl)
        instance.entry_time = int(time.time())
        instance.method = kwargs.get('method', 'GET')
        instance.url = kwargs.get('url', '')
        instance.params = kwargs.get('params', {})
        instance.json = kwargs.get('json', {})
        instance.headers = kwargs.get('headers', {})
        instance.response = kwargs.get('response')
        return instance

class RequestJob(Job):
    required_resources = ["api_cache"]
    method: str
    url: str
    params: dict = {}
    json: dict = {}
    headers: dict = {}

    def __init__(self):
        Job.__init__(self)

    def __repr__(self):
        return f"[{self.__class__.__name__}]"

    def execute(self, resources: dict[str, Resource], **kwargs):
        start_time = time.perf_counter()
        default_kwargs = {}
        for key, value in inspect.getmembers(self.__class__):
            if key.startswith("_"): continue
            if callable(value): continue
            if key in ["required_resources"]: continue
            if not isinstance(value, type): default_kwargs[key] = value

        # log.debug(f"{self}: defaults: {default_kwargs}")
        # log.debug(f"{self}: kwargs: {kwargs}")
        kwargs = default_kwargs | kwargs

        try:
            cache = resources["api_cache"].peek()
            hash_key = RequestHash.from_request(**kwargs).hash_key
            if not (cache_entry := CacheEntry.fetch(hash_key, cache)):
                try:
                    log.warning(f"{self}: Couldn't find a request to '{kwargs['url']}' in the cache...")
                    log.info(f"{self}: Making '{kwargs['method'].lower()}' request to {kwargs['url']}")

                    response = httpx.request(
                        method=kwargs["method"],
                        url=kwargs["url"],
                        params=kwargs["params"],
                        json=kwargs["json"],
                        headers=kwargs["headers"],
                    )
                    response.raise_for_status()

                    try:
                        kwargs["response"] = response.json()
                    except (json.JSONDecodeError, ValueError):
                        kwargs["response"] = {
                            "text": response.text,
                            "status_code": response.status_code,
                            "headers": dict(response.headers)
                        }

                except httpx.HTTPStatusError as e:
                    raise Exception(f"Failed to make request to '{kwargs['url']}': {e}")
                except httpx.RequestError as e:
                    raise Exception(f"Failed to make request to '{kwargs.get('url', 'unknown')}': {e}")
                except Exception as e:
                    raise Exception(f"Unexpected error for '{kwargs.get('url', 'unknown')}': {e}")

                try:
                    cache_entry = CacheEntry.from_kwargs(**kwargs)
                    with resources["api_cache"] as c:
                        cache_entry.commit(c)
                    if cache_entry.hash_key in resources["api_cache"].peek(): log.info(f"{self}: Successfully cached request as '{cache_entry.hash_key}'")
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    log.debug(f"{self}: Executed fresh request in: {duration:.4f} seconds")
                    return cache_entry.response

                except Exception as e:
                    raise Exception(f"Error caching request for '{self.url}': {e}")

            else:
                end_time = time.perf_counter()
                duration = end_time - start_time
                log.debug(f"{self}: Retrieved from cache in: {duration:.4f} seconds")
                return cache_entry.response

        except Exception as e:
            raise Exception

class APICache(JSONResource):
    def __init__(self, identifier: str = None, cwd: Path = Path.cwd()):
        if not identifier: identifier = self.__class__.__name__.lower()
        identifier = f"{identifier}-api-cache"
        super().__init__(identifier, cwd)

class RequestJobs(Jobs):
    def __init__(self, identifier: str = None, cwd: Path = Path.cwd()):
        if not identifier: identifier = self.__class__.__name__.lower()
        self.identifier = identifier
        if "api_cache" not in self.resources: self.resources["api_cache"] = APICache(identifier, cwd)
        super().__init__()
        log.debug(f"{self}: Initialized with {len(self.types)} jobs and {len(self.resources)} resources for API Calls")

    def __repr__(self):
        return f"[{self.__class__.__name__}.RequestJobs]"

class RequestMessageQueue(MessageQueue):
    def __init__(self, job_types: type[RequestJobs], executor: type[Executor] = Executor, auto_start: bool = True):
        super().__init__(job_types, executor, auto_start)


class APIClient:
    headers = {}
    job_types: type[RequestJobs]
    auto_start: bool = True

    def __init__(self):
        if self.__class__.__name__ == "APIClient": raise RuntimeError("APIClient cannot be instantiated directly, it must be inherited")
        self.header_deviations: dict[str, dict[str, str]] = {}
        for job_name, job_type in self.job_types.__annotations__.items():
            job_type: RequestJob
            for pointer in job_type.__dict__:
                if pointer == "headers":
                    log.debug(f"{self}: Identified header deviation from default in job type '{job_type.__name__}'")
                    self.header_deviations[job_name] = job_type.__dict__[pointer]

        if not self.job_types: raise AttributeError("No job_types referenced")
        self.mq = RequestMessageQueue(self.job_types, executor=Executor, auto_start=self.auto_start)

    def __repr__(self):
        return f"[{self.__class__.__name__}.APIClient]"

    def _compile_headers(self, job_type, **kwargs):
        if not job_type in self.header_deviations:
            headers = self.headers
            if kwargs.get("headers"): headers = self.headers | kwargs["headers"]
            else: kwargs = { "headers": headers } | kwargs
        return kwargs

    def request(self, job_type: str, **kwargs) -> UUID:
        kwargs = self._compile_headers(job_type, **kwargs)
        return self.mq.send(job_type, **kwargs)

    def response(self, request_id: UUID) -> Response:
        return self.mq.receive(request_id)

    def request_and_response(self, job_type: str, timeout: int = 10, **kwargs) -> Response:
        kwargs = self._compile_headers(job_type, **kwargs)
        return self.mq.send_and_receive(job_type, timeout, **kwargs)

    def batch_request(self, messages: dict[str, Message]) -> dict[str, UUID]:
        for message in messages.values():
            if not message.get("payload"): continue
            message["payload"] = self._compile_headers(message.job_type, **message.payload)
        return self.mq.batch_send(messages)

    def batch_response(self, message_ids: dict[str, UUID], min_timeout: float = 1.0, max_iteration: int = 10) -> tuple[dict[str, Response], dict[str, Response]]:
        return self.mq.batch_receive(message_ids, min_timeout, max_iteration)

    def batch_request_and_response(self, messages: dict[str, Message], min_timeout: float = 1.0, max_iteration: int = 10):
        for message in messages.values():
            if not message.get("payload"): continue
            message["payload"] = self._compile_headers(message.job_type, **message.payload)
        return self.mq.batch_send_and_receive(messages, min_timeout=min_timeout, max_iteration=max_iteration)