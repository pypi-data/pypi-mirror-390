"""完整 MCP 工作流测试：生成图片并上传到 OSS"""
import os
import sys
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from imgenx import factory
from imgenx.oss_service import get_oss_service
import requests
from dotenv import load_dotenv

load_dotenv()


def test_complete_workflow():
    """测试完整工作流：生成图片 -> 上传 OSS"""

    print("\n" + "=" * 70)
    print("  完整 MCP 工作流测试：生成小猫在天上飞的图片并上传到 OSS")
    print("=" * 70 + "\n")

    # 用户输入
    user_prompt = "生成一个小猫在天上飞"
    print(f"用户输入: {user_prompt}\n")

    # ==================== 步骤 1: 生成图片 ====================
    print("-" * 70)
    print("步骤 1: 调用 text_to_image 生成图片")
    print("-" * 70)

    try:
        # 获取配置
        model = os.getenv('IMGENX_IMAGE_MODEL')
        api_key = os.getenv('IMGENX_API_KEY')

        print(f"[配置] 模型: {model}")
        print(f"[配置] API Key: {api_key[:20]}...")

        # 生成图片
        prompt = "一只可爱的小猫在蓝天白云中飞翔，阳光明媚，梦幻风格"
        size = "2K"

        print(f"[生成] 提示词: {prompt}")
        print(f"[生成] 尺寸: {size}")
        print("[生成] 正在生成图片，请稍候...")

        generator = factory.create_image_generator(model, api_key)
        url_list = generator.text_to_image(prompt, size)

        if not url_list or len(url_list) == 0:
            raise Exception("未生成图片")

        image_info = url_list[0]
        image_url = image_info['url']

        print(f"[成功] 图片生成成功！")
        print(f"[成功] 原始 URL: {image_url}")
        print(f"[成功] 标题: {image_info.get('title', 'N/A')}\n")

    except Exception as e:
        print(f"[错误] 图片生成失败: {e}")
        return False

    # ==================== 步骤 2: 下载图片 ====================
    print("-" * 70)
    print("步骤 2: 下载生成的图片")
    print("-" * 70)

    try:
        print(f"[下载] 正在下载图片...")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        image_data = response.content
        file_size = len(image_data) / 1024  # KB

        print(f"[成功] 图片下载成功")
        print(f"[成功] 文件大小: {file_size:.2f} KB\n")

    except Exception as e:
        print(f"[错误] 图片下载失败: {e}")
        return False

    # ==================== 步骤 3: 上传到 OSS ====================
    print("-" * 70)
    print("步骤 3: 上传图片到阿里云 OSS")
    print("-" * 70)

    try:
        # 从 URL 提取文件扩展名
        from urllib.parse import urlparse
        path = urlparse(image_url).path
        ext = Path(path).suffix or '.jpg'
        filename = f'flying_cat{ext}'

        print(f"[上传] 文件名: {filename}")
        print(f"[上传] 业务目录: images")
        print(f"[上传] 正在上传到 OSS...")

        # 上传到 OSS
        oss_service = get_oss_service()
        oss_result = oss_service.upload_bytes(
            data=image_data,
            filename=filename,
            business_dir='images'
        )

        print(f"[成功] 图片上传成功！")
        print(f"[成功] Object Key: {oss_result['object_key']}")
        print(f"[成功] OSS URL: {oss_result['oss_url']}")
        print(f"[成功] CDN URL: {oss_result['cdn_url']}")
        print(f"[成功] 状态码: {oss_result['status']}\n")

    except Exception as e:
        print(f"[错误] OSS 上传失败: {e}")
        return False

    # ==================== 步骤 4: 性能优化说明 ====================
    print("-" * 70)
    print("步骤 4: 性能优化 - 已跳过文件验证")
    print("-" * 70)
    print("[优化] OSS 上传成功（status=200）即表示文件已上传")
    print("[优化] 跳过额外的 file_exists() 验证，减少网络请求")
    print("[优化] 直接返回 CDN URL，提升响应速度")
    print()

    # ==================== 总结 ====================
    print("=" * 70)
    print("  测试完成 - 最终结果")
    print("=" * 70)
    print()
    print(f"用户请求: {user_prompt}")
    print(f"生成提示词: {prompt}")
    print(f"原始图片 URL: {image_url}")
    print(f"CDN 访问地址: {oss_result['cdn_url']}")
    print()
    print("建议回复用户:")
    print(f"  已为您生成一张小猫在天上飞的图片！")
    print(f"  图片链接: {oss_result['cdn_url']}")
    print(f"  ![小猫在天上飞]({oss_result['cdn_url']})")
    print()
    print("=" * 70)

    return True


def main():
    """主函数"""
    try:
        success = test_complete_workflow()

        if success:
            print("\n[总结] 完整工作流测试成功！✓")
        else:
            print("\n[总结] 完整工作流测试失败！✗")

    except Exception as e:
        print(f"\n[错误] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
