import os
from utils.uuid_tools import validate_uuid
from file_handler import FileHandler
from processors.text_processor import TextProcessor

class FolderProcessor:
    def __init__(self, root_dir, old_uuid, new_uuid):
        self.root_dir = os.path.normpath(root_dir)
        self.old_uuid = validate_uuid(old_uuid)
        self.new_uuid = validate_uuid(new_uuid)
        self.file_handler = FileHandler(
            self.old_uuid, self.new_uuid, 
            on_modify_callback=lambda x: self.on_modify(x)
        )
        
        # 回调函数
        self.on_scan = lambda x: None
        self.on_modify = lambda x: None
        self.on_rename = lambda x,y: None

    def set_callbacks(self, on_scan, on_modify, on_rename):
        self.on_scan = on_scan
        self.on_modify = on_modify
        self.on_rename = on_rename
        self.file_handler.set_callbacks(on_modify=self.on_modify, on_rename=self.on_rename)

    def process(self):
        for root, dirs, files in os.walk(self.root_dir, topdown=False):
            # 处理文件
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    self.on_scan(file_path)  # 触发扫描回调
                    self.file_handler.handle_file(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

            # 处理目录
            for name in dirs:
                self._rename_entry(root, name)

    def _rename_entry(self, root, name):
        old_path = os.path.join(root, name)
        processor = TextProcessor(self.old_uuid, self.new_uuid)
        new_name = processor.pattern.sub(processor._match_handler, name)
        
        if new_name != name:
            new_path = os.path.join(root, new_name)
            try:
                os.rename(old_path, new_path)
                self.on_rename(old_path, new_path)  # 触发重命名回调
            except Exception as e:
                print(f"重命名失败 {old_path} -> {new_path}: {str(e)}")