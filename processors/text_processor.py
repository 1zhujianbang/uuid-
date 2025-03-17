import re
from .base_processor import BaseProcessor
from utils.uuid_tools import format_uuid

class TextProcessor(BaseProcessor):
    def __init__(self, old_uuid, new_uuid, on_rename_callback=None):
        self.old_uuid = old_uuid.replace('-', '').lower()
        self.new_uuid = new_uuid.replace('-', '').lower()
        self.pattern = re.compile(r'\b[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}\b', re.IGNORECASE)
        self.on_rename = on_rename_callback or (lambda old, new: None)

    def process_file(self, file_path):
        self._process_content(file_path)
        self._rename_file(file_path)

    def _process_content(self, file_path):
        with open(file_path, 'r+', encoding='utf-8') as f:
            content = f.read()
            modified = self.pattern.sub(self._match_handler, content)
            f.seek(0)
            f.write(modified)
            f.truncate()

    def _rename_file(self, file_path):
        import os
        dirname, filename = os.path.split(file_path)
        newname = self.pattern.sub(self._match_handler, filename)
        if newname != filename:
            new_path = os.path.join(dirname, newname)
            os.rename(file_path, new_path)
            self.on_rename(file_path, new_path)

    def _match_handler(self, match):
        matched = match.group().replace('-', '').lower()
        return format_uuid(self.new_uuid) if matched == self.old_uuid else match.group()