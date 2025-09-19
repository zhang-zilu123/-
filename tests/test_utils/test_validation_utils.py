"""
测试验证工具函数
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.validation_utils import (
    is_none_or_empty,
    check_required_fields, 
    is_data_complete,
    get_missing_fields
)


class TestValidationUtils(unittest.TestCase):
    """验证工具函数测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.required_fields = ["商品标题", "时间", "价格", "销售", "商品详情"]
        
        # 完整数据示例
        self.complete_data = {
            "商品标题": "猫窝大号四季通用棉编织睡窝",
            "时间": [["最早上架时间：2025-09-08 16:56:26"]],
            "价格": [["券后¥16.9"]],
            "销售": [["年销量", "0件"]],
            "商品详情": [["材质", "棉"]]
        }
        
        # 不完整数据示例
        self.incomplete_data = {
            "商品标题": "猫窝大号四季通用棉编织睡窝",
            "时间": None,
            "价格": "",
            "销售": [],
            "商品详情": [["材质", "棉"]]
        }
    
    def test_is_none_or_empty(self):
        """测试is_none_or_empty函数"""
        # 测试None值
        self.assertTrue(is_none_or_empty(None))
        
        # 测试空字符串
        self.assertTrue(is_none_or_empty(""))
        self.assertTrue(is_none_or_empty("   "))  # 空白字符串
        
        # 测试空列表和字典
        self.assertTrue(is_none_or_empty([]))
        self.assertTrue(is_none_or_empty({}))
        
        # 测试非空值
        self.assertFalse(is_none_or_empty("有效数据"))
        self.assertFalse(is_none_or_empty([1, 2, 3]))
        self.assertFalse(is_none_or_empty({"key": "value"}))
        self.assertFalse(is_none_or_empty(0))  # 数字0不应该被认为是空    
    def test_check_required_fields(self):
        """测试check_required_fields函数"""
        # 测试完整数据
        result = check_required_fields(self.complete_data, self.required_fields)
        expected = {field: True for field in self.required_fields}
        self.assertEqual(result, expected)
        
        # 测试不完整数据
        result = check_required_fields(self.incomplete_data, self.required_fields)
        expected = {
            "商品标题": True,
            "时间": False,
            "价格": False, 
            "销售": False,
            "商品详情": True
        }
        self.assertEqual(result, expected)
        
        # 测试缺少字段的数据
        partial_data = {"商品标题": "测试标题"}
        result = check_required_fields(partial_data, self.required_fields)
        self.assertTrue(result["商品标题"])
        self.assertFalse(result["时间"])
        self.assertFalse(result["价格"])
        self.assertFalse(result["销售"])
        self.assertFalse(result["商品详情"])
    
    def test_is_data_complete(self):
        """测试is_data_complete函数"""
        # 测试完整数据
        self.assertTrue(is_data_complete(self.complete_data, self.required_fields))
        
        # 测试不完整数据
        self.assertFalse(is_data_complete(self.incomplete_data, self.required_fields))
        
        # 测试空数据
        empty_data = {}
        self.assertFalse(is_data_complete(empty_data, self.required_fields))
    
    def test_get_missing_fields(self):
        """测试get_missing_fields函数"""
        # 测试完整数据
        missing = get_missing_fields(self.complete_data, self.required_fields)
        self.assertEqual(missing, [])
        
        # 测试不完整数据
        missing = get_missing_fields(self.incomplete_data, self.required_fields)
        expected_missing = ["时间", "价格", "销售"]
        self.assertEqual(sorted(missing), sorted(expected_missing))
        
        # 测试完全缺失的数据
        empty_data = {}
        missing = get_missing_fields(empty_data, self.required_fields)
        self.assertEqual(sorted(missing), sorted(self.required_fields))


if __name__ == '__main__':
    unittest.main()