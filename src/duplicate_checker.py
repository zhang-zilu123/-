import os
import json
from typing import List, Dict, Any,Tuple
from collections import defaultdict

from utils.logger_utils import setup_logger
from config.config import SPLIT_CONFIG

class DuplicateChecker:
    """
    重名检查器类（修正版）
    负责检查商品标题重复情况并按新格式输出
    """
    
    def __init__(self):
        """初始化重名检查器"""
        self.logger = setup_logger("duplicate_checker")
        self.chunk_size = SPLIT_CONFIG.get("chunk_size", 300)
        self.logger.info(f"重名检查器初始化完成，每文件商品数: {self.chunk_size}")

    def _are_prices_equal(self, price1: str, price2: str) -> bool:
        """
        比较两个价格字符串是否相等（考虑可能的格式差异）
        
        Args:
            price1: 第一个价格字符串
            price2: 第二个价格字符串
            
        Returns:
            价格是否相等
        """
        # 简单的字符串比较，因为需求要求"完全一致"
        return price1 == price2
    
    def _extract_sku_info(self, sku_list: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        提取SKU信息中的颜色规格和价格映射
        
        Args:
            sku_list: SKU商品详情列表
            
        Returns:
            颜色规格到价格的映射字典
        """
        sku_map = {}
        for sku in sku_list:
            color_spec = sku.get("颜色规格", "")
            price = sku.get("价格", "")
            if color_spec and price:
                sku_map[color_spec] = price
        return sku_map
    
    def _are_sku_info_equal(self, sku_list1: List[Dict[str, Any]], 
                           sku_list2: List[Dict[str, Any]]) -> bool:
        """
        比较两个商品的SKU信息是否完全一致
        
        Args:
            sku_list1: 第一个商品的SKU列表
            sku_list2: 第二个商品的SKU列表
            
        Returns:
            SKU信息是否一致
        """
        sku_map1 = self._extract_sku_info(sku_list1)
        sku_map2 = self._extract_sku_info(sku_list2)
        
        # 比较两个映射是否完全相同
        return sku_map1 == sku_map2

    def _filter_duplicate_products(self, title_groups: Dict[str, List[Dict[str, Any]]]) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        """
        对重名商品进行二次检查，按照新的规则进行分类：
        1. 价格相同的视为冗余，只保留一个
        2. 价格不同但公司相同的情况下：
        - SKU信息一致视为冗余，归入唯一商品
        - SKU信息不一致归入重名商品
        3. 公司不同视为不同产品，归入唯一商品
        
        Args:
            title_groups: 按标题分组的重名商品
            
        Returns:
            filtered_unique: 根据新规则归类的唯一商品
            filtered_duplicates: 根据新规则归类的重名商品
        """
        filtered_unique = []
        filtered_duplicates = defaultdict(list)
        total_duplicates = 0
        filtered_out = 0
        
        for title, products in title_groups.items():
            total_duplicates += len(products)
       
            # 首先按公司分组
            company_groups = defaultdict(list)
            for product in products:
                company_info = product.get("公司基本信息", {})
                company = company_info.get("公司名称", "") if isinstance(company_info, dict) else ""
                company_groups[company].append(product)
            
            # 对每个公司组进行处理
            for company, company_products in company_groups.items():
                # 在公司内部按价格分组
                price_groups = defaultdict(list)
                for product in company_products:
                    price = product.get("价格", "")
                    price_groups[price].append(product)
                
                # 处理价格相同的商品（去重）
                for price, price_group in price_groups.items():
                    if len(price_group) > 1:
                        # 价格相同的商品，只保留一个
                        filtered_unique.append(price_group[0])
                        filtered_out += len(price_group) - 1
                        self.logger.info(f"发现价格相同的重名商品: '{title}' 价格: '{price}', 过滤掉 {len(price_group)-1} 条冗余数据")
                
                # 获取所有价格唯一的商品
                unique_price_products = [product for product_list in price_groups.values() if len(product_list) == 1 
                                    for product in product_list]
                
                if len(unique_price_products) == 1:
                    # 公司下只有一个价格唯一的商品，归入唯一商品
                    filtered_unique.extend(unique_price_products)
                elif len(unique_price_products) > 1:
                    # 公司下有多个价格唯一的商品，需要比较SKU
                    self.logger.info(f"公司'{company}'下标题为'{title}'的商品有多个价格唯一的项，进行SKU信息比对")
                    base_product = unique_price_products[0]
                    base_sku_info = base_product.get("sku商品详情图片和信息", [])
                    
                    same_sku_products = [base_product]
                    different_sku_products = []
                    
                    for product in unique_price_products[1:]:
                        sku_info = product.get("sku商品详情图片和信息", [])
                        if self._are_sku_info_equal(base_sku_info, sku_info):
                            same_sku_products.append(product)
                        else:
                            different_sku_products.append(product)
                    
                    # SKU信息一致的只保留一个
                    if same_sku_products:
                        filtered_unique.append(same_sku_products[0])
                        filtered_out += len(same_sku_products) - 1
                        self.logger.info(f"发现同一公司'{company}'SKU信息一致的商品: '{title}', 过滤掉 {len(same_sku_products)-1} 条冗余数据")
                    
                    # SKU信息不一致的归入重名商品
                    if different_sku_products:
                        filtered_duplicates[title].extend(different_sku_products)
                        for prod in different_sku_products:
                            price = prod.get("价格", "")
                            self.logger.info(f"发现同一公司'{company}'SKU信息不一致的商品: '{title}' 价格: '{price}'")
        
        self.logger.info(f"重名商品二次检查：共处理 {total_duplicates} 个重名商品，过滤掉 {filtered_out} 个冗余商品")
        return filtered_unique, dict(filtered_duplicates)
    
    def normalize_title(self, title: str) -> str:
        """
        标准化商品标题（仅去除空格）
        
        Args:
            title: 原始商品标题
            
        Returns:
            标准化后的商品标题
        """
        if not title:
            return ""
        return title.replace(" ", "")
    
    def check_duplicates(self, input_dir: str, 
                        unique_output_dir: str, 
                        duplicate_output_dir: str) -> Dict[str, Any]:
        """
        检查商品标题重复情况并输出结果（修正版）
        
        Args:
            input_dir: 输入目录，包含step2清洗后的JSON文件
            unique_output_dir: 唯一商品输出目录
            duplicate_output_dir: 重名商品输出目录
            
        Returns:
            处理结果统计
        """
        # 创建输出目录
        os.makedirs(unique_output_dir, exist_ok=True)
        os.makedirs(duplicate_output_dir, exist_ok=True)
        
        self.logger.info(f"开始重名检查，输入目录: {input_dir}")
        self.logger.info(f"唯一商品输出目录: {unique_output_dir}")
        self.logger.info(f"重名商品输出目录: {duplicate_output_dir}")
        
        # 1. 收集所有商品数据
        all_products = []
        json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
        
        if not json_files:
            self.logger.error(f"输入目录 {input_dir} 中没有找到JSON文件")
            return {
                "total_files": 0,
                "total_products": 0,
                "unique_products": 0,
                "duplicate_products": 0,
                "unique_files": 0,
                "duplicate_files": 0
            }
        
        for file_name in json_files:
            file_path = os.path.join(input_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                    all_products.extend(products)
                self.logger.debug(f"已加载文件: {file_name}, 商品数量: {len(products)}")
            except Exception as e:
                self.logger.error(f"加载文件 {file_name} 时出错: {e}")
        
        self.logger.info(f"共加载 {len(all_products)} 条商品数据")
        
        # 2. 统计标题出现频率
        title_count = defaultdict(int)
        missing_title_count = 0
        
        for product in all_products:
            title = product.get("商品标题", "")
            if not title:
                missing_title_count += 1
                continue
                
            normalized_title = self.normalize_title(title)
            title_count[normalized_title] += 1
        
        if missing_title_count > 0:
            self.logger.warning(f"发现 {missing_title_count} 条记录缺少商品标题")
        
        # 3. 修正：按标题分组重名商品
        title_groups = defaultdict(list)
        unique_products = []
        
        # 按原始顺序处理商品
        for product in all_products:
            title = product.get("商品标题", "")
            if not title:
                continue
                
            normalized_title = self.normalize_title(title)
            if title_count[normalized_title] == 1:
                # 唯一商品
                unique_products.append(product)
            else:
                # 重名商品：按标题分组
                title_groups[normalized_title].append(product)
        
        # 4. 二次检查：对重名商品按价格进行过滤
        additional_unique, filtered_duplicates = self._filter_duplicate_products(title_groups)
        
        # 将价格相同的重名商品添加到唯一商品列表
        unique_products.extend(additional_unique)
        
        # 5. 修正：为唯一商品生成连续索引
        processed_unique_products = []
        for i, product in enumerate(unique_products):
            # 创建新字典，确保_unique_index在最前面
            new_product = {"_unique_index": i}
            
            # 移除原始索引（如果存在）并复制其他字段
            for key, value in product.items():
                if key != "_original_index":
                    new_product[key] = value
            
            processed_unique_products.append(new_product)
        
        unique_products = processed_unique_products
        
        # 6. 修正：将重名商品按标题分组展平
        # 保持原始数据中标题首次出现的顺序
        first_occurrence = {}
        for idx, product in enumerate(all_products):
            title = product.get("商品标题", "")
            if not title:
                continue
            normalized_title = self.normalize_title(title)
            if normalized_title in filtered_duplicates and normalized_title not in first_occurrence:
                first_occurrence[normalized_title] = idx
        
        # 按标题首次出现顺序排序
        sorted_titles = sorted(filtered_duplicates.keys(), key=lambda x: first_occurrence.get(x, float('inf')))
        duplicate_products = []
        for title in sorted_titles:
            duplicate_products.extend(filtered_duplicates[title])
        
        self.logger.info(f"发现 {len(unique_products)} 个唯一商品")
        self.logger.info(f"发现 {len(duplicate_products)} 个重名商品")
            
        # 6. 保存结果
        unique_files = self._save_results(
            unique_products, 
            unique_output_dir,
            "unique_data_"
        )
        
        duplicate_files = self._save_results(
            duplicate_products, 
            duplicate_output_dir,
            "duplicate_data_"
        )
        
        # 7. 生成统计报告
        result = {
            "total_files": len(json_files),
            "total_products": len(all_products),
            "missing_title_count": missing_title_count,
            "unique_products": len(unique_products),
            "duplicate_products": len(duplicate_products),
            "unique_files": len(unique_files),
            "duplicate_files": len(duplicate_files),
            "unique_output": unique_output_dir,
            "duplicate_output": duplicate_output_dir
        }
        
        self.logger.info(f"重名检查完成。唯一商品文件: {len(unique_files)}，重名商品文件: {len(duplicate_files)}")

        
        return result
    
    def _save_results(self, items: List[Dict[str, Any]], 
                     output_dir: str, prefix: str) -> List[str]:
        """
        保存结果到JSON文件（按300商品/文件分割）
        
        Args:
            items: 要保存的商品列表
            output_dir: 输出目录
            prefix: 文件名前缀
            
        Returns:
            生成的文件列表
        """
        if not items:
            self.logger.info(f"没有数据需要保存到 {output_dir}")
            return []
        
        # 按chunk_size分割
        chunk_size = self.chunk_size
        chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
        
        saved_files = []
        for i, chunk in enumerate(chunks):
            output_file = os.path.join(output_dir, f"{prefix}{i+1}.json")
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(chunk, f, ensure_ascii=False, indent=2)
                saved_files.append(output_file)
                self.logger.info(f"已保存 {len(chunk)} 个商品到 {output_file}")
            except Exception as e:
                self.logger.error(f"保存文件 {output_file} 时出错: {e}")
        
        return saved_files