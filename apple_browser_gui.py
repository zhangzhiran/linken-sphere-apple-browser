#!/usr/bin/env python3
"""
Apple Website Browser - 图形用户界面
美观的GUI界面，支持配置和实时监控
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import asyncio
import sys
import os
from datetime import datetime
import platform
import subprocess

# 尝试导入主程序
try:
    from apple_website_browser import AppleWebsiteBrowser
except ImportError:
    AppleWebsiteBrowser = None

class AppleBrowserGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.browser_thread = None
        self.is_running = False
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("🍎 Apple Website Browser v2.1")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        self.root.configure(bg='#2c2c2c')  # 深色背景

        # 设置窗口图标（如果存在）
        try:
            if platform.system() == "Windows":
                self.root.iconbitmap("apple_icon.ico")
            else:
                # Mac/Linux 使用 PNG 图标
                icon = tk.PhotoImage(file="apple_icon.png")
                self.root.iconphoto(True, icon)
        except:
            pass  # 图标文件不存在时忽略

        # 设置最小窗口大小
        self.root.minsize(700, 550)

        # 居中显示窗口
        self.center_window()
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_styles(self):
        """设置主题样式"""
        style = ttk.Style()

        # 设置主题
        try:
            style.theme_use('clam')  # 现代化主题
        except:
            pass

        # 深色主题样式
        style.configure('Title.TLabel',
                       font=('Microsoft YaHei', 18, 'bold'),
                       foreground='#1890ff',
                       background='#2c2c2c')

        style.configure('Subtitle.TLabel',
                       font=('Microsoft YaHei', 10),
                       foreground='#888888',
                       background='#2c2c2c')

        style.configure('Config.TLabel',
                       font=('Microsoft YaHei', 9),
                       foreground='#ffffff',
                       background='#2c2c2c')

        style.configure('Success.TButton',
                       font=('Microsoft YaHei', 10, 'bold'),
                       padding=8)

        style.configure('Danger.TButton',
                       font=('Microsoft YaHei', 10, 'bold'),
                       padding=8)

        # 配置Frame样式
        style.configure('Dark.TFrame',
                       background='#2c2c2c')

        style.configure('Dark.TLabelFrame',
                       background='#2c2c2c',
                       foreground='#ffffff',
                       borderwidth=1,
                       relief='solid')

        style.configure('Dark.TLabelFrame.Label',
                       background='#2c2c2c',
                       foreground='#1890ff',
                       font=('Microsoft YaHei', 10, 'bold'))
        
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = tk.Frame(self.root, bg='#2c2c2c', padx=25, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题区域
        self.create_header(main_frame)
        
        # 配置区域
        self.create_config_section(main_frame)
        
        # 控制按钮区域
        self.create_control_section(main_frame)
        
        # 状态显示区域
        self.create_status_section(main_frame)
        
        # 日志显示区域
        self.create_log_section(main_frame)
        
    def create_header(self, parent):
        """创建标题区域"""
        header_frame = tk.Frame(parent, bg='#2c2c2c')
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 25))

        # 主标题
        title_label = tk.Label(header_frame,
                              text="🍎 Apple Website Browser",
                              font=('Microsoft YaHei', 18, 'bold'),
                              fg='#1890ff',
                              bg='#2c2c2c')
        title_label.grid(row=0, column=0, sticky=tk.W)

        # 副标题
        subtitle_label = tk.Label(header_frame,
                                 text="智能双层循环浏览 | 精确时间控制 | 网络重试机制",
                                 font=('Microsoft YaHei', 10),
                                 fg='#888888',
                                 bg='#2c2c2c')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(8, 0))

        # 系统信息
        system_info = f"系统: {platform.system()} | Python: {sys.version.split()[0]} | 浏览器: 自动识别"
        system_label = tk.Label(header_frame,
                               text=system_info,
                               font=('Microsoft YaHei', 9),
                               fg='#666666',
                               bg='#2c2c2c')
        system_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
    def create_config_section(self, parent):
        """创建配置区域"""
        config_frame = tk.LabelFrame(parent,
                                    text="⚙️ 浏览配置",
                                    font=('Microsoft YaHei', 10, 'bold'),
                                    fg='#1890ff',
                                    bg='#2c2c2c',
                                    padx=20, pady=15)
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # 浏览时间配置
        tk.Label(config_frame, text="每页浏览时间 (秒):",
                font=('Microsoft YaHei', 9), fg='#ffffff', bg='#2c2c2c').grid(
            row=0, column=0, sticky=tk.W, pady=8)
        self.browse_duration_var = tk.StringVar(value="60")
        browse_duration_entry = tk.Entry(config_frame, textvariable=self.browse_duration_var,
                                        width=12, font=('Microsoft YaHei', 9))
        browse_duration_entry.grid(row=0, column=1, sticky=tk.W, padx=(15, 0), pady=8)

        # 大循环次数配置
        tk.Label(config_frame, text="大循环次数:",
                font=('Microsoft YaHei', 9), fg='#ffffff', bg='#2c2c2c').grid(
            row=1, column=0, sticky=tk.W, pady=8)
        self.major_cycles_var = tk.StringVar(value="3")
        major_cycles_entry = tk.Entry(config_frame, textvariable=self.major_cycles_var,
                                     width=12, font=('Microsoft YaHei', 9))
        major_cycles_entry.grid(row=1, column=1, sticky=tk.W, padx=(15, 0), pady=8)

        # 重试配置
        tk.Label(config_frame, text="最大重试次数:",
                font=('Microsoft YaHei', 9), fg='#ffffff', bg='#2c2c2c').grid(
            row=2, column=0, sticky=tk.W, pady=8)
        self.max_retries_var = tk.StringVar(value="3")
        max_retries_entry = tk.Entry(config_frame, textvariable=self.max_retries_var,
                                    width=12, font=('Microsoft YaHei', 9))
        max_retries_entry.grid(row=2, column=1, sticky=tk.W, padx=(15, 0), pady=8)

        # 重试间隔配置
        tk.Label(config_frame, text="重试间隔 (秒):",
                font=('Microsoft YaHei', 9), fg='#ffffff', bg='#2c2c2c').grid(
            row=3, column=0, sticky=tk.W, pady=8)
        self.retry_delay_var = tk.StringVar(value="5")
        retry_delay_entry = tk.Entry(config_frame, textvariable=self.retry_delay_var,
                                    width=12, font=('Microsoft YaHei', 9))
        retry_delay_entry.grid(row=3, column=1, sticky=tk.W, padx=(15, 0), pady=8)
        
        # 计算预计时间
        calc_frame = tk.Frame(config_frame, bg='#2c2c2c')
        calc_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))

        self.calc_button = tk.Button(calc_frame, text="🧮 计算预计耗时",
                                    command=self.calculate_time,
                                    font=('Microsoft YaHei', 9, 'bold'),
                                    bg='#1890ff', fg='white',
                                    relief='flat', padx=15, pady=5,
                                    cursor='hand2')
        self.calc_button.grid(row=0, column=0, sticky=tk.W)

        self.time_label = tk.Label(calc_frame, text="",
                                  font=('Microsoft YaHei', 9),
                                  fg='#888888', bg='#2c2c2c')
        self.time_label.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
    def create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = tk.Frame(parent, bg='#2c2c2c')
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # 按钮样式配置
        button_config = {
            'font': ('Microsoft YaHei', 10, 'bold'),
            'relief': 'flat',
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2'
        }

        # 开始按钮
        self.start_button = tk.Button(control_frame, text="🚀 开始浏览",
                                     command=self.start_browsing,
                                     bg='#52c41a', fg='white',
                                     **button_config)
        self.start_button.grid(row=0, column=0, padx=(0, 15))

        # 停止按钮
        self.stop_button = tk.Button(control_frame, text="⏹️ 停止浏览",
                                    command=self.stop_browsing,
                                    bg='#ff4d4f', fg='white',
                                    state='disabled',
                                    **button_config)
        self.stop_button.grid(row=0, column=1, padx=(0, 15))

        # 测试按钮
        test_button = tk.Button(control_frame, text="🧪 运行测试",
                               command=self.run_tests,
                               bg='#722ed1', fg='white',
                               **button_config)
        test_button.grid(row=0, column=2, padx=(0, 15))

        # 帮助按钮
        help_button = tk.Button(control_frame, text="❓ 帮助",
                               command=self.show_help,
                               bg='#1890ff', fg='white',
                               **button_config)
        help_button.grid(row=0, column=3)
        
    def create_status_section(self, parent):
        """创建状态显示区域"""
        status_frame = tk.LabelFrame(parent,
                                    text="📊 运行状态",
                                    font=('Microsoft YaHei', 10, 'bold'),
                                    fg='#1890ff', bg='#2c2c2c',
                                    padx=20, pady=15)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        status_frame.columnconfigure(1, weight=1)

        # 状态标签
        tk.Label(status_frame, text="当前状态:",
                font=('Microsoft YaHei', 9), fg='#ffffff', bg='#2c2c2c').grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                    font=('Microsoft YaHei', 9, 'bold'),
                                    fg='#52c41a', bg='#2c2c2c')
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(15, 0), pady=5)

        # 进度条
        tk.Label(status_frame, text="进度:",
                font=('Microsoft YaHei', 9), fg='#ffffff', bg='#2c2c2c').grid(
            row=1, column=0, sticky=tk.W, pady=(8, 0))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var,
                                           maximum=100, length=350, mode='determinate')
        self.progress_bar.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(15, 0), pady=(8, 0))
        
    def create_log_section(self, parent):
        """创建日志显示区域"""
        log_frame = tk.LabelFrame(parent,
                                 text="📝 运行日志",
                                 font=('Microsoft YaHei', 10, 'bold'),
                                 fg='#1890ff', bg='#2c2c2c',
                                 padx=15, pady=10)
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(4, weight=1)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=14, width=85,
                                                 font=('Consolas', 9),
                                                 bg='#1e1e1e', fg='#ffffff',
                                                 insertbackground='white',
                                                 selectbackground='#264f78')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))

        # 清空日志按钮
        clear_button = tk.Button(log_frame, text="🗑️ 清空日志",
                                command=self.clear_log,
                                font=('Microsoft YaHei', 9),
                                bg='#ff4d4f', fg='white',
                                relief='flat', padx=15, pady=5,
                                cursor='hand2')
        clear_button.grid(row=1, column=0, sticky=tk.E, pady=(8, 0))
        
    def calculate_time(self):
        """计算预计耗时"""
        try:
            browse_duration = int(self.browse_duration_var.get())
            major_cycles = int(self.major_cycles_var.get())
            total_pages = major_cycles * 8  # 每个大循环8次访问
            total_minutes = (total_pages * browse_duration) / 60
            
            time_text = f"总页面: {total_pages} | 预计耗时: {total_minutes:.1f} 分钟"
            self.time_label.config(text=time_text)
        except ValueError:
            self.time_label.config(text="请输入有效数字")
            
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        
    def start_browsing(self):
        """开始浏览"""
        if AppleWebsiteBrowser is None:
            messagebox.showerror("错误", "无法导入主程序模块，请确保 apple_website_browser.py 存在")
            return
            
        try:
            # 获取配置参数
            browse_duration = int(self.browse_duration_var.get())
            major_cycles = int(self.major_cycles_var.get())
            max_retries = int(self.max_retries_var.get())
            retry_delay = int(self.retry_delay_var.get())
            
            # 验证参数
            if browse_duration <= 0 or major_cycles <= 0:
                raise ValueError("时间和循环次数必须大于0")
                
        except ValueError as e:
            messagebox.showerror("配置错误", f"请检查配置参数: {e}")
            return
            
        # 更新界面状态
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_var.set("正在启动...")
        self.progress_var.set(0)
        
        # 清空日志
        self.clear_log()
        self.log_message("🚀 开始启动 Apple Website Browser")
        self.log_message(f"配置: {browse_duration}秒/页, {major_cycles}个大循环, 总计{major_cycles*8}页")
        
        # 在新线程中运行浏览器
        self.browser_thread = threading.Thread(target=self.run_browser_async, 
                                              args=(browse_duration, major_cycles, max_retries, retry_delay))
        self.browser_thread.daemon = True
        self.browser_thread.start()
        
    def run_browser_async(self, browse_duration, major_cycles, max_retries, retry_delay):
        """在异步环境中运行浏览器"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 创建浏览器实例
            browser = AppleWebsiteBrowser(
                browse_duration=browse_duration,
                major_cycles=major_cycles,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
            
            # 运行浏览器
            loop.run_until_complete(browser.run())
            
        except Exception as e:
            self.log_message(f"❌ 运行出错: {e}")
        finally:
            # 恢复界面状态
            self.root.after(0, self.browsing_finished)
            
    def stop_browsing(self):
        """停止浏览"""
        self.is_running = False
        self.log_message("⏹️ 用户请求停止浏览")
        self.browsing_finished()
        
    def browsing_finished(self):
        """浏览完成后的清理工作"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("已完成")
        self.progress_var.set(100)
        self.log_message("✅ 浏览任务完成")
        
    def run_tests(self):
        """运行测试"""
        TestWindow(self.root)
        
    def show_help(self):
        """显示帮助信息"""
        help_text = """
🍎 Apple Website Browser 使用帮助

📋 功能说明:
• 双层循环浏览: 外层控制大循环次数，内层固定8次页面访问
• 精确时间控制: 每页浏览时间精确到秒
• 智能重试机制: 自动处理网络问题
• URL屏蔽系统: 自动过滤搜索页面等不适合的链接

⚙️ 配置参数:
• 每页浏览时间: 在每个页面停留的时间（秒）
• 大循环次数: 外层循环的次数，总页面数 = 大循环次数 × 8
• 最大重试次数: 网络失败时的重试次数
• 重试间隔: 重试之间的等待时间

🎯 使用步骤:
1. 配置浏览参数
2. 点击"计算预计耗时"查看总时间
3. 点击"开始浏览"启动程序
4. 观察日志和进度
5. 可随时点击"停止浏览"中断

🔧 系统要求:
• Python 3.7+
• Playwright 浏览器引擎
• 网络连接

💡 提示:
• 首次使用需要安装 Playwright: pip install playwright
• 然后安装浏览器: playwright install
• 程序会自动选择适合的浏览器引擎
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("600x500")
        help_window.resizable(False, False)
        
        # 居中显示
        help_window.transient(self.root)
        help_window.grab_set()
        
        # 帮助文本
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, 
                                                    font=('Microsoft YaHei UI', 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        
    def run(self):
        """运行GUI"""
        self.log_message("🎉 Apple Website Browser GUI 已启动")
        self.log_message("请配置参数后点击'开始浏览'")
        self.root.mainloop()

class TestWindow:
    """测试窗口"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("测试工具")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_test_widgets()
        
    def create_test_widgets(self):
        """创建测试界面"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🧪 测试工具", 
                 font=('Microsoft YaHei UI', 14, 'bold')).pack(pady=(0, 20))
        
        # 测试按钮
        tests = [
            ("滚动行为测试", "test_scroll.py"),
            ("双层循环逻辑测试", "test_dual_loop.py"),
            ("网络重试机制测试", "test_network_retry.py"),
            ("URL屏蔽功能测试", "test_url_blocking.py"),
        ]
        
        for test_name, test_file in tests:
            btn = ttk.Button(main_frame, text=test_name, 
                           command=lambda f=test_file: self.run_test(f))
            btn.pack(fill=tk.X, pady=5)
            
        # 关闭按钮
        ttk.Button(main_frame, text="关闭", 
                  command=self.window.destroy).pack(pady=(20, 0))
                  
    def run_test(self, test_file):
        """运行测试文件"""
        try:
            subprocess.Popen([sys.executable, test_file], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0)
            messagebox.showinfo("测试启动", f"已启动 {test_file}")
        except Exception as e:
            messagebox.showerror("启动失败", f"无法启动测试: {e}")

if __name__ == "__main__":
    app = AppleBrowserGUI()
    app.run()
