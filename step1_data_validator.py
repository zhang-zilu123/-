"""
数据验证模块使用示例
演示如何使用DataValidator进行第一步数据验证
"""
import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_validator import DataValidator
from utils import setup_logger  # 使用新的通用logger工具


def load_data_from_excel(excel_path):
    """从Excel文件读取数据并转换为所需格式"""
    logger = setup_logger(__name__)  # 使用通用logger
    
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
    logger = setup_logger(__name__)
    logger.info("=== ProductQuotation 数据验证示例开始 ===")
    
    # 创建验证器实例
    validator = DataValidator()
    
    # 从Excel文件读取真实数据
    excel_file_path = os.path.join("data", "input", "猫狗窝page21-22.xlsx")
    sample_data = load_data_from_excel(excel_file_path)
    
    print("=== ProductQuotation 数据验证示例 ===\n")
    
    # 第一步：验证必需字段
    print("1. 开始验证数据完整性...")
    validation_results = validator.validate_required_fields(sample_data)
    
    # 显示验证摘要
    print("\n2. 验证摘要:")
    print(validator.get_validation_summary())
    
    # 第二步：分离完整和不完整数据
    print("\n3. 分离数据...")
    complete_data, incomplete_data = validator.separate_data(sample_data)
    
    print(f"完整数据: {len(complete_data)} 条")
    print(f"不完整数据: {len(incomplete_data)} 条")
    
    # 第三步：生成详细验证报告
    print("\n4. 生成验证报告...")
    report = validator.generate_validation_report()
    
    print("验证报告生成完成，主要信息:")
    print(f"- 总数据量: {report['总数据量']}")
    print(f"- 完整率: {report['完整率']}")
    print("- 字段缺失率:")
    for field, rate in report.get('字段缺失率', {}).items():
        print(f"  {field}: {rate}")
    
    # 第四步：保存验证结果
    print("\n5. 保存验证结果...")
    saved_files = validator.save_validation_results()
    
    print("文件保存完成:")
    for file_type, file_path in saved_files.items():
        print(f"- {file_type}: {file_path}")
    
    print("\n=== 数据验证流程完成 ===")
    logger.info("=== ProductQuotation 数据验证示例完成 ===")
    
    # 显示不完整数据的详细信息
    if incomplete_data:
        print(f"\n不完整数据详情 (共{len(incomplete_data)}条):")
        for i, item in enumerate(incomplete_data, 1):
            missing_fields = item.get('_missing_fields', [])
            print(f"  第{i}条 - 缺失字段: {', '.join(missing_fields)}")


if __name__ == "__main__":
    main() 