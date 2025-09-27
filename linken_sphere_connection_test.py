#!/usr/bin/env python3
"""
Linken Sphere 连接测试和诊断工具
用于验证 API 连接、会话状态和调试端口的可用性
"""

import requests
import json
import time
import sys

class LinkenSphereConnectionTester:
    def __init__(self):
        self.api_url = "http://127.0.0.1:40080"  # 正确的 API 端口
        
    def test_api_connection(self):
        """测试 Linken Sphere API 连接"""
        print("🔍 测试 Linken Sphere API 连接...")
        try:
            response = requests.get(f"{self.api_url}/sessions", timeout=5)
            if response.status_code == 200:
                sessions = response.json()
                print(f"✅ API 连接成功，发现 {len(sessions)} 个会话")
                return True, sessions
            else:
                print(f"❌ API 响应错误: {response.status_code}")
                return False, None
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到 Linken Sphere API")
            print("   请确保 Linken Sphere 客户端正在运行")
            return False, None
        except Exception as e:
            print(f"❌ API 连接异常: {e}")
            return False, None
    
    def analyze_sessions(self, sessions):
        """分析会话状态"""
        print("\n📊 会话状态分析:")
        print("-" * 50)
        
        if not sessions:
            print("❌ 没有找到任何会话")
            return
            
        running_sessions = []
        stopped_sessions = []
        
        for i, session in enumerate(sessions, 1):
            name = session.get('name', 'Unknown')
            uuid = session.get('uuid', 'Unknown')
            status = session.get('status', 'Unknown')
            debug_port = session.get('debug_port', 'Not assigned')
            
            print(f"{i}. 会话: {name}")
            print(f"   UUID: {uuid}")
            print(f"   状态: {status}")
            print(f"   调试端口: {debug_port}")
            
            # 判断会话是否运行中
            if 'running' in status.lower() or 'automation' in status.lower():
                running_sessions.append(session)
                print("   🟢 运行中")
            else:
                stopped_sessions.append(session)
                print("   🔴 已停止")
            print()
        
        print(f"总结: 🟢 {len(running_sessions)} 个运行中, 🔴 {len(stopped_sessions)} 个已停止")
        return running_sessions, stopped_sessions
    
    def test_debug_ports(self, sessions):
        """测试调试端口连接"""
        print("\n🔍 测试调试端口连接:")
        print("-" * 50)
        
        available_ports = []
        
        for session in sessions:
            debug_port = session.get('debug_port')
            if debug_port:
                print(f"测试端口 {debug_port}...")
                if self.check_debug_port(debug_port):
                    available_ports.append(debug_port)
                    print(f"✅ 端口 {debug_port} 可用")
                else:
                    print(f"❌ 端口 {debug_port} 不可用")
            else:
                print(f"⚠️ 会话 {session.get('name')} 没有分配调试端口")
        
        return available_ports
    
    def check_debug_port(self, port):
        """检查单个调试端口"""
        try:
            response = requests.get(f"http://127.0.0.1:{port}/json", timeout=3)
            if response.status_code == 200:
                tabs = response.json()
                return len(tabs) > 0
        except:
            pass
        return False
    
    def test_session_creation(self):
        """测试会话创建流程"""
        print("\n🚀 测试会话创建流程:")
        print("-" * 50)
        
        try:
            # 创建快速会话
            print("1. 创建新会话...")
            create_response = requests.post(f"{self.api_url}/sessions/create_quick", timeout=15)
            
            if create_response.status_code != 200:
                print(f"❌ 创建会话失败: {create_response.status_code}")
                return False
                
            session_info = create_response.json()
            session_name = session_info.get('name')
            session_uuid = session_info.get('uuid')
            
            print(f"✅ 会话创建成功: {session_name}")
            print(f"   UUID: {session_uuid}")
            
            # 启动会话
            print("2. 启动会话...")
            start_payload = {
                "uuid": session_uuid,
                "headless": False
            }
            
            start_response = requests.post(
                f"{self.api_url}/sessions/start",
                json=start_payload,
                timeout=30
            )
            
            if start_response.status_code == 200:
                session_data = start_response.json()
                debug_port = session_data.get('debug_port')
                print(f"✅ 会话启动成功")
                print(f"   分配的调试端口: {debug_port}")
                
                # 等待一下让浏览器完全启动
                print("3. 等待浏览器启动...")
                time.sleep(5)
                
                # 测试调试端口
                if debug_port and self.check_debug_port(debug_port):
                    print(f"✅ 调试端口 {debug_port} 连接成功")
                    
                    # 停止会话
                    print("4. 停止测试会话...")
                    stop_payload = {"uuid": session_uuid}
                    stop_response = requests.post(
                        f"{self.api_url}/sessions/stop",
                        json=stop_payload,
                        timeout=15
                    )
                    
                    if stop_response.status_code == 200:
                        print("✅ 会话停止成功")
                        return True
                    else:
                        print(f"⚠️ 停止会话失败: {stop_response.status_code}")
                        return True  # 启动成功就算测试通过
                else:
                    print(f"❌ 调试端口 {debug_port} 连接失败")
                    return False
            else:
                print(f"❌ 启动会话失败: {start_response.status_code}")
                print(f"   响应: {start_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 测试会话创建异常: {e}")
            return False
    
    def run_full_test(self):
        """运行完整的连接测试"""
        print("🔗 Linken Sphere 连接诊断工具")
        print("=" * 60)
        
        # 1. 测试 API 连接
        api_ok, sessions = self.test_api_connection()
        if not api_ok:
            print("\n❌ API 连接失败，请检查:")
            print("   1. Linken Sphere 客户端是否正在运行")
            print("   2. API 端口是否为 40080")
            print("   3. 防火墙是否阻止了连接")
            return False
        
        # 2. 分析现有会话
        if sessions:
            running_sessions, stopped_sessions = self.analyze_sessions(sessions)
            
            # 3. 测试运行中会话的调试端口
            if running_sessions:
                available_ports = self.test_debug_ports(running_sessions)
                if available_ports:
                    print(f"\n✅ 发现 {len(available_ports)} 个可用的调试端口")
                else:
                    print("\n⚠️ 没有可用的调试端口")
        
        # 4. 测试会话创建流程
        creation_ok = self.test_session_creation()
        
        # 总结
        print("\n" + "=" * 60)
        print("📋 诊断总结:")
        print(f"   API 连接: {'✅ 正常' if api_ok else '❌ 失败'}")
        print(f"   会话创建: {'✅ 正常' if creation_ok else '❌ 失败'}")
        
        if api_ok and creation_ok:
            print("\n🎉 所有测试通过！Linken Sphere 连接正常")
            return True
        else:
            print("\n⚠️ 部分测试失败，请检查 Linken Sphere 配置")
            return False

def main():
    """主函数"""
    tester = LinkenSphereConnectionTester()
    success = tester.run_full_test()
    
    if not success:
        print("\n💡 故障排除建议:")
        print("   1. 确保 Linken Sphere 客户端正在运行且已授权")
        print("   2. 检查 API 端口配置 (应为 40080)")
        print("   3. 尝试重启 Linken Sphere 客户端")
        print("   4. 检查系统防火墙设置")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
