"""
文件操作示例

演示如何在 Agent 中进行文件上传、下载、列表和清理操作
"""

import os
import uuid
from gateway_sdk import GatewayClient


def main():
    # 从环境变量获取 internal token
    # 注意：在实际 Agent 中，这个 token 由网关通过请求头传入
    internal_token = os.environ.get("X_INTERNAL_TOKEN")
    if not internal_token:
        print("❌ Error: X_INTERNAL_TOKEN environment variable not set")
        return

    # 初始化客户端
    client = GatewayClient(internal_token=internal_token)
    print("✅ Gateway client initialized\n")

    # ========== 示例 1: 上传永久文件 ==========
    print("=== 示例 1: 上传永久文件到 agent-outputs ===")
    
    # 创建测试文件
    test_file_permanent = "/tmp/result.txt"
    with open(test_file_permanent, "w") as f:
        f.write("This is a permanent output file\n")
    
    try:
        result = client.upload_file(test_file_permanent)
        print(f"✅ 上传成功:")
        print(f"   S3 URL: {result['s3_url']}")
        print(f"   文件名: {result['filename']}")
        print(f"   大小: {result['size']} bytes\n")
        
        permanent_s3_url = result['s3_url']
    except Exception as e:
        print(f"❌ 上传失败: {e}\n")
        return

    # ========== 示例 2: 上传临时文件（默认 TTL） ==========
    print("=== 示例 2: 上传临时文件（默认 24 小时后删除） ===")
    
    test_file_temp = "/tmp/intermediate.txt"
    with open(test_file_temp, "w") as f:
        f.write("This is a temporary file\n")
    
    try:
        result = client.upload_temp_file(test_file_temp)
        print(f"✅ 上传成功:")
        print(f"   S3 URL: {result['s3_url']}")
        print(f"   文件名: {result['filename']}\n")
    except Exception as e:
        print(f"❌ 上传失败: {e}\n")

    # ========== 示例 3: 上传临时文件（自定义 TTL 和 session_id） ==========
    print("=== 示例 3: 上传临时文件（1 小时后删除，关联到 session） ===")
    
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}")
    
    test_file_temp2 = "/tmp/temp_session.txt"
    with open(test_file_temp2, "w") as f:
        f.write("This is a session-linked temporary file\n")
    
    try:
        result = client.upload_temp_file(
            test_file_temp2, 
            ttl=3600,  # 1 小时
            session_id=session_id
        )
        print(f"✅ 上传成功:")
        print(f"   S3 URL: {result['s3_url']}")
        print(f"   文件名: {result['filename']}\n")
        
        temp_s3_url = result['s3_url']
    except Exception as e:
        print(f"❌ 上传失败: {e}\n")
        return

    # ========== 示例 4: 列出永久文件 ==========
    print("=== 示例 4: 列出永久文件 ===")
    
    try:
        result = client.list_files(limit=10)
        print(f"✅ 找到 {len(result['files'])} 个永久文件:")
        for file in result['files'][:3]:  # 只显示前 3 个
            print(f"   - {file['s3_url']} ({file['size']} bytes)")
        if result.get('next_token'):
            print(f"   (有更多文件，使用 next_token 翻页)")
        print()
    except Exception as e:
        print(f"❌ 列出文件失败: {e}\n")

    # ========== 示例 5: 列出临时文件（指定 session） ==========
    print("=== 示例 5: 列出临时文件（指定 session） ===")
    
    try:
        result = client.list_temp_files(session_id=session_id)
        print(f"✅ 找到 {len(result['files'])} 个临时文件:")
        for file in result['files']:
            print(f"   - {file['s3_url']} ({file['size']} bytes)")
        print()
    except Exception as e:
        print(f"❌ 列出文件失败: {e}\n")

    # ========== 示例 6: 获取预签名 URL ==========
    print("=== 示例 6: 获取预签名 URL（用于直接下载） ===")
    
    try:
        presigned_url = client.get_presigned_url(permanent_s3_url, expires_in=3600)
        print(f"✅ 预签名 URL 生成成功:")
        print(f"   {presigned_url[:80]}...")
        print(f"   （有效期: 1 小时）\n")
    except Exception as e:
        print(f"❌ 获取预签名 URL 失败: {e}\n")

    # ========== 示例 7: 下载文件 ==========
    print("=== 示例 7: 下载文件 ===")
    
    download_path = "/tmp/downloaded_result.txt"
    try:
        client.download_file(permanent_s3_url, download_path)
        
        # 验证下载
        if os.path.exists(download_path):
            with open(download_path, "r") as f:
                content = f.read()
            print(f"✅ 下载成功:")
            print(f"   本地路径: {download_path}")
            print(f"   内容: {content.strip()}\n")
    except Exception as e:
        print(f"❌ 下载失败: {e}\n")

    # ========== 示例 8: 清理临时文件 ==========
    print("=== 示例 8: 清理指定 session 的临时文件 ===")
    
    try:
        deleted_count = client.cleanup_temp_files(session_id=session_id)
        print(f"✅ 清理完成，删除了 {deleted_count} 个文件\n")
    except Exception as e:
        print(f"❌ 清理失败: {e}\n")

    # ========== 完整工作流示例 ==========
    print("\n" + "=" * 60)
    print("=== 完整工作流示例: 视频处理 ===")
    print("=" * 60 + "\n")
    
    # 假设我们要处理一个视频
    session_id = str(uuid.uuid4())
    print(f"1️⃣ 创建 Session: {session_id}\n")
    
    # 2. 下载输入文件（假设从前端上传或其他 Agent 传入）
    print("2️⃣ 下载输入视频...")
    # input_video_url = "s3://bucket/agent-inputs/..."
    # client.download_file(input_video_url, "/tmp/input.mp4")
    print("   ✅ 已下载\n")
    
    # 3. 处理过程中产生中间文件（临时）
    print("3️⃣ 提取音频（临时文件）...")
    audio_file = "/tmp/audio.wav"
    with open(audio_file, "w") as f:
        f.write("fake audio data\n")
    
    audio_result = client.upload_temp_file(audio_file, ttl=7200, session_id=session_id)
    print(f"   ✅ 音频已上传: {audio_result['s3_url']}\n")
    
    print("4️⃣ 提取帧（临时文件）...")
    frame_file = "/tmp/frame.jpg"
    with open(frame_file, "w") as f:
        f.write("fake frame data\n")
    
    frame_result = client.upload_temp_file(frame_file, ttl=7200, session_id=session_id)
    print(f"   ✅ 帧已上传: {frame_result['s3_url']}\n")
    
    # 4. 上传最终结果（永久）
    print("5️⃣ 上传处理结果（永久文件）...")
    output_file = "/tmp/output.mp4"
    with open(output_file, "w") as f:
        f.write("fake processed video data\n")
    
    output_result = client.upload_file(output_file)
    print(f"   ✅ 结果已上传: {output_result['s3_url']}\n")
    
    # 5. 清理临时文件
    print("6️⃣ 清理临时文件...")
    deleted_count = client.cleanup_temp_files(session_id=session_id)
    print(f"   ✅ 已删除 {deleted_count} 个临时文件\n")
    
    print("🎉 工作流完成！\n")
    print("最终输出文件:", output_result['s3_url'])


if __name__ == "__main__":
    main()

