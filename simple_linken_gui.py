#!/usr/bin/env python3
"""
Linken Sphere Apple Browser - 简化GUI界面
紧凑、简洁、功能完整的用户界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import asyncio
import json
import os
import sys
import platform
from datetime import datetime

# 尝试导入主程序
try:
    from linken_sphere_playwright_browser import LinkenSphereAppleBrowser
except ImportError:
    LinkenSphereAppleBrowser = None

class SimpleLinkenGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # 配置
        self.config = {
            'browse_duration': 60,
            'major_cycles': 3,
            'minor_cycles_per_major': 8,
            'max_retries': 3,
            'linken_api_port': 36555,
            'debug_port': 12345,
            'max_threads': 2
        }
        
        # 状态
        self.browser_threads = {}
        self.thread_counter = 0
        self.is_running = False
        self.available_profiles = []  # 可用的配置文件列表
        self.used_profiles = set()    # 已使用的配置文件UUID
        
        self.create_widgets()
        self.load_config()
        self.refresh_profiles()  # 获取可用的配置文件
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("🔗 Linken Sphere Apple Browser")
        self.root.geometry("700x500")
        self.root.configure(bg='#2c2c2c')
        self.root.resizable(True, True)
        self.root.minsize(600, 400)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 设置应用图标
        self.set_application_icon()

    def set_application_icon(self):
        """设置应用程序图标 - 跨平台支持"""
        try:
            # 获取当前脚本目录
            if getattr(sys, 'frozen', False):
                # 如果是打包的可执行文件
                app_dir = os.path.dirname(sys.executable)
            else:
                # 如果是Python脚本
                app_dir = os.path.dirname(os.path.abspath(__file__))

            # 根据平台选择图标文件
            if platform.system() == "Windows":
                icon_path = os.path.join(app_dir, "app_icon.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    print(f"✅ 设置Windows图标: {icon_path}")
                else:
                    print(f"⚠️ Windows图标文件不存在: {icon_path}")

            elif platform.system() == "Darwin":  # macOS
                # macOS使用PNG图标
                icon_path = os.path.join(app_dir, "app_icon.png")
                if os.path.exists(icon_path):
                    # 在macOS上，tkinter可以使用PNG作为图标
                    try:
                        from PIL import Image, ImageTk
                        img = Image.open(icon_path)
                        img = img.resize((32, 32), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.root.iconphoto(True, photo)
                        print(f"✅ 设置macOS图标: {icon_path}")
                    except ImportError:
                        # 如果没有PIL，使用默认方法
                        self.root.iconbitmap(icon_path)
                        print(f"✅ 设置macOS图标(默认): {icon_path}")
                else:
                    print(f"⚠️ macOS图标文件不存在: {icon_path}")

            else:  # Linux和其他系统
                icon_path = os.path.join(app_dir, "app_icon.png")
                if os.path.exists(icon_path):
                    try:
                        from PIL import Image, ImageTk
                        img = Image.open(icon_path)
                        img = img.resize((32, 32), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.root.iconphoto(True, photo)
                        print(f"✅ 设置Linux图标: {icon_path}")
                    except ImportError:
                        print(f"⚠️ PIL不可用，无法设置Linux图标")
                else:
                    print(f"⚠️ Linux图标文件不存在: {icon_path}")

        except Exception as e:
            print(f"⚠️ 设置图标失败: {e}")

    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = tk.Frame(self.root, bg='#2c2c2c')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = tk.Label(main_frame, text="🔗 Linken Sphere Apple Browser", 
                              bg='#2c2c2c', fg='white', font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 配置区域
        self.create_config_section(main_frame)
        
        # 控制区域
        self.create_control_section(main_frame)
        
        # 状态区域
        self.create_status_section(main_frame)
        
        # 日志区域
        self.create_log_section(main_frame)
    
    def create_config_section(self, parent):
        """创建配置区域"""
        config_frame = tk.LabelFrame(parent, text="⚙️ 配置", bg='#2c2c2c', fg='white', font=('Arial', 10, 'bold'))
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 配置变量
        self.browse_duration_var = tk.StringVar(value=str(self.config['browse_duration']))
        self.major_cycles_var = tk.StringVar(value=str(self.config['major_cycles']))
        self.minor_cycles_var = tk.StringVar(value=str(self.config['minor_cycles_per_major']))
        self.max_threads_var = tk.StringVar(value=str(self.config['max_threads']))
        
        # 第一行：基本配置
        row1 = tk.Frame(config_frame, bg='#2c2c2c')
        row1.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(row1, text="浏览时长(秒):", bg='#2c2c2c', fg='white').pack(side=tk.LEFT)
        tk.Entry(row1, textvariable=self.browse_duration_var, width=8, bg='#404040', fg='white').pack(side=tk.LEFT, padx=(5, 15))
        
        tk.Label(row1, text="大循环:", bg='#2c2c2c', fg='white').pack(side=tk.LEFT)
        tk.Entry(row1, textvariable=self.major_cycles_var, width=5, bg='#404040', fg='white').pack(side=tk.LEFT, padx=(5, 15))
        
        tk.Label(row1, text="小循环:", bg='#2c2c2c', fg='white').pack(side=tk.LEFT)
        tk.Entry(row1, textvariable=self.minor_cycles_var, width=5, bg='#404040', fg='white').pack(side=tk.LEFT, padx=(5, 15))
        
        tk.Label(row1, text="线程数:", bg='#2c2c2c', fg='white').pack(side=tk.LEFT)
        tk.Entry(row1, textvariable=self.max_threads_var, width=5, bg='#404040', fg='white').pack(side=tk.LEFT, padx=5)
        
        # 配置按钮
        button_row = tk.Frame(config_frame, bg='#2c2c2c')
        button_row.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(button_row, text="💾 保存", command=self.save_config, 
                 bg='#0d7377', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(button_row, text="📁 导入", command=self.import_config, 
                 bg='#0d7377', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(button_row, text="📤 导出", command=self.export_config, 
                 bg='#0d7377', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
    
    def create_control_section(self, parent):
        """创建控制区域"""
        control_frame = tk.LabelFrame(parent, text="🎮 控制", bg='#2c2c2c', fg='white', font=('Arial', 10, 'bold'))
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = tk.Frame(control_frame, bg='#2c2c2c')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 主要控制按钮
        self.start_button = tk.Button(button_frame, text="🚀 开始", command=self.start_automation,
                                     bg='#28a745', fg='white', font=('Arial', 10, 'bold'), width=8)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="⏹️ 停止", command=self.stop_all_automation,
                                    bg='#dc3545', fg='white', font=('Arial', 10, 'bold'), width=8)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.new_thread_button = tk.Button(button_frame, text="➕ 新线程", command=self.create_new_thread,
                                          bg='#17a2b8', fg='white', font=('Arial', 10, 'bold'), width=8)
        self.new_thread_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🗑️ 清理", command=self.cleanup_finished_threads,
                 bg='#6c757d', fg='white', font=('Arial', 10, 'bold'), width=8).pack(side=tk.LEFT, padx=5)
    
    def create_status_section(self, parent):
        """创建状态区域"""
        status_frame = tk.LabelFrame(parent, text="📊 状态", bg='#2c2c2c', fg='white', font=('Arial', 10, 'bold'))
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_content = tk.Frame(status_frame, bg='#2c2c2c')
        status_content.pack(fill=tk.X, padx=10, pady=5)
        
        # 状态标签
        self.status_label = tk.Label(status_content, text="状态: 就绪", bg='#2c2c2c', fg='#28a745', font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT)
        
        self.threads_label = tk.Label(status_content, text="线程: 0/2", bg='#2c2c2c', fg='#17a2b8', font=('Arial', 10))
        self.threads_label.pack(side=tk.RIGHT)
        
        # 线程列表框架
        thread_list_frame = tk.Frame(status_frame, bg='#2c2c2c')
        thread_list_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        # 线程列表
        self.thread_listbox = tk.Listbox(thread_list_frame, height=3, bg='#404040', fg='white',
                                        selectbackground='#0d7377', font=('Consolas', 9))
        self.thread_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 线程控制按钮
        thread_control_frame = tk.Frame(thread_list_frame, bg='#2c2c2c')
        thread_control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        tk.Button(thread_control_frame, text="⏸️", command=self.pause_selected_thread,
                 bg='#ffc107', fg='black', font=('Arial', 8), width=3).pack(pady=1)
        tk.Button(thread_control_frame, text="▶️", command=self.resume_selected_thread,
                 bg='#28a745', fg='white', font=('Arial', 8), width=3).pack(pady=1)
        tk.Button(thread_control_frame, text="⏹️", command=self.stop_selected_thread,
                 bg='#dc3545', fg='white', font=('Arial', 8), width=3).pack(pady=1)
    
    def create_log_section(self, parent):
        """创建日志区域"""
        log_frame = tk.LabelFrame(parent, text="📝 日志", bg='#2c2c2c', fg='white', font=('Arial', 10, 'bold'))
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志控制
        log_control = tk.Frame(log_frame, bg='#2c2c2c')
        log_control.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(log_control, text="🗑️ 清空", command=self.clear_logs, 
                 bg='#6c757d', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(log_control, text="💾 保存", command=self.save_logs, 
                 bg='#6c757d', fg='white', font=('Arial', 8)).pack(side=tk.LEFT, padx=2)
        
        # 日志文本
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, bg='#1e1e1e', fg='#00ff00',
                                                 font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(2, 5))
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists("linken_sphere_config.json"):
                with open("linken_sphere_config.json", 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)

                # 更新GUI
                self.browse_duration_var.set(str(self.config['browse_duration']))
                self.major_cycles_var.set(str(self.config['major_cycles']))
                self.minor_cycles_var.set(str(self.config['minor_cycles_per_major']))
                self.max_threads_var.set(str(self.config['max_threads']))

                self.log_message("✅ 配置已加载")
        except Exception as e:
            self.log_message(f"⚠️ 加载配置失败: {e}")

    def refresh_profiles(self):
        """刷新可用的配置文件列表"""
        try:
            import requests
            response = requests.get("http://127.0.0.1:36555/sessions", timeout=5)
            if response.status_code == 200:
                self.available_profiles = response.json()
                self.log_message(f"🔍 发现 {len(self.available_profiles)} 个配置文件")

                # 显示配置文件信息
                for profile in self.available_profiles:
                    name = profile.get('name', 'Unknown')
                    uuid = profile.get('uuid', 'Unknown')
                    self.log_message(f"  📋 {name} ({uuid[:8]}...)")

            else:
                self.log_message("⚠️ 无法获取配置文件列表")
                self.available_profiles = []
        except Exception as e:
            self.log_message(f"⚠️ 获取配置文件失败: {e}")
            self.available_profiles = []

    def get_next_available_profile(self):
        """获取下一个可用的配置文件"""
        if not self.available_profiles:
            self.refresh_profiles()

        # 查找未使用的配置文件
        for profile in self.available_profiles:
            uuid = profile.get('uuid')
            if uuid and uuid not in self.used_profiles:
                self.used_profiles.add(uuid)
                return profile

        # 如果所有配置文件都在使用，返回None
        return None
    
    def save_config(self):
        """保存配置"""
        try:
            # 从GUI更新配置
            self.config['browse_duration'] = int(self.browse_duration_var.get())
            self.config['major_cycles'] = int(self.major_cycles_var.get())
            self.config['minor_cycles_per_major'] = int(self.minor_cycles_var.get())
            self.config['max_threads'] = int(self.max_threads_var.get())
            
            with open("linken_sphere_config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.log_message("✅ 配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def import_config(self):
        """导入配置"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_config = json.load(f)
                
                self.config.update(imported_config)
                
                # 更新GUI
                self.browse_duration_var.set(str(self.config['browse_duration']))
                self.major_cycles_var.set(str(self.config['major_cycles']))
                self.minor_cycles_var.set(str(self.config['minor_cycles_per_major']))
                self.max_threads_var.set(str(self.config['max_threads']))
                
                self.log_message(f"📁 配置已导入: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"导入配置失败: {e}")
    
    def export_config(self):
        """导出配置"""
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # 更新配置
                self.config['browse_duration'] = int(self.browse_duration_var.get())
                self.config['major_cycles'] = int(self.major_cycles_var.get())
                self.config['minor_cycles_per_major'] = int(self.minor_cycles_var.get())
                self.config['max_threads'] = int(self.max_threads_var.get())
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                
                self.log_message(f"📤 配置已导出: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"导出配置失败: {e}")
    
    def start_automation(self):
        """开始自动化"""
        if LinkenSphereAppleBrowser is None:
            messagebox.showerror("错误", "无法导入 LinkenSphereAppleBrowser 模块")
            return
        
        try:
            self.save_config()  # 保存当前配置
            self.create_new_thread()
            self.log_message("🚀 自动化已开始")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {e}")
    
    def stop_all_automation(self):
        """停止所有自动化"""
        stopped_count = 0
        for thread_info in self.browser_threads.values():
            if thread_info['status'] in ['running', 'paused', 'starting']:
                thread_info['status'] = 'stopping'
                thread_info['stop_event'].set()
                thread_info['pause_event'].set()  # 确保线程不会卡在暂停状态
                stopped_count += 1

        self.is_running = False
        self.log_message(f"⏹️ 已发送停止信号给 {stopped_count} 个线程")
        self.update_display()

        # 等待一段时间后检查线程状态
        self.root.after(2000, self.check_thread_status)
    
    def create_new_thread(self):
        """创建新线程"""
        if len([t for t in self.browser_threads.values() if t['status'] in ['running', 'starting']]) >= self.config['max_threads']:
            messagebox.showwarning("警告", f"已达到最大线程数 ({self.config['max_threads']})")
            return

        # 获取下一个可用的配置文件
        profile = self.get_next_available_profile()
        if not profile:
            messagebox.showwarning("警告", "没有可用的配置文件。请确保有足够的 Linken Sphere 配置文件。")
            return

        self.thread_counter += 1
        thread_id = f"Thread-{self.thread_counter}"
        profile_name = profile.get('name', 'Unknown')
        profile_uuid = profile.get('uuid')

        thread_info = {
            'id': thread_id,
            'status': 'starting',
            'stop_event': threading.Event(),
            'pause_event': threading.Event(),
            'thread': None,
            'profile_uuid': profile_uuid,
            'profile_name': profile_name
        }

        # 初始状态为运行（不暂停）
        thread_info['pause_event'].set()

        thread = threading.Thread(target=self.run_browser_thread, args=(thread_info,))
        thread_info['thread'] = thread

        self.browser_threads[thread_id] = thread_info
        thread.start()

        self.is_running = True
        self.update_display()
        self.log_message(f"➕ 创建线程: {thread_id} (配置: {profile_name})")
    
    def run_browser_thread(self, thread_info):
        """运行浏览器线程"""
        thread_id = thread_info['id']
        profile_uuid = thread_info['profile_uuid']
        profile_name = thread_info['profile_name']
        stop_event = thread_info['stop_event']
        pause_event = thread_info['pause_event']

        try:
            # 检查是否在启动前就被停止
            if stop_event.is_set():
                thread_info['status'] = 'stopped'
                return

            browser = LinkenSphereAppleBrowser(
                browse_duration=self.config['browse_duration'],
                major_cycles=self.config['major_cycles'],
                max_retries=self.config['max_retries'],
                profile_uuid=profile_uuid  # 传递指定的配置文件UUID
            )

            thread_info['status'] = 'running'
            self.log_message(f"🚀 {thread_id} 开始运行 (配置: {profile_name})")
            self.update_display()

            # 运行自动化，带有停止和暂停控制
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # 创建一个可控制的运行任务
                task = loop.create_task(self.run_browser_with_control(browser, thread_info))
                loop.run_until_complete(task)
            finally:
                loop.close()

        except Exception as e:
            self.log_message(f"❌ {thread_id} 运行失败: {e}")
            thread_info['status'] = 'error'
        finally:
            # 释放配置文件
            if profile_uuid in self.used_profiles:
                self.used_profiles.remove(profile_uuid)

            if thread_info['status'] != 'error':
                thread_info['status'] = 'finished'

            self.log_message(f"✅ {thread_id} 已完成 (已释放配置: {profile_name})")
            self.update_display()

    async def run_browser_with_control(self, browser, thread_info):
        """带控制的真实浏览器运行"""
        stop_event = thread_info['stop_event']
        pause_event = thread_info['pause_event']

        try:
            # 修改浏览器实例以支持控制信号
            browser.stop_event = stop_event
            browser.pause_event = pause_event
            browser.thread_info = thread_info
            browser.gui_log_callback = self.log_message
            browser.gui_update_callback = self.update_display

            # 运行真实的浏览器自动化
            await browser.run()

        except Exception as e:
            self.log_message(f"❌ {thread_info['id']} 浏览器运行异常: {e}")
            raise
    
    def cleanup_finished_threads(self):
        """清理已完成的线程"""
        finished = [tid for tid, info in self.browser_threads.items() 
                   if info['status'] in ['finished', 'error']]
        
        for thread_id in finished:
            del self.browser_threads[thread_id]
        
        self.update_display()
        self.log_message(f"🗑️ 已清理 {len(finished)} 个线程")

    def pause_selected_thread(self):
        """暂停选中的线程"""
        selection = self.thread_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个线程")
            return

        # 从显示文本中提取线程ID
        selected_text = self.thread_listbox.get(selection[0])
        thread_id = selected_text.split(' - ')[0].split(' ')[1]  # 提取Thread-X

        if thread_id in self.browser_threads:
            thread_info = self.browser_threads[thread_id]
            if thread_info['status'] == 'running':
                thread_info['status'] = 'paused'
                thread_info['pause_event'].clear()  # 暂停线程
                self.log_message(f"⏸️ 线程 {thread_id} 已暂停")
                self.update_display()
            else:
                messagebox.showinfo("信息", f"线程 {thread_id} 当前状态: {thread_info['status']}")

    def resume_selected_thread(self):
        """恢复选中的线程"""
        selection = self.thread_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个线程")
            return

        # 从显示文本中提取线程ID
        selected_text = self.thread_listbox.get(selection[0])
        thread_id = selected_text.split(' - ')[0].split(' ')[1]  # 提取Thread-X

        if thread_id in self.browser_threads:
            thread_info = self.browser_threads[thread_id]
            if thread_info['status'] == 'paused':
                thread_info['status'] = 'running'
                thread_info['pause_event'].set()  # 恢复线程
                self.log_message(f"▶️ 线程 {thread_id} 已恢复")
                self.update_display()
            else:
                messagebox.showinfo("信息", f"线程 {thread_id} 当前状态: {thread_info['status']}")

    def stop_selected_thread(self):
        """停止选中的线程"""
        selection = self.thread_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个线程")
            return

        # 从显示文本中提取线程ID
        selected_text = self.thread_listbox.get(selection[0])
        thread_id = selected_text.split(' - ')[0].split(' ')[1]  # 提取Thread-X

        if thread_id in self.browser_threads:
            thread_info = self.browser_threads[thread_id]
            if thread_info['status'] in ['running', 'paused', 'starting']:
                thread_info['status'] = 'stopping'
                thread_info['stop_event'].set()
                thread_info['pause_event'].set()  # 确保不会卡在暂停状态
                self.log_message(f"⏹️ 线程 {thread_id} 正在停止")
                self.update_display()
            else:
                messagebox.showinfo("信息", f"线程 {thread_id} 当前状态: {thread_info['status']}")

    def check_thread_status(self):
        """检查线程状态"""
        active_threads = [tid for tid, info in self.browser_threads.items()
                         if info['status'] in ['running', 'paused', 'starting']]

        if active_threads:
            self.log_message(f"⚠️ 仍有 {len(active_threads)} 个线程在运行")
        else:
            self.log_message("✅ 所有线程已停止")
    
    def update_display(self):
        """更新显示 - 线程安全"""
        def _update():
            try:
                # 更新状态
                running = len([t for t in self.browser_threads.values() if t['status'] == 'running'])
                paused = len([t for t in self.browser_threads.values() if t['status'] == 'paused'])
                active = len([t for t in self.browser_threads.values() if t['status'] in ['running', 'starting', 'paused']])

                if running > 0:
                    self.status_label.config(text="状态: 运行中", fg='#28a745')
                elif paused > 0:
                    self.status_label.config(text="状态: 已暂停", fg='#ffc107')
                else:
                    self.status_label.config(text="状态: 就绪", fg='#6c757d')

                # 显示详细的线程状态
                if paused > 0:
                    self.threads_label.config(text=f"线程: {running}运行 {paused}暂停/{self.config['max_threads']}")
                else:
                    self.threads_label.config(text=f"线程: {active}/{self.config['max_threads']}")

                # 更新线程列表
                self.thread_listbox.delete(0, tk.END)
                for thread_id, info in self.browser_threads.items():
                    status_emoji = {
                        'starting': '🔄',
                        'running': '▶️',
                        'paused': '⏸️',
                        'stopping': '⏹️',
                        'stopped': '🛑',
                        'finished': '✅',
                        'error': '❌'
                    }.get(info['status'], '❓')

                    # 显示配置文件信息
                    profile_name = info.get('profile_name', 'Unknown')
                    profile_short = profile_name[:12] + "..." if len(profile_name) > 12 else profile_name

                    self.thread_listbox.insert(tk.END, f"{status_emoji} {thread_id} - {info['status']} ({profile_short})")
            except tk.TclError:
                # GUI已关闭，忽略错误
                pass

        # 确保在主线程中执行GUI更新
        try:
            self.root.after(0, _update)
        except (tk.TclError, RuntimeError):
            # GUI已关闭，忽略错误
            pass
    
    def log_message(self, message):
        """记录日志 - 线程安全"""
        def _log():
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"

            try:
                self.log_text.insert(tk.END, formatted_message)
                self.log_text.see(tk.END)

                # 限制日志行数
                lines = int(self.log_text.index('end-1c').split('.')[0])
                if lines > 1000:
                    self.log_text.delete('1.0', '500.0')
            except tk.TclError:
                # GUI已关闭，忽略错误
                pass

            print(formatted_message.strip())

        # 确保在主线程中执行GUI更新
        try:
            self.root.after(0, _log)
        except (tk.TclError, RuntimeError):
            # GUI已关闭，只打印到控制台
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def clear_logs(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🗑️ 日志已清空")
    
    def save_logs(self):
        """保存日志"""
        file_path = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"💾 日志已保存: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败: {e}")
    
    def on_closing(self):
        """窗口关闭"""
        if self.is_running:
            if messagebox.askokcancel("确认退出", "程序正在运行，确定退出吗？"):
                self.stop_all_automation()
                self.save_config()
                self.root.destroy()
        else:
            self.save_config()
            self.root.destroy()

def main():
    """主函数"""
    app = SimpleLinkenGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
