"""
数据清洗模块 - 将完整的原始数据转换为标准化JSON格式
实现第二步：对验证通过的完整数据进行字段清洗和格式转换
"""
import json
import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from collections import defaultdict

# 导入配置和工具函数
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import REQUIRED_FIELDS, OUTPUT_SETTINGS, PROCESSING_RULES
from utils.logger_utils import setup_logger
from utils.validation_utils import is_none_or_empty
import ast


class DataCleaner:
    """
    数据清洗器类
    负责将原始的完整数据转换为标准化的JSON格式
    """
    
    def __init__(self):
        """
        初始化数据清洗器
        
        Args:
            log_file_path: 日志文件路径，如果为None则使用默认路径
        """
        self.logger = setup_logger(log_name="step2_data_cleaner")
        self.output_settings = OUTPUT_SETTINGS
        self.processing_rules = PROCESSING_RULES
        
        # 清洗结果存储
        self.cleaning_results = {
            "total_count": 0,
            "success_count": 0,
            "error_count": 0,
            "cleaned_data": [],
            "error_data": [],
            "cleaning_report": {}
        }
        
        self.logger.info("数据清洗器初始化完成")
    
    def _safe_parse_string_list(self, value: Any) -> Any:
        """
        安全地解析字符串化的列表数据
        
        Args:
            value: 可能是字符串化的列表或原始数据
            
        Returns:
            解析后的数据或原始数据
        """
        if isinstance(value, str) and (value.startswith('[') or value.startswith("'[")):
            try:
                # 使用ast.literal_eval更安全地解析
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                # 如果解析失败，返回原始字符串
                return value
        return value
    
    def clean_product_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        清洗商品数据主函数
        
        Args:
            data: 完整的原始数据列表
            
        Returns:
            Dict[str, Any]: 清洗结果
        """
        self.logger.info(f"开始清洗数据，共 {len(data)} 条记录")
        
        # 重置清洗结果
        self.cleaning_results = {
            "total_count": len(data),
            "success_count": 0,
            "error_count": 0,
            "cleaned_data": [],
            "error_data": [],
            "cleaning_report": {}
        }
        
        # 逐条清洗数据
        for index, row in enumerate(data):
            try:
                cleaned_item = self._clean_single_item(row, index)
                if cleaned_item:
                    self.cleaning_results["cleaned_data"].append(cleaned_item)
                    self.cleaning_results["success_count"] += 1
                else:
                    self._handle_cleaning_error(row, index, "清洗后数据为空")
                    
            except Exception as e:
                self.logger.error(f"清洗第 {index} 条数据时出错: {e}")
                self._handle_cleaning_error(row, index, str(e))
        
        # 生成清洗报告
        self._generate_cleaning_report()
        
        self.logger.info(f"数据清洗完成：成功 {self.cleaning_results['success_count']} 条，"
                        f"失败 {self.cleaning_results['error_count']} 条")
        
        return self.cleaning_results
    
    def _clean_single_item(self, item: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """
        清洗单个数据项
        
        Args:
            item: 单个原始数据项
            index: 数据项索引
            
        Returns:
            Optional[Dict[str, Any]]: 清洗后的数据项，失败时返回None
        """
        cleaned_item = {
            "_original_index": index,
        }
        
        # 清洗各个字段
        field_cleaners = {
            "商品标题": self._clean_title,
            "时间": self._clean_time_data,
            "价格": self._clean_price_data,
            "销售": self._clean_sales_data,
            "商品详情": self._clean_product_details,
            "包装重量": self._clean_package_weight,
            "主产品图片": self._clean_image_urls,
            "商品详情图片": self._clean_image_urls,
            "sku商品详情图片和信息": self._clean_sku_data,
            "产品网址": self._clean_product_url,
            "公司基本信息": self._clean_company_info,
            "公司详情信息": self._clean_company_details
        }
        
        for field_name, cleaner_func in field_cleaners.items():
            try:
                raw_value = item.get(field_name)
                if not is_none_or_empty(raw_value):
                    # 先尝试解析字符串化的列表数据
                    parsed_value = self._safe_parse_string_list(raw_value)
                    cleaned_value = cleaner_func(parsed_value)
                    if cleaned_value is not None:
                        cleaned_item[field_name] = cleaned_value
                    else:
                        self.logger.warning(f"字段 '{field_name}' 清洗后为空，索引: {index}")
                else:
                    self.logger.warning(f"字段 '{field_name}' 原始数据为空，索引: {index}")
                    
            except Exception as e:
                self.logger.error(f"清洗字段 '{field_name}' 时出错，索引: {index}，错误: {e}")
                # 继续处理其他字段，不因单个字段错误而失败
        
        return cleaned_item if len(cleaned_item) > 2 else None  # 除了元数据外至少要有一个业务字段
    
    def _clean_title(self, raw_title: Any) -> Optional[str]:
        """
        清洗商品标题
        
        输入格式: [['猫窝大号四季通用棉编织睡窝舒适耐磨耐抓猫咪睡觉宠物用品']]
        输出格式: "猫窝大号四季通用棉编织睡窝舒适耐磨耐抓猫咪睡觉宠物用品"
        """
        try:
            if isinstance(raw_title, list) and len(raw_title) > 0:
                if isinstance(raw_title[0], list) and len(raw_title[0]) > 0:
                    title = str(raw_title[0][0]).strip()
                    return title if title else None
            elif isinstance(raw_title, str):
                return raw_title.strip() if raw_title.strip() else None
        except Exception:
            pass
        
        return None
    
    def _clean_time_data(self, raw_time: Any) -> Optional[Dict[str, str]]:
        """
        清洗时间数据
        
        输入格式: [['最早上架时间：2025-09-08 16:56:26'], ['最新发布时间：2025-09-17 15:28:44']]
        输出格式: {"最早上架时间": "2025-09-08 16:56:26", "最新发布时间": "2025-09-17 15:28:44"}
        """
        if not isinstance(raw_time, list):
            return None
        
        time_dict = {}
        for item in raw_time:
            if isinstance(item, list) and len(item) > 0:
                time_str = str(item[0])
                if '：' in time_str or ':' in time_str:
                    # 使用中文冒号或英文冒号分割
                    parts = time_str.split('：') if '：' in time_str else time_str.split(':')
                    if len(parts) >= 2:
                        key = parts[0].strip()
                        value = ':'.join(parts[1:]).strip()
                        if key and value:
                            time_dict[key] = value
        
        return time_dict if time_dict else None
    
    def _clean_price_data(self, raw_price: Any) -> Optional[Dict[str, str]]:
        """
        清洗价格数据: 
        - 单个 \n 删除
        - 两个及以上连续 \n 替换为空格
        """
        if not isinstance(raw_price, list) or len(raw_price) == 0:
            return None

        # 取出原始文本（兼容 [[str]] 或 [str] 两种结构）
        first = raw_price[0]
        price_text_raw = str(first[0]) if isinstance(first, list) and len(first) > 0 else str(first)
        price_text_raw = price_text_raw.replace('\r\n', '\n').strip()

        # 两个及以上换行替换为空格
        price_text_raw = re.sub(r'\n{2,}', ' ', price_text_raw)
        # 单个换行去掉
        price_text_raw = price_text_raw.replace('\n', '')

        return price_text_raw
    
    def _clean_sales_data(self, raw_sales: Any) -> Optional[Dict[str, str]]:
        """
        清洗销售数据
        
        输入格式: [['年销量', '0件'], ['近30天销量', '0件']]
        输出格式: {"年销量": "0件", "近30天销量": "0件"}
        """
        if not isinstance(raw_sales, list):
            return None
        
        sales_dict = {}
        for item in raw_sales:
            if isinstance(item, list) and len(item) >= 2:
                key = str(item[0]).strip()
                value = str(item[1]).strip()
                if key and value:
                    sales_dict[key] = value
        
        return sales_dict if sales_dict else None
    
    def _clean_product_details(self, raw_details: Any) -> Optional[Dict[str, str]]:
        """
        清洗商品详情
        
        输入格式: [['材质', '棉', '产地', '山东'], ['是否进口', '否']]
        输出格式: {"材质": "棉", "产地": "山东", "是否进口": "否"}
        """
        if not isinstance(raw_details, list):
            return None
        
        details_dict = {}
        for item in raw_details:
            if isinstance(item, list):
                # 按照偶数索引为键，奇数索引为值的规则配对
                for i in range(0, len(item) - 1, 2):
                    if i + 1 < len(item):
                        key = str(item[i]).strip()
                        value = str(item[i + 1]).strip()
                        # 跳过关键词为"否"的项
                        if key and value and key != "否":
                            details_dict[key] = value
        
        return details_dict if details_dict else None
    
    def _clean_package_weight(self, raw_weight: Any) -> List[Dict[str, Union[str, int]]]:
        """
        清洗包装重量数据
        
        输入格式: [['规格\t颜色\t长(cm)\t宽(cm)\t高(cm)\t体积(cm³)\t重量(g)\n大号【直径约50厘米】\t蓝色\t50\t50\t13\t32500\t810\n...']]
        输出格式: [{"规格": "大号【直径约50厘米】", "颜色": "蓝色", "长(cm)": 50, ...}] 或空字符串
        """
        if raw_weight is None:
            return ""
        
        try:
            if isinstance(raw_weight, list) and len(raw_weight) > 0:
                if isinstance(raw_weight[0], list) and len(raw_weight[0]) > 0:
                    table_str = str(raw_weight[0][0]).strip()
                elif isinstance(raw_weight[0], str):
                    table_str = raw_weight[0].strip()
                else:
                    return ""
            elif isinstance(raw_weight, str):
                table_str = raw_weight.strip()
            else:
                return ""
            
            if not table_str:
                return ""
            
            # 按行分割（处理\r\n和\n）
            lines = table_str.replace('\\n', '\n').split('\n')
            if len(lines) < 2:  # 至少需要表头和一行数据
                return ""
            
            # 第一行为表头
            headers = lines[0].split('\t')
            if not headers:
                return ""
            
            # 解析数据行
            result = []
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                values = line.split('\t')
                if len(values) != len(headers):
                    continue
                
                row_dict = {}
                for i, header in enumerate(headers):
                    header = header.strip()
                    value = values[i].strip() if i < len(values) else ""
                    
                    # 数值型字段转换为数字
                    if '(cm)' in header or '(cm³)' in header or '(g)' in header:
                        try:
                            row_dict[header] = int(value) if value.isdigit() else value
                        except ValueError:
                            row_dict[header] = value
                    else:
                        row_dict[header] = value
                
                if row_dict:
                    result.append(row_dict)
            
            return result if result else ""
        
        except Exception:
            return ""
    
    def _clean_image_urls(self, raw_images: Any) -> Optional[List[str]]:
        """
        清洗图片URL列表
        
        输入格式: ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
        输出格式: ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
        """
        if isinstance(raw_images, list):
            urls = []
            for item in raw_images:
                url = str(item).strip()
                if url and (url.startswith('http://') or url.startswith('https://')):
                    urls.append(url)
            return urls if urls else None
        elif isinstance(raw_images, str):
            url = raw_images.strip()
            if url and (url.startswith('http://') or url.startswith('https://')):
                return [url]
        
        return None
    
    def _clean_sku_data(self, raw_sku: Any) -> Optional[List[Dict[str, str]]]:
        """
        清洗 SKU 数据，返回指定格式：
        {
        "sku商品详情图片和信息": [
            {"颜色规格": "...", "图片": "...", "价格": "..."},
            ...
        ]
        }

        输入格式:
        - 字符串表格数据（行用\r\n或\n分隔，列用\t分隔）
        - 或者列表，每个元素是一行 SKU 信息
        """

        if raw_sku is None:
            return None

        sku_items = []

        # 统一转成行列表
        if isinstance(raw_sku, str):
            lines = raw_sku.replace("\r\n", "\n").split("\n")
        elif isinstance(raw_sku, list):
            lines = [str(item) for item in raw_sku]
        else:
            return None

        for line in lines:
            line = line.strip()
            if not line or "\t" not in line:
                continue

            parts = line.split("\t")

            # 按固定列数解析：颜色规格在第4列，图片在第5列，价格在第6列
            color_spec = parts[3].strip() if len(parts) > 3 else ""
            image_url = parts[4].strip() if len(parts) > 4 and parts[4].startswith("http") else ""
            price = parts[5].strip() if len(parts) > 5 and parts[5] != "--" else ""

            sku_items.append({
                "颜色规格": color_spec,
                "图片": image_url,
                "价格": price
            })

        return sku_items if sku_items else None
    
    def _clean_product_url(self, raw_url: Any) -> Optional[str]:
        """
        清洗产品网址
        
        输入格式: "https://dj.1688.com/ci_bb?a=19394&e=..."
        输出格式: "https://dj.1688.com/ci_bb?a=19394&e=..."
        """
        if isinstance(raw_url, str):
            url = raw_url.strip()
            if url and (url.startswith('http://') or url.startswith('https://')):
                return url
        
        return None
    
    def _clean_company_info(self, raw_company: Any) -> Optional[Dict[str, str]]:
        """
        清洗公司基本信息
        
        输入格式: [['公司名称'], ['回头率信息'], ['成立时间信息'], ['公司简介']]
        输出格式: {"公司名称": "...", "回头率": "...", "成立时间": "...", ...}
        """
        if not isinstance(raw_company, list):
            return None
        
        company_dict = {}
        
        for i, item in enumerate(raw_company):
            if isinstance(item, list) and len(item) > 0:
                content = str(item[0])
                
                if i == 0:
                    # 第一个元素通常是公司名称
                    company_dict["公司名称"] = content.strip()
                elif i == 1:
                    # 第二个元素包含回头率等信息
                    if "回头率" in content:
                        match = re.search(r'回头率\s*(\d+%)', content)
                        if match:
                            company_dict["回头率"] = match.group(1)
                    if "主营" in content:
                        parts = content.split("主营")
                        if len(parts) > 1:
                            company_dict["主营"] = parts[1].strip()
                elif i == 2:
                    # 第三个元素包含成立时间
                    if "成立时间" in content:
                        match = re.search(r'成立时间\s*(\d{4}-\d{2}-\d{2})', content)
                        if match:
                            company_dict["成立时间"] = match.group(1)
                elif i == 3:
                    # 第四个元素是公司简介
                    if "进入黄页" in content:
                        intro = content.split("进入黄页")[0].strip()
                        if intro:
                            company_dict["公司简介"] = intro
                    else:
                        company_dict["公司简介"] = content.strip()
        
        return company_dict if company_dict else None
    
    def _clean_company_details(self, raw_details: Any) -> Union[Dict[str, str], Dict[str, Dict[str, str]]]:
        """
        清洗公司详情信息
        
        输入格式1: [['经营模式\\n生产型\\n年交易额\\n0万\\n代工模式\\nOEM,ODM,OBM\\n厂房面积\\n17701m²']]
        输入格式2: [['基本信息\\n注册资金\\n人民币200万元\\n经营模式\\n生产厂家\\n行业信息\\n主要市场\\n全国\\n经营信息\\n品牌名称\\n丰渔行']]
        输出格式: 根据内容结构返回相应的字典格式，如果为空则返回空字符串
        """
        if raw_details is None:
            return ""
        
        try:
            if isinstance(raw_details, list) and len(raw_details) > 0:
                if isinstance(raw_details[0], list) and len(raw_details[0]) > 0:
                    details_str = str(raw_details[0][0]).strip()
                elif isinstance(raw_details[0], str):
                    details_str = raw_details[0].strip()
                else:
                    return ""
            elif isinstance(raw_details, str):
                details_str = raw_details.strip()
            else:
                return ""
            
            if not details_str:
                return ""
            
            # 清理换行符
            details_str = details_str.replace('\\n', '\n')
            
            # 按换行符分割
            parts = [part.strip() for part in details_str.split('\n') if part.strip()]
            
            if not parts:
                return ""
            
            # 情况1：开头为"经营模式"（简单键值对结构）
            if parts[0] == "经营模式":
                result = {}
                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts):
                        key = parts[i].strip()
                        value = parts[i + 1].strip()
                        if key and value:
                            result[key] = value
                return result if result else ""
            
            # 情况2：开头为"基本信息"（三层结构）
            elif parts[0] == "基本信息":
                result = {}
                current_section = None
                
                i = 1  # 跳过"基本信息"
                while i < len(parts):
                    part = parts[i]
                    
                    # 检查是否是新的主要分类
                    if part in ["行业信息", "经营信息"]:
                        current_section = part
                        result[current_section] = {}
                        i += 1
                    else:
                        # 处理键值对
                        if i + 1 < len(parts):
                            key = part
                            value = parts[i + 1]
                            
                            if current_section:
                                result[current_section][key] = value
                            else:
                                # 基本信息部分
                                if "基本信息" not in result:
                                    result["基本信息"] = {}
                                result["基本信息"][key] = value
                            
                            i += 2  # 跳过键和值
                        else:
                            i += 1
                
                return result if result else ""
            
            # 其他情况：尝试简单的键值对解析
            else:
                result = {}
                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts):
                        key = parts[i].strip()
                        value = parts[i + 1].strip()
                        if key and value:
                            result[key] = value
                return result if result else ""
        
        except Exception:
            return ""
    
    def _handle_cleaning_error(self, item: Dict[str, Any], index: int, error_msg: str):
        """
        处理清洗错误
        """
        error_item = {
            "_original_index": index,
            "_error_message": error_msg,
            "_error_time": datetime.now().isoformat(),
            "_original_data": item
        }
        
        self.cleaning_results["error_data"].append(error_item)
        self.cleaning_results["error_count"] += 1
    
    def _generate_cleaning_report(self):
        """
        生成清洗报告
        """
        total = self.cleaning_results["total_count"]
        success = self.cleaning_results["success_count"]
        error = self.cleaning_results["error_count"]
        
        self.cleaning_results["cleaning_report"] = {
            "总数据量": total,
            "成功清洗": success,
            "清洗失败": error,
            "成功率": f"{(success / total * 100):.2f}%" if total > 0 else "0%",
            "失败率": f"{(error / total * 100):.2f}%" if total > 0 else "0%",
            "清洗时间": datetime.now().isoformat()
        }
    

    
    def convert_to_json(self, indent: Optional[int] = None) -> str:
        """
        将清洗结果转换为JSON字符串
        
        Args:
            indent: JSON缩进，如果为None则使用配置中的默认值
            
        Returns:
            str: JSON字符串
        """
        indent_value = indent if indent is not None else self.output_settings.get("indent", 2)
        
        try:
            return json.dumps(
                self.cleaning_results["cleaned_data"],
                ensure_ascii=False,
                indent=indent_value
            )
        except Exception as e:
            self.logger.error(f"转换JSON时出错: {e}")
            return "[]"
    

    
    def save_cleaned_data(self, output_path: str) -> bool:
        """
        保存清洗后的数据到文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    self.cleaning_results["cleaned_data"],
                    f,
                    ensure_ascii=False,
                    indent=self.output_settings.get("indent", 2)
                )
            
            self.logger.info(f"清洗数据已保存到: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存清洗数据时出错: {e}")
            return False
    
    def save_error_data(self, output_path: str) -> bool:
        """
        保存清洗失败的数据到文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if not self.cleaning_results["error_data"]:
                self.logger.info("没有清洗失败的数据需要保存")
                return True
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    self.cleaning_results["error_data"],
                    f,
                    ensure_ascii=False,
                    indent=self.output_settings.get("indent", 2)
                )
            
            self.logger.info(f"清洗失败数据已保存到: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存清洗失败数据时出错: {e}")
            return False 
        

