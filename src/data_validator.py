"""
数据验证模块 - 检查数据完整性，识别缺失字段
实现第一步：判断每个字段是否为None
"""
import logging
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from collections import defaultdict
import json
from datetime import datetime

# 导入配置和工具函数
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import REQUIRED_FIELDS, VALIDATION_CONFIG, LOGGING_CONFIG
from utils.validation_utils import (
    is_none_or_empty, 
    check_required_fields, 
    is_data_complete,
    get_missing_fields
)
from utils.data_utils import (
    convert_excel_to_dict_list,
    separate_complete_incomplete_data,
    create_validation_summary
)


class DataValidator:
    """
    数据验证器类
    负责检查数据完整性，分离完整和不完整的数据
    """
    
    def __init__(self, required_fields: Optional[List[str]] = None):
        """
        初始化数据验证器
        
        Args:
            required_fields: 必需字段列表，如果为None则使用配置中的默认值
        """
        self.required_fields = required_fields or REQUIRED_FIELDS
        self.validation_config = VALIDATION_CONFIG
        self.logger = self._setup_logger()
        
        # 验证结果存储
        self.validation_results = {
            "total_count": 0,
            "complete_count": 0, 
            "incomplete_count": 0,
            "complete_data": [],
            "incomplete_data": [],
            "missing_fields_stats": defaultdict(int),
            "validation_report": {}
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
        
        # 创建文件处理器
        os.makedirs(os.path.dirname(LOGGING_CONFIG["file_path"]), exist_ok=True)
        file_handler = logging.FileHandler(LOGGING_CONFIG["file_path"], encoding='utf-8')
        file_handler.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
        
        # 创建格式器
        formatter = logging.Formatter(LOGGING_CONFIG["format"])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger    
    def validate_required_fields(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证必需字段的完整性
        
        Args:
            data: 要验证的数据列表
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        self.logger.info(f"开始验证数据，共 {len(data)} 条记录")
        
        # 重置验证结果
        self.validation_results = {
            "total_count": len(data),
            "complete_count": 0,
            "incomplete_count": 0,
            "complete_data": [],
            "incomplete_data": [],
            "missing_fields_stats": defaultdict(int),
            "validation_report": {}
        }
        
        # 遍历每行数据进行验证
        for index, row in enumerate(data):
            missing_fields = get_missing_fields(row, self.required_fields)
            
            if not missing_fields:
                # 数据完整
                self.validation_results["complete_data"].append(row)
                self.validation_results["complete_count"] += 1
            else:
                # 数据不完整
                row_with_index = row.copy()
                row_with_index["_missing_fields"] = missing_fields
                row_with_index["_row_index"] = index
                
                self.validation_results["incomplete_data"].append(row_with_index)
                self.validation_results["incomplete_count"] += 1
                
                # 统计缺失字段
                for field in missing_fields:
                    self.validation_results["missing_fields_stats"][field] += 1
        
        self.logger.info(f"验证完成：完整数据 {self.validation_results['complete_count']} 条，"
                        f"不完整数据 {self.validation_results['incomplete_count']} 条")
        
        return self.validation_results
    
    def check_data_integrity(self, data: List[Dict[str, Any]]) -> bool:
        """
        检查数据完整性
        
        Args:
            data: 要检查的数据列表
            
        Returns:
            bool: 如果所有数据都完整则返回True
        """
        validation_results = self.validate_required_fields(data)
        return validation_results["incomplete_count"] == 0    
    def separate_data(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        分离完整和不完整的数据
        
        Args:
            data: 原始数据列表
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (完整数据列表, 不完整数据列表)
        """
        self.logger.info("开始分离完整和不完整数据")
        
        # 如果还没有进行验证，先进行验证
        if self.validation_results["total_count"] == 0:
            self.validate_required_fields(data)
        
        complete_data = self.validation_results["complete_data"]
        incomplete_data = self.validation_results["incomplete_data"]
        
        self.logger.info(f"数据分离完成：完整数据 {len(complete_data)} 条，不完整数据 {len(incomplete_data)} 条")
        
        return complete_data, incomplete_data
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """
        生成验证报告
        
        Returns:
            Dict[str, Any]: 验证报告
        """
        if self.validation_results["total_count"] == 0:
            self.logger.warning("尚未进行数据验证，无法生成报告")
            return {}
        
        # 创建详细的验证报告
        report = create_validation_summary(
            total_count=self.validation_results["total_count"],
            complete_count=self.validation_results["complete_count"],
            incomplete_count=self.validation_results["incomplete_count"],
            missing_fields_stats=dict(self.validation_results["missing_fields_stats"])
        )
        
        # 添加额外信息
        report["必需字段"] = self.required_fields
        report["验证配置"] = self.validation_config
        
        # 计算字段缺失率
        field_missing_rates = {}
        for field, missing_count in self.validation_results["missing_fields_stats"].items():
            missing_rate = (missing_count / self.validation_results["total_count"]) * 100
            field_missing_rates[field] = f"{missing_rate:.2f}%"
        
        report["字段缺失率"] = field_missing_rates
        
        self.validation_results["validation_report"] = report
        
        self.logger.info("验证报告生成完成")
        return report    
    def save_validation_results(self, output_dir: str = "data/output") -> Dict[str, str]:
        """
        保存验证结果到文件
        
        Args:
            output_dir: 输出目录
            
        Returns:
            Dict[str, str]: 保存的文件路径
        """
        if self.validation_results["total_count"] == 0:
            self.logger.warning("尚未进行数据验证，无法保存结果")
            return {}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}
        
        try:
            # 保存完整数据
            if self.validation_results["complete_data"]:
                complete_file = f"{output_dir}/complete/complete_data_{timestamp}.json"
                os.makedirs(os.path.dirname(complete_file), exist_ok=True)
                
                with open(complete_file, 'w', encoding='utf-8') as f:
                    json.dump(self.validation_results["complete_data"], f, 
                             ensure_ascii=False, indent=2)
                
                saved_files["complete_data"] = complete_file
                self.logger.info(f"完整数据已保存到: {complete_file}")
            
            # 保存不完整数据
            if self.validation_results["incomplete_data"]:
                incomplete_file = f"{output_dir}/incomplete/incomplete_data_{timestamp}.json"
                os.makedirs(os.path.dirname(incomplete_file), exist_ok=True)
                
                with open(incomplete_file, 'w', encoding='utf-8') as f:
                    json.dump(self.validation_results["incomplete_data"], f, 
                             ensure_ascii=False, indent=2)
                
                saved_files["incomplete_data"] = incomplete_file
                self.logger.info(f"不完整数据已保存到: {incomplete_file}")
            
            # 保存验证报告
            if self.validation_results["validation_report"]:
                report_file = f"{output_dir}/logs/validation_report_{timestamp}.json"
                os.makedirs(os.path.dirname(report_file), exist_ok=True)
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(self.validation_results["validation_report"], f, 
                             ensure_ascii=False, indent=2)
                
                saved_files["validation_report"] = report_file
                self.logger.info(f"验证报告已保存到: {report_file}")
        
        except Exception as e:
            self.logger.error(f"保存验证结果时发生错误: {str(e)}")
            raise
        
        return saved_files
    
    def get_validation_summary(self) -> str:
        """
        获取验证结果摘要信息
        
        Returns:
            str: 验证摘要字符串
        """
        if self.validation_results["total_count"] == 0:
            return "尚未进行数据验证"
        
        summary = f"""
数据验证摘要：
=============
总数据量: {self.validation_results['total_count']}
完整数据: {self.validation_results['complete_count']} 条
不完整数据: {self.validation_results['incomplete_count']} 条
完整率: {(self.validation_results['complete_count'] / self.validation_results['total_count'] * 100):.2f}%

缺失字段统计:
"""
        
        for field, count in self.validation_results["missing_fields_stats"].items():
            rate = (count / self.validation_results["total_count"]) * 100
            summary += f"  {field}: {count} 条 ({rate:.2f}%)\n"
        
        return summary