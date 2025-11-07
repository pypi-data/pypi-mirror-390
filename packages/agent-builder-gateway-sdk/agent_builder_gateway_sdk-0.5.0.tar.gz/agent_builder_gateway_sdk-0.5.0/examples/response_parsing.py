#!/usr/bin/env python3
"""
SDK 响应解析示例

展示如何使用 SDK 的便捷方法正确解析预制件响应
"""

from gateway_sdk import GatewayClient

# 初始化客户端
client = GatewayClient(api_key="your-api-key")


# ============================================
# 示例 1：使用新的便捷方法（推荐）
# ============================================

def example_with_convenience_methods():
    """使用便捷方法解析响应（推荐）"""
    
    result = client.run(
        prefab_id="file-processing-prefab",
        version="0.1.5",
        function_name="parse_file",
        parameters={},
        files={"input": ["s3://bucket/document.pdf"]}
    )
    
    # ✅ 第 1 步：检查 SDK 调用是否成功
    if result.is_success():
        print("✅ SDK 调用成功")
        
        # ✅ 第 2 步：检查业务是否成功（使用便捷方法）
        if result.get_business_success():
            print("🎉 业务执行成功")
            
            # ✅ 第 3 步：获取业务数据
            message = result.get_business_message()
            print(f"消息: {message}")
            
            # ✅ 第 4 步：获取完整的函数返回值
            function_result = result.get_function_result()
            content = function_result.get('content')
            print(f"内容长度: {len(content) if content else 0}")
            
            # ✅ 第 5 步：获取输出文件
            output_files = result.get_files()
            if 'output' in output_files:
                s3_url = output_files['output'][0]
                print(f"输出文件: {s3_url}")
        
        else:
            # 业务失败（使用便捷方法）
            print("❌ 业务执行失败")
            error = result.get_business_error()
            error_code = result.get_business_error_code()
            print(f"错误: {error}")
            print(f"错误码: {error_code}")
    
    else:
        # SDK 调用失败
        print("❌ SDK 调用失败")
        print(f"错误: {result.error}")


# ============================================
# 示例 2：手动解析（不推荐，但也可以工作）
# ============================================

def example_with_manual_parsing():
    """手动解析响应（不推荐，容易出错）"""
    
    result = client.run(
        prefab_id="file-processing-prefab",
        version="0.1.5",
        function_name="parse_file",
        parameters={},
        files={"input": ["s3://bucket/document.pdf"]}
    )
    
    if result.is_success():
        # ⚠️ 手动处理双层嵌套（容易出错）
        function_result = result.output.get('output', {}) if result.output else {}
        
        if function_result.get('success'):
            message = function_result.get('message', '')
            content = function_result.get('content')
            
            # 获取输出文件
            files = result.output.get('files', {}) if result.output else {}
            output_s3_url = files.get('output', [])[0] if files.get('output') else None
            
            print(f"消息: {message}")
            print(f"输出文件: {output_s3_url}")
        else:
            error = function_result.get('error')
            print(f"错误: {error}")


# ============================================
# 示例 3：在 PocketFlow Node 中使用
# ============================================

class FileParsingNode:
    """文件解析节点示例"""
    
    def __init__(self, gateway_client):
        self.client = gateway_client
    
    async def exec_async(self, prep_res: dict) -> dict:
        """执行阶段：调用预制件"""
        try:
            file_s3_url = prep_res.get('file_s3_url')
            
            # 调用预制件
            result = self.client.run(
                prefab_id="file-processing-prefab",
                version="0.1.5",
                function_name="parse_file",
                parameters={},
                files={"input": [file_s3_url]}
            )
            
            # ✅ 使用便捷方法解析响应
            if result.is_success():
                if result.get_business_success():
                    # 业务成功
                    function_result = result.get_function_result()
                    output_files = result.get_files()
                    
                    return {
                        "success": True,
                        "message": result.get_business_message(),
                        "content": function_result.get('content'),
                        "output_file": output_files.get('output', [])[0] if output_files.get('output') else None
                    }
                else:
                    # 业务失败
                    return {
                        "success": False,
                        "error": result.get_business_error(),
                        "error_code": result.get_business_error_code()
                    }
            else:
                # SDK 调用失败
                return {
                    "success": False,
                    "error": result.error
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ============================================
# 示例 4：常见错误（避免）
# ============================================

def common_mistakes():
    """常见错误示例（不要这样做）"""
    
    result = client.run(...)
    
    # ❌ 错误 1：直接访问 result.output，没有处理嵌套
    # data = result.output.get('data')  # 错误！data 不在这一层
    
    # ❌ 错误 2：没有检查 result.output 是否存在
    # function_result = result.output['output']  # 可能 KeyError
    
    # ❌ 错误 3：混淆两层 output
    # success = result.output.get('success')  # 错误！success 在 output['output'] 中
    
    # ✅ 正确：使用便捷方法
    if result.is_success() and result.get_business_success():
        function_result = result.get_function_result()
        success = function_result.get('success')


if __name__ == "__main__":
    print("SDK 响应解析示例")
    print("=" * 60)
    print()
    print("推荐使用便捷方法，避免手动处理响应嵌套！")
    print()
    print("便捷方法列表：")
    print("- result.get_function_result()     # 获取函数返回值")
    print("- result.get_business_success()    # 判断业务成功")
    print("- result.get_business_message()    # 获取业务消息")
    print("- result.get_business_error()      # 获取业务错误")
    print("- result.get_business_error_code() # 获取错误代码")
    print("- result.get_files()               # 获取输出文件")

