"""测试文件解析功能

使用第三方集成方式（API Key）测试文件上传和解析
"""

import sys
from pathlib import Path

# 添加 SDK 到 Python 路径
sdk_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(sdk_path))

from gateway_sdk import GatewayClient


def test_file_parsing():
    """测试文件解析流程"""
    
    # 1. 使用 API Key 初始化客户端（第三方集成方式）
    api_key = "sk-4xxxxxQ"
    print("🔑 使用 API Key 初始化客户端...")
    
    try:
        client = GatewayClient.from_api_key(api_key)
        print("✅ 客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. 上传测试文件
    test_file = Path(__file__).parent / "test.docx"
    print(f"\n📤 上传文件: {test_file}")
    
    try:
        file_url = client.upload_input_file(
            file_path=str(test_file),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        print(f"✅ 文件上传成功: {file_url}")
    except Exception as e:
        print(f"❌ 文件上传失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 调用文件解析预制件
    prefab_id = "file-processing-prefab"
    version = "0.1.5"
    function_name = "parse_file"
    print(f"\n🔧 调用预制件: {prefab_id}@{version}")
    print(f"📄 函数: {function_name}")
    print(f"📄 文件 URL: {file_url}")
    
    try:
        result = client.run(
            prefab_id=prefab_id,
            version=version,
            function_name=function_name,
            parameters={},  # 参数字典
            files={"input": [file_url]}  # 文件参数 key 是 "input"
        )
        
        print(f"\n✅ 解析成功!")
        print(f"状态: {result.status}")
        print(f"Job ID: {result.job_id}")
        print(f"\n完整输出:")
        import json
        print(json.dumps(result.output, indent=2, ensure_ascii=False))
        
        if result.error:
            print(f"错误: {result.error}")
        
    except Exception as e:
        print(f"❌ 预制件调用失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("文件解析测试")
    print("=" * 60)
    test_file_parsing()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

