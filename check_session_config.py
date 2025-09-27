#!/usr/bin/env python3
"""
检查 Linken Sphere 会话配置
"""

import requests
import json

def check_sessions():
    """检查会话配置"""
    try:
        url = "http://127.0.0.1:40080/sessions"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"发现 {len(sessions)} 个会话:")
            print("=" * 60)
            
            for i, session in enumerate(sessions, 1):
                name = session.get('name', 'Unknown')
                uuid = session.get('uuid', 'Unknown')
                status = session.get('status', 'Unknown')
                
                print(f"{i}. 会话: {name}")
                print(f"   UUID: {uuid}")
                print(f"   状态: {status}")
                
                # 检查代理配置
                proxy = session.get('proxy', {})
                if proxy:
                    print(f"   代理配置:")
                    print(f"     协议: {proxy.get('protocol', 'Unknown')}")
                    print(f"     主机: {proxy.get('host', 'Unknown')}")
                    print(f"     端口: {proxy.get('port', 'Unknown')}")
                    print(f"     用户名: {proxy.get('login', 'None')}")
                else:
                    print(f"   ⚠️ 没有代理配置")
                
                # 检查其他配置
                print(f"   完整配置:")
                print(json.dumps(session, indent=2, ensure_ascii=False))
                print("-" * 60)
                
        else:
            print(f"获取会话失败: {response.status_code}")
            
    except Exception as e:
        print(f"检查会话异常: {e}")

def test_simple_start(session_uuid):
    """测试简单启动（不设置连接）"""
    print(f"\n测试简单启动会话: {session_uuid[:8]}...")
    
    try:
        url = "http://127.0.0.1:40080/sessions/start"
        
        # 最简单的启动载荷
        payload = f'{{\n    "uuid": "{session_uuid}",\n    "headless": false\n}}'
        headers = {'Content-Type': 'application/json'}
        
        print("请求载荷:", payload)
        
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"启动异常: {e}")
        return False

if __name__ == "__main__":
    print("🔍 检查 Linken Sphere 会话配置")
    print("=" * 60)
    
    check_sessions()
    
    # 尝试启动第一个会话
    try:
        response = requests.get("http://127.0.0.1:40080/sessions", timeout=5)
        if response.status_code == 200:
            sessions = response.json()
            if sessions:
                first_session = sessions[0]
                session_uuid = first_session.get('uuid')
                test_simple_start(session_uuid)
    except:
        pass
