#!/usr/bin/env python3
"""
诊断 Linken Sphere 会话问题
"""

import requests
import json

def get_session_details():
    """获取会话详细信息"""
    try:
        response = requests.get("http://127.0.0.1:40080/sessions", timeout=5)
        if response.status_code == 200:
            sessions = response.json()
            print(f"发现 {len(sessions)} 个会话:")
            print("=" * 80)

            for i, session in enumerate(sessions, 1):
                print(f"{i}. 会话详细信息:")
                print(json.dumps(session, indent=2, ensure_ascii=False))
                print("-" * 80)

            return sessions
        else:
            print(f"获取会话失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取会话异常: {e}")
        return None

def test_different_payloads(session_uuid):
    """测试不同的载荷格式"""
    print(f"\n🧪 测试不同载荷格式 (会话: {session_uuid[:8]}...)")
    print("=" * 80)

    # 测试1: 最简单的载荷
    print("测试1: 最简单的载荷")
    test_payload_1 = f'{{\n    "uuid": "{session_uuid}"\n}}'
    test_request(test_payload_1, "最简单载荷")

    # 测试2: 只有 headless
    print("\n测试2: 只有 headless")
    test_payload_2 = f'{{\n    "uuid": "{session_uuid}",\n    "headless": false\n}}'
    test_request(test_payload_2, "包含 headless")

    # 测试3: 官方示例格式
    print("\n测试3: 官方示例格式")
    test_payload_3 = f'{{\n    "uuid": "{session_uuid}",\n    "headless": false,\n    "debug_port": 12345\n}}'
    test_request(test_payload_3, "官方示例格式")

    # 测试4: 不指定调试端口
    print("\n测试4: 不指定调试端口")
    test_payload_4 = f'{{\n    "uuid": "{session_uuid}",\n    "headless": false,\n    "automation": true\n}}'
    test_request(test_payload_4, "包含 automation 标志")

def test_request(payload, description):
    """测试单个请求"""
    try:
        url = "http://127.0.0.1:40080/sessions/start"
        headers = {}

        print(f"  📋 {description}:")
        print(f"     载荷: {payload}")

        response = requests.request("POST", url, headers=headers, data=payload)

        print(f"     状态码: {response.status_code}")
        print(f"     响应: {response.text}")

        if response.status_code == 200:
            print("     ✅ 成功")
            return True
        elif response.status_code == 409:
            print("     ⚠️ 会话已运行")
            return True
        else:
            print("     ❌ 失败")
            return False

    except Exception as e:
        print(f"     ❌ 异常: {e}")
        return False

def check_api_endpoints():
    """检查其他 API 端点"""
    print("\n🔍 检查其他 API 端点:")
    print("=" * 80)

    endpoints = [
        "/sessions",
        "/sessions/profiles",
        "/sessions/running",
    ]

    for endpoint in endpoints:
        try:
            url = f"http://127.0.0.1:40080{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  数据: {len(data) if isinstance(data, list) else 'object'}")
                except:
                    print(f"  响应: {response.text[:100]}...")
        except Exception as e:
            print(f"{endpoint}: 异常 - {e}")

def create_quick_and_start():
    """
    按官方文档执行：create_quick -> start（不指定 debug_port，自动分配）-> 验证调试端口
    """
    try:
        print("\n🚀 按官方流程创建并启动会话:")
        # 1) create_quick
        cq_url = "http://127.0.0.1:40080/sessions/create_quick"
        cq_resp = requests.post(cq_url, timeout=15)
        print(f"create_quick 状态: {cq_resp.status_code}")
        print(f"create_quick 响应: {cq_resp.text}")
        if cq_resp.status_code != 200:
            return False
        info = cq_resp.json()
        # create_quick 可能返回对象或包含单个对象的列表
        if isinstance(info, list) and info:
            info = info[0]
        uuid = info.get("uuid")
        name = info.get("name")
        print(f"✅ 已创建会话: {name} ({uuid})")

        # 2) start（不传 debug_port）
        start_url = "http://127.0.0.1:40080/sessions/start"
        start_payload = json.dumps({"uuid": uuid, "headless": False})
        print("发送 start 载荷:")
        print(start_payload)
        start_resp = requests.request("POST", start_url, headers={}, data=start_payload)
        print(f"start 状态: {start_resp.status_code}")
        print(f"start 响应: {start_resp.text}")
        if start_resp.status_code != 200:
            return False
        data = start_resp.json()
        debug_port = data.get("debug_port")
        print(f"✅ 会话启动成功，调试端口: {debug_port}")

        # 3) 验证调试端口
        return verify_debug_port(debug_port)
    except Exception as e:
        print(f"❌ 按官方流程失败: {e}")
        return False

def verify_debug_port(port):
    """验证调试端口是否可用"""
    try:
        print(f"\n🔎 验证调试端口 {port} ...")
        v1 = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=5)
        print(f"/json/version -> {v1.status_code}")
        if v1.status_code == 200:
            print(v1.text[:200])
        v2 = requests.get(f"http://127.0.0.1:{port}/json", timeout=5)
        print(f"/json -> {v2.status_code}")
        if v2.status_code == 200:
            try:
                tabs = v2.json()
                print(f"发现 {len(tabs)} 个页面")
            except Exception:
                print(v2.text[:200])
        return v1.status_code == 200 or v2.status_code == 200
    except Exception as e:
        print(f"❌ 端口验证异常: {e}")
        return False

def main():
    """主函数"""
    print("🔍 Linken Sphere 会话诊断")
    print("=" * 80)

    # 1. 检查 API 端点
    check_api_endpoints()

    # 2. 获取会话详细信息
    sessions = get_session_details()

    if sessions:
        # 3. 测试第一个会话的不同载荷格式（对比格式是否影响）
        first_session = sessions[0]
        session_uuid = first_session.get('uuid')
        test_different_payloads(session_uuid)

    # 4. 官方流程：create_quick -> start（不指定 debug_port）-> 验证端口
    ok = create_quick_and_start()
    print(f"\n� 官方流程结果: {'成功' if ok else '失败'}")

    print("\n�💡 诊断建议:")
    print("1. 确保 Linken Sphere 客户端已完全启动并授权")
    print("2. 如果仍返回 Connection validation failed：请在 GUI 中打开该会话设置，保存一次（确保网络/代理参数有效），再重试")
    print("3. 防火墙/安全软件不要拦截 40080 以及分配的调试端口")

if __name__ == "__main__":
    main()
