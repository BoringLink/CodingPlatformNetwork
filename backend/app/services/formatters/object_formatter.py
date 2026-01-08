"""对象格式化器"""

from typing import Any, Dict, Optional, List

from .base_formatter import BaseFormatter


class ObjectFormatter(BaseFormatter):
    """对象格式化器，用于格式化复杂的嵌套对象"""

    def __init__(self, formatter_registry: Optional[Dict[str, BaseFormatter]] = None):
        """初始化对象格式化器
        
        Args:
            formatter_registry: 格式化器注册表
        """
        self.formatter_registry = formatter_registry or {}
    
    def format(self, value: Any, field_name: str = "", context: Optional[Dict[str, Any]] = None) -> Any:
        """格式化对象数据
        
        Args:
            value: 要格式化的对象数据
            field_name: 字段名
            context: 上下文信息
            
        Returns:
            格式化后的对象
        """
        # 处理字典类型
        if isinstance(value, dict):
            return self._format_dict(value, field_name, context)
        
        # 处理列表类型
        elif isinstance(value, list):
            return self._format_list(value, field_name, context)
        
        # 无法处理的类型，返回原始值
        return value
    
    def _format_dict(self, value: Dict[str, Any], field_name: str = "", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """格式化字典类型
        
        Args:
            value: 要格式化的字典
            field_name: 字段名
            context: 上下文信息
            
        Returns:
            格式化后的字典
        """
        formatted_dict = {}
        
        for key, val in value.items():
            # 构建完整字段名
            full_field_name = f"{field_name}.{key}" if field_name else key
            
            # 选择合适的格式化器
            formatter = self._get_formatter(val)
            
            # 格式化值
            formatted_val = formatter.format(val, full_field_name, context)
            
            # 添加到结果字典
            formatted_dict[key] = formatted_val
        
        return formatted_dict
    
    def _format_list(self, value: List[Any], field_name: str = "", context: Optional[Dict[str, Any]] = None) -> List[Any]:
        """格式化列表类型
        
        Args:
            value: 要格式化的列表
            field_name: 字段名
            context: 上下文信息
            
        Returns:
            格式化后的列表
        """
        formatted_list = []
        
        for i, item in enumerate(value):
            # 构建完整字段名
            item_field_name = f"{field_name}[{i}]" if field_name else f"[{i}]"
            
            # 选择合适的格式化器
            formatter = self._get_formatter(item)
            
            # 格式化值
            formatted_item = formatter.format(item, item_field_name, context)
            
            # 添加到结果列表
            formatted_list.append(formatted_item)
        
        return formatted_list
    
    def _get_formatter(self, value: Any) -> BaseFormatter:
        """获取合适的格式化器
        
        Args:
            value: 要格式化的值
            
        Returns:
            合适的格式化器
        """
        for formatter in self.formatter_registry.values():
            if formatter.can_handle(value):
                return formatter
        
        # 默认返回基类格式化器（直接返回原始值）
        return BaseFormatter()
    
    def can_handle(self, value: Any) -> bool:
        """检查是否能处理该类型的数据
        
        Args:
            value: 要检查的数据
            
        Returns:
            是否能处理
        """
        return isinstance(value, (dict, list))
