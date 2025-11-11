"""阿里云 OSS 上传服务"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import oss2
from dotenv import load_dotenv


load_dotenv()


class OSSService:
    """阿里云 OSS 服务类"""

    def __init__(self):
        """初始化 OSS 客户端"""
        self.access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
        self.bucket_name = os.getenv('OSS_BUCKET')
        self.endpoint = os.getenv('OSS_ENDPOINT')
        self.cdn_url = os.getenv('OSS_CDN_URL', '').rstrip('/')

        if not all([self.access_key_id, self.access_key_secret, self.bucket_name, self.endpoint]):
            raise ValueError('OSS 配置不完整，请检查环境变量')

        # 创建认证对象
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)

        # 创建 Bucket 对象
        self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)

    def generate_object_key(self, filename: str, business_dir: str = 'data') -> str:
        """
        生成 OSS 对象键（存储路径）

        格式: /{business_dir}/{YYYYMM}/{timestamp}_{uuid}.{ext}

        Args:
            filename: 原始文件名
            business_dir: 业务目录，默认 'data'

        Returns:
            str: OSS 对象键
        """
        # 获取文件扩展名
        ext = Path(filename).suffix.lower()

        # 生成年月目录
        now = datetime.now()
        date_dir = now.strftime('%Y%m')

        # 生成唯一文件名
        timestamp = int(now.timestamp() * 1000)
        unique_id = uuid.uuid4().hex[:8]
        new_filename = f'{timestamp}_{unique_id}{ext}'

        # 组合完整路径
        object_key = f'{business_dir}/{date_dir}/{new_filename}'

        return object_key

    def upload_file(self, file_path: str, object_key: Optional[str] = None,
                   business_dir: str = 'data') -> dict:
        """
        上传本地文件到 OSS

        Args:
            file_path: 本地文件路径
            object_key: OSS 对象键，如果为 None 则自动生成
            business_dir: 业务目录，默认 'data'

        Returns:
            dict: 上传结果，包含 object_key, url, cdn_url
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f'文件不存在: {file_path}')

        # 如果未指定 object_key，则自动生成
        if object_key is None:
            object_key = self.generate_object_key(file_path.name, business_dir)

        # 上传文件
        with open(file_path, 'rb') as f:
            result = self.bucket.put_object(object_key, f)

        if result.status != 200:
            raise Exception(f'上传失败: {result.status}')

        # 生成访问 URL
        oss_url = f'https://{self.bucket_name}.{self.endpoint}/{object_key}'
        cdn_url = f'{self.cdn_url}/{object_key}' if self.cdn_url else oss_url

        return {
            'object_key': object_key,
            'oss_url': oss_url,
            'cdn_url': cdn_url,
            'status': result.status
        }

    def upload_bytes(self, data: bytes, filename: str,
                    object_key: Optional[str] = None,
                    business_dir: str = 'data') -> dict:
        """
        上传字节数据到 OSS

        Args:
            data: 字节数据
            filename: 文件名（用于提取扩展名）
            object_key: OSS 对象键，如果为 None 则自动生成
            business_dir: 业务目录，默认 'data'

        Returns:
            dict: 上传结果，包含 object_key, url, cdn_url
        """
        # 如果未指定 object_key，则自动生成
        if object_key is None:
            object_key = self.generate_object_key(filename, business_dir)

        # 上传数据
        result = self.bucket.put_object(object_key, data)

        if result.status != 200:
            raise Exception(f'上传失败: {result.status}')

        # 生成访问 URL
        oss_url = f'https://{self.bucket_name}.{self.endpoint}/{object_key}'
        cdn_url = f'{self.cdn_url}/{object_key}' if self.cdn_url else oss_url

        return {
            'object_key': object_key,
            'oss_url': oss_url,
            'cdn_url': cdn_url,
            'status': result.status
        }

    def delete_file(self, object_key: str) -> bool:
        """
        删除 OSS 文件

        Args:
            object_key: OSS 对象键

        Returns:
            bool: 删除是否成功
        """
        try:
            result = self.bucket.delete_object(object_key)
            return result.status == 204
        except Exception as e:
            print(f'删除文件失败: {e}')
            return False

    def file_exists(self, object_key: str) -> bool:
        """
        检查文件是否存在

        Args:
            object_key: OSS 对象键

        Returns:
            bool: 文件是否存在
        """
        try:
            return self.bucket.object_exists(object_key)
        except Exception:
            return False

    def get_file_url(self, object_key: str, use_cdn: bool = True) -> str:
        """
        获取文件访问 URL

        Args:
            object_key: OSS 对象键
            use_cdn: 是否使用 CDN URL

        Returns:
            str: 文件访问 URL
        """
        if use_cdn and self.cdn_url:
            return f'{self.cdn_url}/{object_key}'
        return f'https://{self.bucket_name}.{self.endpoint}/{object_key}'


# 创建全局单例
_oss_service_instance = None


def get_oss_service() -> OSSService:
    """获取 OSS 服务单例"""
    global _oss_service_instance
    if _oss_service_instance is None:
        _oss_service_instance = OSSService()
    return _oss_service_instance
