"""
数据验证相关工具函数
"""
from typing import Any, List, Dict, Union


def is_none_or_empty(value: Any) -> bool:
    """
    检查值是否为None或空值
    
    Args:
        value: 要检查的值
        
    Returns:
        bool: 如果值为None、空字符串、空列表或空字典则返回True
    """
    if value is None:
        return True
    
    if isinstance(value, str) and value.strip() == "":
        return True
        
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
        
    return False


def check_required_fields(data_row: Dict[str, Any], required_fields: List[str]) -> Dict[str, bool]:
    """
    检查数据行中必需字段的完整性
    
    Args:
        data_row: 单行数据字典
        required_fields: 必需字段列表
        
    Returns:
        Dict[str, bool]: 字段名到是否完整的映射
    """
    field_status = {}
    
    for field in required_fields:
        if field not in data_row:
            field_status[field] = False
        else:
            field_status[field] = not is_none_or_empty(data_row[field])
    
    return field_status





def get_missing_fields(data_row: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    获取数据行中缺失的字段列表
    
    Args:
        data_row: 单行数据字典
        required_fields: 必需字段列表
        
    Returns:
        List[str]: 缺失的字段名列表
    """
    field_status = check_required_fields(data_row, required_fields)
    return [field for field, is_complete in field_status.items() if not is_complete]