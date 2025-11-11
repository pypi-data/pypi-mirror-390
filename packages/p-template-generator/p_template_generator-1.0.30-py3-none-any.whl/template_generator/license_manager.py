import os, random, platform, time, json, hashlib, traceback, base64, requests
from threading import Thread, Lock
from typing import Optional, Tuple

def _get_config_dir():
    if platform.system() == "Windows":
        appdata = os.environ.get('APPDATA', '')
        config_dir = os.path.join(appdata, 'template_generator')
    else:
        home = os.path.expanduser('~')
        config_dir = os.path.join(home, '.config', 'template_generator')
    
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def _get_license_file_path():
    return os.path.join(_get_config_dir(), 'license.txt')

def _get_state_file_path():
    return os.path.join(_get_config_dir(), '.state')

def _encrypt_data(data: str) -> str:
    data_bytes = data.encode('utf-8')
    # 使用base64和简单的异或混淆
    import base64
    key = b'tg_secret_key_2024'
    encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(data_bytes)])
    return base64.b64encode(encrypted).decode('utf-8')

def _decrypt_data(encrypted: str) -> str:
    try:
        import base64
        key = b'tg_secret_key_2024'
        encrypted_bytes = base64.b64decode(encrypted.encode('utf-8'))
        decrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted_bytes)])
        return decrypted.decode('utf-8')
    except Exception:
        return None

class LicenseManager:
    _instance = None
    _lock = Lock()
    
    VERIFY_INTERVAL = 24 * 3600     # 24小时验证一次
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.state = self._load_state()
            self._ensure_install_time()
            self._start_background_verify()
    
    def _load_state(self) -> dict:
        try:
            state_file = _get_state_file_path()
            if os.path.exists(state_file):
                with open(state_file, 'r', encoding='utf-8') as f:
                    encrypted_data = f.read()
                    decrypted_data = _decrypt_data(encrypted_data)
                    if decrypted_data:
                        return json.loads(decrypted_data)
        except Exception as e:
            pass
        return {}
    
    def _save_state(self):
        try:
            state_file = _get_state_file_path()
            json_data = json.dumps(self.state)
            encrypted_data = _encrypt_data(json_data)
            with open(state_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
        except Exception as e:
            pass
    
    def _ensure_install_time(self):
        if self.state.get('install_time') is None:
            self.state['install_time'] = time.time()
            self._save_state()
    
    def _hash_license(self, license_key: str) -> str:
        return hashlib.sha256(license_key.encode('utf-8')).hexdigest()
    
    def _start_background_verify(self):
        def verify_task():
            self._periodic_verify()
        if self.should_verify():
            thread = Thread(target=verify_task, daemon=True)
            thread.start()
    
    def should_verify(self) -> bool:
        last_verify = self.state.get('last_verify_time')
        if last_verify is None:
            return True
        return (time.time() - last_verify) > self.VERIFY_INTERVAL
    
    def _periodic_verify(self):
        try:
            license_key = self.read_license()
            if license_key:
                api_result = self._verify_license_with_api(license_key)
                self.state['last_verify_time'] = time.time()
                if api_result:
                    self.state['valid'] = api_result['valid']
                    self.state['company_name'] = api_result['company_name']
                    self.state['sdk'] = api_result['sdk']
                    self.state['expires_at'] = api_result['expires_at']
                    self.state['days_remaining'] = api_result['days_remaining']
                else:
                    self.state['valid'] = False
                    self.state['company_name'] = None
                    self.state['sdk'] = None
                    self.state['expires_at'] = None
                    self.state['days_remaining'] = None
                self._save_state()
        except Exception as e:
            pass
    
    def _verify_license_with_api(self, license_key: str) -> bool:
        try:
            response = requests.post("https://api.zjtemplate.com/business/verify-license", 
                                     json={
                    'license': license_key
                }, headers= {
                    'Content-Type': 'application/json',
                    'usertoken': 'a1b2c3d4e5f67890abcdef12345678901234567890abcdef'
                }, timeout=30, verify=False)

            if response.status_code != 200:
                return None

            resp_json = response.json()
            if isinstance(resp_json, dict):
                if resp_json.get('code') == 0:
                    data = resp_json.get('data')
                    if 'valid' in data and data['valid']:
                        return {
                            'valid': True,
                            'company_name': data.get('company_name'),
                            'sdk': data.get('sdk'),
                            'expires_at': data.get('expires_at'),
                            'days_remaining': data.get('days_remaining')
                        }
                    return None
                return None
            return None
        except Exception as e:
            return None
    
    def check_license(self) -> Tuple[bool, str]:
        current_time = time.time()
        install_time = self.state.get('install_time', current_time)
        license_key = self.read_license()
        
        if not license_key:
            days_since_install = (current_time - install_time) / (24 * 3600)
            if days_since_install > 30:
                return f"您已使用{int(days_since_install)}天，完整功能请使用License。"
            else:
                remaining_days = 30 - int(days_since_install)
                if remaining_days < 5:
                    return f"试用期剩余{5}天，请及时购买License。"
                return ""
        
        valid = self.state.get('valid', False)
        days_remaining = self.state.get('days_remaining', 0)
        if valid:
            if days_remaining < 7:
                return f"剩余{days_remaining}天"
        else:
            return ""
    
    def read_license(self) -> Optional[str]:
        try:
            file_path = _get_license_file_path()
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception:
            pass
        return None

    def write_license(self, license_key: str) -> bool:
        if not license_key:
            print("License为空")
            return False
        
        try:
            file_path = _get_license_file_path()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(license_key)
            license_hash = self._hash_license(license_key)
            api_result = self._verify_license_with_api(license_key)
            self.state['last_verify_time'] = time.time()
            if api_result:
                self.state['valid'] = api_result['valid']
                self.state['company_name'] = api_result['company_name']
                self.state['sdk'] = api_result['sdk']
                self.state['expires_at'] = api_result['expires_at']
                self.state['days_remaining'] = api_result['days_remaining']
            else:
                self.state['valid'] = False
                self.state['company_name'] = None
                self.state['sdk'] = None
                self.state['expires_at'] = None
                self.state['days_remaining'] = None
                print("License验证未通过")
            self._save_state()
            return True
        except Exception as e:
            return False

_license_manager = None

def _get_manager() -> LicenseManager:
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager

def read_license():
    return _get_manager().read_license()

def write_license(license_key):
    return _get_manager().write_license(license_key)

def require_valid_license(func):
    def wrapper(*args, **kwargs):
        if random.random() < 0.2:
            message = _get_manager().check_license()
            if message and len(message) > 0:
                print(f"ℹ️ {message}")
        return func(*args, **kwargs)
    return wrapper