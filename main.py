import os, string, subprocess, sys
import tkinter as tk
from tkinter import messagebox, ttk


class DarkExplorer:

    def __init__(self, root):
        self.root = root
        self.root.title("XinoExplorer")
        self.root.iconbitmap("icon.ico")
        self.root.geometry("950x600")
        self.current_path = "THIS_PC"

        # Настройка единого стиля One Dark
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.root.configure(bg="#21252b")

        self.style.configure("Top.TFrame", background="#21252b")
        self.style.configure("Left.TFrame", background="#21252b")
        self.style.configure(
            "TButton",
            background="#282c34",
            foreground="#abb2bf",
            borderwidth=1,
            font=("Segoe UI", 9, "bold"),
        )
        self.style.map(
            "TButton", background=[("active", "#4b5263")], foreground=[("active", "#ffffff")]
        )
        self.style.configure(
            "Menu.TButton",
            background="#21252b",
            foreground="#abb2bf",
            borderwidth=0,
            anchor=tk.W,
            font=("Segoe UI", 10),
        )
        self.style.map(
            "Menu.TButton", background=[("active", "#3e4452")], foreground=[("active", "#61afef")]
        )
        self.style.configure(
            "Modern.Treeview",
            background="#282c34",
            foreground="#abb2bf",
            fieldbackground="#282c34",
            rowheight=30,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        self.style.configure(
            "Modern.Treeview.Heading",
            background="#21252b",
            foreground="#abb2bf",
            font=("Segoe UI", 10, "bold"),
            borderwidth=1,
        )
        self.style.map(
            "Modern.Treeview", background=[("selected", "#3e4452")], foreground=[("selected", "#ffffff")]
        )

        # Верхняя панель
        self.top_frame = ttk.Frame(self.root, padding=8, style="Top.TFrame")
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(self.top_frame, text=" ⬅  Назад ", command=self.go_back).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(self.top_frame, text=" 🔄  Обновить ", command=self.refresh).pack(
            side=tk.LEFT, padx=3
        )

        self.path_entry = ttk.Entry(self.top_frame, font=("Segoe UI", 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.path_entry.bind("<Return>", self.go_to_entered_path)

        # Главный контейнер
        self.workspace = ttk.Frame(self.root)
        self.workspace.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Левое меню
        self.left_menu = ttk.Frame(self.workspace, width=190, style="Left.TFrame", padding=5)
        self.left_menu.pack(side=tk.LEFT, fill=tk.Y)
        self.left_menu.pack_propagate(False)

        ttk.Label(
            self.left_menu,
            text="БЫСТРЫЙ ДОСТУП",
            font=("Segoe UI", 9, "bold"),
            background="#21252b",
            foreground="#5c6370",
        ).pack(anchor=tk.W, padx=5, pady=8)
        ttk.Button(
            self.left_menu, text=" 🖥  Этот компьютер", style="Menu.TButton", command=self.show_drives
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            self.left_menu,
            text=" 📂  Рабочий стол",
            style="Menu.TButton",
            command=lambda: self.load_path(os.path.expanduser("~/Desktop")),
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            self.left_menu,
            text=" 📥  Загрузки",
            style="Menu.TButton",
            command=lambda: self.load_path(os.path.expanduser("~/Downloads")),
        ).pack(fill=tk.X, pady=2)

        ttk.Label(
            self.left_menu,
            text="УСТРОЙСТВА",
            font=("Segoe UI", 9, "bold"),
            background="#21252b",
            foreground="#5c6370",
        ).pack(anchor=tk.W, padx=5, pady=8)
        for d in self.get_drives():
            ttk.Button(
                self.left_menu,
                text=f" 💾  Локальный диск ({d})",
                style="Menu.TButton",
                command=lambda drv=d: self.load_path(drv),
            ).pack(fill=tk.X, pady=2)

        # Правая таблица
        self.right_frame = ttk.Frame(self.workspace, padding=5)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = ttk.Scrollbar(self.right_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            self.right_frame,
            columns=("name", "type", "size", "path"),
            show="headings",
            yscrollcommand=self.scrollbar.set,
            style="Modern.Treeview",
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.tree.yview)

        self.tree.heading("name", text="  Имя")
        self.tree.heading("type", text="Тип")
        self.tree.heading("size", text="Размер")
        self.tree.column("name", width=400, anchor=tk.W)
        self.tree.column("type", width=100, anchor=tk.CENTER)
        self.tree.column("size", width=120, anchor=tk.E)
        self.tree.column("path", width=0, minwidth=0, stretch=tk.NO)

        self.tree.tag_configure("dir", foreground="#61afef")
        self.tree.tag_configure("file", foreground="#abb2bf")
        self.tree.tag_configure("drive", foreground="#98c379")

        self.tree.bind("<Double-1>", self.on_double_click)
        self.show_drives()

    def get_drives(self):
        drives = []
        if sys.platform == "win32":
            for l in string.ascii_uppercase:
                drw = f"{l}:\\"
                if os.path.exists(drw):
                    drives.append(drw)
        else:
            drives.append("/")
        return drives

    def show_drives(self):
        self.current_path = "THIS_PC"
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, "Этот компьютер")
        for i in self.tree.get_children():
            self.tree.delete(i)
        for d in self.get_drives():
            self.tree.insert(
                "", tk.END, values=(f"💾  Локальный диск ({d})", "Системный диск", "", d), tags=("drive",)
            )

    def load_path(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            messagebox.showerror("Ошибка", "Путь недоступен!")
            return
        self.current_path = os.path.abspath(path)
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.current_path)
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            items = os.listdir(path)
            dirs = [x for x in items if os.path.isdir(os.path.join(path, x))]
            files = [x for x in items if not os.path.isdir(os.path.join(path, x))]
            dirs.sort()
            files.sort()
            for d in dirs:
                fp = os.path.join(path, d)
                self.tree.insert("", tk.END, values=(f"📁  {d}", "Папка", "<DIR>", fp), tags=("dir",))
            for f in files:
                fp = os.path.join(path, f)
                try:
                    sz = f"{os.path.getsize(fp) // 1024} КБ"
                except OSError:
                    sz = "Ошибка"
                ext = os.path.splitext(f).upper().replace(".", "") or "Файл"
                self.tree.insert("", tk.END, values=(f"📄  {f}", ext, sz, fp), tags=("file",))
        except PermissionError:
            messagebox.showerror("Ошибка", "Доступ ограничен!")
            self.go_back()

    def on_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel, "values")
        if not vals:
            return
        tgt = vals[3]
        if os.path.isdir(tgt):
            self.load_path(tgt)
        else:
            try:
                if sys.platform == "win32":
                    os.startfile(tgt)
                elif sys.platform == "darwin":
                    subprocess.call(["open", tgt])
                else:
                    subprocess.call(["xdg-open", tgt])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть:\n{e}")

    def go_back(self):
        if self.current_path != "THIS_PC":
            p = os.path.dirname(self.current_path)
            self.show_drives() if p == self.current_path else self.load_path(p)

    def refresh(self):
        self.show_drives() if self.current_path == "THIS_PC" else self.load_path(self.current_path)

    def go_to_entered_path(self, event):
        p = self.path_entry.get().strip()
        if p.lower() in ["этот компьютер", "this pc", ""]:
            self.show_drives()
        else:
            self.load_path(p)


if __name__ == "__main__":
    root = tk.Tk()
    app = DarkExplorer(root)
    root.mainloop()
