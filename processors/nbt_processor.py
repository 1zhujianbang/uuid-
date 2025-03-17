import nbtlib
from nbtlib import Long, Compound, List, IntArray
from .text_processor import TextProcessor

class NBTProcessor(TextProcessor):
    def __init__(self, old_uuid, new_uuid, on_rename_callback=None):
        super().__init__(old_uuid, new_uuid, on_rename_callback=on_rename_callback)

    def process_file(self, file_path):
        super()._rename_file(file_path)  # 先处理文件名
        self._process_nbt_content(file_path)

    def _process_nbt_content(self, file_path):
        nbt_data = nbtlib.load(file_path)
        self._process_tag(nbt_data)
        nbt_data.save(file_path)

    def _process_tag(self, tag):
        if isinstance(tag, Compound):
            self._process_compound(tag)
        elif isinstance(tag, List):
            self._process_list(tag)

    def _process_compound(self, compound):
        for key in list(compound.keys()):
            if key.endswith('UUIDMost') and (least_key := key.replace('Most', 'Least')) in compound:
                self._replace_long_pair(compound, key, least_key)
            self._process_tag(compound[key])

    def _replace_long_pair(self, compound, most_key, least_key):
        most = compound[most_key].value
        least = compound[least_key].value
        current = f"{most:016x}{least:016x}"

        if current == self.old_uuid:
            new_hex = self.new_uuid
            compound[most_key] = Long(int(new_hex[:16], 16))
            compound[least_key] = Long(int(new_hex[16:], 16))

    def _process_list(self, lst):
        for i, item in enumerate(lst):
            if isinstance(lst, IntArray) and len(lst) == 4:
                current = ''.join(f"{x:08x}" for x in lst)
                if current == self.old_uuid:
                    new_hex = self.new_uuid
                    lst[:] = [int(new_hex[i:i+8], 16) for i in range(0, 32, 8)]
            else:
                self._process_tag(item)