import os
import shutil
import zipfile
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from datetime import datetime


class FileManager:
    def __init__(self, window):
        self.window = window
        self.window.title("FileManager")
        self.window.geometry("1000x600")

        self.left_frame = ttk.Frame(self.window)
        self.left_frame.grid(row=0, column=0, sticky="news")
        self.right_frame = ttk.Frame(self.window)
        self.right_frame.grid(row=0, column=1, sticky="news")

        self.folder_tree = ttk.Treeview(self.left_frame)
        self.folder_tree.pack(fill="both", expand=True)
        self.folder_tree.bind('<<TreeviewSelect>>', self.display_folder_contents)

        self.file_tree = ttk.Treeview(self.right_frame, columns=('size', 'created', 'modified'), show="headings")
        self.file_tree.heading('size', text="Size")
        self.file_tree.heading('created', text="Created")
        self.file_tree.heading('modified', text="Modified")
        self.file_tree.pack(fill="both", expand=True)

        self.load_drivers()

        self.create_context_menu()

    def create_context_menu(self):
        self.context_menu = ttk.Menu(self.window)
        self.context_menu.add_command(label="Create Folder", command=self.create_folder)
        self.context_menu.add_command(label="Delete", command=self.delete_item)
        self.context_menu.add_command(label="Rename", command=self.rename_item)
        self.context_menu.add_command(label="Zip Folder", command=self.zip_filder)
        self.context_menu.add_command(label="Extract Zip", command=self.extract_zip)
        self.file_tree.bind("<<Button-3>>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_window, event.y_window)

    def load_drives(self):
        drives = [f'{d}:' for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f'{d}:')]
        for drive in drives:
            self.folder_tree.insert('', 'end', text=drive, values=(drive, '', ''))
            self.folder_tree.bind('<<TreeviewSelect>>', self.load_folders)


