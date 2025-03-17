from processors.nbt_processor import NBTProcessor
from processors.text_processor import TextProcessor
import os

class FileHandler:
    def __init__(self, old_uuid, new_uuid, on_modify_callback=None, on_rename_callback=None):
        self.old_uuid = old_uuid
        self.new_uuid = new_uuid
        self.processors = {
            'text': TextProcessor(old_uuid, new_uuid, on_rename_callback=on_rename_callback),
            'nbt': NBTProcessor(old_uuid, new_uuid, on_rename_callback=on_rename_callback)
        }
        self.on_modify = on_modify_callback or (lambda x: None)

    def set_on_modify(self, callback):
        self.on_modify = callback or (lambda x: None)

    def set_callbacks(self, on_modify, on_rename):
        self.on_modify = on_modify
        self.processors['text'].on_rename = on_rename
        self.processors['nbt'].on_rename = on_rename
    
    def handle_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in ('.txt', '.json', '.json5', '.yaml', '.yml'):
                self.processors['text'].process_file(file_path)
                self.on_modify(file_path)  # 触发修改回调
            elif ext in ('.dat', '.mca', '.mcc'):
                self.processors['nbt'].process_file(file_path)
                self.on_modify(file_path)  # 触发修改回调
        except Exception as e:
            print(f"Error handling {file_path}: {str(e)}")