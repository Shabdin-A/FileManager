import os
import shutil
import zipfile
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
from datetime import datetime

class FileManager:
    def __init__(self, window):
        self.window = window
        self.window.title("FileManager")
        self.window.geometry("1000x600")

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        self.search_bar = ttk.Entry(self.window)
        self.search_bar.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.search_bar.bind("<Return>", self.search_item)

        self.address_bar = ttk.Entry(self.window)
        self.address_bar.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.address_bar.bind("<Return>", self.go_to_address)

        self.left_frame = ttk.Frame(self.window)
        self.left_frame.grid(row=2, column=0, sticky="news")

        self.right_frame = ttk.Frame(self.window)
        self.right_frame.grid(row=2, column=1, sticky="news")

        self.folder_tree = ttk.Treeview(self.left_frame)
        self.folder_tree.pack(fill="both", expand=True)
        self.folder_tree.bind('<<TreeviewSelect>>', self.display_folder_contents)

        self.file_tree = ttk.Treeview(self.right_frame, columns=('name', 'size', 'created', 'modified'), show="headings")
        self.file_tree.heading('name', text="Name")
        self.file_tree.heading('size', text="Size")
        self.file_tree.heading('created', text="Created")
        self.file_tree.heading('modified', text="Modified")
        self.file_tree.pack(fill="both", expand=True)

        self.load_drives()
        self.create_context_menu()

    def create_context_menu(self):
        self.context_menu = ttk.Menu(self.window)
        self.context_menu.add_command(label="Create Folder", command=self.create_folder)
        self.context_menu.add_command(label="Delete", command=self.delete_item)
        self.context_menu.add_command(label="Rename", command=self.rename_item)
        self.context_menu.add_command(label="Zip Folder", command=self.zip_folder)
        self.context_menu.add_command(label="Extract Zip", command=self.extract_zip)
        self.file_tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def load_drives(self):
        drives = [f'{d}:' for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f'{d}:')]
        for drive in drives:
            self.folder_tree.insert('', 'end', text=drive)
        self.folder_tree.bind('<<TreeviewSelect>>', self.load_folders)

    def load_folders(self, event=None):
        selected_item = self.folder_tree.selection()[0]
        path = self.folder_tree.item(selected_item, 'text')
        if os.path.isdir(path):
            self.folder_tree.delete(*self.folder_tree.get_children(selected_item))
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    self.folder_tree.insert(selected_item, 'end', text=item_path)
            self.display_folder_contents(event)

    def display_folder_contents(self, event):
        self.file_tree.delete(*self.file_tree.get_children())
        selected_item = self.folder_tree.selection()[0]
        folder_path = self.folder_tree.item(selected_item, 'text')
        self.address_bar.delete(0, 'end')
        self.address_bar.insert(0, folder_path)

        if os.path.isdir(folder_path):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                size = os.path.getsize(item_path)
                created = datetime.fromtimestamp(os.path.getctime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
                modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
                self.file_tree.insert('', 'end', values=(item, self.convert_size(size), created, modified))

    def convert_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    def create_folder(self):
        select_item = self.folder_tree.selection()[0]
        path = self.folder_tree.item(select_item, 'text')
        if os.path.isdir(path):
            folder_name = simpledialog.askstring("Folder Name", "Enter folder name:")
            if folder_name:
                os.makedirs(os.path.join(path, folder_name))
                self.load_folders(None)

    def delete_item(self):
        select_item = self.file_tree.selection()[0]
        folder_item = self.folder_tree.selection()[0]
        file_name = self.file_tree.item(select_item, 'values')[0]
        path = os.path.join(self.folder_tree.item(folder_item, 'text'), file_name)
        if messagebox.askyesno("Delete", f"Are you sure you want to delete {file_name}?"):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.display_folder_contents(None)

    def rename_item(self):
        selected_item = self.file_tree.selection()[0]
        folder_item = self.folder_tree.selection()[0]
        file_name = self.file_tree.item(selected_item, 'values')[0]
        path = os.path.join(self.folder_tree.item(folder_item, 'text'), file_name)
        new_name = simpledialog.askstring("Rename", f"Enter new name for {file_name}:")
        if new_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            os.rename(path, new_path)
            self.display_folder_contents(None)

    def zip_folder(self):
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No file or folder selected.")
            return

        selected_item = selected_items[0]
        folder_item = self.folder_tree.selection()[0]
        file_name = self.file_tree.item(selected_item, 'values')[0]
        path = os.path.join(self.folder_tree.item(folder_item, 'text'), file_name)

        if os.path.isdir(path):
            zip_name = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")])
            if zip_name:
                shutil.make_archive(zip_name.replace(".zip", ""), 'zip', path)

    def extract_zip(self):
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No file or folder selected.")
            return

        selected_item = selected_items[0]
        folder_item = self.folder_tree.selection()[0]
        file_name = self.file_tree.item(selected_item, 'values')[0]
        path = os.path.join(self.folder_tree.item(folder_item, 'text'), file_name)

        if path.endswith(".zip"):
            extract_path = filedialog.askdirectory()
            if extract_path:
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)

    def go_to_address(self, event):
        path = self.address_bar.get()
        if os.path.isdir(path):
            self.folder_tree.selection_set('')
            self.load_folders(None)
            self.display_folder_contents(event)
        else:
            messagebox.showerror("Error", "Invalid path")

    def search_item(self, event):
        search_query = self.search_bar.get().lower()
        for child in self.file_tree.get_children():
            file_name = self.file_tree.item(child, 'values')[0].lower()
            if search_query in file_name:
                self.file_tree.selection_set(child)
                self.file_tree.see(child)
                return
        messagebox.showinfo("Not Found", "No matching file or folder found.")

if __name__ == "__main__":
    window = ttk.Window(themename="darkly")
    window.option_add("*TButton.Padding", [10, 10])
    window.option_add("*TButton.Relief", "flat")

    app = FileManager(window)
    window.mainloop()
