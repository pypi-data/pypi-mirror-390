import json
from pathlib import Path

from ezmq import Resource

class JSONResource(Resource):
    def __init__(self, identifier: str, cwd: Path = Path.cwd()):
        self.identifier = identifier
        self.cwd = cwd
        super().__init__(identifier=identifier)
        try:
            self.file_path = cwd / f"{self.identifier}.json"
            self.file_path.touch(exist_ok=True)
            if not self.file_path.exists(): raise FileNotFoundError(f"Could not locate {self.file_path}")
        except Exception as e:
            raise e

    def _enter(self):
        with open(self.file_path, 'r') as f:
            content = f.read()
            return json.loads(content) if content else {}

    def _exit(self):
        with open(self.file_path, 'w') as f:
            json.dump(self._resource, f, indent=2)

    def _peek(self):
        with open(self.file_path, 'r') as f:
            content = f.read()
            return json.loads(content) if content else {}
