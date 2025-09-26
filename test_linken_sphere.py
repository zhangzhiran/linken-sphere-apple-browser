#!/usr/bin/env python3
"""
Linken Sphere 集成测试脚本
测试 API 连接、配置文件创建、会话管理等功能
"""

import sys
import time
import logging
from typing import Dict, Optional

try:
    from linken_sphere_api import LinkenSphereManager, LinkenSphereAPI
except ImportError:
    print("❌ 无法导入 Linken Sphere API 模块")
    print("请确保 linken_sphere_api.py 文件存在")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkenSphereTest:
    """Linken Sphere 测试类"""
    
    def __init__(self, api_host: str = "127.0.0.1", api_port: int = 3001):
        self.api_host = api_host
        self.api_port = api_port
        self.manager = LinkenSphereManager(api_host, api_port)
        self.test_results = {}
    
    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        print("🧪 开始 Linken Sphere 集成测试")
        print("=" * 60)
        
        tests = [
            ("API 连接测试", self.test_api_connection),
            ("配置文件列表测试", self.test_get_profiles),
            ("配置文件创建测试", self.test_create_profile),
            ("会话管理测试", self.test_session_management),
            ("完整流程测试", self.test_full_workflow)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                self.test_results[test_name] = result
                
                if result:
                    print(f"✅ {test_name} - 通过")
                else:
                    print(f"❌ {test_name} - 失败")
                    
            except Exception as e:
                print(f"❌ {test_name} - 异常: {e}")
                self.test_results[test_name] = False
        
        self.print_summary()
        return self.test_results
    
    def test_api_connection(self) -> bool:
        """测试 API 连接"""
        try:
            print(f"正在连接到 {self.api_host}:{self.api_port}")
            
            # 测试基础连接
            api = LinkenSphereAPI(self.api_host, self.api_port)
            connection_ok = api.check_connection()
            
            if connection_ok:
                print("✅ API 连接成功")
                return True
            else:
                print("❌ API 连接失败")
                return False
                
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    def test_get_profiles(self) -> bool:
        """测试获取配置文件列表"""
        try:
            if not self.manager.initialize():
                print("❌ 管理器初始化失败")
                return False
            
            profiles = self.manager.api.get_profiles()
            print(f"📋 找到 {len(profiles)} 个配置文件")
            
            for i, profile in enumerate(profiles[:3]):  # 只显示前3个
                print(f"  {i+1}. {profile.get('name', 'Unknown')} (ID: {profile.get('id', 'N/A')})")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取配置文件失败: {e}")
            return False
    
    def test_create_profile(self) -> bool:
        """测试创建配置文件"""
        try:
            if not self.manager.initialize():
                print("❌ 管理器初始化失败")
                return False
            
            test_profile_name = f"Test Profile {int(time.time())}"
            print(f"🔧 创建测试配置文件: {test_profile_name}")
            
            profile = self.manager.profile_manager.create_default_profile(test_profile_name)
            
            if profile and 'id' in profile:
                print(f"✅ 配置文件创建成功")
                print(f"  - 名称: {profile.get('name')}")
                print(f"  - ID: {profile.get('id')}")
                return True
            else:
                print("❌ 配置文件创建失败")
                return False
                
        except Exception as e:
            print(f"❌ 创建配置文件异常: {e}")
            return False
    
    def test_session_management(self) -> bool:
        """测试会话管理"""
        try:
            if not self.manager.initialize():
                print("❌ 管理器初始化失败")
                return False
            
            test_profile_name = f"Session Test Profile {int(time.time())}"
            print(f"🚀 测试会话管理，配置文件: {test_profile_name}")
            
            # 创建会话
            session = self.manager.create_browser_session(test_profile_name)
            
            if not session:
                print("❌ 会话创建失败")
                return False
            
            session_id = session.get('session_id')
            print(f"✅ 会话创建成功")
            print(f"  - 会话ID: {session_id}")
            print(f"  - 主机: {session.get('host', 'N/A')}")
            print(f"  - 端口: {session.get('port', 'N/A')}")
            
            # 等待一下
            print("⏳ 等待 3 秒...")
            time.sleep(3)
            
            # 获取会话信息
            session_info = self.manager.api.get_session_info(session_id)
            if session_info:
                print(f"📊 会话信息获取成功")
            
            # 关闭会话
            if self.manager.close_session(session_id):
                print(f"✅ 会话关闭成功")
                return True
            else:
                print(f"❌ 会话关闭失败")
                return False
                
        except Exception as e:
            print(f"❌ 会话管理异常: {e}")
            return False
    
    def test_full_workflow(self) -> bool:
        """测试完整工作流程"""
        try:
            print("🔄 测试完整工作流程")
            
            # 1. 初始化
            if not self.manager.initialize():
                print("❌ 步骤1: 初始化失败")
                return False
            print("✅ 步骤1: 初始化成功")
            
            # 2. 创建配置文件
            profile_name = f"Workflow Test {int(time.time())}"
            profile = self.manager.profile_manager.create_default_profile(profile_name)
            if not profile:
                print("❌ 步骤2: 配置文件创建失败")
                return False
            print("✅ 步骤2: 配置文件创建成功")
            
            # 3. 启动会话
            session = self.manager.create_browser_session(profile_name)
            if not session:
                print("❌ 步骤3: 会话启动失败")
                return False
            print("✅ 步骤3: 会话启动成功")
            
            session_id = session['session_id']
            
            # 4. 验证会话状态
            time.sleep(2)
            session_info = self.manager.api.get_session_info(session_id)
            if not session_info:
                print("❌ 步骤4: 会话状态验证失败")
                return False
            print("✅ 步骤4: 会话状态验证成功")
            
            # 5. 清理资源
            if not self.manager.close_session(session_id):
                print("❌ 步骤5: 资源清理失败")
                return False
            print("✅ 步骤5: 资源清理成功")
            
            print("🎉 完整工作流程测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 完整工作流程异常: {e}")
            return False
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name:<30} {status}")
        
        print("-" * 60)
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有测试都通过了！Linken Sphere 集成正常工作。")
        else:
            print("⚠️ 部分测试失败，请检查 Linken Sphere 配置和连接。")


def main():
    """主函数"""
    print("Linken Sphere 集成测试工具")
    print("=" * 60)
    
    # 获取用户配置
    try:
        api_host = input("请输入 Linken Sphere API 地址 (默认: 127.0.0.1): ").strip() or "127.0.0.1"
        api_port_input = input("请输入 API 端口 (默认: 3001): ").strip()
        api_port = int(api_port_input) if api_port_input else 3001
        
        print(f"\n使用配置:")
        print(f"- API 地址: {api_host}")
        print(f"- API 端口: {api_port}")
        
        confirm = input("\n开始测试? (y/N): ").lower()
        if confirm != 'y':
            print("测试已取消")
            return
            
    except ValueError:
        print("❌ 端口号必须是数字")
        return
    except KeyboardInterrupt:
        print("\n测试已取消")
        return
    
    # 运行测试
    tester = LinkenSphereTest(api_host, api_port)
    results = tester.run_all_tests()
    
    # 退出代码
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
