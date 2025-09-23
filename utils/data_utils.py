"""
数据处理相关工具函数
"""
from typing import List, Dict, Any, Tuple
import pandas as pd



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