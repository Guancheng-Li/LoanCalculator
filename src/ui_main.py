"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Mainloop for GUI.
"""

from datetime import datetime
import os
import re
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

from core.annuity_calculator import AnnuityCalculator
from core.linear_calculator import LinearCalculator


def show_in_notepad(content):
    # 指定文件路径
    file_path = "result.txt"

    # 将字符串保存到文件
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"保存文件时出现错误: {e}")

    # 检查操作系统是否为 Windows
    if os.name == 'nt':
        try:
            # 使用 subprocess 模块打开记事本并显示文件
            subprocess.Popen(['notepad.exe', file_path])
        except Exception as e:
            print(f"打开记事本时出现错误: {e}")
    else:
        print("此方法仅适用于 Windows 系统。")

def is_valid_date(date_str):
    """验证8位日期字符串是否合法"""
    if len(date_str) != 8 or not date_str.isdigit():
        return False
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False


def validate_float(input_str):
    """使用正则表达式验证两位小数的浮点数（支持负数）"""
    if input_str in ("", "-", ".", "-."):  # 允许中间输入状态
        return True
    pattern = r'^-?\d+\.?\d{0,2}$|^-?\d*\.\d{1,2}$'
    return re.fullmatch(pattern, input_str) is not None


class LoanCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("提前贷款计算器")

        # 注册验证命令
        self.vcmd_float = (self.root.register(validate_float), "%P")

        # 输入区组件
        self.create_input_section()
        # 表格区组件
        self.create_table_section()

        # 计算器
        self.calculator = None

    def create_input_section(self):
        """创建顶部输入区域"""
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # 输入组件变量
        self.remaining_loan = tk.DoubleVar(value=100000.00)
        self.remaining_term = tk.IntVar(value=12)
        self.annual_rate = tk.DoubleVar(value=4.90)
        self.method = tk.StringVar(value="annuity")

        # 输入验证函数
        validate_int = (frame.register(lambda p: p.isdigit() or p == ""), "%P")

        # 布局
        ttk.Label(frame, text="剩余还款额度（元）:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.remaining_loan, validate="key", validatecommand=self.vcmd_float).grid(row=0, column=1)

        ttk.Label(frame, text="剩余还款期限（月）:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.remaining_term, validate="key", validatecommand=validate_int).grid(row=1, column=1)

        ttk.Label(frame, text="年化利率（%）:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.annual_rate, validate="key", validatecommand=self.vcmd_float).grid(row=2, column=1)

        ttk.Label(frame, text="还款方式:").grid(row=3, column=0, sticky="w")
        ttk.Radiobutton(frame, text="等额本息", variable=self.method, value="annuity").grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(frame, text="等额本金", variable=self.method, value="linear").grid(row=3, column=1, sticky="e")

        ttk.Button(frame, text="计算", command=self.show_calculation).grid(row=4, column=0, pady=10)
        ttk.Button(frame, text="导出PDF", command=self.export_pdf).grid(row=4, column=1, pady=10)

    def create_table_section(self):
        """创建底部表格区域"""
        frame = ttk.Frame(self.root)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # 表格组件
        self.tree = ttk.Treeview(frame, columns=("操作", "日期", "金额", "周期类型"), show="headings", height=8)
        self.tree.heading("操作", text="")
        self.tree.heading("日期", text="日期（YYYYMMDD）")
        self.tree.heading("金额", text="提前还款额度（元）")
        self.tree.heading("周期类型", text="周期类型")

        # 设置列宽
        self.tree.column("操作", width=50, anchor="center")
        self.tree.column("日期", width=120, anchor="center")
        self.tree.column("金额", width=150, anchor="center")
        self.tree.column("周期类型", width=100, anchor="center")

        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 表格操作按钮
        ttk.Button(self.root, text="+ 添加记录", command=self.open_add_dialog).grid(row=2, column=0, pady=10)

        # 绑定点击事件
        self.tree.bind("<Button-1>", self.on_table_click)

    def on_table_click(self, event):
        """处理表格点击事件"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            if column == "#1":  # 操作列
                self.tree.delete(item)

    def open_add_dialog(self):
        """打开添加记录对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加提前还款记录")

        # 输入变量
        date_var = tk.StringVar(value="20250501")
        amount_var = tk.DoubleVar(value=20000.0)
        cycle_type_var = tk.StringVar(value="short")

        # 输入组件
        ttk.Label(dialog, text="日期（8位数字）:").grid(row=0, column=0, padx=5, pady=5)
        date_entry = ttk.Entry(dialog, textvariable=date_var)
        date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="提前还款额度:").grid(row=1, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(dialog, textvariable=amount_var)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="周期类型:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Radiobutton(dialog, text="缩短周期", variable=cycle_type_var, value="short").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(dialog, text="固定周期", variable=cycle_type_var, value="fixed").grid(row=2, column=1, sticky="e")

        # 保存操作
        def save_record():
            if not is_valid_date(date_var.get()):
                messagebox.showerror("错误", "无效的日期格式，请输入8位有效日期（如20230915）")
                return
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    raise ValueError
            except:
                messagebox.showerror("错误", "请输入有效的正数金额")
                return

            self.tree.insert("", "end", values=("-", date_var.get(), f"{amount:.2f}", cycle_type_var.get()))
            dialog.destroy()

        # 按钮
        ttk.Button(dialog, text="保存", command=save_record).grid(row=3, column=0, padx=5, pady=10)
        ttk.Button(dialog, text="取消", command=dialog.destroy).grid(row=3, column=1, padx=5, pady=10)

    def get_table_data(self):
        """获取表格中所有行的数据"""
        data = []
        for item_id in self.tree.get_children():
            # 获取该行的值（返回元组）
            values = self.tree.item(item_id, "values")
            # 转换为字典格式（示例）
            data.append({
                "date": values[1],        # 日期字符串（YYYYMMDD）
                "amount": float(values[2]),  # 转换为浮点数
                "cycle_type": values[3]   # 周期类型
            })
        return data

    def show_calculation(self):
        """计算按钮示例"""
        if self.method.get() == "annuity":
            self.calculator = AnnuityCalculator(
                self.annual_rate.get() * 0.01,
                self.remaining_loan.get(),
                self.remaining_term.get(),
                datetime.now().strftime("%Y%m%d")  # 假设当前日期为开始日期
            )
        elif self.method.get() == "linear":
            self.calculator = LinearCalculator(
                self.annual_rate.get() * 0.01,
                self.remaining_loan.get(),
                self.remaining_term.get(),
                datetime.now().strftime("%Y%m%d")  # 假设当前日期为开始日期
            )
        if self.calculator is None:
            messagebox.showerror("错误", "计算器未初始化")
            return
        self.calculator.calculate()
        early_payment_records = self.get_table_data()
        for record in early_payment_records:
            if record["cycle_type"] == "short":
                print("short", record["date"], float(record["amount"]))
                self.calculator.early_payment_with_term_change(record["date"], float(record["amount"]))
            elif record["cycle_type"] == "fixed":
                print("fixed", record["date"], float(record["amount"]))
                self.calculator.early_payment_without_term_change(record["date"], float(record["amount"]))
        info = self.calculator.get_info(add_monthly_info=True)
        # messagebox.showinfo("明细", "\n".join(info))
        show_in_notepad("\n".join(info))

    def export_pdf(self):
        """导出PDF示例"""
        messagebox.showinfo("提示", "PDF导出功能（示例提示）")


if __name__ == "__main__":
    root = tk.Tk()
    app = LoanCalculator(root)
    root.mainloop()
