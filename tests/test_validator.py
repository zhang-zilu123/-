"""
测试数据验证模块
"""
import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_validator import DataValidator


class TestDataValidator(unittest.TestCase):
    """数据验证器测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.validator = DataValidator()
        
        # 测试数据
        self.test_data = [
            {
                "商品标题": "猫窝大号四季通用棉编织睡窝",
                "时间": [["最早上架时间：2025-09-08 16:56:26"]],
                "价格": [["券后¥16.9"]],
                "销售": [["年销量", "0件"]],
                "商品详情": [["材质", "棉"]],
                "主产品图片": ["http://example.com/image1.jpg"],
                "商品详情图片": ["http://example.com/detail1.jpg"],
                "sku商品详情图片和信息": ["sku_info"],
                "产品网址": "http://example.com/product",
                "公司基本信息": [["公司名称"]]
            },
            {
                "商品标题": "另一个商品标题",
                "时间": None,  # 缺失
                "价格": "",    # 空字符串
                "销售": [],    # 空列表
                "商品详情": [["材质", "棉"]],
                "主产品图片": ["http://example.com/image2.jpg"],
                "商品详情图片": ["http://example.com/detail2.jpg"],
                "sku商品详情图片和信息": ["sku_info"],
                "产品网址": "http://example.com/product2",
                "公司基本信息": [["公司名称2"]]
            },
            {
                "商品标题": "第三个商品",
                "时间": [["时间信息"]],
                "价格": [["价格信息"]],
                "销售": [["销售信息"]],
                "商品详情": [["详情信息"]],
                "主产品图片": ["http://example.com/image3.jpg"],
                "商品详情图片": ["http://example.com/detail3.jpg"],
                "sku商品详情图片和信息": ["sku_info"],
                "产品网址": "http://example.com/product3",
                "公司基本信息": None  # 缺失
            }
        ]
    
    def test_validate_required_fields(self):
        """测试验证必需字段功能"""
        results = self.validator.validate_required_fields(self.test_data)
        
        # 检查总数
        self.assertEqual(results["total_count"], 3)
        
        # 检查完整数据数量（第1条数据完整）
        self.assertEqual(results["complete_count"], 1)
        
        # 检查不完整数据数量（第2、3条数据不完整）
        self.assertEqual(results["incomplete_count"], 2)
        
        # 检查完整数据内容
        self.assertEqual(len(results["complete_data"]), 1)
        self.assertEqual(results["complete_data"][0]["商品标题"], "猫窝大号四季通用棉编织睡窝")
        
        # 检查不完整数据内容
        self.assertEqual(len(results["incomplete_data"]), 2)
        
        # 检查缺失字段统计
        self.assertGreater(results["missing_fields_stats"]["时间"], 0)
        self.assertGreater(results["missing_fields_stats"]["价格"], 0)
        self.assertGreater(results["missing_fields_stats"]["销售"], 0)
        self.assertGreater(results["missing_fields_stats"]["公司基本信息"], 0)    
    def test_check_data_integrity(self):
        """测试检查数据完整性功能"""
        # 使用包含不完整数据的测试数据
        result = self.validator.check_data_integrity(self.test_data)
        self.assertFalse(result)  # 应该返回False，因为有不完整数据
        
        # 使用只包含完整数据的测试数据
        complete_only_data = [self.test_data[0]]  # 只有第一条是完整的
        result = self.validator.check_data_integrity(complete_only_data)
        self.assertTrue(result)  # 应该返回True，所有数据都完整
    
    def test_separate_data(self):
        """测试分离数据功能"""
        complete_data, incomplete_data = self.validator.separate_data(self.test_data)
        
        # 检查分离结果
        self.assertEqual(len(complete_data), 1)
        self.assertEqual(len(incomplete_data), 2)
        
        # 检查完整数据内容
        self.assertEqual(complete_data[0]["商品标题"], "猫窝大号四季通用棉编织睡窝")
        
        # 检查不完整数据是否包含缺失字段信息
        for item in incomplete_data:
            self.assertIn("_missing_fields", item)
            self.assertIn("_row_index", item)
    
    def test_generate_validation_report(self):
        """测试生成验证报告功能"""
        # 先进行验证
        self.validator.validate_required_fields(self.test_data)
        
        # 生成报告
        report = self.validator.generate_validation_report()
        
        # 检查报告内容
        self.assertIn("总数据量", report)
        self.assertIn("完整数据量", report)
        self.assertIn("不完整数据量", report)
        self.assertIn("完整率", report)
        self.assertIn("缺失字段统计", report)
        self.assertIn("必需字段", report)
        self.assertIn("验证时间", report)
        self.assertIn("字段缺失率", report)
        
        # 检查数值
        self.assertEqual(report["总数据量"], 3)
        self.assertEqual(report["完整数据量"], 1)
        self.assertEqual(report["不完整数据量"], 2)
        self.assertEqual(report["完整率"], "33.33%")
    
    @patch('builtins.open')
    @patch('os.makedirs')
    def test_save_validation_results(self, mock_makedirs, mock_open):
        """测试保存验证结果功能"""
        # 先进行验证
        self.validator.validate_required_fields(self.test_data)
        self.validator.generate_validation_report()
        
        # 保存结果
        with tempfile.TemporaryDirectory() as temp_dir:
            saved_files = self.validator.save_validation_results(temp_dir)
            
            # 检查返回的文件路径
            self.assertIn("complete_data", saved_files)
            self.assertIn("incomplete_data", saved_files)
            self.assertIn("validation_report", saved_files)
    
    def test_get_validation_summary(self):
        """测试获取验证摘要功能"""
        # 未验证前
        summary = self.validator.get_validation_summary()
        self.assertEqual(summary, "尚未进行数据验证")
        
        # 验证后
        self.validator.validate_required_fields(self.test_data)
        summary = self.validator.get_validation_summary()
        
        # 检查摘要内容
        self.assertIn("数据验证摘要", summary)
        self.assertIn("总数据量: 3", summary)
        self.assertIn("完整数据: 1", summary)
        self.assertIn("不完整数据: 2", summary)
        self.assertIn("完整率: 33.33%", summary)
        self.assertIn("缺失字段统计", summary)


if __name__ == '__main__':
    unittest.main()