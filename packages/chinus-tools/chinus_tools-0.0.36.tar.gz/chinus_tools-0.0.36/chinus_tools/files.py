import json
import yaml

__all__ = ['json', 'yaml']


class FileManager:
    def __init__(self, __manager):
        self._manager = __manager

    def loads(self, **kwargs):
        return self._manager.loads(**kwargs)

    def dumps(self, **kwargs):
        return self._manager.dumps(**kwargs)

    def load(self, file_path: str, **kwargs):
        with open(str(file_path), 'r', encoding='utf-8') as f:
            return self._manager.load(f, **kwargs)

    def dump(self, obj, file_path: str, **kwargs):
        with open(str(file_path), 'w', encoding='utf-8') as f:
            self._manager.dump(obj, f, **kwargs)

    def safe_load(self, file_path: str):
        with open(str(file_path), 'r', encoding='utf-8') as f:
            return self._manager.safe_load(f)

    def safe_dump(self, obj, file_path: str, **kwargs):
        with open(str(file_path), 'w', encoding='utf-8') as f:
            self._manager.safe_dump(obj, f, **kwargs)


json = FileManager(json)
yaml = FileManager(yaml)
