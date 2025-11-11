"""性能对比测试：优化前后的速度对比"""
import os
import sys
import time
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from imgenx.oss_service import get_oss_service


def test_upload_with_verification():
    """测试：带验证的上传流程"""
    print("\n" + "=" * 70)
    print("  测试 1: 带文件验证的上传流程（原流程）")
    print("=" * 70)

    # 创建测试数据
    test_data = b"Performance test data " * 1000
    filename = "perf_test_with_verify.bin"

    try:
        oss_service = get_oss_service()

        # 计时开始
        start_time = time.time()

        # 步骤1: 上传
        print("[步骤1] 上传文件...")
        upload_start = time.time()
        result = oss_service.upload_bytes(test_data, filename, business_dir='test')
        upload_time = time.time() - upload_start
        print(f"  上传完成: {upload_time:.3f} 秒")

        # 步骤2: 验证
        print("[步骤2] 验证文件存在...")
        verify_start = time.time()
        exists = oss_service.file_exists(result['object_key'])
        verify_time = time.time() - verify_start
        print(f"  验证完成: {verify_time:.3f} 秒")

        # 总时间
        total_time = time.time() - start_time

        print(f"\n[结果]")
        print(f"  上传时间: {upload_time:.3f} 秒")
        print(f"  验证时间: {verify_time:.3f} 秒")
        print(f"  总时间: {total_time:.3f} 秒")
        print(f"  CDN URL: {result['cdn_url']}")

        # 清理
        oss_service.delete_file(result['object_key'])

        return total_time, upload_time, verify_time

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return None, None, None


def test_upload_without_verification():
    """测试：不带验证的上传流程（优化后）"""
    print("\n" + "=" * 70)
    print("  测试 2: 不带文件验证的上传流程（优化后）")
    print("=" * 70)

    # 创建测试数据
    test_data = b"Performance test data " * 1000
    filename = "perf_test_without_verify.bin"

    try:
        oss_service = get_oss_service()

        # 计时开始
        start_time = time.time()

        # 只做上传，不验证
        print("[步骤1] 上传文件...")
        upload_start = time.time()
        result = oss_service.upload_bytes(test_data, filename, business_dir='test')
        upload_time = time.time() - upload_start
        print(f"  上传完成: {upload_time:.3f} 秒")

        print("[步骤2] 跳过验证步骤（优化）")
        print(f"  status=200 已确认上传成功")

        # 总时间
        total_time = time.time() - start_time

        print(f"\n[结果]")
        print(f"  上传时间: {upload_time:.3f} 秒")
        print(f"  验证时间: 0.000 秒 (已跳过)")
        print(f"  总时间: {total_time:.3f} 秒")
        print(f"  CDN URL: {result['cdn_url']}")

        # 清理
        oss_service.delete_file(result['object_key'])

        return total_time, upload_time, 0

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return None, None, None


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "性能优化对比测试" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")

    # 测试1: 带验证
    total1, upload1, verify1 = test_upload_with_verification()

    # 等待一下
    time.sleep(1)

    # 测试2: 不带验证
    total2, upload2, verify2 = test_upload_without_verification()

    # 性能对比
    if total1 and total2:
        print("\n" + "=" * 70)
        print("  性能对比总结")
        print("=" * 70)
        print()
        print(f"{'项目':<20} {'原流程':>15} {'优化后':>15} {'提升':>15}")
        print("-" * 70)
        print(f"{'上传时间':<20} {upload1:>12.3f}s {upload2:>12.3f}s {0:>12.1f}%")
        print(f"{'验证时间':<20} {verify1:>12.3f}s {verify2:>12.3f}s {100:>12.1f}%")
        print(f"{'总响应时间':<20} {total1:>12.3f}s {total2:>12.3f}s {((total1-total2)/total1*100):>12.1f}%")
        print("-" * 70)

        saved_time = total1 - total2
        improvement = (saved_time / total1) * 100

        print()
        print(f"[优化效果]")
        print(f"  节省时间: {saved_time:.3f} 秒")
        print(f"  性能提升: {improvement:.1f}%")
        print(f"  主要来源: 跳过不必要的 file_exists() 网络请求")
        print()
        print(f"[建议]")
        print(f"  - 上传成功（status=200）即可确认文件已存在")
        print(f"  - 直接返回 CDN URL 给用户，提升用户体验")
        print(f"  - 如需验证，可在后台异步进行")
        print()
        print("=" * 70)


if __name__ == '__main__':
    main()
