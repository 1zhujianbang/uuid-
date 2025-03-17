import re

def validate_uuid(uuid_str):
    """验证并标准化UUID格式"""
    cleaned = re.sub(r'-', '', uuid_str)
    if len(cleaned) != 32 or not re.match(r'^[0-9a-fA-F]{32}$', cleaned):
        raise ValueError("Invalid UUID format")
    return cleaned.lower()

def format_uuid(uuid_str):
    """格式化UUID为带连字符的标准形式"""
    uuuid = validate_uuid(uuid_str)
    return f"{uuuid[:8]}-{uuuid[8:12]}-{uuuid[12:16]}-{uuuid[16:20]}-{uuuid[20:]}"