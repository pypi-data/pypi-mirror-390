import os
import requests

class CloudflareRequestsClient:
    def __init__(self, token=None):
        if token is None:
            token = os.getenv('R2_ACCESS_TOKEN')
        if not token:
            raise ValueError("Token must be provided or set in environment variable R2_ACCESS_TOKEN")
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.account_id = None

    def validate_token(self):
        response = requests.get(f"{self.base_url}/user/tokens/verify", headers=self.headers)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text

    def get_token_status(self):
        return self.validate_token()

    def get_id(self):
        success, data = self.validate_token()
        if success:
            return data['result']['id']
        else:
            return None

    def get_account_id_name(self):
        response = requests.get(f"{self.base_url}/accounts", headers=self.headers)
        if response.status_code == 200:
            accounts = response.json()['result']
            if accounts:
                self.account_id = accounts[0]['id']
                name = accounts[0]['name']
                return self.account_id, name
            else:
                return None, None
        else:
            return None, None

    def get_buckets(self):
        if not self.account_id:
            self.get_account_id_name()
        if self.account_id:
            response = requests.get(f"{self.base_url}/accounts/{self.account_id}/r2/buckets", headers=self.headers)
            if response.status_code == 200:
                buckets = response.json()['result']['buckets']
                return buckets
            else:
                return None
        else:
            return None