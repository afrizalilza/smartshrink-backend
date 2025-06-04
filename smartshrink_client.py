import requests

class SmartShrinkClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def upload(self, file_path):
        files = {'file': open(file_path, 'rb')}
        resp = requests.post(f'{self.base_url}/upload', files=files)
        return resp.json()

    def compress(self, file_id, method='ai', sensitive_mode=False, profile='default'):
        data = {'file_id': file_id, 'method': method, 'sensitive_mode': sensitive_mode, 'profile': profile}
        resp = requests.post(f'{self.base_url}/compress', data=data)
        return resp.json()

    def download(self, file_id, out_path):
        resp = requests.get(f'{self.base_url}/download/{file_id}')
        with open(out_path, 'wb') as f:
            f.write(resp.content)
        return out_path

    def compare(self, file_id):
        resp = requests.get(f'{self.base_url}/compare/{file_id}')
        return resp.json()

    def batch_compress(self, items):
        resp = requests.post(f'{self.base_url}/batch_compress', json={'items': items})
        return resp.json()

    def diff_compress(self, file_id, base_file_id, method='patch', patch_file_id=None):
        data = {'file_id': file_id, 'base_file_id': base_file_id, 'method': method}
        if patch_file_id:
            data['patch_file_id'] = patch_file_id
        resp = requests.post(f'{self.base_url}/diff_compress', data=data)
        return resp.json()
