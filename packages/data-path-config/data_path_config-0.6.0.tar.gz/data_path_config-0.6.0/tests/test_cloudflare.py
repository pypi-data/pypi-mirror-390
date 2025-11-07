import os
import sys
import time
import requests
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the local package
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables from .env file
load_dotenv('.env')

# Get the access token from environment
access_token = os.getenv('ACCESS_TOKEN')
if not access_token:
    raise ValueError("ACCESS_TOKEN not found in .env file")

# Get the R2 domain for verification
r2_domain = os.getenv('R2_DOMAIN')

# Import the clients
from data_path_config.cloudflare.requests_client import CloudflareRequestsClient
from data_path_config.cloudflare.boto3_client import CloudflareBoto3Client

def test_requests_client():
    print("Testing CloudflareRequestsClient...")
    client = CloudflareRequestsClient(access_token)

    # Test token validation
    is_valid, data = client.validate_token()
    print(f"Token valid: {is_valid}")
    if not is_valid:
        print(f"Error: {data}")
        assert False, f"Token validation failed: {data}"

    # Get account info
    account_id, name = client.get_account_id_name()
    print(f"Account ID: {account_id}, Name: {name}")
    assert account_id is not None

    # Get buckets via API
    buckets = client.get_buckets()
    print(f"Buckets (API): {buckets}")

def test_boto3_client():
    print("\nTesting CloudflareBoto3Client...")
    # First get account_id
    req_client = CloudflareRequestsClient(access_token)
    account_id, _ = req_client.get_account_id_name()
    assert account_id is not None, "Failed to get account ID"

    boto_client = CloudflareBoto3Client(access_token, account_id)

    # List buckets via S3
    buckets = boto_client.list_buckets()
    print(f"Buckets (S3): {buckets}")

    # Test create bucket
    test_bucket_name = f"test-bucket-{int(time.time())}"
    create_result = boto_client.create_bucket(test_bucket_name)
    print(f"Create bucket result: {create_result}")
    
    if create_result:
        # Verify bucket was created
        buckets_after_create = boto_client.list_buckets()
        bucket_names = [b['Name'] for b in buckets_after_create] if buckets_after_create else []
        if test_bucket_name in bucket_names:
            print("Bucket creation verified successfully")
        else:
            print("Bucket creation verification failed")
        
        # Test delete bucket (only if empty)
        delete_result = boto_client.delete_bucket(test_bucket_name)
        print(f"Delete bucket result: {delete_result}")
        
        if delete_result:
            # Verify bucket was deleted
            buckets_after_delete = boto_client.list_buckets()
            bucket_names_after = [b['Name'] for b in buckets_after_delete] if buckets_after_delete else []
            if test_bucket_name not in bucket_names_after:
                print("Bucket deletion verified successfully")
            else:
                print("Bucket deletion verification failed")
    else:
        print("Bucket creation failed, skipping delete test")

    if buckets:
        bucket_name = buckets[0]['Name']
        key = f"test-upload-boto3-{int(time.time())}"
        content = b"test boto3 upload content"
        result = boto_client.upload_file(bucket_name, key, content)
        print(f"Upload result: {result}")
        if result and r2_domain:
            # Verify upload
            url = f"{r2_domain.rstrip('/')}/{key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and response.content == content:
                print("Upload verified successfully")
            else:
                print(f"Verification failed: status {response.status_code}, content match: {response.content == content}")
        elif result:
            print("Upload successful, but R2_DOMAIN not set, skipping verification")
        
        # Test delete
        if result:
            delete_result = boto_client.delete_file(bucket_name, key)
            print(f"Delete result: {delete_result}")
            if delete_result and r2_domain:
                # Verify delete
                url = f"{r2_domain.rstrip('/')}/{key}"
                response = requests.get(url, timeout=10)
                if response.status_code == 404:
                    print("Delete verified successfully")
                else:
                    print(f"Delete verification failed: status {response.status_code}")
            elif delete_result:
                print("Delete successful, but R2_DOMAIN not set, skipping verification")
    else:
        print("No buckets found, skipping upload test")

if __name__ == "__main__":
    test_requests_client()
    test_boto3_client()