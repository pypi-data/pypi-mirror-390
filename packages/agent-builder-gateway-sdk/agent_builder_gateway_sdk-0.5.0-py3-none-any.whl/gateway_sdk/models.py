"""数据模型"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class CallStatus(str, Enum):
    """调用状态"""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class StreamEventType(str, Enum):
    """流式事件类型"""

    START = "start"
    CONTENT = "content"
    PROGRESS = "progress"
    DONE = "done"
    ERROR = "error"


@dataclass
class PrefabCall:
    """预制件调用请求"""

    prefab_id: str
    version: str
    function_name: str
    parameters: Dict[str, Any]
    files: Optional[Dict[str, List[str]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        inputs: Dict[str, Any] = {"parameters": self.parameters}
        if self.files:
            inputs["files"] = self.files

        return {
            "prefab_id": self.prefab_id,
            "version": self.version,
            "function_name": self.function_name,
            "inputs": inputs,
        }


@dataclass
class PrefabResult:
    """预制件执行结果"""

    status: CallStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    job_id: Optional[str] = None

    def is_success(self) -> bool:
        """判断是否成功"""
        return self.status == CallStatus.SUCCESS

    def get(self, key: str, default: Any = None) -> Any:
        """便捷获取输出字段"""
        if self.output:
            return self.output.get(key, default)
        return default

    def get_result(self) -> Any:
        """
        获取完整的 output 字典（保持向后兼容）
        
        Returns:
            完整的 output 字典，包含 status, output, files 等
        """
        return self.output

    def get_function_result(self) -> Dict[str, Any]:
        """
        获取预制件函数的返回值（对应 manifest.returns）
        
        这是响应的嵌套结构：
        - result.output 是 Gateway 的响应
        - result.output['output'] 是预制件函数的实际返回值
        
        Returns:
            预制件函数的返回值字典
            
        Example:
            >>> result = client.run(...)
            >>> function_result = result.get_function_result()
            >>> if function_result.get('success'):
            ...     print(function_result.get('message'))
        """
        if self.output and isinstance(self.output, dict):
            return self.output.get('output', {})
        return {}

    def get_business_success(self) -> bool:
        """
        判断业务是否成功（检查函数返回值中的 success 字段）
        
        注意：
        - result.is_success() 表示 SDK 调用成功
        - result.get_business_success() 表示业务逻辑成功
        
        Returns:
            业务是否成功
            
        Example:
            >>> result = client.run(...)
            >>> if result.is_success() and result.get_business_success():
            ...     print("调用成功且业务成功")
        """
        function_result = self.get_function_result()
        return function_result.get('success', False)

    def get_business_message(self) -> str:
        """
        获取业务消息
        
        Returns:
            业务消息字符串，如果没有消息则返回空字符串
            
        Example:
            >>> result = client.run(...)
            >>> print(f"消息: {result.get_business_message()}")
        """
        function_result = self.get_function_result()
        return function_result.get('message', '')

    def get_business_error(self) -> Optional[str]:
        """
        获取业务错误信息
        
        Returns:
            错误信息字符串，如果没有错误则返回 None
            
        Example:
            >>> result = client.run(...)
            >>> if not result.get_business_success():
            ...     print(f"错误: {result.get_business_error()}")
        """
        function_result = self.get_function_result()
        return function_result.get('error')

    def get_business_error_code(self) -> Optional[str]:
        """
        获取业务错误代码
        
        Returns:
            错误代码字符串，如果没有错误码则返回 None
            
        Example:
            >>> result = client.run(...)
            >>> if not result.get_business_success():
            ...     print(f"错误码: {result.get_business_error_code()}")
        """
        function_result = self.get_function_result()
        return function_result.get('error_code')

    def get_files(self) -> Dict[str, List[str]]:
        """
        获取输出文件（S3 URL 列表）
        
        Returns:
            文件字典，key 对应 manifest.files 中定义的 key
            
        Example:
            >>> result = client.run(...)
            >>> output_files = result.get_files()
            >>> # 获取特定 key 的输出文件
            >>> if 'output' in output_files:
            ...     s3_url = output_files['output'][0]
        """
        if self.output:
            return self.output.get("files", {})
        return {}


@dataclass
class BatchResult:
    """批量执行结果"""

    job_id: str
    status: str
    results: List[PrefabResult]

    def all_success(self) -> bool:
        """判断是否全部成功"""
        return all(r.is_success() for r in self.results)

    def get_failed(self) -> List[PrefabResult]:
        """获取失败的结果"""
        return [r for r in self.results if not r.is_success()]


@dataclass
class StreamEvent:
    """流式事件"""

    type: StreamEventType
    data: Any

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamEvent":
        """从字典创建"""
        event_type = data.get("type", "content")
        try:
            event_type_enum = StreamEventType(event_type)
        except ValueError:
            event_type_enum = StreamEventType.CONTENT

        return cls(type=event_type_enum, data=data.get("data"))
