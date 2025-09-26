#!/usr/bin/env python3
"""
测试更新后的 Linken Sphere API
验证新的端点配置是否正常工作
"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    from linken_sphere_api import LinkenSphereManager, LinkenSphereAPI
except ImportError as e:
    print(f"❌ 无法导入 Linken Sphere API 模块: {e}")
    sys.exit(1)

def test_basic_connection():
    """测试基础连接"""
    print("🔍 测试基础连接...")
    
    try:
        api = LinkenSphereAPI()
        if api.check_connection():
            print("✅ 基础连接测试通过")
            return True
        else:
            print("❌ 基础连接测试失败")
            return False
    except Exception as e:
        print(f"❌ 连接测试异常: {e}")
        return False

def test_get_profiles():
    """测试获取配置文件"""
    print("\n📋 测试获取配置文件...")
    
    try:
        api = LinkenSphereAPI()
        profiles = api.get_profiles()
        
        if profiles:
            print(f"✅ 成功获取 {len(profiles)} 个配置文件:")
            for i, profile in enumerate(profiles, 1):
                print(f"   {i}. {profile.get('name', 'Unknown')} (ID: {profile.get('id', 'N/A')}, 状态: {profile.get('status', 'Unknown')})")
            return True
        else:
            print("⚠️ 未找到配置文件")
            return False
            
    except Exception as e:
        print(f"❌ 获取配置文件异常: {e}")
        return False

def test_manager_initialization():
    """测试管理器初始化"""
    print("\n🔧 测试管理器初始化...")
    
    try:
        manager = LinkenSphereManager()
        if manager.initialize():
            print("✅ 管理器初始化成功")
            return True
        else:
            print("❌ 管理器初始化失败")
            return False
    except Exception as e:
        print(f"❌ 管理器初始化异常: {e}")
        return False

def test_session_operations():
    """测试会话操作（如果可能）"""
    print("\n🚀 测试会话操作...")
    
    try:
        manager = LinkenSphereManager()
        
        if not manager.initialize():
            print("❌ 管理器初始化失败，跳过会话测试")
            return False
        
        # 获取现有配置文件
        profiles = manager.api.get_profiles()
        if not profiles:
            print("⚠️ 没有可用的配置文件，无法测试会话操作")
            return False
        
        # 选择第一个配置文件进行测试
        test_profile = profiles[0]
        profile_name = test_profile.get('name')
        
        print(f"📝 尝试使用配置文件: {profile_name}")
        
        # 注意：这里可能会失败，因为可能需要不同的API端点
        # 但我们可以尝试
        try:
            session = manager.create_browser_session(profile_name)
            if session:
                print("✅ 会话创建成功")
                print(f"   会话响应: {session}")

                # 检查响应格式
                if 'uuid' in session and 'debug_port' in session:
                    print(f"   配置文件UUID: {session.get('uuid')}")
                    print(f"   调试端口: {session.get('debug_port')}")
                    print("   🎯 会话启动成功！")
                    return True
                elif 'session_id' in session:
                    # 如果有session_id，尝试关闭会话
                    session_id = session['session_id']
                    print(f"   会话ID: {session_id}")
                    if manager.close_session(session_id):
                        print("✅ 会话关闭成功")
                    else:
                        print("⚠️ 会话关闭失败")
                    return True
                else:
                    print("⚠️ 响应格式未知")
                    return True
            else:
                print("❌ 会话创建失败")
                return False
                
        except Exception as e:
            print(f"⚠️ 会话操作可能不支持: {e}")
            print("💡 这可能是正常的，因为会话管理可能需要不同的API端点")
            return False
            
    except Exception as e:
        print(f"❌ 会话操作测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🧪 Linken Sphere API 更新验证测试")
    print("=" * 60)
    print("验证基于实际端点发现的API更新是否正常工作")
    print("=" * 60)
    
    tests = [
        ("基础连接测试", test_basic_connection),
        ("配置文件获取测试", test_get_profiles),
        ("管理器初始化测试", test_manager_initialization),
        ("会话操作测试", test_session_operations)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 发生异常: {e}")
            results[test_name] = False
    
    # 总结结果
    print(f"\n{'='*60}")
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试都通过了！")
        print("✅ Linken Sphere API 更新成功，可以正常使用")
        print("\n💡 下一步:")
        print("1. 运行 python linken_sphere_browser.py 测试完整功能")
        print("2. 或使用 python start_browser.py 选择 Linken Sphere 模式")
    elif passed > 0:
        print(f"\n⚠️ 部分测试通过 ({passed}/{total})")
        print("✅ 基础功能可用，但某些高级功能可能需要进一步配置")
        print("\n💡 建议:")
        print("1. 检查失败的测试项目")
        print("2. 可以尝试使用手动集成模式")
        print("3. 或联系 Linken Sphere 技术支持")
    else:
        print("\n❌ 所有测试都失败了")
        print("💡 建议:")
        print("1. 检查 Linken Sphere 是否正在运行")
        print("2. 验证 API 端口配置")
        print("3. 尝试使用手动集成模式: python linken_sphere_manual.py")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
