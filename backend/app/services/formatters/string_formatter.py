"""字符串格式化器"""

from typing import Any, Dict, Optional

from .base_formatter import BaseFormatter
from app.services.field_mapping import field_mapping


class StringFormatter(BaseFormatter):
    """字符串格式化器，用于格式化字符串类型的数据"""

    def format(self, value: Any, field_name: str = "", context: Optional[Dict[str, Any]] = None) -> Any:
        """格式化字符串数据
        
        Args:
            value: 要格式化的字符串数据
            field_name: 字段名
            context: 上下文信息
            
        Returns:
            格式化后的字符串
        """
        # 确保值是字符串类型
        if not isinstance(value, str):
            return value
        
        # 业务术语翻译
        mapped_value = field_mapping.get_term_mapping(field_name, value)
        if mapped_value != value:
            return mapped_value
        
        # 首字母大写处理（仅对英文单词）
        if self._should_capitalize(value):
            return value.capitalize()
        
        # 其他字符串处理
        return value
    
    def _should_capitalize(self, value: str) -> bool:
        """判断是否需要首字母大写
        
        Args:
            value: 字符串值
            
        Returns:
            是否需要首字母大写
        """
        # 仅对英文单词进行首字母大写
        return len(value) > 0 and value[0].isalpha() and not value[0].isupper()
    
    def can_handle(self, value: Any) -> bool:
        """检查是否能处理该类型的数据
        
        Args:
            value: 要检查的数据
            
        Returns:
            是否能处理
        """
        return isinstance(value, str)
