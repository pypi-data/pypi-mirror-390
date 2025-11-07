import boto3
import hashlib
import mimetypes
import os
import requests

class CloudflareBoto3Client:
    def __init__(self, token=None, account_id=None):
        if token is None:
            token = os.getenv('R2_ACCESS_TOKEN')
        if account_id is None:
            account_id = os.getenv('R2_ACCOUNT_ID')
        if not token or not account_id:
            raise ValueError("Token and account_id must be provided or set in environment variables R2_ACCESS_TOKEN and R2_ACCOUNT_ID")
        self.token = token
        self.account_id = account_id
        self.s3_client = None
        self._setup_s3_client()

    def get_id(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get("https://api.cloudflare.com/client/v4/user/tokens/verify", headers=headers)
        if response.status_code == 200:
            return response.json()['result']['id']
        else:
            return None

    def _setup_s3_client(self):
        token_id = self.get_id()
        if token_id and self.account_id:
            access_key_id = token_id
            secret_access_key = hashlib.sha256(self.token.encode()).hexdigest()
            self.s3_client = boto3.client('s3',
                endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key
            )

    def list_buckets(self):
        if self.s3_client:
            buckets = self.s3_client.list_buckets()
            return buckets['Buckets']
        else:
            return None

    def upload_file(self, bucket_name, key, content, content_type=None):
        if self.s3_client:
            if content_type is None:
                content_type = mimetypes.guess_type(key)[0]
            kwargs = {'Bucket': bucket_name, 'Key': key, 'Body': content}
            if content_type:
                kwargs['ContentType'] = content_type
            self.s3_client.put_object(**kwargs)
            return True
        else:
            return False

    def delete_file(self, bucket_name, key):
        if self.s3_client:
            self.s3_client.delete_object(Bucket=bucket_name, Key=key)
            return True
        else:
            return False

    def create_bucket(self, bucket_name):
        if self.s3_client:
            self.s3_client.create_bucket(Bucket=bucket_name)
            return True
        else:
            return False

    def delete_bucket(self, bucket_name):
        if self.s3_client:
            self.s3_client.delete_bucket(Bucket=bucket_name)
            return True
        else:
            return False