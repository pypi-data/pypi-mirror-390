"""
基础用法示例
"""

from gateway_sdk import GatewayClient
from gateway_sdk.exceptions import GatewayError

# 初始化客户端（使用 JWT Token）
client = GatewayClient(jwt_token="your-jwt-token-here")

# 或使用 API Key
# client = GatewayClient(api_key="sk-xxx")


def example_simple_call():
    """示例 1：简单调用"""
    print("=== 示例 1：简单调用 ===")
    
    try:
        result = client.run(
            prefab_id="llm-client",
            version="1.0.0",
            function_name="chat",
            parameters={
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "model": "gpt-4"
            }
        )
        
        if result.is_success():
            print(f"成功: {result.get_result()}")
        else:
            print(f"失败: {result.error}")
            
    except GatewayError as e:
        print(f"错误: {e}")


def example_chain_call():
    """示例 2：链式调用"""
    print("\n=== 示例 2：链式调用 ===")
    
    try:
        # 获取预制件对象
        llm = client.prefab("llm-client", "1.0.0")
        
        # 调用函数
        result = llm.call(
            "chat",
            messages=[{"role": "user", "content": "Translate 'hello' to Chinese"}],
            model="gpt-4"
        )
        
        if result.is_success():
            print(f"翻译结果: {result.get_result()}")
            
    except GatewayError as e:
        print(f"错误: {e}")


def example_dynamic_method():
    """示例 3：动态方法调用"""
    print("\n=== 示例 3：动态方法调用 ===")
    
    try:
        llm = client.prefab("llm-client", "1.0.0")
        
        # 直接使用函数名作为方法
        result = llm.chat(
            messages=[{"role": "user", "content": "What is Python?"}],
            model="gpt-4"
        )
        
        if result.is_success():
            print(f"回答: {result.get_result()}")
            
    except GatewayError as e:
        print(f"错误: {e}")


def example_batch_call():
    """示例 4：批量调用"""
    print("\n=== 示例 4：批量调用 ===")
    
    from gateway_sdk import PrefabCall
    
    try:
        calls = [
            PrefabCall(
                prefab_id="translator",
                version="1.0.0",
                function_name="translate",
                parameters={"text": "Hello", "target": "zh"}
            ),
            PrefabCall(
                prefab_id="translator",
                version="1.0.0",
                function_name="translate",
                parameters={"text": "World", "target": "zh"}
            ),
            PrefabCall(
                prefab_id="translator",
                version="1.0.0",
                function_name="translate",
                parameters={"text": "Python", "target": "zh"}
            )
        ]
        
        result = client.run_batch(calls)
        
        print(f"任务 ID: {result.job_id}")
        print(f"状态: {result.status}")
        print(f"全部成功: {result.all_success()}")
        
        for i, r in enumerate(result.results):
            if r.is_success():
                print(f"结果 {i+1}: {r.get_result()}")
            else:
                print(f"结果 {i+1} 失败: {r.error}")
                
    except GatewayError as e:
        print(f"错误: {e}")


def example_list_prefabs():
    """示例 5：列出预制件"""
    print("\n=== 示例 5：列出预制件 ===")
    
    try:
        prefabs = client.list_prefabs(status="deployed")
        
        print(f"找到 {len(prefabs)} 个预制件:")
        for prefab in prefabs[:5]:  # 只显示前 5 个
            print(f"- {prefab.prefab_id} v{prefab.version}")
            print(f"  描述: {prefab.description}")
            print(f"  官方: {prefab.is_official}")
            print(f"  需要密钥: {prefab.requires_secrets}")
            
    except GatewayError as e:
        print(f"错误: {e}")


def example_get_spec():
    """示例 6：获取预制件规格"""
    print("\n=== 示例 6：获取预制件规格 ===")
    
    try:
        spec = client.get_prefab_spec("llm-client", "1.0.0")
        
        print(f"预制件: {spec.get('name')}")
        print(f"版本: {spec.get('version')}")
        print(f"描述: {spec.get('description')}")
        print("\n可用函数:")
        
        for func in spec.get("functions", []):
            print(f"- {func.get('name')}: {func.get('description')}")
            
    except GatewayError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 运行所有示例
    example_simple_call()
    example_chain_call()
    example_dynamic_method()
    example_batch_call()
    example_list_prefabs()
    example_get_spec()

