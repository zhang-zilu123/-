"""
数据处理相关工具函数
"""
from typing import List, Dict, Any, Tuple
import pandas as pd


def convert_excel_to_dict_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    将pandas DataFrame转换为字典列表
    
    Args:
        df: pandas DataFrame
        
    Returns:
        List[Dict[str, Any]]: 字典列表，每个字典代表一行数据
    """
    return df.to_dict('records')


def separate_complete_incomplete_data(
    data_list: List[Dict[str, Any]], 
    required_fields: List[str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    将数据分离为完整和不完整两个列表
    
    Args:
        data_list: 原始数据列表
        required_fields: 必需字段列表
        
    Returns:
        Tuple[List[Dict], List[Dict]]: (完整数据列表, 不完整数据列表)
    """
    from .validation_utils import is_data_complete
    
    complete_data = []
    incomplete_data = []
    
    for row in data_list:
        if is_data_complete(row, required_fields):
            complete_data.append(row)
        else:
            incomplete_data.append(row)
    
    return complete_data, incomplete_data


def create_validation_summary(
    total_count: int,
    complete_count: int, 
    incomplete_count: int,
    missing_fields_stats: Dict[str, int]
) -> Dict[str, Any]:
    """
    创建数据验证摘要报告
    
    Args:
        total_count: 总数据条数
        complete_count: 完整数据条数
        incomplete_count: 不完整数据条数
        missing_fields_stats: 各字段缺失统计
        
    Returns:
        Dict[str, Any]: 验证摘要报告
    """
    return {
        "总数据量": total_count,
        "完整数据量": complete_count,
        "不完整数据量": incomplete_count,
        "完整率": f"{(complete_count / total_count * 100):.2f}%" if total_count > 0 else "0%",
        "缺失字段统计": missing_fields_stats,
        "验证时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }