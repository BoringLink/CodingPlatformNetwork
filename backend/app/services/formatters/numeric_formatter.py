"""数值格式化器"""

from typing import Any, Dict, Optional

from .base_formatter import BaseFormatter


class NumericFormatter(BaseFormatter):
    """数值格式化器，用于格式化数值类型的数据"""

    def format(self, value: Any, field_name: str = "", context: Optional[Dict[str, Any]] = None) -> Any:
        """格式化数值数据
        
        Args:
            value: 要格式化的数值数据
            field_name: 字段名
            context: 上下文信息
            
        Returns:
            格式化后的数值
        """
        # 确保值是数值类型
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return value
        
        # 根据字段名判断格式化方式
        if self._is_percentage_field(field_name):
            return self._format_percentage(num_value)
        
        elif self._is_duration_field(field_name):
            return self._format_duration(num_value)
        
        elif self._is_integer_field(field_name) or num_value.is_integer():
            return self._format_integer(int(num_value))
        
        else:
            return self._format_float(num_value)
    
    def _is_percentage_field(self, field_name: str) -> bool:
        """判断是否为百分比字段
        
        Args:
            field_name: 字段名
            
        Returns:
            是否为百分比字段
        """
        percentage_keywords = ["rate", "completeness", "percentage"]
        return any(keyword in field_name.lower() for keyword in percentage_keywords)
    
    def _is_duration_field(self, field_name: str) -> bool:
        """判断是否为时长字段
        
        Args:
            field_name: 字段名
            
        Returns:
            是否为时长字段
        """
        duration_keywords = ["duration", "session_duration"]
        return any(keyword in field_name.lower() for keyword in duration_keywords)
    
    def _is_integer_field(self, field_name: str) -> bool:
        """判断是否为整数字段
        
        Args:
            field_name: 字段名
            
        Returns:
            是否为整数字段
        """
        integer_keywords = ["count", "age", "id", "score"]
        return any(keyword in field_name.lower() for keyword in integer_keywords)
    
    def _format_percentage(self, value: float) -> str:
        """格式化百分比
        
        Args:
            value: 百分比值（0-1之间）
            
        Returns:
            格式化后的百分比字符串
        """
        if 0 <= value <= 1:
            return f"{int(value * 100)}%"
        return f"{value:.1f}%"
    
    def _format_duration(self, value: float) -> str:
        """格式化时长（分钟）
        
        Args:
            value: 时长（分钟）
            
        Returns:
            格式化后的时长字符串
        """
        hours = int(value // 60)
        minutes = int(value % 60)
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{minutes}分钟"
    
    def _format_integer(self, value: int) -> str:
        """格式化整数，添加千分位
        
        Args:
            value: 整数
            
        Returns:
            格式化后的整数字符串
        """
        return f"{value:,}"
    
    def _format_float(self, value: float) -> str:
        """格式化浮点数
        
        Args:
            value: 浮点数
            
        Returns:
            格式化后的浮点数字符串
        """
        # 根据数值大小决定保留小数位数
        if abs(value) >= 1000:
            return f"{value:,.1f}"
        elif abs(value) >= 100:
            return f"{value:,.2f}"
        elif abs(value) >= 1:
            return f"{value:.3f}"
        else:
            return f"{value:.4f}"
    
    def can_handle(self, value: Any) -> bool:
        """检查是否能处理该类型的数据
        
        Args:
            value: 要检查的数据
            
        Returns:
            是否能处理
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
