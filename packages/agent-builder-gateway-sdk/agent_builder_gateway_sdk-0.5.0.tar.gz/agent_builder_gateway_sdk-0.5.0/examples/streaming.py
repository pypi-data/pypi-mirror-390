"""
流式响应示例
"""

from gateway_sdk import GatewayClient
from gateway_sdk.exceptions import GatewayError
from gateway_sdk.models import StreamEventType

# 初始化客户端
client = GatewayClient(jwt_token="your-jwt-token-here")


def example_basic_streaming():
    """示例 1：基础流式调用"""
    print("=== 示例 1：基础流式调用 ===")
    
    try:
        for event in client.run(
            prefab_id="llm-client",
            version="1.0.0",
            function_name="chat_stream",
            parameters={
                "messages": [{"role": "user", "content": "Tell me a short story"}],
                "model": "gpt-4"
            },
            stream=True
        ):
            if event.type == StreamEventType.CONTENT:
                # 实时输出内容
                print(event.data, end="", flush=True)
            elif event.type == StreamEventType.DONE:
                print("\n\n[完成]")
            elif event.type == StreamEventType.ERROR:
                print(f"\n[错误]: {event.data}")
                
    except GatewayError as e:
        print(f"错误: {e}")


def example_streaming_with_metadata():
    """示例 2：处理流式元数据"""
    print("\n=== 示例 2：处理流式元数据 ===")
    
    try:
        content_buffer = []
        
        for event in client.run(
            prefab_id="llm-client",
            version="1.0.0",
            function_name="chat_stream",
            parameters={
                "messages": [{"role": "user", "content": "What is AI?"}],
                "model": "gpt-4"
            },
            stream=True
        ):
            if event.type == StreamEventType.START:
                print(f"[开始] 模型: {event.data.get('model')}")
                print(f"[开始] 温度: {event.data.get('temperature')}")
                print("\n回复: ", end="")
                
            elif event.type == StreamEventType.CONTENT:
                content_buffer.append(event.data)
                print(event.data, end="", flush=True)
                
            elif event.type == StreamEventType.PROGRESS:
                # 某些预制件可能会发送进度信息
                print(f"\n[进度]: {event.data}")
                
            elif event.type == StreamEventType.DONE:
                print(f"\n\n[完成]")
                print(f"总字符数: {len(''.join(content_buffer))}")
                if isinstance(event.data, dict):
                    print(f"完成原因: {event.data.get('finish_reason')}")
                    
            elif event.type == StreamEventType.ERROR:
                print(f"\n[错误]: {event.data}")
                break
                
    except GatewayError as e:
        print(f"错误: {e}")


def example_streaming_with_prefab():
    """示例 3：使用 Prefab 对象进行流式调用"""
    print("\n=== 示例 3：使用 Prefab 对象进行流式调用 ===")
    
    try:
        llm = client.prefab("llm-client", "1.0.0")
        
        print("问题: 解释什么是机器学习\n")
        print("回答: ", end="")
        
        for event in llm.stream(
            "chat_stream",
            messages=[{"role": "user", "content": "Explain machine learning in simple terms"}],
            model="gpt-4"
        ):
            if event.type == StreamEventType.CONTENT:
                print(event.data, end="", flush=True)
            elif event.type == StreamEventType.DONE:
                print("\n")
                
    except GatewayError as e:
        print(f"错误: {e}")


def example_streaming_with_callback():
    """示例 4：使用回调函数处理流式事件"""
    print("\n=== 示例 4：使用回调函数处理流式事件 ===")
    
    def on_start(data):
        print(f"[开始] {data}")
    
    def on_content(data):
        print(data, end="", flush=True)
    
    def on_done(data):
        print(f"\n[完成] {data}")
    
    def on_error(data):
        print(f"\n[错误] {data}")
    
    # 事件处理器映射
    handlers = {
        StreamEventType.START: on_start,
        StreamEventType.CONTENT: on_content,
        StreamEventType.DONE: on_done,
        StreamEventType.ERROR: on_error,
    }
    
    try:
        for event in client.run(
            prefab_id="llm-client",
            version="1.0.0",
            function_name="chat_stream",
            parameters={
                "messages": [{"role": "user", "content": "Count from 1 to 5"}],
                "model": "gpt-4"
            },
            stream=True
        ):
            handler = handlers.get(event.type)
            if handler:
                handler(event.data)
                
    except GatewayError as e:
        print(f"错误: {e}")


def example_streaming_with_timeout():
    """示例 5：处理流式超时"""
    print("\n=== 示例 5：处理流式超时 ===")
    
    import time
    
    try:
        # 创建一个超时时间较短的客户端
        short_timeout_client = GatewayClient(
            jwt_token="your-jwt-token-here",
            timeout=5  # 5 秒超时
        )
        
        start_time = time.time()
        
        for event in short_timeout_client.run(
            prefab_id="llm-client",
            version="1.0.0",
            function_name="chat_stream",
            parameters={
                "messages": [{"role": "user", "content": "Write a long essay"}],
                "model": "gpt-4"
            },
            stream=True
        ):
            if event.type == StreamEventType.CONTENT:
                print(event.data, end="", flush=True)
                
        elapsed = time.time() - start_time
        print(f"\n\n耗时: {elapsed:.2f} 秒")
        
    except GatewayError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 运行所有示例
    example_basic_streaming()
    example_streaming_with_metadata()
    example_streaming_with_prefab()
    example_streaming_with_callback()
    # example_streaming_with_timeout()  # 可能会超时，谨慎运行

