"""
ProductQuotation 项目配置文件
包含所有系统配置和字段映射规则
"""

# 必需字段配置 - 用于数据完整性验证
REQUIRED_FIELDS = [
    "商品标题",
    "时间", 
    "价格",
    "销售",
    "商品详情",
    "主产品图片",
    "商品详情图片", 
    "sku商品详情图片和信息",
    "产品网址",
    "公司基本信息"
]

# Excel处理配置
EXCEL_CONFIG = {
    "visible": False,           # Excel应用是否可见
    "add_book": False,         # 是否添加新工作簿
    "screen_updating": False,  # 是否更新屏幕显示
    "display_alerts": False    # 是否显示警告
}

# xlwings设置
XLWINGS_SETTINGS = {
    "app_visible": False,      # Excel应用可见性
    "automatic_calculation": True,  # 自动计算
    "enable_events": False,    # 启用事件
    "interactive": False       # 交互模式
}

# 输出设置# 输出设置
OUTPUT_SETTINGS = {
    "format": "json",          # 输出格式
    "encoding": "utf-8",       # 文件编码
    "backup_enabled": True,    # 是否启用备份
    "indent": 2               # JSON缩进
}

# 处理规则
PROCESSING_RULES = {
    "batch_size": 100,         # 批处理大小
    "log_level": "INFO",       # 日志级别
    "max_retries": 3,          # 最大重试次数
    "timeout": 30              # 超时时间(秒)
}

# 数据验证配置
VALIDATION_CONFIG = {
    "check_none": True,        # 检查None值
    "check_empty_string": True, # 检查空字符串
    "check_empty_list": True,  # 检查空列表
    "generate_report": True,   # 生成验证报告
    "save_incomplete_data": True  # 保存不完整数据
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": "data/output/logs/validation.log"
}


# 分割配置
SPLIT_CONFIG = {
    "chunk_size": 300,              # 每个分割文件的数据条数
    "create_subdirs": True,         # 是否创建子目录
    "split_threshold": 300,         # 分割阈值，超过此数量才进行分割
    "output_subdir": "split_data",  # 分割文件输出子目录名
    "auto_split": True              # 是否自动分割
}

# 产品属性提取配置
PRODUCT_ATTRIBUTE_CONFIG = {
    "output_files": {
        "complete_file": "step3_complete.json",
        "error_file": "step3_error.json"
    },
    "required_fields": ["规格", "尺寸", "价格", "重量_g", "图片"],
    "default_values": {
        "weight": 0,
        "image": "",
        "spec": "无规格",
        "price": 0.0
    }
}