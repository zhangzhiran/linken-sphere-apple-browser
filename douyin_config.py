# -*- coding: utf-8 -*-
"""
抖音多直播间聊天监控工具系统配置文件
集中管理所有配置项，避免硬编码
"""

import os

class DouyinConfig:
    """系统配置类"""
    
    # 服务器配置 - 使用比特授权同一台服务器
    SERVER_HOST = "155.94.153.141"
    SERVER_PORT = 5001
    SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
    
    # 认证配置
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "douyin123456"
    
    # 应用配置
    APP_NAME = "抖音多直播间聊天监控工具"
    APP_VERSION = "5.0"
    
    # 文件路径配置
    ICON_FILE = "icon.ico"
    
    # 用户管理器配置
    USER_MANAGER_TITLE = "抖音聊天监控 - 用户管理器"
    USER_MANAGER_GEOMETRY = "900x700"

    # 系统托盘配置
    TRAY_CONFIG = {
        'app_name': 'DouyinChatMonitor',
        'tooltip': '抖音聊天监控工具',
        'icon_file': 'tray_icon.ico'
    }

    # 开机自启动配置
    AUTOSTART_CONFIG = {
        'registry_key': r'Software\Microsoft\Windows\CurrentVersion\Run',
        'app_name': 'DouyinChatMonitor',
        'startup_args': ['--minimized']
    }
    
    # 登录窗口配置
    LOGIN_WINDOW_TITLE = "抖音多直播间聊天监控工具 - 用户登录"
    LOGIN_WINDOW_GEOMETRY = "500x450"
    
    # 主程序配置
    MAIN_APP_TITLE = "抖音多直播间聊天监控工具"
    MAIN_APP_GEOMETRY = "1920x1080"
    
    # 安全配置
    CREDENTIALS_EXPIRE_DAYS = 90
    ENCRYPTION_SALT = b'douyin_chat_monitor_salt_2024'
    
    # API端点配置
    API_ENDPOINTS = {
        'status': '/api/status',
        'users': '/api/users',
        'add_user': '/api/add_user',
        'delete_user': '/api/delete_user',
        'update_user': '/api/update_user',
        'set_user_time': '/api/set_user_time',
        'verify_user': '/api/verify_user',
        'upload_file': '/api/upload_file'
    }
    
    # 文件上传配置
    UPLOAD_CONFIG = {
        'max_file_size': 50 * 1024 * 1024,  # 50MB
        'allowed_extensions': ['.txt', '.json', '.log', '.csv', '.xml', '.html'],
        'upload_dir': 'uploads',
        'chunk_size': 1024 * 1024  # 1MB chunks
    }
    
    # 系统托盘配置
    TRAY_CONFIG = {
        'icon_file': 'tray_icon.ico',
        'tooltip': '抖音聊天监控工具',
        'menu_items': [
            '显示主窗口',
            '开始监控',
            '停止监控',
            '导出数据',
            '设置',
            '退出程序'
        ]
    }
    
    # 自启动配置
    AUTOSTART_CONFIG = {
        'app_name': 'DouyinChatMonitor',
        'registry_key': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        'startup_args': ['--minimized', '--auto-start']
    }
    
    # 数据库配置（如果需要）
    DATABASE_CONFIG = {
        'type': 'json',  # 当前使用JSON文件
        'file_path': 'douyin_users.json'
    }
    
    # 日志配置
    LOG_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'douyin_chat_monitor.log',
        'max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
    
    # UI配置
    UI_CONFIG = {
        'theme': 'clam',
        'font_family': 'Microsoft YaHei',
        'font_size': 10,
        'colors': {
            'primary': '#1890ff',
            'secondary': '#722ed1',
            'success': '#52c41a',
            'warning': '#faad14',
            'error': '#f5222d',
            'info': '#13c2c2',
            'dark_bg': '#2c2c2c',
            'light_bg': '#f0f0f0'
        }
    }
    
    # 聊天监控配置
    CHAT_CONFIG = {
        'max_rooms': 12,
        'max_messages_per_room': 1000,
        'max_display_lines': 500,
        'auto_save_interval': 300,  # 5分钟
        'memory_cleanup_interval': 600,  # 10分钟
        'default_colors': [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
            '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
        ]
    }
    
    @classmethod
    def get_server_url(cls):
        """获取服务器URL"""
        return cls.SERVER_URL
    
    @classmethod
    def get_api_url(cls, endpoint_name):
        """获取API URL"""
        endpoint = cls.API_ENDPOINTS.get(endpoint_name)
        if endpoint:
            return f"{cls.SERVER_URL}{endpoint}"
        raise ValueError(f"未知的API端点: {endpoint_name}")
    
    @classmethod
    def get_admin_credentials(cls):
        """获取管理员凭据"""
        return {
            'username': cls.DEFAULT_ADMIN_USERNAME,
            'password': cls.DEFAULT_ADMIN_PASSWORD
        }
    
    @classmethod
    def load_from_env(cls):
        """从环境变量加载配置（可选）"""
        cls.SERVER_HOST = os.getenv('DOUYIN_SERVER_HOST', cls.SERVER_HOST)
        cls.SERVER_PORT = int(os.getenv('DOUYIN_SERVER_PORT', cls.SERVER_PORT))
        cls.SERVER_URL = f"http://{cls.SERVER_HOST}:{cls.SERVER_PORT}"
        cls.DEFAULT_ADMIN_PASSWORD = os.getenv('DOUYIN_ADMIN_PASSWORD', cls.DEFAULT_ADMIN_PASSWORD)
    
    @classmethod
    def validate_config(cls):
        """验证配置有效性"""
        errors = []
        
        # 检查必要的配置项
        if not cls.SERVER_HOST:
            errors.append("服务器主机地址不能为空")
        
        if not cls.SERVER_PORT or cls.SERVER_PORT <= 0:
            errors.append("服务器端口必须是正整数")
        
        if not cls.DEFAULT_ADMIN_PASSWORD:
            errors.append("管理员密码不能为空")
        
        if cls.CHAT_CONFIG['max_rooms'] <= 0:
            errors.append("最大直播间数量必须大于0")
        
        if errors:
            raise ValueError("配置验证失败: " + "; ".join(errors))
        
        return True
    
    @classmethod
    def get_upload_path(cls, filename):
        """获取上传文件的完整路径"""
        upload_dir = cls.UPLOAD_CONFIG['upload_dir']
        os.makedirs(upload_dir, exist_ok=True)
        return os.path.join(upload_dir, filename)
    
    @classmethod
    def is_allowed_file(cls, filename):
        """检查文件扩展名是否允许"""
        if not filename:
            return False
        ext = os.path.splitext(filename)[1].lower()
        return ext in cls.UPLOAD_CONFIG['allowed_extensions']

# 全局配置实例
douyin_config = DouyinConfig()

# 在导入时加载环境变量配置
try:
    douyin_config.load_from_env()
    douyin_config.validate_config()
except Exception as e:
    print(f"[WARNING] 配置加载失败: {e}")

# 导出常用配置
SERVER_URL = douyin_config.SERVER_URL
ADMIN_PASSWORD = douyin_config.DEFAULT_ADMIN_PASSWORD
API_ENDPOINTS = douyin_config.API_ENDPOINTS
CHAT_CONFIG = douyin_config.CHAT_CONFIG

# 创建兼容的config实例
config = douyin_config
