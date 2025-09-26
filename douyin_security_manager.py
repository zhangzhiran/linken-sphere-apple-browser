# -*- coding: utf-8 -*-
"""
抖音聊天监控工具安全管理模块
处理用户认证、远程服务器验证等功能
"""

import os
import json
import hashlib
import secrets
import base64
import time
import requests
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from douyin_config import config

class DouyinSecurityManager:
    def __init__(self):
        self.app_name = "DouyinChatMonitor"
        self.config_dir = self._get_secure_config_dir()
        # 使用更隐蔽的文件名
        self.auth_file = os.path.join(self.config_dir, "douyin_auth.cache")
        self.config_file = os.path.join(self.config_dir, "douyin_config.registry")
        
        # 远程服务器配置
        self.server_host = config.SERVER_HOST
        self.server_port = config.SERVER_PORT
        self.server_url = config.get_server_url()
        
        # 确保配置目录存在
        self._ensure_writable_config_dir()
        
        # 设置文件为隐藏（Windows）
        if os.name == 'nt':
            try:
                import ctypes
                for file_path in [self.auth_file, self.config_file]:
                    if os.path.exists(file_path):
                        ctypes.windll.kernel32.SetFileAttributesW(file_path, 2)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
    
    def _get_secure_config_dir(self) -> str:
        """获取安全的配置目录路径"""
        try:
            # 优先使用AppData目录，权限更好
            if os.name == 'nt':  # Windows
                appdata = os.environ.get('APPDATA')
                if appdata:
                    config_dir = os.path.join(appdata, "DouyinChatMonitor")
                    return config_dir

            # 回退到用户主目录
            user_home = os.path.expanduser("~")
            config_dir = os.path.join(user_home, "DouyinChatMonitor")
            return config_dir
        except Exception:
            # 最后回退到临时目录
            import tempfile
            return os.path.join(tempfile.gettempdir(), "DouyinChatMonitor")
    
    def _ensure_writable_config_dir(self):
        """确保配置目录可写"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            print(f"[INFO] 使用配置目录: {self.config_dir}")
            
            # 设置目录权限（尽力而为）
            try:
                if os.name == 'nt':  # Windows
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(self.config_dir, 2)  # FILE_ATTRIBUTE_HIDDEN
                else:  # Linux/Mac
                    os.chmod(self.config_dir, 0o700)
            except:
                pass
                
        except Exception as e:
            print(f"[ERROR] 创建配置目录失败: {e}")
            # 使用临时目录作为备选
            import tempfile
            self.config_dir = os.path.join(tempfile.gettempdir(), 'douyin_chat_monitor_' + str(os.getpid()))
            try:
                os.makedirs(self.config_dir, exist_ok=True)
                print(f"[INFO] 使用备选配置目录: {self.config_dir}")
                self.auth_file = os.path.join(self.config_dir, "douyin_auth.cache")
                self.config_file = os.path.join(self.config_dir, "douyin_config.registry")
            except Exception as e2:
                print(f"[ERROR] 创建备选配置目录也失败: {e2}")
    
    def _simple_encrypt(self, data: str, key: str) -> str:
        """简单的XOR加密"""
        key_bytes = hashlib.sha256(key.encode()).digest()
        data_bytes = data.encode('utf-8')
        
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(encrypted).decode()
    
    def _simple_decrypt(self, encrypted_data: str, key: str) -> str:
        """简单的XOR解密"""
        try:
            key_bytes = hashlib.sha256(key.encode()).digest()
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return decrypted.decode('utf-8')
        except:
            return ""
    
    def verify_user_remote(self, username: str, password: str) -> bool:
        """远程服务器验证用户"""
        try:
            # 准备验证数据
            auth_data = {
                'username': username,
                'password': password,
                'app_name': 'douyin_chat_monitor',
                'timestamp': int(time.time())
            }
            
            # 发送验证请求
            response = requests.post(
                f"{self.server_url}/api/verify_user",
                json=auth_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            else:
                print(f"[ERROR] 服务器验证失败，状态码: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 连接服务器失败: {e}")
            # 如果服务器连接失败，尝试本地验证作为备选
            return self.verify_user_local(username, password)
        except Exception as e:
            print(f"[ERROR] 远程验证出错: {e}")
            return False
    
    def verify_user_local(self, username: str, password: str) -> bool:
        """本地验证用户（备选方案）"""
        try:
            # 加载本地用户数据
            users_data = self._load_local_users_data()
            
            # 检查用户是否存在
            if username not in users_data.get('users', {}):
                return False
            
            user_data = users_data['users'][username]
            stored_password = user_data.get('password')
            
            # 简单密码验证
            return stored_password == password
            
        except Exception as e:
            print(f"[ERROR] 本地验证失败: {e}")
            return False
    
    def _load_local_users_data(self) -> dict:
        """加载本地用户数据"""
        try:
            if not os.path.exists(self.auth_file):
                # 如果没有本地用户数据，创建默认用户
                default_users = {
                    'users': {
                        'admin': {'password': 'douyin123456'},
                        'test': {'password': 'test123456'}
                    }
                }
                self._save_local_users_data(default_users)
                return default_users
            
            with open(self.auth_file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._simple_decrypt(encrypted_data, "douyin_users_key_2024")
            if not decrypted_data:
                return {'users': {}}
            
            return json.loads(decrypted_data)
        except:
            return {'users': {}}
    
    def _save_local_users_data(self, users_data: dict) -> bool:
        """保存本地用户数据"""
        try:
            json_data = json.dumps(users_data)
            encrypted_data = self._simple_encrypt(json_data, "douyin_users_key_2024")
            
            os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
            
            with open(self.auth_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            # 设置文件为隐藏
            if os.name == 'nt':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(self.auth_file, 6)  # HIDDEN + SYSTEM
                except:
                    pass
            
            return True
        except Exception as e:
            print(f"[ERROR] 保存本地用户数据失败: {e}")
            return False
    
    def save_config(self, config_data: dict, username: str) -> bool:
        """保存用户配置"""
        try:
            config_json = json.dumps(config_data, ensure_ascii=False, indent=2)
            encrypted_config = self._simple_encrypt(config_json, f"config_{username}")
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_config)
            
            return True
        except Exception as e:
            print(f"[ERROR] 保存配置失败: {e}")
            return False
    
    def load_config(self, username: str) -> Optional[dict]:
        """加载用户配置"""
        try:
            if not os.path.exists(self.config_file):
                return {}
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                encrypted_config = f.read()
            
            decrypted_config = self._simple_decrypt(encrypted_config, f"config_{username}")
            if not decrypted_config:
                return {}
            
            return json.loads(decrypted_config)
        except Exception as e:
            print(f"[ERROR] 加载配置失败: {e}")
            return {}
    
    def save_last_login_user(self, username: str) -> bool:
        """保存最后登录的用户名"""
        try:
            last_user_file = os.path.join(self.config_dir, "last_login.dat")
            
            user_data = {
                'username': username,
                'login_time': time.time()
            }
            
            encrypted_data = self._simple_encrypt(json.dumps(user_data), "last_login_key")
            
            with open(last_user_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"[ERROR] 保存最后登录用户失败: {e}")
            return False
    
    def get_last_login_user(self) -> str:
        """获取最后登录的用户名"""
        try:
            last_user_file = os.path.join(self.config_dir, "last_login.dat")
            
            if not os.path.exists(last_user_file):
                return ""
            
            with open(last_user_file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._simple_decrypt(encrypted_data, "last_login_key")
            user_data = json.loads(decrypted_data)
            
            return user_data.get('username', '')
        except Exception as e:
            print(f"[ERROR] 获取最后登录用户失败: {e}")
            return ""

    def _get_machine_key(self) -> bytes:
        """生成基于机器特征的密钥"""
        try:
            import platform
            import getpass

            # 收集机器特征
            machine_info = {
                'node': platform.node(),
                'system': platform.system(),
                'processor': platform.processor(),
                'user': getpass.getuser(),
                'app_name': self.app_name
            }

            # 创建机器指纹
            machine_string = json.dumps(machine_info, sort_keys=True)
            machine_bytes = machine_string.encode('utf-8')

            # 使用PBKDF2生成密钥
            salt = douyin_config.ENCRYPTION_SALT  # 固定盐值
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_bytes))
            return key

        except Exception as e:
            print(f"[ERROR] 生成机器密钥失败: {e}")
            # 回退到简单密钥
            fallback_key = hashlib.sha256(f"{self.app_name}_fallback".encode()).digest()
            return base64.urlsafe_b64encode(fallback_key)

    def save_credentials(self, username: str, password: str) -> bool:
        """保存用户凭据（加密存储）"""
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                # 确保配置目录存在且可写
                if not os.path.exists(self.config_dir):
                    os.makedirs(self.config_dir, exist_ok=True)

                # 生成机器密钥
                key = self._get_machine_key()
                fernet = Fernet(key)

                # 准备要保存的数据
                credentials_data = {
                    'username': username,
                    'password': password,
                    'saved_time': time.time(),
                    'app_version': douyin_config.APP_VERSION
                }

                # 加密数据
                json_data = json.dumps(credentials_data)
                encrypted_data = fernet.encrypt(json_data.encode('utf-8'))

                # 尝试不同的文件名
                if attempt == 0:
                    credentials_file = os.path.join(self.config_dir, "douyin_credentials.secure")
                elif attempt == 1:
                    credentials_file = os.path.join(self.config_dir, f"douyin_cred_{os.getpid()}.secure")
                else:
                    # 最后尝试临时目录
                    import tempfile
                    temp_dir = tempfile.gettempdir()
                    credentials_file = os.path.join(temp_dir, f"douyin_cred_{os.getpid()}.secure")

                # 保存到文件
                with open(credentials_file, 'wb') as f:
                    f.write(encrypted_data)

                # 设置文件为隐藏（Windows）
                if os.name == 'nt':
                    try:
                        import ctypes
                        ctypes.windll.kernel32.SetFileAttributesW(credentials_file, 2)  # FILE_ATTRIBUTE_HIDDEN
                    except:
                        pass

                print(f"[INFO] 凭据已安全保存到: {credentials_file}")

                # 更新实例变量以记住成功的路径
                self._credentials_file = credentials_file
                return True

            except PermissionError as e:
                print(f"[WARNING] 保存凭据权限错误 (尝试 {attempt + 1}/{max_attempts}): {e}")
                if attempt < max_attempts - 1:
                    continue
                else:
                    print(f"[ERROR] 所有尝试都失败，无法保存凭据")
                    return False

            except Exception as e:
                print(f"[ERROR] 保存凭据失败 (尝试 {attempt + 1}/{max_attempts}): {e}")
                if attempt < max_attempts - 1:
                    continue
                else:
                    return False

        return False

    def _find_credentials_file(self) -> Optional[str]:
        """查找凭据文件"""
        # 检查是否有记录的成功路径
        if hasattr(self, '_credentials_file') and os.path.exists(self._credentials_file):
            return self._credentials_file

        # 尝试常见的文件位置
        possible_files = [
            os.path.join(self.config_dir, "douyin_credentials.secure"),
            os.path.join(self.config_dir, f"douyin_cred_{os.getpid()}.secure"),
        ]

        # 添加临时目录的可能位置
        import tempfile
        temp_dir = tempfile.gettempdir()
        possible_files.append(os.path.join(temp_dir, f"douyin_cred_{os.getpid()}.secure"))

        # 查找现有文件
        for file_path in possible_files:
            if os.path.exists(file_path):
                self._credentials_file = file_path
                return file_path

        return None

    def load_credentials(self) -> Optional[Dict[str, str]]:
        """加载保存的用户凭据"""
        try:
            credentials_file = self._find_credentials_file()

            if not credentials_file:
                return None

            # 生成机器密钥
            key = self._get_machine_key()
            fernet = Fernet(key)

            # 读取加密数据
            with open(credentials_file, 'rb') as f:
                encrypted_data = f.read()

            # 解密数据
            decrypted_data = fernet.decrypt(encrypted_data)
            credentials_data = json.loads(decrypted_data.decode('utf-8'))

            # 检查数据有效性
            required_fields = ['username', 'password', 'saved_time']
            if not all(field in credentials_data for field in required_fields):
                print("[WARNING] 凭据数据格式无效")
                return None

            # 检查保存时间（可选：设置过期时间）
            saved_time = credentials_data.get('saved_time', 0)
            current_time = time.time()
            # 设置凭据有效期为90天
            if current_time - saved_time > douyin_config.CREDENTIALS_EXPIRE_DAYS * 24 * 3600:
                print("[WARNING] 保存的凭据已过期")
                self.clear_credentials()
                return None

            return {
                'username': credentials_data['username'],
                'password': credentials_data['password']
            }

        except Exception as e:
            print(f"[ERROR] 加载凭据失败: {e}")
            return None

    def clear_credentials(self) -> bool:
        """清除保存的凭据"""
        try:
            credentials_file = self._find_credentials_file()

            if credentials_file and os.path.exists(credentials_file):
                os.remove(credentials_file)
                print("[INFO] 已清除保存的凭据")
                # 清除记录的路径
                if hasattr(self, '_credentials_file'):
                    delattr(self, '_credentials_file')
                return True
            else:
                print("[INFO] 没有找到保存的凭据")
                return True

        except Exception as e:
            print(f"[ERROR] 清除凭据失败: {e}")
            return False

    def has_saved_credentials(self) -> bool:
        """检查是否有保存的凭据"""
        credentials_file = self._find_credentials_file()
        return credentials_file is not None and os.path.exists(credentials_file)

    def verify_user_remote(self, username: str, password: str) -> bool:
        """远程服务器用户验证"""
        try:
            print(f"[INFO] 开始远程验证用户: {username}")

            # 构建验证请求数据
            data = {
                'username': username,
                'password': password,
                'app_name': 'douyin_chat_monitor'
            }

            # 发送验证请求
            verify_url = config.get_api_url('verify_user')
            print(f"[INFO] 发送验证请求到: {verify_url}")

            response = requests.post(
                verify_url,
                json=data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            print(f"[INFO] 服务器响应状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"[INFO] 服务器响应: {result}")

                if result.get('success'):
                    print(f"[INFO] 远程验证成功: {username}")
                    return True
                else:
                    print(f"[WARNING] 远程验证失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"[ERROR] 服务器响应错误: {response.status_code}")
                # 尝试解析错误信息
                try:
                    error_data = response.json()
                    print(f"[ERROR] 错误详情: {error_data.get('message', '未知错误')}")
                except:
                    print(f"[ERROR] 无法解析错误响应")
                return False

        except requests.exceptions.ConnectionError:
            print(f"[ERROR] 无法连接到远程服务器: {self.server_url}")
            return False
        except requests.exceptions.Timeout:
            print(f"[ERROR] 远程验证请求超时")
            return False
        except Exception as e:
            print(f"[ERROR] 远程验证异常: {e}")
            return False

    def test_server_connection(self) -> bool:
        """测试服务器连接"""
        try:
            status_url = config.get_api_url('status')
            response = requests.get(status_url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                print(f"[INFO] 服务器连接正常: {data.get('service', 'unknown')}")
                return True
            else:
                print(f"[WARNING] 服务器状态异常: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 服务器连接测试失败: {e}")
            return False
