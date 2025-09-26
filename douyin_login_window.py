# -*- coding: utf-8 -*-
"""
抖音聊天监控工具登录界面模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from douyin_security_manager import DouyinSecurityManager
from douyin_config import config

class DouyinLoginWindow:
    def __init__(self):
        self.security_manager = DouyinSecurityManager()
        self.login_successful = False
        self.username = ""
        self.password = ""
        self.is_closing = False  # 窗口关闭状态标志
        
        # 创建登录窗口
        self.window = tk.Tk()
        self.window.title(config.LOGIN_WINDOW_TITLE)
        self.window.geometry(config.LOGIN_WINDOW_GEOMETRY)
        self.window.resizable(False, False)
        self.window.configure(bg='#2c2c2c')
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 设置窗口居中
        self.center_window()
        
        # 设置窗口样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()

        # 加载保存的凭据
        self.load_saved_credentials()

        # 绑定回车键
        self.window.bind('<Return>', lambda e: self.login())

        # 设置窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            import os
            import sys
            
            # 获取图标文件路径
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, config.ICON_FILE)

            if not os.path.exists(icon_path):
                icon_path = config.ICON_FILE
            
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
                print(f"[INFO] 登录窗口图标设置成功: {icon_path}")
            else:
                print("[WARNING] 登录窗口图标文件未找到，使用默认图标")
                
        except Exception as e:
            print(f"[WARNING] 登录窗口图标设置失败: {e}")
    
    def center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', 
                       font=('Microsoft YaHei', 18, 'bold'), 
                       foreground='#1890ff',
                       background='#2c2c2c')
        style.configure('Login.TButton', 
                       font=('Microsoft YaHei', 11, 'bold'), 
                       padding=12)
        style.configure('Info.TLabel', 
                       font=('Microsoft YaHei', 9), 
                       foreground='#888888',
                       background='#2c2c2c')
        style.configure('Info.TButton', 
                       font=('Microsoft YaHei', 8), 
                       padding=5)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = tk.Frame(self.window, bg='#2c2c2c', padx=40, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(main_frame, 
                              text="🎬 抖音聊天监控工具", 
                              font=('Microsoft YaHei', 18, 'bold'),
                              fg='#1890ff',
                              bg='#2c2c2c')
        title_label.pack(pady=(0, 10))
        
        # 副标题
        subtitle_label = tk.Label(main_frame, 
                                 text="请登录以继续使用", 
                                 font=('Microsoft YaHei', 10),
                                 fg='#888888',
                                 bg='#2c2c2c')
        subtitle_label.pack(pady=(0, 30))
        
        # 登录表单框架
        form_frame = tk.Frame(main_frame, bg='#2c2c2c')
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 用户名
        tk.Label(form_frame, text="用户名:", 
                font=('Microsoft YaHei', 11),
                fg='white', bg='#2c2c2c').pack(anchor=tk.W, pady=(0, 8))
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(form_frame, 
                                      textvariable=self.username_var, 
                                      font=('Microsoft YaHei', 11),
                                      bg='#3c3c3c',
                                      fg='white',
                                      insertbackground='white',
                                      relief='flat',
                                      bd=8)
        self.username_entry.pack(fill=tk.X, pady=(0, 15))

        # 设置默认焦点到用户名输入框
        self.username_entry.focus_set()

        # 密码
        tk.Label(form_frame, text="密码:", 
                font=('Microsoft YaHei', 11),
                fg='white', bg='#2c2c2c').pack(anchor=tk.W, pady=(0, 8))
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(form_frame, 
                                      textvariable=self.password_var, 
                                      show="*", 
                                      font=('Microsoft YaHei', 11),
                                      bg='#3c3c3c',
                                      fg='white',
                                      insertbackground='white',
                                      relief='flat',
                                      bd=8)
        self.password_entry.pack(fill=tk.X, pady=(0, 15))

        # 绑定回车键到登录功能
        self.username_entry.bind('<Return>', lambda event: self.password_entry.focus_set())
        self.password_entry.bind('<Return>', lambda event: self.login())

        # 记住密码选项框架
        remember_frame = tk.Frame(form_frame, bg='#2c2c2c')
        remember_frame.pack(fill=tk.X, pady=(0, 20))

        # 记住密码复选框
        self.remember_password = tk.BooleanVar()
        self.remember_checkbox = tk.Checkbutton(
            remember_frame,
            text="记住密码",
            variable=self.remember_password,
            command=self.on_remember_changed,
            font=('Microsoft YaHei', 10),
            fg='white',
            bg='#2c2c2c',
            selectcolor='#1890ff',
            activebackground='#2c2c2c',
            activeforeground='white'
        )
        self.remember_checkbox.pack(side=tk.LEFT)

        # 清除密码按钮
        self.clear_btn = tk.Button(
            remember_frame,
            text="清除保存的密码",
            command=self.clear_saved_password,
            font=('Microsoft YaHei', 9),
            fg='#888888',
            bg='#2c2c2c',
            relief='flat',
            bd=0,
            cursor='hand2'
        )
        self.clear_btn.pack(side=tk.RIGHT)

        # 登录按钮
        self.login_btn = tk.Button(form_frame, 
                                  text="🚀 登录", 
                                  command=self.login,
                                  font=('Microsoft YaHei', 12, 'bold'),
                                  bg='#1890ff',
                                  fg='white',
                                  relief='flat',
                                  bd=0,
                                  padx=20,
                                  pady=12,
                                  cursor='hand2')
        self.login_btn.pack(fill=tk.X, expand=True)
        
        # 状态标签
        self.status_label = tk.Label(main_frame, 
                                    text="", 
                                    font=('Microsoft YaHei', 10),
                                    fg='#f5222d', 
                                    bg='#2c2c2c')
        self.status_label.pack(pady=(20, 0))
        
        # 服务器状态标签
        self.server_status_label = tk.Label(main_frame, 
                                           text="正在检查服务器连接...", 
                                           font=('Microsoft YaHei', 9),
                                           fg='#faad14', 
                                           bg='#2c2c2c')
        self.server_status_label.pack(pady=(10, 0))
        
        # 帮助信息
        help_frame = tk.Frame(main_frame, bg='#2c2c2c')
        help_frame.pack(fill=tk.X, pady=(20, 0))
        
        help_text = "默认账户: admin / douyin123456\n如需注册新账户，请联系管理员"
        help_label = tk.Label(help_frame, 
                             text=help_text, 
                             font=('Microsoft YaHei', 9),
                             fg='#888888', 
                             bg='#2c2c2c',
                             justify=tk.CENTER)
        help_label.pack()
        
        # 设置焦点
        self.username_entry.focus()
        
        # 加载初始数据
        self.load_initial_data()
        
        # 检查服务器状态
        threading.Thread(target=self.check_server_status, daemon=True).start()
    
    def load_initial_data(self):
        """加载初始数据"""
        # 获取最后登录的用户名
        last_username = self.security_manager.get_last_login_user()
        if last_username:
            self.username_var.set(last_username)
            self.password_entry.focus()  # 如果有用户名，焦点移到密码框
        else:
            # 如果没有保存的用户名，预填充默认测试账号
            self.username_var.set("admin")
            self.password_entry.focus()  # 焦点移到密码框
    
    def check_server_status(self):
        """检查服务器状态"""
        try:
            import requests
            response = requests.get(f"{self.security_manager.server_url}/api/status", timeout=5)
            if response.status_code == 200:
                if not self.is_closing:
                    self.window.after(0, lambda: self.server_status_label.config(
                        text="✅ 服务器连接正常", fg='#52c41a'))
            else:
                if not self.is_closing:
                    self.window.after(0, lambda: self.server_status_label.config(
                        text="⚠️ 服务器响应异常，将使用本地验证", fg='#faad14'))
        except:
            if not self.is_closing:
                self.window.after(0, lambda: self.server_status_label.config(
                    text="⚠️ 无法连接服务器，将使用本地验证", fg='#faad14'))

    def login(self):
        """登录验证"""
        print("[DEBUG] 登录按钮被点击")

        # 直接从输入框获取值（更可靠）
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        print(f"[DEBUG] 获取到用户名: '{username}', 密码长度: {len(password)}")

        # 额外调试信息
        print(f"[DEBUG] 用户名变量内容: '{self.username_var.get()}'")
        print(f"[DEBUG] 密码变量内容长度: {len(self.password_var.get())}")

        if not username or not password:
            print("[DEBUG] 用户名或密码为空")
            self.status_label.config(text="⚠️ 请输入用户名和密码", fg='#f5222d')
            # 设置焦点到空的输入框
            if not username:
                self.username_entry.focus_set()
            else:
                self.password_entry.focus_set()
            return

        print("[DEBUG] 开始验证流程")
        # 禁用登录按钮，显示加载状态
        self.login_btn.config(state='disabled', text='🔄 验证中...')
        self.status_label.config(text="正在验证登录信息...", fg='#1890ff')

        # 在后台线程中验证登录
        threading.Thread(target=self._verify_login, args=(username, password), daemon=True).start()

    def _verify_login(self, username, password):
        """后台验证登录"""
        try:
            print(f"[INFO] 开始验证用户: {username}")

            # 首先尝试远程验证
            result = self.security_manager.verify_user_remote(username, password)
            print(f"[INFO] 验证结果: {result}")

            if result:
                # 登录成功
                if not self.is_closing:
                    self.window.after(0, self._login_success, username, password)
            else:
                # 登录失败
                if not self.is_closing:
                    self.window.after(0, self._login_failed)

        except Exception as e:
            print(f"[ERROR] 验证出错: {e}")
            if not self.is_closing:
                self.window.after(0, self._login_error, str(e))

    def _login_success(self, username, password):
        """登录成功处理"""
        print(f"[INFO] 登录成功: {username}")
        self.username = username
        self.password = password
        self.login_successful = True

        # 保存最后登录的用户名
        self.security_manager.save_last_login_user(username)

        # 如果用户选择了记住密码，则保存凭据
        self.save_credentials_if_needed()

        self.status_label.config(text="✅ 登录成功！正在启动程序...", fg='#52c41a')

        # 延迟关闭窗口
        if not self.is_closing:
            self.window.after(1500, self._close_window)

    def _close_window(self):
        """关闭登录窗口"""
        print(f"[INFO] 关闭登录窗口")
        self.is_closing = True
        try:
            self.window.quit()
            self.window.destroy()
        except tk.TclError:
            # 窗口已被销毁
            pass

    def _login_failed(self):
        """登录失败处理"""
        print(f"[INFO] 登录失败")
        self.login_btn.config(state='normal', text='🚀 登录')
        self.status_label.config(text="❌ 用户名或密码错误", fg='#f5222d')
        self.password_var.set("")
        self.password_entry.focus()

    def _login_error(self, error_msg):
        """登录错误处理"""
        self.login_btn.config(state='normal', text='🚀 登录')
        self.status_label.config(text=f"❌ 登录验证出错: {error_msg}", fg='#f5222d')

    def on_closing(self):
        """窗口关闭事件"""
        self.is_closing = True
        try:
            self.window.quit()
            self.window.destroy()
        except tk.TclError:
            # 窗口已被销毁
            pass

    def load_saved_credentials(self):
        """加载保存的凭据"""
        try:
            credentials = self.security_manager.load_credentials()
            if credentials:
                self.username_var.set(credentials['username'])
                self.password_var.set(credentials['password'])
                self.remember_password.set(True)
                print("[INFO] 已加载保存的凭据")

                # 更新清除按钮状态
                self.update_clear_button_state()
            else:
                # 没有保存的凭据，隐藏清除按钮
                self.clear_btn.pack_forget()

        except Exception as e:
            print(f"[ERROR] 加载保存的凭据失败: {e}")
            self.clear_btn.pack_forget()

    def on_remember_changed(self):
        """记住密码选项改变时的处理"""
        self.update_clear_button_state()

    def update_clear_button_state(self):
        """更新清除按钮的显示状态"""
        if self.security_manager.has_saved_credentials():
            self.clear_btn.pack(side=tk.RIGHT)
        else:
            self.clear_btn.pack_forget()

    def clear_saved_password(self):
        """清除保存的密码"""
        try:
            if messagebox.askyesno("确认", "确定要清除保存的密码吗？"):
                if self.security_manager.clear_credentials():
                    self.remember_password.set(False)
                    self.update_clear_button_state()
                    messagebox.showinfo("成功", "已清除保存的密码")
                else:
                    messagebox.showerror("错误", "清除密码失败")
        except Exception as e:
            messagebox.showerror("错误", f"清除密码时出错: {e}")

    def save_credentials_if_needed(self):
        """如果用户选择了记住密码，则保存凭据"""
        if self.remember_password.get():
            try:
                username = self.username_var.get().strip()
                password = self.password_var.get().strip()

                if username and password:
                    if self.security_manager.save_credentials(username, password):
                        print("[INFO] 凭据已保存")
                    else:
                        print("[WARNING] 凭据保存失败")
            except Exception as e:
                print(f"[ERROR] 保存凭据时出错: {e}")

    def show(self):
        """显示登录窗口"""
        self.window.mainloop()
        return self.login_successful, self.username, self.password

if __name__ == "__main__":
    login = DouyinLoginWindow()
    success, username, password = login.show()
    if success:
        print(f"登录成功: {username}")
    else:
        print("登录失败或取消")
