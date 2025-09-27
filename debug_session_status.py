#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试会话状态问题
"""

import requests
import json

def check_session_status():
    """检查会话状态"""
    try:
        print("🔍 检查 Linken Sphere 会话状态")
        print("=" * 60)
        
        response = requests.get("http://127.0.0.1:36555/sessions", timeout=5)
        response.raise_for_status()
        sessions = response.json()
        
        print(f"📊 总会话数: {len(sessions)}")
        print()
        
        # 收集所有状态值
        all_statuses = set()
        
        for i, session in enumerate(sessions, 1):
            name = session.get('name', 'Unknown')
            uuid = session.get('uuid', 'Unknown')
            status = session.get('status', 'Unknown')
            proxy = session.get('proxy', {})
            protocol = proxy.get('protocol', 'Unknown')
            
            all_statuses.add(status)
            
            print(f"{i}. 📋 {name}")
            print(f"   UUID: {uuid}")
            print(f"   状态: {status}")
            print(f"   代理: {protocol}")
            print()
        
        print("=" * 60)
        print("📊 发现的所有状态值:")
        for status in sorted(all_statuses):
            count = len([s for s in sessions if s.get('status') == status])
            print(f"   • {status}: {count} 个会话")
        
        print()
        print("🔍 当前代码的判断逻辑:")
        print("   • 只认为 status == 'running' 是运行中")
        print("   • 其他状态都被认为是已停止")
        
        print()
        print("💡 建议的修复方案:")
        print("   • 将 'automationRunning' 也视为运行中")
        print("   • 可能还需要包含其他运行状态")
        
        # 分析哪些状态应该被认为是"运行中"
        print()
        print("🎯 状态分析:")
        running_like_statuses = []
        stopped_like_statuses = []
        
        for status in all_statuses:
            if 'running' in status.lower() or 'automation' in status.lower():
                running_like_statuses.append(status)
            elif 'stopped' in status.lower() or 'stop' in status.lower():
                stopped_like_statuses.append(status)
            else:
                print(f"   ❓ 未知状态: {status}")
        
        if running_like_statuses:
            print(f"   🟢 应该视为运行中: {running_like_statuses}")
        
        if stopped_like_statuses:
            print(f"   🔴 应该视为已停止: {stopped_like_statuses}")
        
        return sessions, all_statuses
        
    except Exception as e:
        print(f"❌ 检查会话状态失败: {e}")
        return [], set()

def test_current_logic(sessions):
    """测试当前逻辑"""
    print()
    print("🧪 测试当前逻辑:")
    print("=" * 60)
    
    # 当前逻辑
    current_running = [s for s in sessions if s.get('status') == 'running']
    current_stopped = [s for s in sessions if s.get('status') == 'stopped']
    
    print(f"当前逻辑认为运行中: {len(current_running)} 个")
    print(f"当前逻辑认为已停止: {len(current_stopped)} 个")
    print(f"未分类的会话: {len(sessions) - len(current_running) - len(current_stopped)} 个")
    
    # 显示未分类的会话
    unclassified = [s for s in sessions if s.get('status') not in ['running', 'stopped']]
    if unclassified:
        print()
        print("❓ 未分类的会话:")
        for session in unclassified:
            name = session.get('name', 'Unknown')
            status = session.get('status', 'Unknown')
            print(f"   • {name}: {status}")

def suggest_fix(all_statuses):
    """建议修复方案"""
    print()
    print("🔧 建议的修复代码:")
    print("=" * 60)
    
    # 分析状态并生成建议
    running_statuses = []
    for status in all_statuses:
        if any(keyword in status.lower() for keyword in ['running', 'automation', 'active']):
            running_statuses.append(status)
    
    if running_statuses:
        print("# 修改判断逻辑，将以下状态都视为运行中:")
        print("RUNNING_STATUSES = [")
        for status in sorted(running_statuses):
            print(f"    '{status}',")
        print("]")
        print()
        print("# 使用新的判断逻辑:")
        print("running_sessions = [s for s in sessions if s.get('status') in RUNNING_STATUSES]")
        print()
        print("# 或者使用更简单的方式:")
        print("def is_session_running(session):")
        print("    status = session.get('status', '').lower()")
        print("    return 'running' in status or 'automation' in status")
        print()
        print("running_sessions = [s for s in sessions if is_session_running(s)]")

def main():
    """主函数"""
    print("🔍 Linken Sphere 会话状态调试工具")
    print("=" * 80)
    
    sessions, all_statuses = check_session_status()
    
    if sessions:
        test_current_logic(sessions)
        suggest_fix(all_statuses)
        
        print()
        print("=" * 80)
        print("📝 总结:")
        print("✅ 成功获取会话信息")
        print("✅ 识别了状态判断问题")
        print("✅ 提供了修复建议")
        
        print()
        print("🚀 下一步:")
        print("1. 修改代码中的状态判断逻辑")
        print("2. 将 'automationRunning' 等状态视为运行中")
        print("3. 重新构建程序")
        print("4. 测试修复效果")
    else:
        print()
        print("❌ 无法获取会话信息，请检查:")
        print("1. Linken Sphere 是否正在运行")
        print("2. API 端口 36555 是否可访问")
        print("3. 网络连接是否正常")

if __name__ == "__main__":
    main()
