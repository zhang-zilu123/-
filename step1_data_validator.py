"""
步骤一：数据验证模块使用示例
演示如何使用DataValidator进行第一步数据验证
输入：Excel原始数据文件
输出：完整数据JSON文件和不完整数据JSON文件，以及分割后的小文件
"""
import sys
import os
import pandas as pd
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_validator import DataValidator
from utils import setup_logger
from utils.data_splitter_utils import split_json_file, get_split_summary
from config.config import SPLIT_CONFIG


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


def split_complete_data_files(saved_files):
    """对保存的完整数据文件进行分割"""
    logger = setup_logger(log_name="step1_data_validator")
    
    # 检查是否有完整数据文件需要分割
    complete_file = saved_files.get("complete_data")
    if not complete_file:
        logger.info("没有完整数据文件需要分割")
        return
    
    logger.info("=== 开始数据分割处理 ===")
    logger.info(f"5. 分割完整数据文件: {os.path.basename(complete_file)}")
    logger.info(f"分割配置: 每个文件 {SPLIT_CONFIG['chunk_size']} 条数据")
    
    try:
        # 执行分割，使用配置中的参数
        split_result = split_json_file(
            input_file_path=complete_file,
            chunk_size=SPLIT_CONFIG['chunk_size'],
            create_subdirs=SPLIT_CONFIG['create_subdirs']
        )
        
        if split_result["status"] == "success":
            logger.info("数据分割成功！")
            logger.info(get_split_summary(split_result))
            
            # 显示分割文件列表
            logger.info("分割文件列表:")
            for i, split_file in enumerate(split_result["split_files"], 1):
                filename = os.path.basename(split_file)
                logger.info(f"  {i}. {filename}")
                
        else:
            logger.error(f"数据分割失败: {split_result.get('error', '未知错误')}")
            
    except Exception as e:
        logger.error(f"分割数据时发生异常: {str(e)}")


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

    # 第四步：数据分割（使用配置文件中的设定）
    if saved_files and "complete_data" in saved_files and SPLIT_CONFIG['auto_split']:
        # 判断是否需要分割（数据量大于配置的split_threshold时进行分割）
        complete_count = len(complete_data)
        chunk_size = SPLIT_CONFIG['chunk_size']
        split_threshold = SPLIT_CONFIG['split_threshold']
        
        if complete_count > split_threshold:
            logger.info(f"完整数据量较大 ({complete_count} 条)，超过分割阈值 ({split_threshold} 条)，开始进行数据分割...")
            split_complete_data_files(saved_files)
        else:
            logger.info(f"完整数据量适中 ({complete_count} 条)，未超过分割阈值 ({split_threshold} 条)，无需分割")
    elif not SPLIT_CONFIG['auto_split']:
        logger.info("自动分割功能已禁用")
    else:
        logger.info("没有完整数据文件，跳过分割")

    # 显示不完整数据的详细信息
    if incomplete_data:
        logger.info(f"不完整数据详情 (共{len(incomplete_data)}条):")
        

    logger.info("=== ProductQuotation 步骤一：数据验证完成 === \n")
    

if __name__ == "__main__":
    main() 