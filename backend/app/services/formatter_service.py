"""数据格式化服务"""

from typing import Any, Dict, Optional

from app.models.nodes import NodeType
from app.services.field_mapping import field_mapping
from app.services.formatters import (
    DateTimeFormatter,
    NumericFormatter,
    StringFormatter,
    ObjectFormatter,
)


class FormatterService:
    """数据格式化服务，用于将原始数据格式化为前端友好的中文数据"""

    def __init__(self):
        """初始化格式化服务"""
        # 初始化格式化器
        self.formatters = {
            "datetime": DateTimeFormatter(),
            "numeric": NumericFormatter(),
            "string": StringFormatter(),
            "object": ObjectFormatter(
                {
                    "datetime": DateTimeFormatter(),
                    "numeric": NumericFormatter(),
                    "string": StringFormatter(),
                }
            ),
        }
    
    def format_node(self, node_type: NodeType, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化节点数据
        
        Args:
            node_type: 节点类型
            node_data: 节点原始数据
            
        Returns:
            格式化后的节点数据
        """
        # 获取字段映射
        mapping = field_mapping.get_mapping(node_type)
        
        # 格式化数据
        formatted_data = self._format_data(node_data, mapping)
        
        # 转换字段名为中文
        chinese_data = self._convert_to_chinese_fields(formatted_data, mapping)
        
        return chinese_data
    
    def _format_data(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """格式化数据
        
        Args:
            data: 原始数据
            mapping: 字段映射
            
        Returns:
            格式化后的数据
        """
        formatted_data = {}
        
        for key, value in data.items():
            # 选择合适的格式化器
            formatter = self._get_formatter(value)
            
            # 格式化值
            formatted_value = formatter.format(value, key)
            
            # 添加到结果字典
            formatted_data[key] = formatted_value
        
        return formatted_data
    
    def _convert_to_chinese_fields(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """将字段名转换为中文
        
        Args:
            data: 格式化后的数据
            mapping: 字段映射
            
        Returns:
            中文字段名的数据
        """
        chinese_data = {}
        
        for key, value in data.items():
            # 查找中文映射
            chinese_key = mapping.get(key, key)
            
            # 处理嵌套结构
            if isinstance(value, dict):
                # 构建嵌套字段的映射
                nested_mapping = {}
                for full_field_name, chinese_name in mapping.items():
                    if full_field_name.startswith(f"{key}."):
                        nested_key = full_field_name[len(f"{key}."):]
                        nested_chinese_name = chinese_name[len(chinese_key) + 1:]
                        nested_mapping[nested_key] = nested_chinese_name
                
                # 递归转换嵌套结构
                chinese_value = self._convert_to_chinese_fields(value, nested_mapping)
            
            # 处理列表结构
            elif isinstance(value, list):
                # 格式化列表中的每个元素
                chinese_value = []
                for item in value:
                    if isinstance(item, dict):
                        # 构建列表项的映射
                        item_mapping = {}
                        for full_field_name, chinese_name in mapping.items():
                            if full_field_name.startswith(f"{key}."):
                                nested_key = full_field_name[len(f"{key}."):]
                                nested_chinese_name = chinese_name[len(chinese_key) + 1:]
                                item_mapping[nested_key] = nested_chinese_name
                        
                        # 递归转换列表项
                        chinese_item = self._convert_to_chinese_fields(item, item_mapping)
                        chinese_value.append(chinese_item)
                    else:
                        chinese_value.append(item)
            
            # 普通值
            else:
                chinese_value = value
            
            # 添加到结果字典
            chinese_data[chinese_key] = chinese_value
        
        return chinese_data
    
    def _get_formatter(self, value: Any) -> Any:
        """获取合适的格式化器
        
        Args:
            value: 要格式化的值
            
        Returns:
            合适的格式化器
        """
        # 检查类型并选择格式化器
        if isinstance(value, (dict, list)):
            return self.formatters["object"]
        elif isinstance(value, (int, float)):
            return self.formatters["numeric"]
        elif isinstance(value, str):
            return self.formatters["string"]
        else:
            # 尝试判断是否为日期时间类型
            datetime_formatter = self.formatters["datetime"]
            if datetime_formatter.can_handle(value):
                return datetime_formatter
            return self.formatters["object"]


# 全局格式化服务实例
formatter_service = FormatterService()
