import shutil
import os.path

from ..common.additionals import allowed_types
from .data import FileBlob


class Context:

    def __init__(self, subworker):
        self.subworker = subworker
        self.id_counter = 0
        self.staged_data = set()
        self.debug_messages = []
        self.additionals = {}

    def set(self, key, value):
        if not isinstance(key, str):
            raise Exception("Key of additional has to be string")
        if type(value) not in allowed_types:
            raise Exception("Invalid value for additional {}", key)
        self.additionals[key] = value

    def stage_file(self, path):
        self.id_counter += 1
        target = os.path.join(self.subworker.stage_path, str(self.id_counter))
        shutil.move(path, target)
        data = FileBlob(target)
        self.staged_data.add(data)
        return data

    def debug(self, message):
        if not isinstance(message, str):
            raise Exception("Method 'debug' accepts only strings")
        self.debug_messages.append(message)

    def _cleanup(self, results):
        for result in results:
            if result in self.staged_data:
                self.staged_data.remove(result)

        for data in self.staged_data:
            data._remove()

    def _cleanup_on_fail(self):
        for data in self.staged_data:
            data._remove()