"""时间格式化器"""

from datetime import datetime, date, time
from typing import Any, Dict, Optional

from .base_formatter import BaseFormatter


class DateTimeFormatter(BaseFormatter):
    """时间格式化器，用于格式化日期时间数据"""

    def format(self, value: Any, field_name: str = "", context: Optional[Dict[str, Any]] = None) -> str:
        """格式化日期时间数据
        
        Args:
            value: 要格式化的日期时间数据
            field_name: 字段名
            context: 上下文信息
            
        Returns:
            格式化后的日期时间字符串
        """
        # 处理ISO字符串
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
                return self._format_datetime(dt)
            except ValueError:
                return value
        
        # 处理datetime对象
        elif isinstance(value, datetime):
            return self._format_datetime(value)
        
        # 处理date对象
        elif isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        
        # 处理time对象
        elif isinstance(value, time):
            return value.strftime("%H:%M:%S")
        
        # 处理复杂的datetime对象（如Neo4j返回的对象）
        elif isinstance(value, dict) and "_DateTime__date" in value:
            date_part = value["_DateTime__date"]
            time_part = value["_DateTime__time"]
            
            try:
                dt = datetime(
                    year=date_part.get("_Date__year", 1970),
                    month=date_part.get("_Date__month", 1),
                    day=date_part.get("_Date__day", 1),
                    hour=time_part.get("_Time__hour", 0),
                    minute=time_part.get("_Time__minute", 0),
                    second=time_part.get("_Time__second", 0),
                    microsecond=time_part.get("_Time__nanosecond", 0) // 1000
                )
                return self._format_datetime(dt)
            except (ValueError, TypeError):
                return str(value)
        
        # 无法处理的类型，返回原始值
        return str(value)
    
    def _format_datetime(self, dt: datetime) -> str:
        """格式化datetime对象
        
        Args:
            dt: datetime对象
            
        Returns:
            格式化后的日期时间字符串
        """
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def can_handle(self, value: Any) -> bool:
        """检查是否能处理该类型的数据
        
        Args:
            value: 要检查的数据
            
        Returns:
            是否能处理
        """
        return isinstance(value, (datetime, date, time, str)) or (
            isinstance(value, dict) and "_DateTime__date" in value
        )
