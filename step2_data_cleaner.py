"""
步骤二：数据清洗模块使用示例
演示如何使用DataCleaner进行数据清洗和格式转换
输入：步骤1生成的complete数据JSON文件
输出：清洗后的标准化JSON数据
"""
import sys
import os
import json
import glob
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_cleaner import DataCleaner
from utils import setup_logger


def find_complete_json_files(complete_dir):
    """查找complete目录中的所有JSON文件"""
    logger = setup_logger("step2_data_cleaner")
    
    try:
        # 查找所有JSON文件
        json_pattern = os.path.join(complete_dir, "*.json")
        json_files = glob.glob(json_pattern)
        
        if not json_files:
            logger.warning(f"在目录 {complete_dir} 中没有找到JSON文件")
            return []
        
        logger.info(f"找到 {len(json_files)} 个JSON文件 {json_files}")
       
        return json_files
        
    except Exception as e:
        logger.error(f"查找JSON文件时出错: {e}")
        return []


def load_complete_data_from_json(json_path):
    """从步骤1生成的complete JSON文件读取完整数据"""
    logger = setup_logger("step2_data_cleaner")
    
    try:
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"成功读取JSON文件: {json_path}")
        logger.info(f"数据条数: {len(data)}")
        
        return data
        
    except FileNotFoundError:
        logger.error(f"JSON文件不存在: {json_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON文件格式错误: {e}")
        return None
    except Exception as e:
        logger.error(f"读取JSON文件时出错: {e}")
        return None


def process_single_json_file(json_file_path, output_dir):
    """处理单个JSON文件的数据清洗"""
    logger = setup_logger("step2_data_cleaner")
    logger.info(f"正在处理文件: {os.path.basename(json_file_path)}")

    
    # 读取完整数据
    complete_data = load_complete_data_from_json(json_file_path)
    
    if complete_data is None or not complete_data:
        logger.error(f"无法读取文件或文件为空: {json_file_path}")
        return False, 0
    
    logger.info(f"数据统计: {len(complete_data)} 条完整数据")
    
    # 数据清洗
    cleaner = DataCleaner()
    cleaning_results = cleaner.clean_product_data(complete_data)
    
    
    # 生成输出文件名
    input_filename = Path(json_file_path).stem
    timestamp = input_filename.split('_')[-1] if '_' in input_filename else "unknown"
    
    # 保存数据
    success_file = os.path.join(output_dir, "step2_cleandata", "complete", f"cleaned_data_{timestamp}.json")
    error_file = os.path.join(output_dir, "step2_cleandata", "error", f"cleaning_errors_{timestamp}.json")
    
    success = cleaner.save_cleaned_data(success_file)
    if cleaning_results["error_data"]:
        cleaner.save_error_data(error_file)
    
    return success, len(complete_data)

def main():
    """主函数 - 批量处理complete目录中的所有JSON文件"""
    
    # 设置主程序logger
    logger = setup_logger("step2_data_cleaner")
    logger.info("=== ProductQuotation 步骤二：批量数据清洗开始 ===")
    
    # 第一步：查找complete目录中的所有JSON文件
    logger.info("第一步：查找步骤1生成的完整数据 complete文件夹...")
    
    complete_dir = r"data\output\step1_data_validator\split_data"
    
    if not os.path.exists(complete_dir):
        logger.error(f"错误：complete目录不存在: {complete_dir}")
        return
    
    # 查找所有JSON文件
    json_files = find_complete_json_files(complete_dir)
    
    if not json_files:
        logger.error(f"错误：在 {complete_dir} 中没有找到JSON文件")
        return
    
    logger.info(f"找到 {len(json_files)} 个JSON文件:")
    for i, file in enumerate(json_files, 1):
        logger.info(f"  {i}. {os.path.basename(file)}")
    
    # 第二步：确保输出目录存在
    output_dir = os.path.join("data", "output")
    os.makedirs(os.path.join(output_dir, "step2_cleandata","complete"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "step2_cleandata","error"), exist_ok=True)
    
    # 第三步：批量处理每个JSON文件
    logger.info(f"第二步：开始批量处理 {len(json_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    total_cleaned_items = 0
    
    for i, json_file in enumerate(json_files, 1):
        logger.info(f"处理进度: {i}/{len(json_files)}")
        
        try:
            success, item_count = process_single_json_file(json_file, output_dir)
            if success:
                success_count += 1
                total_cleaned_items += item_count
            else:
                error_count += 1
                
        except Exception as e:
            logger.error(f"处理文件 {json_file} 时出现异常: {e}")
            error_count += 1
    

    
    # 第四步：显示总体统计
    logger.info("批量处理总结")
    logger.info(f"总文件数: {len(json_files)}")
    logger.info(f"成功处理: {success_count}")
    logger.info(f"处理失败: {error_count}")
    logger.info(f"总数据条数: {total_cleaned_items}")
    logger.info(f"处理成功率: {(success_count/len(json_files)*100):.2f}%")



    logger.info(f"=== 批量数据清洗流程完成 ===")


if __name__ == "__main__":
    main() 