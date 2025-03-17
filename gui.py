import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from tkinter import messagebox
from utils.uuid_tools import validate_uuid
from folder_processor import FolderProcessor


class UUIDRedirectorGUI:
    def __init__(self, master):
        self.master = master
        master.title("UUID重定向工具 v1.0")
        
        # 状态跟踪变量
        self.scanned_files = []
        self.modified_files = []
        self.renamed_entries = []
        
        # 主界面布局
        self._create_widgets()
        self._configure_layout()

    def _create_widgets(self):
        """创建界面组件"""
        self.main_frame = ttk.Frame(self.master, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # 路径选择
        ttk.Label(self.main_frame, text="世界文件夹路径:").grid(row=0, column=0, sticky="w")
        self.path_entry = ttk.Entry(self.main_frame, width=40)
        self.path_entry.grid(row=0, column=1, padx=5)
        ttk.Button(self.main_frame, text="浏览...", command=self.select_folder).grid(row=0, column=2)

        # UUID输入
        uuid_validate = self.master.register(self._validate_uuid_input)
        ttk.Label(self.main_frame, text="旧UUID:").grid(row=1, column=0, sticky="w")
        self.old_uuid_entry = ttk.Entry(self.main_frame, validate="key", validatecommand=(uuid_validate, '%P'))
        self.old_uuid_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky="we")
        
        ttk.Label(self.main_frame, text="新UUID:").grid(row=2, column=0, sticky="w")
        self.new_uuid_entry = ttk.Entry(self.main_frame, validate="key", validatecommand=(uuid_validate, '%P'))
        self.new_uuid_entry.grid(row=2, column=1, columnspan=2, pady=5, sticky="we")

        # 统计信息面板
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="处理统计", padding=10)
        self.stats_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky="we")
        
        self.scanned_label = ttk.Label(self.stats_frame, text="已扫描文件: 0")
        self.scanned_label.pack(side=tk.LEFT, padx=10)
        
        self.modified_label = ttk.Label(self.stats_frame, text="已修改文件: 0")
        self.modified_label.pack(side=tk.LEFT, padx=10)
        
        self.renamed_label = ttk.Label(self.stats_frame, text="已重命名条目: 0")
        self.renamed_label.pack(side=tk.LEFT, padx=10)

        # 详细日志
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=4, column=0, columnspan=3, sticky="nsew")
        
        # 扫描日志标签页
        self.scan_tab = ttk.Frame(self.notebook)
        self.scan_log = scrolledtext.ScrolledText(self.scan_tab, wrap=tk.WORD, state='disabled')
        self.scan_log.pack(expand=True, fill='both')
        self.notebook.add(self.scan_tab, text="扫描日志")
        
        # 操作日志标签页
        self.op_tab = ttk.Frame(self.notebook)
        self.op_log = scrolledtext.ScrolledText(self.op_tab, wrap=tk.WORD, state='disabled')
        self.op_log.pack(expand=True, fill='both')
        self.notebook.add(self.op_tab, text="操作详情")

        # 控制按钮
        self.execute_btn = ttk.Button(self.main_frame, text="开始处理", command=self.start_process)
        self.execute_btn.grid(row=5, column=0, columnspan=3, pady=10)

    def _configure_layout(self):
        """配置布局参数"""
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(4, weight=1)
        self.master.geometry("800x600")
        
    def _validate_uuid_input(self, text):
        cleaned = re.sub(r'-', '', text)
        return re.fullmatch(r'[0-9a-fA-F]{0,32}', cleaned) is not None

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def _update_stats(self):
        self.master.after(0, lambda: [
            self.scanned_label.config(text=f"已扫描文件: {len(self.scanned_files)}"),
            self.modified_label.config(text=f"已修改文件: {len(self.modified_files)}"),
            self.renamed_label.config(text=f"已重命名条目: {len(self.renamed_entries)}")
        ])

    def _log_scan(self, message):
        """记录扫描日志"""
        self.master.after(0, lambda: self._update_log(self.scan_log, f"[扫描] {message}\n"))

    def _log_operation(self, message):
        """记录操作日志"""
        self.master.after(0, lambda: self._update_log(self.op_log, f"[操作] {message}\n"))

    def _update_log(self, log_widget, message):
        """更新日志"""
        log_widget.configure(state='normal')
        log_widget.insert(tk.END, message)
        log_widget.see(tk.END)
        log_widget.configure(state='disabled')


    def start_process(self):
        """启动处理流程"""
        # 重置状态
        self.scanned_files.clear()
        self.modified_files.clear()
        self.renamed_entries.clear()
        self._update_stats()
        
        # 输入验证
        path = self.path_entry.get()
        old_uuid = self.old_uuid_entry.get().strip()
        new_uuid = self.new_uuid_entry.get().strip()

        try:
            validate_uuid(old_uuid)
            validate_uuid(new_uuid)
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return

        if not path:
            messagebox.showerror("路径错误", "请选择有效的文件夹路径")
            return

        # 创建处理器并绑定回调
        processor = FolderProcessor(
            root_dir=path,
            old_uuid=old_uuid,
            new_uuid=new_uuid
        )
        
        # 设置回调函数
        processor.set_callbacks(
            on_scan=lambda x: self._handle_scan(x),
            on_modify=lambda x: self._handle_modify(x),
            on_rename=lambda x,y: self._handle_rename(x,y)
        )

        def process_thread():
                try:
                    processor.process()
                    self.master.after(0, lambda: messagebox.showinfo("完成", "处理已完成！"))
                except Exception as e:
                    self.master.after(0, lambda: messagebox.showerror("错误", f"处理过程中发生错误：{str(e)}"))
                finally:
                    self.master.after(0, lambda: self.execute_btn.config(state=tk.NORMAL, text="开始处理"))
        
        threading.Thread(target=process_thread, daemon=True).start()

    def _handle_scan(self, file_path):
        """处理扫描到的文件"""
        if file_path not in self.scanned_files:
            self.scanned_files.append(file_path)
            self._log_scan(f"找到文件：{file_path}")
            self._update_stats()

    def _handle_modify(self, file_path):
        """处理文件修改"""
        if file_path not in self.modified_files:
            self.modified_files.append(file_path)
            self._log_operation(f"修改内容：{file_path}")
            self._update_stats()

    def _handle_rename(self, old_path, new_path):
        """处理重命名操作"""
        self.renamed_entries.append((old_path, new_path))
        self._log_operation(f"重命名：{old_path} → {new_path}")
        self._update_stats()