#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重名检查主程序（修正版）
检查商品标题重复情况，输出唯一商品和重名商品
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.duplicate_checker import DuplicateChecker
from config.config import SPLIT_CONFIG

def main():
    """主函数 - 执行重名检查流程"""
    # 定义目录路径
    base_dir = os.path.join(project_root, "data", "output")
    input_dir = os.path.join(base_dir, "step2_cleandata", "complete")
    unique_output_dir = os.path.join(base_dir, "step3_unique", "complete")
    duplicate_output_dir = os.path.join(base_dir, "step3_unique", "duplicate")
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        logging.error(f"输入目录不存在: {input_dir}")
        print(f"错误: 输入目录不存在: {input_dir}")
        sys.exit(1)
    
    # 创建重名检查器
    checker = DuplicateChecker()
    
    try:
        # 执行重名检查
        result = checker.check_duplicates(
            input_dir=input_dir,
            unique_output_dir=unique_output_dir,
            duplicate_output_dir=duplicate_output_dir
        )
        
        # 打印结果摘要
        print("\n===== 重名检查结果摘要 =====")
        print(f"处理的JSON文件数量: {result['total_files']}")
        print(f"处理的商品总数: {result['total_products']}")
        print(f"唯一商品数量: {result['unique_products']}")
        print(f"重名商品数量: {result['duplicate_products']}")
        print(f"缺失标题的商品数: {result['missing_title_count']}")
        print(f"生成的唯一商品文件数: {result['unique_files']}")
        print(f"生成的重名商品文件数: {result['duplicate_files']}")
        print(f"唯一商品输出目录: {result['unique_output']}")
        print(f"重名商品输出目录: {result['duplicate_output']}")
        print("==========================\n")
        
        if result['duplicate_products'] > 0:
            print(f"发现 {result['duplicate_products']} 个重名商品，请检查 {duplicate_output_dir} 目录")
        
    except Exception as e:
        logging.exception("重名检查过程中发生未处理的异常")
        print(f"错误: 重名检查过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()