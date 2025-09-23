"""
步骤一：数据验证模块使用示例
演示如何使用DataValidator进行第一步数据验证
输入：Excel原始数据文件
输出：完整数据JSON文件和不完整数据JSON文件
"""
import sys
import os
import pandas as pd
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_validator import DataValidator
from utils import setup_logger

def load_data_from_excel(excel_path):
    """从Excel文件读取数据并转换为所需格式"""
    logger = setup_logger(log_name="step1_data_validator")
    
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_path)
        logger.info(f"成功读取Excel文件: {excel_path}")
        logger.info(f"表头列名: {df.columns.tolist()}")
        
        # 转换为所需的数据格式
        sample_data = []
        for index, row in df.iterrows():
            # 创建数据字典，处理可能的空值
            data_item = {}
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    data_item[col] = None
                elif isinstance(value, str) and value.strip() == "":
                    data_item[col] = ""
                else:
                    data_item[col] = value
            sample_data.append(data_item)
        
        logger.info(f"成功转换 {len(sample_data)} 条数据")
        return sample_data
        
    except Exception as e:
        logger.error(f"读取Excel文件时出错: {e}")



def main():
    """主函数 - 演示数据验证流程"""
    
    # 设置主程序logger
    logger = setup_logger(log_name="step1_data_validator")
    logger.info("=== ProductQuotation 步骤一：数据验证示例开始 ===")
    
    # 创建验证器实例
    validator = DataValidator()
    
    # 获取输入目录路径
    input_dir = r"data\input"
    
    # 确保目录存在
    if not os.path.exists(input_dir):
        logger.error(f"输入目录不存在: {input_dir}")
        return
    
    # 获取所有Excel文件
    excel_files = [f for f in os.listdir(input_dir) 
                  if f.endswith('.xlsx') or f.endswith('.xls')]
    
    logger.info(f"发现 {len(excel_files)} 个Excel文件需要处理")
    
     # 如果没有找到Excel文件
    if not excel_files:
        logger.warning("未找到任何Excel文件")
        return
    
    # 初始化 sample_data 为一个空列表
    sample_data = []
    
    # 循环处理每个Excel文件
    for excel_file in excel_files:
        logger.info(f"===== 处理文件: {excel_file} =====")
        excel_file_path = os.path.join(input_dir, excel_file)
        
        # 从Excel文件读取真实数据
        file_data = load_data_from_excel(excel_file_path)
        
        if file_data:
            # 将当前文件的数据追加到 sample_data（关键修改）
            sample_data.extend(file_data)
            logger.info(f"已添加 {len(file_data)} 条数据，当前总计 {len(sample_data)} 条")
        else:
            logger.warning(f"文件 {excel_file} 未加载到有效数据，跳过处理")
    
    if not sample_data:
        logger.error("没有加载到任何有效数据，无法进行验证")
        return

    
    logger.info("=== ProductQuotation 步骤一：数据验证 ===")
    
    # 第一步：验证必需字段
    logger.info("1. 开始验证数据完整性...")
    validation_results = validator.validate_required_fields(sample_data)
    
    # 显示验证摘要
    logger.info("2. 验证摘要:")
    logger.info(validator.get_validation_summary())
    
    # 第二步：分离完整和不完整数据
    logger.info("3. 分离数据...")
    complete_data, incomplete_data = validator.separate_data(sample_data)
    
    # 第三步：保存验证结果
    logger.info("4. 保存验证结果...")
    saved_files = validator.save_validation_results()


    # 显示不完整数据的详细信息
    if incomplete_data:
        logger.info(f"不完整数据详情 (共{len(incomplete_data)}条):")
        for i, item in enumerate(incomplete_data, 1):
            missing_fields = item.get('_missing_fields', [])

    logger.info("=== ProductQuotation 步骤一：数据验证完成 === \n")
    

if __name__ == "__main__":
    main() 