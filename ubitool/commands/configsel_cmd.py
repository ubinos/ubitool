#! /usr/bin/python

#
# Copyright (c) 2019 Sung Ho Park and CSOS
#
# SPDX-License-Identifier: Apache-2.0
#

import os
import sys
import glob
import io
import tkinter as tk
import tkinter.font as font
import json
import copy
import pathlib
import shutil

from tkinter import ttk
from tkinter import Toplevel
from tkinter import messagebox

import typer
from typing import Annotated

debug_level = 3

win_width = 1000
win_height = 700
win_x_offset = 0
win_y_offset = 0

# win_width = 2000
# win_height = 1400
# win_x_offset = -2000
# win_y_offset = 150

def print_help():
    print("===============================================================================")
    print("Usage:")
    print("    python %s <base path> <library relative path>" % (sys.argv[0]))
    print("===============================================================================")

def set_geometry_center(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x_cordinate = (screen_width  // 2) - (width  // 2) + win_x_offset
    y_cordinate = (screen_height // 2) - (height // 2) + win_y_offset
    win.geometry("{}x{}+{}+{}".format(width, height, x_cordinate, y_cordinate))

def set_dialog_geometry_center(parent, win, width, height):
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    x_cordinate = (parent_width  // 2) - (width  // 2) + parent_x - 10
    y_cordinate = (parent_height // 2) - (height // 2) + parent_y - 40
    win.geometry("{}x{}+{}+{}".format(width, height, x_cordinate, y_cordinate))

def file_open(fname, mode):
    if (debug_level > 2):
        print("file_open: name: %s, mode: %s" % (fname, mode))
    if sys.version_info.major >= 3:
        return open(fname, mode, encoding="UTF-8")
    else:
        return open(fname, mode)

class copy_dialog(tk.Toplevel):

    src_config_dir = "app"
    src_config_name = "myapp"
    dst_config_dir = "app"
    dst_config_name_base = "myapp_2"
    src_file_rel_paths = []
    dst_file_rel_paths = []

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.title('Ubinos config copier')

        set_dialog_geometry_center(parent, self, 1100, 500)

        self.transient(self.parent)
        self.protocol("WM_DELETE_WINDOW", self.parent.press_copy_dialog_cancel)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.variables = dict()
        self.variables['source'] = tk.StringVar(value = "source")
        self.variables['destination'] = tk.StringVar(value = "destination")
        self.variables['destination'].trace("w", lambda name, index, mode, var=self.variables['destination']: self.dst_config_name_base_callback(var))

        frame_tv = tk.Frame(self)
        frame_tv.grid(row=0, column=0, sticky="nsew")
        frame_tv.rowconfigure(0, weight=1)
        frame_tv.columnconfigure(0, weight=10)
        frame_tv.columnconfigure(1, weight=1)
        frame_tv.columnconfigure(2, weight=10)

        frame_tvl = tk.Frame(frame_tv)
        frame_tvl.grid(row=0, column=0, sticky="nsew")
        frame_tvl.rowconfigure(0, weight=1)
        frame_tvl.columnconfigure(0, weight=1)

        self.tvl = ttk.Treeview(frame_tvl, columns=(1), show="headings", selectmode="browse")
        self.tvl.grid(row=0, column=0, sticky="nsew")
        self.tvl.heading(1, text="Source")

        sbl = tk.Scrollbar(frame_tvl, orient=tk.VERTICAL)
        sbl.grid(row=0, column=1, sticky="ns")
        self.tvl.config(yscrollcommand=sbl.set)
        sbl.config(command=self.tvl.yview)

        source_entry = ttk.Entry(frame_tvl, textvariable=self.variables['source'])
        source_entry.grid(row=1, column=0, columnspan=2, sticky="ew")
        source_entry.configure(state="disabled")

        arrow_label = tk.Label(frame_tv, text=">")
        arrow_label.grid(row=0, column=1)

        frame_tvr = tk.Frame(frame_tv)
        frame_tvr.grid(row=0, column=2, sticky="nsew")
        frame_tvr.rowconfigure(0, weight=1)
        frame_tvr.columnconfigure(0, weight=1)

        self.tvr = ttk.Treeview(frame_tvr, columns=(1), show="headings", selectmode="browse")
        self.tvr.grid(row=0, column=0, sticky="nsew")
        self.tvr.heading(1, text="Destination")

        sbr = tk.Scrollbar(frame_tvr, orient=tk.VERTICAL)
        sbr.grid(row=0, column=1, sticky="ns")
        self.tvr.config(yscrollcommand=sbr.set)
        sbr.config(command=self.tvr.yview)

        destination_entry = ttk.Entry(frame_tvr, textvariable=self.variables['destination'])
        destination_entry.grid(row=1, column=0, columnspan=2, sticky="ew")

        frame_bt = tk.Frame(self)
        frame_bt.grid(row=1, column=0, sticky="nsew", padx=10, pady=20)

        cancel_button = tk.Button(frame_bt, text="Cancel", command=self.parent.press_copy_dialog_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=0)
        ok_button = tk.Button(frame_bt, text="Ok", command=self.parent.press_copy_dialog_ok)
        ok_button.pack(side=tk.RIGHT, padx=10, pady=0)

        self.update_items(True)

    def dst_config_name_base_callback(self, var):
        self.dst_config_name_base = var.get()
        self.update_items()

    def update_items(self, init=False):
        if init:
            selection = self.parent.config_items[self.parent.config_item_idx]
            self.src_config_dir = selection["dir"]
            self.src_config_name = selection["name"]
            self.src_config_name_base = self.src_config_name
            self.dst_config_name_base = self.src_config_name + "_2"

            self.variables['source'].set(self.src_config_name_base)
            self.variables['destination'].set(self.dst_config_name_base)

        src_file_rel_paths, dst_file_rel_paths, src_config_name_base, dst_config_name = self.parent.get_clone_params(self.src_config_dir, self.src_config_name, self.dst_config_dir, self.dst_config_name_base)

        if debug_level >= 2:
            print(src_file_rel_paths)
            print(dst_file_rel_paths)

        self.src_file_rel_paths = src_file_rel_paths
        self.dst_file_rel_paths = dst_file_rel_paths

        for row in self.tvl.get_children():
            self.tvl.delete(row)
        for row in self.tvr.get_children():
            self.tvr.delete(row)

        for idx, file_path in enumerate(src_file_rel_paths):
            self.tvl.insert(parent='', index=idx, iid=idx, values=(file_path))
        for idx, file_path in enumerate(dst_file_rel_paths):
            self.tvr.insert(parent='', index=idx, iid=idx, values=(file_path))

class confsel(tk.Tk):

    def __init__(self, base_path, lib_rel_path):
        super().__init__()

        if debug_level >= 2:
            print("pwd: %s" % os.getcwd())

        self.base_path = base_path
        self.lib_rel_path = lib_rel_path
        self.config_dir_names = ["app", "config"]
        self.config_names = ["CMakeLists.txt"]
        self.config_cmake_file_name = "config.cmake"
        self.config_cmake_path = os.path.join(self.base_path, self.config_cmake_file_name)

        self.config_items = []
        self.config_item_idx = 0
        self.config_item_len = 0

        if debug_level >= 1:
            print("Ubinos config selector")
            print("    base path : %s" % self.base_path)
            print("    library relative path : %s" % self.lib_rel_path)
            print("")

        self.title('Ubinos config selector')

        set_geometry_center(self, win_width, win_height)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.bind('<Key>', self.key_pressed)

        frame_tv = tk.Frame(self)
        frame_tv.grid(row=0, column=0, sticky="nsew")
        frame_tv.rowconfigure(0, weight=1)
        frame_tv.columnconfigure(0, weight=1)

        self.tv = ttk.Treeview(frame_tv, columns=(1, 2, 3, 4), show="headings", selectmode="browse")
        self.tv.grid(row=0, column=0, sticky="nsew")

        sb = tk.Scrollbar(frame_tv, orient=tk.VERTICAL)
        sb.grid(row=0, column=1, sticky="ns")
        self.tv.config(yscrollcommand=sb.set)
        sb.config(command=self.tv.yview)
        self.tv.bind('<ButtonRelease-1>', self.select_item)

        frame_bt = tk.Frame(self)
        frame_bt.grid(row=1, column=0, sticky="nsew", padx=10, pady=20)

        cancel_button = tk.Button(frame_bt, text="Cancel", command=quit)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=0)
        select_button = tk.Button(frame_bt, text="Select", command=self.press_select)
        select_button.pack(side=tk.RIGHT, padx=10, pady=0)
        clone_button = tk.Button(frame_bt, text="Copy", command=self.press_copy)
        clone_button.pack(side=tk.LEFT, padx=10, pady=0)

        self.tv.heading(1, text="Index")
        self.tv.column(1, width=50)
        self.tv.heading(2, text="Project")
        self.tv.column(2, width=200)
        self.tv.heading(3, text="Name")
        self.tv.column(3, width=450)
        self.tv.heading(4, text="Dir")
        self.tv.column(4, width=280)

        self.update_config_items()
        config_dir, config_name = self.get_config_from_config_cmake(self.config_cmake_path)
        if debug_level > 2:
            print("config_cmake_path = %s" % (self.config_cmake_path))
            print("config_dir = %s, config_name = %s" % (config_dir, config_name))
        for conf in self.config_items:
            self.tv.insert(parent='', index=conf["index"], iid=conf["index"], values=(conf["index"], conf["project"], conf["name"], conf["dir"]))
            item_config_dir = ("\"%s\"" % os.path.join("${CMAKE_CURRENT_LIST_DIR}", conf["dir"]))
            item_config_name = conf["name"]
            if debug_level > 2:
                print("item_config_dir = %s, item_config_name = %s" % (item_config_dir, item_config_name))
            if config_dir == item_config_dir and config_name == item_config_name:
                self.config_item_idx = conf["index"]

        self.tv.selection_set(self.config_item_idx)
        self.tv.see(self.config_item_idx)

    def update_config_items(self):
        index = 0
        prjs = [{"name": ".", "dir": "."}]
        lib_dir = os.path.join(self.base_path, self.lib_rel_path)

        if os.path.exists(lib_dir):
            for file_name in sorted(os.listdir(lib_dir)):
                if debug_level > 2:
                    print("file_name: %s" % file_name)
                prj_dir = os.path.join(lib_dir, file_name)
                prj_rel_dir = os.path.join(self.lib_rel_path, file_name)
                if debug_level > 2:
                    print("prj_dir: %s" % prj_rel_dir)
                if os.path.isdir(prj_dir):
                    prjs += [{"name": file_name, "dir": prj_rel_dir}]

        if debug_level > 2:
            print(lib_dir)
            print(prjs)
            print("")

        for prj in prjs:
            config_dirs = []
            config_rel_dirs = []
            for config_dir_name in self.config_dir_names:
                config_dir = pathlib.Path(self.base_path, os.path.join(prj["dir"], config_dir_name)).as_posix()
                config_rel_dir = pathlib.Path(os.path.join(prj["dir"], config_dir_name)).as_posix()
                if os.path.exists(config_dir) and os.path.isdir(config_dir):
                    config_dirs.append(config_dir)
                    config_rel_dirs.append(config_rel_dir)

            if debug_level > 2:
                print("")
                print(config_dirs)
                print(config_rel_dirs)
                print("")

            for idx, config_dir in enumerate(config_dirs):
                config_rel_dir = config_rel_dirs[idx]
                # Check subdirectories for config_names
                subdirs = [d for d in sorted(os.listdir(config_dir)) if os.path.isdir(os.path.join(config_dir, d))]
                for subdir in subdirs:
                    subdir_path = os.path.join(config_dir, subdir)
                    # Check if any of config_names exists in this subdirectory
                    has_config_file = False
                    for config_name in self.config_names:
                        if os.path.exists(os.path.join(subdir_path, config_name)):
                            has_config_file = True
                            break
                    
                    if has_config_file:
                        # This subdirectory is a config
                        config_name = subdir
                        self.config_items.append({"index": index, "project": prj["name"], "name": config_name, "dir": config_rel_dir, "name": config_name})
                        index += 1

        self.config_len = index

        if debug_level >= 3:
            for conf in self.config_items:
                print(conf)
            print("")

    def load_config_info(self, config_file_path):
        config_info = None

        with file_open(config_file_path, 'r') as file:
            try:
                lines = file.readlines()
                for line in lines:
                    k_idx = line.find(self.config_info_keyword)
                    if k_idx > -1:
                        k_len = len(self.config_info_keyword)
                        config_info_string = line[k_idx + k_len - 1:]
                        config_info = json.loads(config_info_string)
                        break
            except Exception as e:
                print('Exception occurred.', e, config_file_path)

            file.close()

        return config_info

    def get_cmake_include_file_names(self, config_dir, config_name):
        include_file_names = []
        config_file_path = os.path.join(config_dir, config_name)

        with file_open(config_file_path, 'r') as file:
            lines = file.readlines()
            file.close()
            for line in lines:
                if line.startswith(self.cmake_inclucde_file_keyword):
                    k_len = len(self.cmake_inclucde_file_keyword)
                    include_file_name = line[k_len:].strip()[:-1]
                    include_file_path = os.path.join(config_dir, include_file_name)
                    include_file_names.append(include_file_name)
                    sub_include_file_names = self.get_cmake_include_file_names(config_dir, include_file_name)
                    include_file_names += sub_include_file_names

        return include_file_names

    def create_config_cmake(self, config_cmake_path, config_dir, config_name):
        file = file_open(config_cmake_path, 'w+')
        file.write("set(UBI_CONFIG_DIR \"${CMAKE_CURRENT_LIST_DIR}/%s\")\n" % config_dir)
        file.write("set(UBI_CONFIG_NAME %s)\n" % config_name)
        file.write("\n")
        file.close()

    def get_config_from_config_cmake(self, config_cmake_path):
        config_dir = ""
        config_name = ""

        if os.path.exists(config_cmake_path):
            with file_open(config_cmake_path, 'r') as file:
                lines = file.readlines()
                file.close()
                for line in lines:
                    # Parse set(UBI_CONFIG_DIR ...)
                    if "set(UBI_CONFIG_DIR" in line:
                        start = line.find("set(UBI_CONFIG_DIR") + len("set(UBI_CONFIG_DIR")
                        end = line.find(")", start)
                        if start > -1 and end > -1:
                            config_dir = line[start:end].strip()
                    
                    # Parse set(UBI_CONFIG_NAME ...)
                    if "set(UBI_CONFIG_NAME" in line:
                        start = line.find("set(UBI_CONFIG_NAME") + len("set(UBI_CONFIG_NAME")
                        end = line.find(")", start)
                        if start > -1 and end > -1:
                            config_name = line[start:end].strip()

        return config_dir, config_name

    def select_config(self, config_dir, config_name):
        if not os.path.exists(self.config_cmake_path):
            self.create_config_cmake(self.config_cmake_path, config_dir, config_name)

        elif not os.path.isdir(self.config_cmake_path):
            file = file_open(self.config_cmake_path, 'r')
            file.seek(0, io.SEEK_END)
            file_len = file.tell()
            file.close()

            if file_len <= 0:
                self.create_config_cmake(self.config_cmake_path, config_dir, config_name)

            else:
                shutil.copyfile(self.config_cmake_path, self.config_cmake_path + ".bak")

                need_config_dir = True
                need_config_name = True

                file = file_open(self.config_cmake_path, 'r')
                lines = file.readlines()
                file.close()
                file = file_open(self.config_cmake_path, 'w+')
                for line in lines:
                    if "set(UBI_CONFIG_DIR" in line:
                        file.write("set(UBI_CONFIG_DIR \"${CMAKE_CURRENT_LIST_DIR}/%s\")\n" % config_dir)
                        need_config_dir = False
                    elif "set(UBI_CONFIG_NAME" in line:
                        file.write("set(UBI_CONFIG_NAME %s)\n" % config_name)
                        need_config_name = False
                    else:
                        file.write(line)
                file.close()

                # If CONFIG_DIR or CONFIG_NAME not found, append them
                if need_config_dir or need_config_name:
                    file = file_open(self.config_cmake_path, 'a')
                    if need_config_dir:
                        file.write("set(UBI_CONFIG_DIR \"${CMAKE_CURRENT_LIST_DIR}/%s\")\n" % config_dir)
                    if need_config_name:
                        file.write("set(UBI_CONFIG_NAME %s)\n" % config_name)
                    file.close()

    def get_clone_params(self, src_config_dir, src_config_name, dst_config_dir, dst_config_name_base):
        src_file_rel_paths = []
        dst_file_rel_paths = []
        src_config_name_base = ""
        dst_config_name = ""

        src_file_path = os.path.join(src_config_dir, src_config_name)
        src_file_rel_paths.append(src_file_path)
        
        dst_file_path = os.path.join(dst_config_dir, dst_config_name_base)
        dst_file_rel_paths.append(dst_file_path)
        
        src_config_name_base = src_config_name

        dst_config_name = dst_config_name_base

        return src_file_rel_paths, dst_file_rel_paths, src_config_name_base, dst_config_name

    def check_clone_dst_file_rel_paths(self, dst_file_rel_paths):
        is_valid = True

        for file_rel_path in dst_file_rel_paths:
            file_path = os.path.join(self.base_path, file_rel_path)
            if os.path.exists(file_path):
                print("%s is already exists" % file_path)
                is_valid = False

        return is_valid

    def copy_config(self, src_config_dir, src_config_name, dst_config_dir, dst_config_name_base):
        src_file_rel_paths, dst_file_rel_paths, src_config_name_base, dst_config_name = self.get_clone_params(src_config_dir, src_config_name, dst_config_dir, dst_config_name_base)

        if debug_level >= 2:
            print(src_file_rel_paths)
            print(dst_file_rel_paths)
            print("")

        if not os.path.exists(dst_config_dir):
            os.mkdir(dst_config_dir)

        if self.check_clone_dst_file_rel_paths(dst_file_rel_paths):
            for idx, src_file_rel_path in enumerate(src_file_rel_paths):
                dst_file_rel_path = dst_file_rel_paths[idx]
                src_file_path = os.path.join(self.base_path, src_file_rel_path)
                dst_file_path = os.path.join(self.base_path, dst_file_rel_path)
                if os.path.isdir(src_file_path):
                    shutil.copytree(src_file_path, dst_file_path)
                else:
                    shutil.copy(src_file_path, dst_file_path)

            dst_config_file_dir = os.path.join(self.base_path, dst_config_dir, dst_config_name)
            self.update_project_base_dir(self.base_path, dst_config_file_dir)

            self.select_config(dst_config_dir, dst_config_name)

            return True, ("%s cloned %s has been created successfully." % (dst_config_name, os.path.splitext(src_config_name)[0]))

        else:
            return False, "Files already exist."

    def update_project_base_dir(self, base_dir: str, config_dir: str):
        """
        config_dir 하위 파일에서 set(PROJECT_BASE_DIR ...) 줄을 찾아서,
        base_dir까지의 상대 경로로 갱신합니다.
        """
        if debug_level >= 2:
            print(base_dir)
            print(config_dir)
            print("")

        base_dir = os.path.abspath(base_dir)
        for root, _, files in os.walk(config_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except (UnicodeDecodeError, PermissionError):
                    continue  # 텍스트 파일이 아니거나 접근 불가 시 무시

                modified = False
                new_lines = []
                for line in lines:
                    if "set(PROJECT_BASE_DIR" in line:
                        # 파일 위치에서 base_dir 로 가는 상대경로 계산
                        file_dir = os.path.dirname(fpath)
                        rel_path = os.path.relpath(base_dir, file_dir)
                        # CMake 경로 표기를 위해 역슬래시 → 슬래시 변환
                        rel_path = rel_path.replace(os.sep, "/")
                        newline = f'set(PROJECT_BASE_DIR "${{CMAKE_CURRENT_LIST_DIR}}/{rel_path}")\n'
                        new_lines.append(newline)
                        modified = True
                    else:
                        new_lines.append(line)

                if modified:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    print(f"Updated: {fpath}")

    def print_selection(self):
        selection = self.config_items[self.config_item_idx]
        print(selection)
        print("")

    def select_item(self, event):
        item = self.tv.focus()
        if item != '':
            self.config_item_idx = int(item)
            if debug_level >= 2:
                self.print_selection()

    def key_pressed(self, event):
        # print(event.keysym)
        if event.keysym == "Return":
            self.press_select()
        elif event.keysym == "Escape":
            self.quit()
        elif event.keysym == "Up":
            if self.config_item_idx > 0:
                self.config_item_idx -= 1
                self.tv.selection_set(self.config_item_idx)
                self.tv.see(self.config_item_idx)
                if debug_level >= 2:
                    self.print_selection()
        elif event.keysym == "Down":
            if self.config_item_idx < (self.config_len - 1):
                self.config_item_idx += 1
                self.tv.selection_set(self.config_item_idx)
                self.tv.see(self.config_item_idx)
                if debug_level >= 2:
                    self.print_selection()

    def press_select(self):
        if self.config_len > 0:
            if debug_level >= 1:
                print("Select config\n")
                self.print_selection()

            selection = self.config_items[self.config_item_idx]
            self.select_config(selection["dir"], selection["name"])

        self.quit()

    def press_copy(self):
        if self.config_len > 0:
            if debug_level >= 1:
                print("Copy config\n")
                self.print_selection()

            self.copy_dialog = copy_dialog(self)
            self.copy_dialog.grab_set()

    def press_copy_dialog_cancel(self):
        self.copy_dialog.destroy()
        self.deiconify()

    def press_copy_dialog_ok(self):
        result, message = self.copy_config(self.copy_dialog.src_config_dir, self.copy_dialog.src_config_name, self.copy_dialog.dst_config_dir, self.copy_dialog.dst_config_name_base)
        if result:
            messagebox.showinfo(
                title='Copy result',
                message="Copy succeeded",
            )
            self.copy_dialog.destroy()
            self.deiconify()
            self.quit()
        else:
            messagebox.showinfo(
                title='Copy result',
                message="Copy failed",
                detail=message
            )

if __name__ == '__main__':
    if 3 > len(sys.argv):
        # print_help()
        base_path = "."
        lib_rel_path = "lib"
    else:
        base_path = sys.argv[1]
        lib_rel_path = sys.argv[2]
    base_path = os.path.abspath(base_path)

    cs = confsel(base_path, lib_rel_path)
    cs.mainloop()

def configsel_command(
    base_path: Annotated[str, typer.Option("-b", "--base-path", help="Base path")] = ".",
    lib_rel_path: Annotated[str, typer.Option("-l", "--lib-path", help="Library relative path")] = "lib"
):
    """Launch config selector."""
    import os
    
    # Convert relative paths to absolute paths
    base_path = os.path.abspath(base_path)
    
    # Launch the GUI application
    app = confsel(base_path, lib_rel_path)
    app.mainloop()
