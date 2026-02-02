import sys
import ctypes
import subprocess
import threading
import customtkinter as ctk  # 引入现代化UI库


# --- 1. 自动提权逻辑 (在加载界面前执行) ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    # 如果不是管理员，重新运行自身并请求权限
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# --- 2. 界面配置 ---
ctk.set_appearance_mode("Dark")  # 模式: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # 主题色: "blue" (standard), "green", "dark-blue"


class ModernDeployApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 窗口基础设置
        self.title("系统自动化部署助手 Pro")
        self.geometry("700x500")

        # 设置窗口透明度 (模拟玻璃质感，0.0-1.0)
        self.attributes("-alpha", 0.95)

        # 布局网格配置 (2列 x 2行)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === 左侧导航栏 (Sidebar) ===
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Auto Deploy", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_menu_1 = ctk.CTkButton(self.sidebar_frame, text="系统优化", fg_color="transparent", border_width=2,
                                        text_color=("gray10", "#DCE4EE"))
        self.btn_menu_1.grid(row=1, column=0, padx=20, pady=10)

        self.btn_menu_2 = ctk.CTkButton(self.sidebar_frame, text="软件安装", fg_color="transparent",
                                        text_color=("gray10", "#DCE4EE"))
        self.btn_menu_2.grid(row=2, column=0, padx=20, pady=10)

        # === 右侧主内容区 ===
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # 标题
        self.lbl_title = ctk.CTkLabel(self.main_frame, text="第一步：环境准备", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(anchor="w", pady=(0, 20))

        # 功能卡片：停用 Defender
        self.card_frame = ctk.CTkFrame(self.main_frame, fg_color=("gray80", "gray20"), corner_radius=15)
        self.card_frame.pack(fill="x", pady=10)

        self.lbl_desc = ctk.CTkLabel(self.card_frame,
                                     text="临时停用 Windows Defender 实时防护\n(用于防止误杀破解补丁或拦截静默安装)",
                                     justify="left")
        self.lbl_desc.pack(side="left", padx=20, pady=20)

        # 核心按钮
        self.btn_run = ctk.CTkButton(self.card_frame, text="立即执行",
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     height=40, corner_radius=20,
                                     fg_color="#E63946", hover_color="#D62828",  # 红色警示色
                                     command=lambda: self.run_async(self.disable_defender))
        self.btn_run.pack(side="right", padx=20)

        # === 底部日志控制台 ===
        self.log_textbox = ctk.CTkTextbox(self.main_frame, height=200, corner_radius=10, font=("Consolas", 12))
        self.log_textbox.pack(fill="both", expand=True, pady=(20, 0))
        self.log_textbox.insert("0.0", ">>> 系统就绪，等待指令...\n")
        self.log_textbox.configure(state="disabled")

    def log(self, message):
        """线程安全的日志输出"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def run_async(self, func):
        """多线程包装器"""
        threading.Thread(target=func, daemon=True).start()

    def disable_defender(self):
        """调用 PowerShell 关闭 Defender"""
        self.btn_run.configure(state="disabled", text="处理中...")
        self.log("-" * 40)
        self.log("[INFO] 正在尝试关闭实时防护...")

        # PowerShell 命令
        ps_cmd = "Set-MpPreference -DisableRealtimeMonitoring $true"

        try:
            # CREATE_NO_WINDOW 隐藏黑框
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if process.returncode == 0:
                self.log("[SUCCESS] 指令已发送！")
                self.log("[WARN] 若开启了'防篡改保护'，此操作可能无效。")
                self.log("[NOTE] 重启电脑后防护将自动恢复。")
            else:
                self.log(f"[ERROR] 执行失败: {process.stderr}")

        except Exception as e:
            self.log(f"[EXCEPTION] 发生错误: {e}")

        finally:
            self.btn_run.configure(state="normal", text="立即执行")


if __name__ == "__main__":
    app = ModernDeployApp()
    app.mainloop()
