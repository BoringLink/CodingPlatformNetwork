"""格式化器基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseFormatter(ABC):
    """格式化器基类，定义统一的格式化接口"""

    @abstractmethod
    def format(self, value: Any, field_name: str = "", context: Optional[Dict[str, Any]] = None) -> Any:
        """格式化数据
        
        Args:
            value: 要格式化的数据
            field_name: 字段名
            context: 上下文信息
            
        Returns:
            格式化后的数据
        """
        pass

    def can_handle(self, value: Any) -> bool:
        """检查是否能处理该类型的数据
        
        Args:
            value: 要检查的数据
            
        Returns:
            是否能处理
        """
        return True
