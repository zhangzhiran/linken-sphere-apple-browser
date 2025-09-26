#!/usr/bin/env python3
"""
Linken Sphere 诊断工具
自动检测和诊断 Linken Sphere 连接问题
"""

import sys
import socket
import requests
import time
import json
from typing import Dict, List, Tuple

def print_header():
    """打印诊断工具标题"""
    print("🔍 Linken Sphere 诊断工具")
    print("=" * 50)
    print("自动检测 Linken Sphere 连接和配置问题")
    print("=" * 50)

def check_port_open(host: str, port: int, timeout: int = 5) -> bool:
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_http_response(url: str, timeout: int = 10) -> Tuple[bool, str, int]:
    """检查HTTP响应"""
    try:
        response = requests.get(url, timeout=timeout)
        return True, "成功", response.status_code
    except requests.exceptions.ConnectionError:
        return False, "连接被拒绝", 0
    except requests.exceptions.Timeout:
        return False, "连接超时", 0
    except requests.exceptions.RequestException as e:
        return False, f"请求异常: {e}", 0
    except Exception as e:
        return False, f"未知错误: {e}", 0

def check_linken_sphere_api(host: str = "127.0.0.1", port: int = 3001) -> Dict:
    """检查 Linken Sphere API"""
    results = {
        "port_open": False,
        "http_accessible": False,
        "api_responsive": False,
        "status_code": 0,
        "error_message": "",
        "api_endpoints": {}
    }
    
    print(f"🔍 检查 Linken Sphere API ({host}:{port})")
    print("-" * 40)
    
    # 1. 检查端口是否开放
    print(f"1. 检查端口 {port} 是否开放...")
    results["port_open"] = check_port_open(host, port)
    if results["port_open"]:
        print(f"   ✅ 端口 {port} 已开放")
    else:
        print(f"   ❌ 端口 {port} 未开放或无法访问")
        results["error_message"] = f"端口 {port} 未开放"
        return results
    
    # 2. 检查HTTP访问
    base_url = f"http://{host}:{port}"
    print(f"2. 检查HTTP访问 ({base_url})...")
    
    http_ok, http_msg, status_code = check_http_response(base_url)
    results["http_accessible"] = http_ok
    results["status_code"] = status_code
    
    if http_ok:
        print(f"   ✅ HTTP访问正常 (状态码: {status_code})")
    else:
        print(f"   ❌ HTTP访问失败: {http_msg}")
        results["error_message"] = http_msg
        return results
    
    # 3. 检查API端点
    print("3. 检查API端点...")
    api_endpoints = [
        "/api/v1/status",
        "/api/v1/profiles",
        "/api/v1/sessions"
    ]
    
    for endpoint in api_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"   检查 {endpoint}...")
        
        ok, msg, code = check_http_response(url)
        results["api_endpoints"][endpoint] = {
            "accessible": ok,
            "status_code": code,
            "message": msg
        }
        
        if ok:
            print(f"     ✅ {endpoint} 可访问 (状态码: {code})")
            if endpoint == "/api/v1/status":
                results["api_responsive"] = True
        else:
            print(f"     ❌ {endpoint} 不可访问: {msg}")
    
    return results

def check_python_dependencies() -> Dict[str, bool]:
    """检查Python依赖项"""
    print("\n🐍 检查Python依赖项")
    print("-" * 40)
    
    dependencies = {
        "requests": False,
        "selenium": False,
        "playwright": False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
            print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"❌ {dep} 未安装")
    
    return dependencies

def check_linken_sphere_process() -> bool:
    """检查 Linken Sphere 进程是否运行"""
    print("\n🔄 检查 Linken Sphere 进程")
    print("-" * 40)
    
    try:
        import psutil
        
        linken_sphere_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'] and 'linken' in proc.info['name'].lower():
                    linken_sphere_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if linken_sphere_processes:
            print(f"✅ 找到 {len(linken_sphere_processes)} 个相关进程:")
            for proc in linken_sphere_processes:
                print(f"   - PID: {proc['pid']}, 名称: {proc['name']}")
            return True
        else:
            print("❌ 未找到 Linken Sphere 相关进程")
            return False
            
    except ImportError:
        print("⚠️ psutil 未安装，无法检查进程")
        print("可以运行: pip install psutil")
        return False

def provide_solutions(api_results: Dict, deps: Dict[str, bool]):
    """提供解决方案"""
    print("\n💡 解决方案建议")
    print("=" * 50)
    
    if not api_results["port_open"]:
        print("🔧 端口问题解决方案:")
        print("1. 确保 Linken Sphere 应用程序正在运行")
        print("2. 检查 Linken Sphere 设置中的API配置")
        print("3. 确认API端口设置为 3001")
        print("4. 检查防火墙是否阻止了端口访问")
        print("5. 尝试重启 Linken Sphere 应用程序")
        
    elif not api_results["http_accessible"]:
        print("🔧 HTTP访问问题解决方案:")
        print("1. 检查 Linken Sphere API 服务是否已启用")
        print("2. 确认API地址和端口配置正确")
        print("3. 尝试在浏览器中访问: http://127.0.0.1:3001")
        print("4. 检查是否有其他程序占用了3001端口")
        
    elif not api_results["api_responsive"]:
        print("🔧 API响应问题解决方案:")
        print("1. 检查 Linken Sphere 版本是否支持API")
        print("2. 确认API功能已在设置中启用")
        print("3. 查看 Linken Sphere 应用程序的错误日志")
        print("4. 尝试重新安装或更新 Linken Sphere")
    
    # 检查依赖项问题
    missing_deps = [dep for dep, installed in deps.items() if not installed]
    if missing_deps:
        print(f"\n🔧 缺少依赖项解决方案:")
        print(f"运行以下命令安装缺少的依赖项:")
        print(f"pip install {' '.join(missing_deps)}")
    
    print("\n📚 其他建议:")
    print("1. 查看 LINKEN_SPHERE_GUIDE.md 获取详细配置指南")
    print("2. 确保使用的是最新版本的 Linken Sphere")
    print("3. 如果问题持续，可以使用标准浏览器模式")
    print("4. 联系 Linken Sphere 技术支持获取帮助")

def main():
    """主函数"""
    print_header()
    
    # 检查Python依赖项
    deps = check_python_dependencies()
    
    # 检查进程
    process_running = check_linken_sphere_process()
    
    # 检查API
    api_results = check_linken_sphere_api()
    
    # 总结结果
    print("\n📊 诊断结果总结")
    print("=" * 50)
    
    all_good = True
    
    if not all(deps.values()):
        print("❌ Python依赖项不完整")
        all_good = False
    else:
        print("✅ Python依赖项完整")
    
    if not process_running:
        print("⚠️ 未检测到 Linken Sphere 进程")
        all_good = False
    else:
        print("✅ Linken Sphere 进程运行中")
    
    if not api_results["api_responsive"]:
        print("❌ Linken Sphere API 不可用")
        all_good = False
    else:
        print("✅ Linken Sphere API 正常")
    
    if all_good:
        print("\n🎉 所有检查都通过！Linken Sphere 应该可以正常工作。")
        print("您可以运行: python linken_sphere_browser.py")
    else:
        print("\n⚠️ 发现问题，请查看下面的解决方案:")
        provide_solutions(api_results, deps)
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
