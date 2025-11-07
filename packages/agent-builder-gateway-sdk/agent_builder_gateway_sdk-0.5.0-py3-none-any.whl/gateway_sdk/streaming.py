"""流式响应处理"""

import json
from typing import Iterator
from .models import StreamEvent


def parse_sse_stream(response_iter: Iterator[bytes]) -> Iterator[StreamEvent]:
    """
    解析 SSE 流式响应

    Args:
        response_iter: HTTP 响应字节流迭代器

    Yields:
        StreamEvent: 解析后的流式事件
    """
    buffer = b""

    for chunk in response_iter:
        buffer += chunk

        # 按行分割
        while b"\n" in buffer:
            line_bytes, buffer = buffer.split(b"\n", 1)
            line = line_bytes.decode("utf-8").strip()

            # 跳过空行和注释
            if not line or line.startswith(":"):
                continue

            # 解析 SSE 格式：data: {...}
            if line.startswith("data: "):
                data_str = line[6:]  # 去掉 "data: " 前缀
                try:
                    data = json.loads(data_str)
                    yield StreamEvent.from_dict(data)
                except json.JSONDecodeError:
                    # 忽略无法解析的行
                    continue

