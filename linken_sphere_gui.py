#!/usr/bin/env python3
"""
Linken Sphere Apple Browser - 图形用户界面
支持多线程、配置保存、实时监控的现代化GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import asyncio
import sys
import os
import json
import platform
from datetime import datetime
from pathlib import Path
import configparser

# 尝试导入主程序
try:
    from linken_sphere_playwright_browser import LinkenSphereAppleBrowser
except ImportError:
    LinkenSphereAppleBrowser = None

class LinkenSphereGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        
        # 配置管理
        self.config_file = "linken_sphere_config.json"
        self.load_config()
        
        # 多线程支持
        self.browser_threads = {}  # {thread_id: thread_info}
        self.max_threads = 3
        self.thread_counter = 0
        
        # GUI 组件
        self.create_widgets()
        
        # 状态管理
        self.is_running = False
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("🔗 Linken Sphere Apple Browser")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.configure(bg='#2c2c2c')

        # 设置最小窗口大小
        self.root.minsize(700, 500)

        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """设置样式主题"""
        style = ttk.Style()
        
        # 配置深色主题
        style.theme_use('clam')
        
        # 自定义颜色
        colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'select_bg': '#404040',
            'select_fg': '#ffffff',
            'button_bg': '#0d7377',
            'button_fg': '#ffffff',
            'entry_bg': '#2d2d2d',
            'entry_fg': '#ffffff'
        }
        
        # 配置各种组件样式
        style.configure('Title.TLabel', 
                       background=colors['bg'], 
                       foreground=colors['fg'],
                       font=('Arial', 16, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=colors['bg'],
                       foreground=colors['fg'], 
                       font=('Arial', 12, 'bold'))
        
        style.configure('Custom.TButton',
                       background=colors['button_bg'],
                       foreground=colors['button_fg'],
                       font=('Arial', 10, 'bold'))
        
        style.configure('Custom.TEntry',
                       fieldbackground=colors['entry_bg'],
                       foreground=colors['entry_fg'],
                       bordercolor=colors['select_bg'])
        
        style.configure('Custom.TFrame',
                       background=colors['bg'])
    
    def load_config(self):
        """加载配置文件"""
        self.config = {
            'browse_duration': 60,
            'major_cycles': 3,
            'minor_cycles_per_major': 8,
            'max_retries': 3,
            'retry_delay': 5,
            'linken_api_port': 36555,
            'debug_port': 12345,
            'max_threads': 3,
            'auto_save_logs': True,
            'log_level': 'INFO'
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                print(f"✅ 配置已从 {self.config_file} 加载")
        except Exception as e:
            print(f"⚠️ 加载配置失败: {e}")
    
    def save_config(self):
        """保存配置文件"""
        try:
            # 从GUI获取当前配置
            self.update_config_from_gui()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"✅ 配置已保存到 {self.config_file}")
            
            # 显示保存成功消息
            self.log_message("✅ 配置已保存", "INFO")
            
        except Exception as e:
            error_msg = f"❌ 保存配置失败: {e}"
            print(error_msg)
            self.log_message(error_msg, "ERROR")
    
    def update_config_from_gui(self):
        """从GUI更新配置"""
        try:
            self.config['browse_duration'] = int(self.browse_duration_var.get())
            self.config['major_cycles'] = int(self.major_cycles_var.get())
            self.config['minor_cycles_per_major'] = int(self.minor_cycles_var.get())
            self.config['max_retries'] = int(self.max_retries_var.get())
            self.config['retry_delay'] = int(self.retry_delay_var.get())
            self.config['linken_api_port'] = int(self.api_port_var.get())
            self.config['debug_port'] = int(self.debug_port_var.get())
            self.config['max_threads'] = int(self.max_threads_var.get())
        except ValueError as e:
            raise ValueError(f"配置值无效: {e}")
    
    def create_widgets(self):
        """创建GUI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(main_frame, 
                               text="🔗 Linken Sphere Apple Browser",
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 创建笔记本（标签页）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个标签页
        self.create_config_tab()
        self.create_control_tab()
        self.create_threads_tab()
        self.create_logs_tab()
        
        # 底部状态栏
        self.create_status_bar(main_frame)
    
    def create_config_tab(self):
        """创建配置标签页"""
        config_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(config_frame, text="⚙️ 配置")
        
        # 创建滚动框架
        canvas = tk.Canvas(config_frame, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Custom.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 配置变量
        self.browse_duration_var = tk.StringVar(value=str(self.config['browse_duration']))
        self.major_cycles_var = tk.StringVar(value=str(self.config['major_cycles']))
        self.minor_cycles_var = tk.StringVar(value=str(self.config['minor_cycles_per_major']))
        self.max_retries_var = tk.StringVar(value=str(self.config['max_retries']))
        self.retry_delay_var = tk.StringVar(value=str(self.config['retry_delay']))
        self.api_port_var = tk.StringVar(value=str(self.config['linken_api_port']))
        self.debug_port_var = tk.StringVar(value=str(self.config['debug_port']))
        self.max_threads_var = tk.StringVar(value=str(self.config['max_threads']))
        
        # 浏览配置组
        self.create_config_group(scrollable_frame, "🌐 浏览配置", [
            ("每页浏览时长 (秒)", self.browse_duration_var, "每个页面的浏览时间"),
            ("大循环次数", self.major_cycles_var, "主要循环的次数"),
            ("小循环次数", self.minor_cycles_var, "每个大循环中的页面访问次数"),
        ])
        
        # 重试配置组
        self.create_config_group(scrollable_frame, "🔄 重试配置", [
            ("最大重试次数", self.max_retries_var, "操作失败时的最大重试次数"),
            ("重试延迟 (秒)", self.retry_delay_var, "重试之间的等待时间"),
        ])
        
        # Linken Sphere 配置组
        self.create_config_group(scrollable_frame, "🔗 Linken Sphere 配置", [
            ("API 端口", self.api_port_var, "Linken Sphere API 端口"),
            ("调试端口", self.debug_port_var, "浏览器调试端口"),
        ])
        
        # 多线程配置组
        self.create_config_group(scrollable_frame, "🧵 多线程配置", [
            ("最大线程数", self.max_threads_var, "同时运行的最大浏览器数量"),
        ])
        
        # 配置按钮
        button_frame = ttk.Frame(scrollable_frame, style='Custom.TFrame')
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="💾 保存配置", 
                  command=self.save_config, style='Custom.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🔄 重置配置", 
                  command=self.reset_config, style='Custom.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📁 导入配置", 
                  command=self.import_config, style='Custom.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📤 导出配置", 
                  command=self.export_config, style='Custom.TButton').pack(side=tk.LEFT, padx=5)
        
        # 打包滚动框架
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_config_group(self, parent, title, configs):
        """创建配置组"""
        group_frame = ttk.LabelFrame(parent, text=title, style='Custom.TFrame')
        group_frame.pack(fill=tk.X, padx=10, pady=10)
        
        for i, (label, var, tooltip) in enumerate(configs):
            row_frame = ttk.Frame(group_frame, style='Custom.TFrame')
            row_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # 标签
            label_widget = ttk.Label(row_frame, text=label, style='Heading.TLabel')
            label_widget.pack(side=tk.LEFT)
            
            # 输入框
            entry = ttk.Entry(row_frame, textvariable=var, style='Custom.TEntry', width=15)
            entry.pack(side=tk.RIGHT)
            
            # 工具提示（简化版）
            self.create_tooltip(entry, tooltip)
    
    def create_tooltip(self, widget, text):
        """创建简单的工具提示"""
        def on_enter(event):
            widget.configure(cursor="hand2")
        
        def on_leave(event):
            widget.configure(cursor="")
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def reset_config(self):
        """重置配置到默认值"""
        if messagebox.askyesno("确认重置", "确定要重置所有配置到默认值吗？"):
            # 重置配置字典
            self.config = {
                'browse_duration': 60,
                'major_cycles': 3,
                'minor_cycles_per_major': 8,
                'max_retries': 3,
                'retry_delay': 5,
                'linken_api_port': 36555,
                'debug_port': 12345,
                'max_threads': 3,
                'auto_save_logs': True,
                'log_level': 'INFO'
            }
            
            # 更新GUI变量
            self.browse_duration_var.set(str(self.config['browse_duration']))
            self.major_cycles_var.set(str(self.config['major_cycles']))
            self.minor_cycles_var.set(str(self.config['minor_cycles_per_major']))
            self.max_retries_var.set(str(self.config['max_retries']))
            self.retry_delay_var.set(str(self.config['retry_delay']))
            self.api_port_var.set(str(self.config['linken_api_port']))
            self.debug_port_var.set(str(self.config['debug_port']))
            self.max_threads_var.set(str(self.config['max_threads']))
            
            self.log_message("🔄 配置已重置到默认值", "INFO")
    
    def import_config(self):
        """导入配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_config = json.load(f)
                
                # 验证配置
                required_keys = ['browse_duration', 'major_cycles', 'minor_cycles_per_major']
                if all(key in imported_config for key in required_keys):
                    self.config.update(imported_config)
                    
                    # 更新GUI
                    self.browse_duration_var.set(str(self.config['browse_duration']))
                    self.major_cycles_var.set(str(self.config['major_cycles']))
                    # ... 更新其他变量
                    
                    self.log_message(f"📁 配置已从 {file_path} 导入", "INFO")
                else:
                    messagebox.showerror("错误", "配置文件格式无效")
                    
            except Exception as e:
                messagebox.showerror("错误", f"导入配置失败: {e}")
    
    def export_config(self):
        """导出配置文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_config_from_gui()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                
                self.log_message(f"📤 配置已导出到 {file_path}", "INFO")
                
            except Exception as e:
                messagebox.showerror("错误", f"导出配置失败: {e}")
    
    def create_control_tab(self):
        """创建控制标签页"""
        control_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(control_frame, text="🎮 控制")

        # 主控制区域
        main_control_frame = ttk.LabelFrame(control_frame, text="🎮 主控制", style='Custom.TFrame')
        main_control_frame.pack(fill=tk.X, padx=10, pady=10)

        # 控制按钮
        button_frame = ttk.Frame(main_control_frame, style='Custom.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.start_button = ttk.Button(button_frame, text="🚀 开始自动化",
                                      command=self.start_automation, style='Custom.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止所有",
                                     command=self.stop_all_automation, style='Custom.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(button_frame, text="⏸️ 暂停所有",
                                      command=self.pause_all_automation, style='Custom.TButton')
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # 状态显示
        status_frame = ttk.LabelFrame(control_frame, text="📊 状态概览", style='Custom.TFrame')
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        # 状态标签
        self.status_label = ttk.Label(status_frame, text="状态: 就绪", style='Heading.TLabel')
        self.status_label.pack(anchor=tk.W, padx=10, pady=5)

        self.threads_label = ttk.Label(status_frame, text="活跃线程: 0/3", style='Heading.TLabel')
        self.threads_label.pack(anchor=tk.W, padx=10, pady=5)

        self.progress_label = ttk.Label(status_frame, text="总进度: 0%", style='Heading.TLabel')
        self.progress_label.pack(anchor=tk.W, padx=10, pady=5)

        # 进度条
        self.progress_bar = ttk.Progressbar(status_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

    def create_threads_tab(self):
        """创建线程管理标签页"""
        threads_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(threads_frame, text="🧵 线程管理")

        # 线程控制区域
        thread_control_frame = ttk.LabelFrame(threads_frame, text="🧵 线程控制", style='Custom.TFrame')
        thread_control_frame.pack(fill=tk.X, padx=10, pady=10)

        # 新建线程按钮
        new_thread_frame = ttk.Frame(thread_control_frame, style='Custom.TFrame')
        new_thread_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(new_thread_frame, text="➕ 新建线程",
                  command=self.create_new_thread, style='Custom.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Button(new_thread_frame, text="🗑️ 清理已完成",
                  command=self.cleanup_finished_threads, style='Custom.TButton').pack(side=tk.LEFT, padx=5)

        # 线程列表
        list_frame = ttk.LabelFrame(threads_frame, text="📋 线程列表", style='Custom.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建树形视图
        columns = ('ID', '状态', '进度', '当前页面', '操作')
        self.thread_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        # 设置列标题
        for col in columns:
            self.thread_tree.heading(col, text=col)
            self.thread_tree.column(col, width=120)

        # 滚动条
        thread_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.thread_tree.yview)
        self.thread_tree.configure(yscrollcommand=thread_scrollbar.set)

        # 打包
        self.thread_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        thread_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 线程操作按钮
        thread_button_frame = ttk.Frame(threads_frame, style='Custom.TFrame')
        thread_button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(thread_button_frame, text="▶️ 启动选中",
                  command=self.start_selected_thread, style='Custom.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Button(thread_button_frame, text="⏸️ 暂停选中",
                  command=self.pause_selected_thread, style='Custom.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Button(thread_button_frame, text="⏹️ 停止选中",
                  command=self.stop_selected_thread, style='Custom.TButton').pack(side=tk.LEFT, padx=5)

    def create_logs_tab(self):
        """创建日志标签页"""
        logs_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(logs_frame, text="📝 日志")

        # 日志控制区域
        log_control_frame = ttk.Frame(logs_frame, style='Custom.TFrame')
        log_control_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(log_control_frame, text="🗑️ 清空日志",
                  command=self.clear_logs, style='Custom.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Button(log_control_frame, text="💾 保存日志",
                  command=self.save_logs, style='Custom.TButton').pack(side=tk.LEFT, padx=5)

        # 日志级别选择
        ttk.Label(log_control_frame, text="日志级别:", style='Heading.TLabel').pack(side=tk.LEFT, padx=(20, 5))

        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(log_control_frame, textvariable=self.log_level_var,
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], width=10)
        log_level_combo.pack(side=tk.LEFT, padx=5)

        # 日志文本区域
        log_text_frame = ttk.LabelFrame(logs_frame, text="📝 日志输出", style='Custom.TFrame')
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(log_text_frame,
                                                 bg='#1e1e1e', fg='#ffffff',
                                                 font=('Consolas', 10),
                                                 wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent, style='Custom.TFrame')
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 状态标签
        self.status_bar_label = ttk.Label(status_frame, text="就绪", style='Heading.TLabel')
        self.status_bar_label.pack(side=tk.LEFT, padx=5)

        # 时间标签
        self.time_label = ttk.Label(status_frame, text="", style='Heading.TLabel')
        self.time_label.pack(side=tk.RIGHT, padx=5)

        # 更新时间
        self.update_time()

    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def log_message(self, message, level="INFO"):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"

        # 如果日志文本框存在，添加消息
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, formatted_message)
            self.log_text.see(tk.END)

        # 打印到控制台
        print(formatted_message.strip())

    def clear_logs(self):
        """清空日志"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
        self.log_message("🗑️ 日志已清空", "INFO")

    def save_logs(self):
        """保存日志到文件"""
        if hasattr(self, 'log_text'):
            file_path = filedialog.asksaveasfilename(
                title="保存日志文件",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.log_text.get(1.0, tk.END))
                    self.log_message(f"💾 日志已保存到 {file_path}", "INFO")
                except Exception as e:
                    messagebox.showerror("错误", f"保存日志失败: {e}")

    # 多线程控制方法
    def start_automation(self):
        """开始自动化"""
        if LinkenSphereAppleBrowser is None:
            messagebox.showerror("错误", "无法导入 LinkenSphereAppleBrowser 模块")
            return

        try:
            self.update_config_from_gui()
            self.create_new_thread()
            self.log_message("🚀 自动化已开始", "INFO")
        except Exception as e:
            messagebox.showerror("错误", f"启动自动化失败: {e}")

    def stop_all_automation(self):
        """停止所有自动化"""
        for thread_id, thread_info in self.browser_threads.items():
            if thread_info['status'] == 'running':
                thread_info['status'] = 'stopping'
                thread_info['stop_event'].set()

        self.is_running = False
        self.log_message("⏹️ 所有自动化已停止", "INFO")
        self.update_status_display()

    def pause_all_automation(self):
        """暂停所有自动化"""
        for thread_id, thread_info in self.browser_threads.items():
            if thread_info['status'] == 'running':
                thread_info['status'] = 'paused'
                thread_info['pause_event'].clear()

        self.log_message("⏸️ 所有自动化已暂停", "INFO")
        self.update_status_display()

    def create_new_thread(self):
        """创建新的浏览器线程"""
        if len([t for t in self.browser_threads.values() if t['status'] in ['running', 'paused']]) >= self.config['max_threads']:
            messagebox.showwarning("警告", f"已达到最大线程数限制 ({self.config['max_threads']})")
            return

        self.thread_counter += 1
        thread_id = f"Thread-{self.thread_counter}"

        # 创建线程信息
        thread_info = {
            'id': thread_id,
            'status': 'starting',
            'progress': 0,
            'current_page': '准备中...',
            'stop_event': threading.Event(),
            'pause_event': threading.Event(),
            'thread': None
        }

        # 设置暂停事件为已设置状态（不暂停）
        thread_info['pause_event'].set()

        # 创建并启动线程
        thread = threading.Thread(target=self.run_browser_thread, args=(thread_info,))
        thread_info['thread'] = thread

        self.browser_threads[thread_id] = thread_info
        thread.start()

        self.is_running = True
        self.update_thread_display()
        self.log_message(f"➕ 创建新线程: {thread_id}", "INFO")

    def run_browser_thread(self, thread_info):
        """运行浏览器线程"""
        thread_id = thread_info['id']

        try:
            # 创建浏览器实例
            browser = LinkenSphereAppleBrowser(
                browse_duration=self.config['browse_duration'],
                major_cycles=self.config['major_cycles'],
                max_retries=self.config['max_retries'],
                retry_delay=self.config['retry_delay']
            )

            thread_info['status'] = 'running'
            self.log_message(f"🚀 线程 {thread_id} 开始运行", "INFO")

            # 运行自动化（这里需要适配异步）
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(self.run_browser_with_monitoring(browser, thread_info))
            finally:
                loop.close()

        except Exception as e:
            self.log_message(f"❌ 线程 {thread_id} 运行失败: {e}", "ERROR")
            thread_info['status'] = 'error'
        finally:
            thread_info['status'] = 'finished'
            self.update_thread_display()
            self.log_message(f"✅ 线程 {thread_id} 已完成", "INFO")

    async def run_browser_with_monitoring(self, browser, thread_info):
        """运行浏览器并监控状态"""
        # 这里需要修改 LinkenSphereAppleBrowser 的 run 方法以支持监控
        # 暂时使用简化版本
        await browser.run()

    def cleanup_finished_threads(self):
        """清理已完成的线程"""
        finished_threads = [tid for tid, info in self.browser_threads.items()
                           if info['status'] in ['finished', 'error']]

        for thread_id in finished_threads:
            del self.browser_threads[thread_id]

        self.update_thread_display()
        self.log_message(f"🗑️ 已清理 {len(finished_threads)} 个已完成的线程", "INFO")

    def start_selected_thread(self):
        """启动选中的线程"""
        selected = self.thread_tree.selection()
        if selected:
            thread_id = self.thread_tree.item(selected[0])['values'][0]
            if thread_id in self.browser_threads:
                thread_info = self.browser_threads[thread_id]
                if thread_info['status'] == 'paused':
                    thread_info['status'] = 'running'
                    thread_info['pause_event'].set()
                    self.log_message(f"▶️ 线程 {thread_id} 已恢复", "INFO")
                    self.update_thread_display()

    def pause_selected_thread(self):
        """暂停选中的线程"""
        selected = self.thread_tree.selection()
        if selected:
            thread_id = self.thread_tree.item(selected[0])['values'][0]
            if thread_id in self.browser_threads:
                thread_info = self.browser_threads[thread_id]
                if thread_info['status'] == 'running':
                    thread_info['status'] = 'paused'
                    thread_info['pause_event'].clear()
                    self.log_message(f"⏸️ 线程 {thread_id} 已暂停", "INFO")
                    self.update_thread_display()

    def stop_selected_thread(self):
        """停止选中的线程"""
        selected = self.thread_tree.selection()
        if selected:
            thread_id = self.thread_tree.item(selected[0])['values'][0]
            if thread_id in self.browser_threads:
                thread_info = self.browser_threads[thread_id]
                if thread_info['status'] in ['running', 'paused']:
                    thread_info['status'] = 'stopping'
                    thread_info['stop_event'].set()
                    self.log_message(f"⏹️ 线程 {thread_id} 正在停止", "INFO")
                    self.update_thread_display()

    def update_thread_display(self):
        """更新线程显示"""
        # 清空现有项目
        for item in self.thread_tree.get_children():
            self.thread_tree.delete(item)

        # 添加线程信息
        for thread_id, thread_info in self.browser_threads.items():
            status_emoji = {
                'starting': '🔄',
                'running': '▶️',
                'paused': '⏸️',
                'stopping': '⏹️',
                'finished': '✅',
                'error': '❌'
            }.get(thread_info['status'], '❓')

            self.thread_tree.insert('', tk.END, values=(
                thread_id,
                f"{status_emoji} {thread_info['status']}",
                f"{thread_info['progress']}%",
                thread_info['current_page'],
                "操作"
            ))

        # 更新状态显示
        self.update_status_display()

    def update_status_display(self):
        """更新状态显示"""
        active_threads = len([t for t in self.browser_threads.values()
                             if t['status'] in ['running', 'paused']])
        total_threads = len(self.browser_threads)

        if hasattr(self, 'threads_label'):
            self.threads_label.config(text=f"活跃线程: {active_threads}/{self.config['max_threads']}")

        if hasattr(self, 'status_label'):
            if active_threads > 0:
                self.status_label.config(text="状态: 运行中")
            else:
                self.status_label.config(text="状态: 就绪")

    def on_closing(self):
        """窗口关闭事件"""
        if self.is_running:
            if messagebox.askokcancel("确认退出", "自动化正在运行，确定要退出吗？"):
                self.stop_all_automation()
                self.save_config()
                self.root.destroy()
        else:
            self.save_config()
            self.root.destroy()

def main():
    """主函数"""
    app = LinkenSphereGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
