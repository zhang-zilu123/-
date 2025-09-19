"""
数据验证模块使用示例
演示如何使用DataValidator进行第一步数据验证
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_validator import DataValidator


def main():
    """主函数 - 演示数据验证流程"""
    
    # 创建验证器实例
    validator = DataValidator()
    
    # 模拟从Excel读取的原始数据
    sample_data = [
        {
            "商品标题": "猫窝大号四季通用棉编织睡窝舒适耐磨耐抓猫咪睡觉宠物用品",
            "时间": [["最早上架时间：2025-09-08 16:56:26"], ["最新发布时间：2025-09-17 15:28:44"]],
            "价格": [["券后¥16.9首件预估到手价"]],
            "销售": [["年销量", "0件"], ["近30天销量", "0件"]],
            "商品详情": [["材质", "棉", "产地", "山东"]],
            "主产品图片": ["https://cbu01.alicdn.com/img/ibank/O1CN01r2tSMW1HHlP9ppoHa_!!3067830733-0-cib.jpg_b.jpg"],
            "商品详情图片": ["https://cbu01.alicdn.com/img/ibank/O1CN01qoGxxl1HHlKMqn9EN_!!3067830733-0-cib.jpg"],
            "sku商品详情图片和信息": ["猫窝大号\t974813137215\t5927865081351\t蓝色+大号"],
            "产品网址": "https://dj.1688.com/ci_bb?a=19394&e=z5DX82J0p4YM5TuKITK3cW1Vcvk68m",
            "公司基本信息": [["临沂微视角文化传媒有限公司"], ["9年回头率68%"]]
        },
        {
            "商品标题": "宠物用品猫咪玩具",
            "时间": None,  # 缺失字段
            "价格": "",    # 空字符串
            "销售": [],    # 空列表
            "商品详情": [["材质", "塑料"]],
            "主产品图片": ["https://example.com/image2.jpg"],
            "商品详情图片": ["https://example.com/detail2.jpg"],
            "sku商品详情图片和信息": ["玩具信息"],
            "产品网址": "https://example.com/product2",
            "公司基本信息": [["测试公司"]]
        },
        {
            "商品标题": "狗狗食品营养餐",
            "时间": [["上架时间：2025-09-15"]],
            "价格": [["价格：¥25.8"]],
            "销售": [["月销量", "100件"]],
            "商品详情": [["品牌", "宠物乐园"]],
            "主产品图片": ["https://example.com/image3.jpg"],
            "商品详情图片": ["https://example.com/detail3.jpg"],
            "sku商品详情图片和信息": ["狗粮信息"],
            "产品网址": "https://example.com/product3",
            "公司基本信息": None  # 缺失字段
        }
    ]
    
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
    
    # 显示不完整数据的详细信息
    if incomplete_data:
        print(f"\n不完整数据详情 (共{len(incomplete_data)}条):")
        for i, item in enumerate(incomplete_data, 1):
            missing_fields = item.get('_missing_fields', [])
            print(f"  第{i}条 - 缺失字段: {', '.join(missing_fields)}")


if __name__ == "__main__":
    main()