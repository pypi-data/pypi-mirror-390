import uuid
from minio import Minio, S3Error
from io import BytesIO
import requests
from datetime import datetime
from loguru import logger
import os

# 从环境变量读取配置，提供默认值
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio.tinfod.cn:11443")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "NTEFqdi05nWr7sUXtkje")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "b3Ap1drF88qWLOzYdfLkM2oaFdqAzEqpbKA0SyCs")


class DealImage:
    def __init__(self, bucket_name="tendata-enterprise", folder_name="exhibition_images"):
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.bucket_name = bucket_name
        self.folder_name = folder_name
        self.minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=True,
            region="us-east-1",
        )

    def check_object_exists(self, object_name):
        try:
            self.minio_client.stat_object(self.bucket_name, object_name)
            logger.info(f"'{object_name}'已经存在于'{self.bucket_name}'.")
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                pass
            else:
                logger.error(f"Error occurred: {e}")
            return False

    def is_exists(self, image_name):
        file_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, image_name))
        current_date = datetime.now()
        # 更优雅的日期处理
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")

        object_path = f"{self.folder_name}/{year}/{month}/{day}/{file_name}"
        direct_url = f"https://{MINIO_ENDPOINT}/{self.bucket_name}/{object_path}"

        return object_path,direct_url


    def upload_to_minio(self, upload_bytes, image_name):

        object_path, direct_url = self.is_exists(image_name)

        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(bucket_name=self.bucket_name)
            logger.warning(f"Minio-存储桶不存在，创建存储桶: {self.bucket_name}")
        try:
            if not self.check_object_exists(object_path):
                with BytesIO(upload_bytes) as data_stream:
                    self.minio_client.put_object(
                        bucket_name=self.bucket_name,
                        object_name=object_path,
                        data=data_stream,
                        length=len(upload_bytes),
                        content_type="image/jpeg",
                    )
                logger.success(f"{direct_url}-文件已经上传至{self.bucket_name}")
            else:
                logger.info(f"Minio-文件已存在，跳过上传: {object_path}")
            return direct_url
        except S3Error as e:
            logger.error(f"Minio-操作失败：{e}")
            return None
        except Exception as e:
            logger.error(f"Minio-上传文件失败：{e}")

    def crawl_image(self, url):

        if not url:
            logger.error("URL不能为空")
            return None

        if 'http' not in url:
            logger.error("URL异常")
            return None

        try:
            image_res = requests.get(url, headers=self.headers, timeout=60)  # 添加超时 , proxies=kdl_proxy()
            image_res.raise_for_status()
            # 使用 BytesIO 更高效地处理大文件
            image_data = BytesIO()
            for chunk in image_res.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    image_data.write(chunk)

            image_bytes = image_data.getvalue()
            if not image_bytes:
                logger.error("下载的图片数据为空")
                return None

            return image_bytes

        except requests.exceptions.Timeout:
            logger.error(f"图片下载超时: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"图片下载 HTTP错误: {e}, URL: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"图片下载 请求异常: {e}, URL: {url}")
            return None
        except Exception as e:
            logger.error(f"图片处理异常: {e}, URL: {url}")
            return None

    def run(self, url):
        object_path, direct_url = self.is_exists(url)
        if self.check_object_exists(object_path):
            logger.info(f"该文件已经存在，不需要下载和上传：{object_path}")
            return direct_url

        for i in range(5):
            image_bytes = self.crawl_image(url)
            if image_bytes:
                minio_url = self.upload_to_minio(image_bytes, url)
                return minio_url
            else:
                logger.error(f"crawl_image_error_count:{i},{url}")
                continue
        logger.error(f"该图片下载失败:{url}")
        return None