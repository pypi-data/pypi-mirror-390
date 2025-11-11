"""测试阿里云 OSS 上传功能"""
import os
import sys
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from imgenx.oss_service import get_oss_service


def test_oss_config():
    """测试 OSS 配置"""
    print("=" * 60)
    print("测试 1: 检查 OSS 配置")
    print("=" * 60)

    try:
        oss_service = get_oss_service()
        print("[OK] OSS 服务初始化成功")
        print(f"  - Bucket: {oss_service.bucket_name}")
        print(f"  - Endpoint: {oss_service.endpoint}")
        print(f"  - CDN URL: {oss_service.cdn_url}")
        return True
    except Exception as e:
        print(f"[ERROR] OSS 服务初始化失败: {e}")
        return False


def test_upload_file():
    """测试文件上传"""
    print("\n" + "=" * 60)
    print("测试 2: 上传测试文件")
    print("=" * 60)

    # 创建测试文件
    test_file = Path("test_upload.txt")
    test_content = "这是一个测试文件，用于测试 OSS 上传功能。\nTimestamp: " + str(Path(__file__).stat().st_mtime)

    try:
        # 写入测试文件
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        print(f"[OK] 创建测试文件: {test_file}")

        # 上传文件
        oss_service = get_oss_service()
        result = oss_service.upload_file(str(test_file), business_dir='test')

        print("[OK] 文件上传成功")
        print(f"  - Object Key: {result['object_key']}")
        print(f"  - OSS URL: {result['oss_url']}")
        print(f"  - CDN URL: {result['cdn_url']}")
        print(f"  - Status: {result['status']}")

        # 检查文件是否存在
        exists = oss_service.file_exists(result['object_key'])
        print(f"[OK] 验证文件存在: {exists}")

        # 清理测试文件
        test_file.unlink()
        print(f"[OK] 删除本地测试文件")

        return result['object_key']
    except Exception as e:
        print(f"[ERROR] 上传测试失败: {e}")
        if test_file.exists():
            test_file.unlink()
        return None


def test_upload_bytes():
    """测试字节数据上传"""
    print("\n" + "=" * 60)
    print("测试 3: 上传字节数据")
    print("=" * 60)

    try:
        oss_service = get_oss_service()

        # 创建测试数据
        test_data = b"This is a test binary data for OSS upload."

        # 上传字节数据
        result = oss_service.upload_bytes(test_data, 'test_bytes.bin', business_dir='test')

        print("[OK] 字节数据上传成功")
        print(f"  - Object Key: {result['object_key']}")
        print(f"  - OSS URL: {result['oss_url']}")
        print(f"  - CDN URL: {result['cdn_url']}")

        return result['object_key']
    except Exception as e:
        print(f"[ERROR] 字节数据上传失败: {e}")
        return None


def test_delete_file(object_key):
    """测试文件删除"""
    print("\n" + "=" * 60)
    print("测试 4: 删除测试文件")
    print("=" * 60)

    try:
        oss_service = get_oss_service()

        # 删除文件
        success = oss_service.delete_file(object_key)

        if success:
            print(f"[OK] 文件删除成功: {object_key}")

            # 验证文件已删除
            exists = oss_service.file_exists(object_key)
            print(f"[OK] 验证文件已删除: {not exists}")
        else:
            print(f"[ERROR] 文件删除失败: {object_key}")

        return success
    except Exception as e:
        print(f"[ERROR] 删除测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n")
    print("=" * 60)
    print("         阿里云 OSS 上传功能测试")
    print("=" * 60)
    print()

    # 测试 1: 配置检查
    if not test_oss_config():
        print("\n[ERROR] OSS 配置检查失败，退出测试")
        return

    # 测试 2: 文件上传
    object_key_1 = test_upload_file()

    # 测试 3: 字节数据上传
    object_key_2 = test_upload_bytes()

    # 测试 4: 文件删除
    if object_key_1:
        test_delete_file(object_key_1)

    if object_key_2:
        test_delete_file(object_key_2)

    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
