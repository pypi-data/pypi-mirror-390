import io

from minio import Minio
from minio.datatypes import Object, Bucket
from minio.helpers import ObjectWriteResult


class MinIOService:
    """MinIO服务类"""
    def __init__(self, minio_host: str, minio_access_key: str, minio_secret_key: str, minio_secure: bool = False):
        self.client = Minio(
            minio_host,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=minio_secure
        )
    def check_minio_health(self):
        """检查MinIO服务是否正常"""
        try:
            self.client.list_buckets()
            return True
        except Exception as e:
            return False

    def create_bucket(self, bucket_name: str) ->bool:
        """创建bucket"""
        self.client.make_bucket(bucket_name)
        return self.client.bucket_exists(bucket_name)

    def delete_bucket(self, bucket_name: str) ->bool:
        """删除bucket"""
        self.client.remove_bucket(bucket_name)
        return not self.client.bucket_exists(bucket_name)

    def list_buckets(self)->list[Bucket]:
        """列出所有bucket"""
        return self.client.list_buckets()

    def bucket_exists(self, bucket_name: str)->bool:
        """判断bucket是否存在"""
        return self.client.bucket_exists(bucket_name)

    def ensure_bucket_exists(self, bucket_name: str) ->bool:
        """确保bucket存在"""
        if not self.bucket_exists(bucket_name):
            return self.create_bucket(bucket_name)
        return True


    @staticmethod
    def build_object_name(object_path_list: list[str], file_path: str) -> str:
        """
        构建object名称
        :param object_path_list: 对象名列表， 如：['jupyter','user_id', 'project_id']
        :param file_path: 文件路径
        :return:
        """
        # 如果存在，移除file_path的前导斜杠
        clean_file_path = file_path.lstrip('/')
        object_name_list = [tmp for tmp in object_path_list]
        object_name_list.append(clean_file_path)
        return '/'.join(object_name_list)


    def save_file_stream(self, bucket_name: str, object_name: str, content: io.BytesIO)-> ObjectWriteResult:
        """上传文件流"""
        self.ensure_bucket_exists(bucket_name)
        return self.client.put_object(
            bucket_name,
            object_name,
            content,
            content.getbuffer().nbytes
        )
    def save_file(self, bucket_name: str, object_name: str, content: bytes)-> ObjectWriteResult:
        """上传文件"""
        return self.save_file_stream(bucket_name, object_name, io.BytesIO(content))

    def get_file_bytes(self, bucket_name: str, object_name: str) -> bytes:
        response = self.client.get_object(bucket_name, object_name)
        content = response.read()
        response.close()
        response.release_conn()
        return content

    def upload_file(self, bucket_name: str, object_name: str, file_path: str)-> ObjectWriteResult:
        """上传文件"""
        self.ensure_bucket_exists(bucket_name)
        return self.client.fput_object(bucket_name, object_name, file_path)

    def download_file(self, bucket_name: str, object_name: str, out_file: str) -> Object:
        """下载文件"""
        return self.client.fget_object(bucket_name, object_name, out_file)


    def delete_file(self, bucket_name: str, object_name: str)->bool:
        """删除文件"""
        self.client.remove_object(bucket_name, object_name)
        return True

    def list_files(self, bucket_name: str, prefix: str="",recursive: bool = False) -> list[Object]:
        """列出所有文件"""
        objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive)
        return [obj for obj in objects if not obj.object_name[len(prefix):].endswith('.gitkeep')]

    def get_file_stat(self, bucket_name: str, object_name: str)->Object:
        """获取文件信息"""
        return self.client.stat_object(bucket_name, object_name)

    def get_file_url(self, bucket_name: str, object_name: str)->str:
        """获取文件URL"""
        return self.client.presigned_get_object(bucket_name, object_name)

    def file_exists(self, bucket_name: str, object_name: str):
        """判断文件是否存在"""
        try:
            self.get_file_stat(bucket_name, object_name)
            return True
        except Exception as e:
            return False



