"""
数据分割工具模块 - 用于将大型JSON文件分割成小文件
"""
import json
import os
import math
from typing import List, Dict, Any, Tuple
from pathlib import Path

# 导入项目工具
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_utils import setup_logger


def split_json_file(
    input_file_path: str,
    output_dir: str = None,
    chunk_size: int = 1000,
    create_subdirs: bool = True
) -> Dict[str, Any]:
    """
    将大型JSON文件分割成多个小文件
    
    Args:
        input_file_path: 输入JSON文件路径
        output_dir: 输出目录，如果为None则自动生成
        chunk_size: 每个分割文件的数据条数
        create_subdirs: 是否创建子目录
        
    Returns:
        Dict[str, Any]: 分割结果统计
    """
    logger = setup_logger("step1_data_validator")
    
    try:
        # 验证输入文件
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"输入文件不存在: {input_file_path}")
        
        # 读取JSON数据
        # logger.info(f"开始读取文件: {input_file_path}")
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("JSON文件必须包含一个数组")
        
        total_count = len(data)
        # logger.info(f"文件包含 {total_count} 条数据")
        
        # 计算分割信息
        split_info = calculate_split_info(total_count, chunk_size)
        # logger.info(f"将分割为 {split_info['total_files']} 个文件")
        
        # 确定输出目录
        if output_dir is None:
            output_dir = _generate_output_dir(input_file_path)
        
        if create_subdirs:
            os.makedirs(output_dir, exist_ok=True)
        
        # 执行分割
        split_files = []
        base_filename = _extract_base_filename(input_file_path)
        
        for i in range(split_info['total_files']):
            start_idx = i * chunk_size
            end_idx = min(start_idx + chunk_size, total_count)
            chunk_data = data[start_idx:end_idx]
            
            # 生成输出文件名
            output_filename = _create_split_filename(base_filename, i + 1, split_info['total_files'])
            output_path = os.path.join(output_dir, output_filename)
            
            # 保存分割文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, ensure_ascii=False, indent=2)
            
            split_files.append(output_path)
            # logger.info(f"已创建分割文件 {i + 1}/{split_info['total_files']}: {output_filename} ({len(chunk_data)} 条数据)")
        
        # 生成分割报告
        split_result = {
            "input_file": input_file_path,
            "output_dir": output_dir,
            "total_data_count": total_count,
            "chunk_size": chunk_size,
            "total_files": split_info['total_files'],
            "split_files": split_files,
            "status": "success"
        }
        
        # logger.info(f"分割完成！共生成 {len(split_files)} 个文件")
        return split_result
        
    except Exception as e:
        logger.error(f"分割文件时发生错误: {str(e)}")
        return {
            "input_file": input_file_path,
            "error": str(e),
            "status": "failed"
        }


def calculate_split_info(total_count: int, chunk_size: int) -> Dict[str, int]:
    """
    计算分割信息
    
    Args:
        total_count: 总数据条数
        chunk_size: 每块大小
        
    Returns:
        Dict[str, int]: 分割信息
    """
    total_files = math.ceil(total_count / chunk_size)
    return {
        "total_count": total_count,
        "chunk_size": chunk_size,
        "total_files": total_files,
        "last_file_size": total_count % chunk_size or chunk_size
    }


def _generate_output_dir(input_file_path: str) -> str:
    """
    根据输入文件路径生成输出目录
    
    Args:
        input_file_path: 输入文件路径
        
    Returns:
        str: 输出目录路径
    """
    input_dir = os.path.dirname(input_file_path)
    parent_dir = os.path.dirname(input_dir)
    return os.path.join(parent_dir, "split_data")


def _extract_base_filename(input_file_path: str) -> str:
    """
    提取基础文件名（不含扩展名）
    
    Args:
        input_file_path: 输入文件路径
        
    Returns:
        str: 基础文件名
    """
    filename = os.path.basename(input_file_path)
    return os.path.splitext(filename)[0]


def _create_split_filename(base_filename: str, part_num: int, total_parts: int) -> str:
    """
    创建分割文件名
    
    Args:
        base_filename: 基础文件名
        part_num: 当前部分编号
        total_parts: 总部分数
        
    Returns:
        str: 分割文件名
    """
    # 确定编号位数
    digits = len(str(total_parts))
    part_str = str(part_num).zfill(digits)
    
    return f"{base_filename}_part_{part_str}.json"




def get_split_summary(split_result: Dict[str, Any]) -> str:
    """
    生成分割结果摘要
    
    Args:
        split_result: 分割结果
        
    Returns:
        str: 摘要信息
    """
    if split_result["status"] == "failed":
        return f"分割失败: {split_result.get('error', '未知错误')}"
    
    return f"""
数据分割摘要:
- 输入文件: {split_result['input_file']}
- 输出目录: {split_result['output_dir']}
- 总数据量: {split_result['total_data_count']} 条
- 分块大小: {split_result['chunk_size']} 条/文件
- 生成文件: {split_result['total_files']} 个
- 分割状态: 成功
""" 