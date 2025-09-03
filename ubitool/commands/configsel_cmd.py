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

debug_level = 1

config_file_exts = (".cmake", ".mk", ".config")

# config_name_base
# config_name_variation
# config_name = <config_name_base>__<config_name_variation>
# config_extension
# config_file_name = <config_name>.<config_extension>
# config_dir
# config_file_path = <config_dir>/<config_file_name>

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
    print("    python %s <project base dir> <library relative dir>" % (sys.argv[0]))
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
    if sys.version_info.major >= 3:
        return open(fname, mode, encoding="UTF-8")
    else:
        return open(fname, mode)

class copy_dialog(tk.Toplevel):

    src_config_dir = "../app"
    src_config_file_name = "myapp"
    dst_config_dir = "../app"
    dst_config_name_base = "myapp_2"
    src_file_paths = []
    dst_file_paths = []

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
            self.src_config_file_name = selection["file_name"]
            src_file_paths, dst_file_paths, src_config_name_base, dst_config_name = self.parent.get_clone_params(self.src_config_dir, self.src_config_file_name, self.dst_config_dir, self.dst_config_name_base)
            self.src_config_name_base = src_config_name_base
            self.dst_config_name_base = src_config_name_base + "_2"

            self.variables['source'].set(self.src_config_name_base)
            self.variables['destination'].set(self.dst_config_name_base)

        src_file_paths, dst_file_paths, src_config_name_base, dst_config_name = self.parent.get_clone_params(self.src_config_dir, self.src_config_file_name, self.dst_config_dir, self.dst_config_name_base)

        if debug_level >= 2:
            print(src_file_paths)
            print(dst_file_paths)

        self.src_file_paths = src_file_paths
        self.dst_file_paths = dst_file_paths

        for row in self.tvl.get_children():
            self.tvl.delete(row)
        for row in self.tvr.get_children():
            self.tvr.delete(row)

        for idx, file_path in enumerate(src_file_paths):
            self.tvl.insert(parent='', index=idx, iid=idx, values=(file_path))
        for idx, file_path in enumerate(dst_file_paths):
            self.tvr.insert(parent='', index=idx, iid=idx, values=(file_path))

class confsel(tk.Tk):
    config_info_keyword = "ubinos_config_info {"
    cmake_inclucde_file_keyword = "include(${CMAKE_CURRENT_LIST_DIR}/"
    config_dir_names = ["app", "doc", "env", "config"]
    prj_dir_base = ".."
    lib_rel_dir = "library"
    make_file_name = "Makefile"

    config_items = []
    config_item_idx = 0
    config_item_len = 0

    def __init__(self, prj_dir_base, lib_rel_dir):
        super().__init__()

        self.prj_dir_base = prj_dir_base
        self.lib_rel_dir = lib_rel_dir

        if debug_level >= 1:
            print("Ubinos config selector")
            print("    base dir : %s" % self.prj_dir_base)
            print("    library dir : %s" % self.lib_rel_dir)
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
        config_dir, config_name = self.get_config_from_makefile(self.make_file_name)
        for conf in self.config_items:
            self.tv.insert(parent='', index=conf["index"], iid=conf["index"], values=(conf["index"], conf["project"], conf["name"], conf["dir"]))
            if config_dir == conf["dir"] and config_name == conf["name"]:
                self.config_item_idx = conf["index"]

        self.tv.selection_set(self.config_item_idx)
        self.tv.see(self.config_item_idx)

    def update_config_items(self):
        index = 0
        prjs = [{"name": ".", "dir": ".."}]
        lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)

        if os.path.exists(lib_dir):
            for file_name in sorted(os.listdir(lib_dir)):
                prj_dir = os.path.join(lib_dir, file_name)
                if os.path.isdir(prj_dir):
                    prjs += [{"name": file_name, "dir": prj_dir}]

        for prj in prjs:
            config_dirs = []
            for config_dir_name in self.config_dir_names:
                config_dir = pathlib.Path(os.path.join(prj["dir"], config_dir_name)).as_posix()
                if os.path.exists(config_dir) and os.path.isdir(config_dir):
                    config_dirs.append(config_dir)

            for config_dir in config_dirs:
                config_file_names = [file_name for file_name in sorted(os.listdir(config_dir)) if os.path.isfile(os.path.join(config_dir, file_name)) and file_name.endswith(config_file_exts)]
                if debug_level >= 3:
                    print(config_file_names)

                for config_file_name in config_file_names:
                    config_info = self.load_config_info(os.path.join(config_dir, config_file_name))
                    if config_info is not None and "build_type" in config_info:
                        config_name = os.path.splitext(config_file_name)[0]
                        self.config_items.append({"index": index, "project": prj["name"], "name": config_name, "dir": config_dir, "file_name": config_file_name})
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

    def get_cmake_include_file_names(self, config_dir, config_file_name):
        include_file_names = []
        config_file_path = os.path.join(config_dir, config_file_name)

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

    def copy_config_info(self, src_config_info, dst_config_name_base):
        src_config_name_base = src_config_info["name_base"]

        dst_config_info = copy.deepcopy(src_config_info)
        dst_config_info["name_base"] = dst_config_name_base

        if "include_files" in src_config_info:
            for idx, src_file_name in enumerate(src_config_info["include_files"]):
                dst_file_name = src_file_name.replace(src_config_name_base, dst_config_name_base, 1)
                dst_config_info["include_files"][idx] = dst_file_name

        return dst_config_info

    def create_makefile(self, make_file_path, config_dir, config_name):
        file = file_open(make_file_path, 'w+')
        file.write("CONFIG_DIR ?= %s\n" % config_dir)
        file.write("CONFIG_NAME ?= %s\n" % config_name)
        file.write("\n")
        file.write("include makefile.mk\n")
        file.write("\n")
        file.close()

    def get_config_from_makefile(self, make_file_path):
        config_dir = ""
        config_name = ""

        with file_open(make_file_path, 'r') as file:
            lines = file.readlines()
            file.close()
            for line in lines:
                keyword = "CONFIG_DIR"
                if config_dir == "" and line.startswith(keyword):
                    k_len = len(keyword)
                    k_idx = k_len
                    keyword = "="
                    k_idx = line[k_idx:].find(keyword)
                    if k_idx > -1:
                        k_idx += k_len + len(keyword)
                        config_dir = line[k_idx:].strip()

                keyword = "CONFIG_NAME"
                if config_name == "" and line.startswith(keyword):
                    k_len = len(keyword)
                    k_idx = k_len
                    keyword = "="
                    k_idx = line[k_idx:].find(keyword)
                    if k_idx > -1:
                        k_idx += k_len + len(keyword)
                        config_name = line[k_idx:].strip()

        return config_dir, config_name

    def select_config(self, make_file_path, config_dir, config_name):
        if not os.path.exists(make_file_path):
            self.create_makefile(make_file_path, config_dir, config_name)

        elif not os.path.isdir(make_file_path):
            file = file_open(make_file_path, 'r')
            file.seek(0, io.SEEK_END)
            file_len = file.tell()
            file.close()

            if file_len <= 0:
                self.create_makefile(make_file_path, config_dir, config_name)

            else:
                shutil.copyfile(make_file_path, make_file_path + ".bak")

                need_config_dir = True
                need_config_name = True

                file = file_open(make_file_path, 'r')
                lines = file.readlines()
                file.close()
                file = file_open(make_file_path, 'w+')
                for line in lines:
                    if line.startswith("CONFIG_DIR "):
                        file.write("CONFIG_DIR ?= %s\n" % config_dir)
                        need_config_dir = False
                    elif line.startswith("CONFIG_NAME "):
                        file.write("CONFIG_NAME ?= %s\n" % config_name)
                        need_config_name = False
                    else:
                        file.write(line)
                file.close()

                if need_config_dir:
                    file = file_open(make_file_path, 'r')
                    lines = file.readlines()
                    file.close()
                    file = file_open(make_file_path, 'w+')
                    for line in lines:
                        if need_config_dir and line.startswith("include makefile.mk"):
                            file.write("CONFIG_DIR ?= %s\n" % config_dir)
                            file.write("\n")
                            file.write("include makefile.mk\n")
                            need_config_dir = False
                        else:
                            file.write(line)
                    file.close()
                if need_config_name:
                    file = file_open(make_file_path, 'r')
                    lines = file.readlines()
                    file.close()
                    file = file_open(make_file_path, 'w+')
                    for line in lines:
                        if need_config_name and line.startswith("include makefile.mk"):
                            file.write("CONFIG_NAME ?= %s\n" % config_name)
                            file.write("\n")
                            file.write("include makefile.mk\n")
                            need_config_name = False
                        else:
                            file.write(line)
                    file.close()

    def get_clone_params(self, src_config_dir, src_config_file_name, dst_config_dir, dst_config_name_base):
        src_config_file_path = os.path.join(src_config_dir, src_config_file_name)
        src_config_info = self.load_config_info(src_config_file_path)
        src_file_paths = []

        src_config_name_base = src_config_info["name_base"]

        dst_config_file_name = src_config_file_name.replace(src_config_name_base, dst_config_name_base, 1)
        dst_config_name = os.path.splitext(dst_config_file_name)[0]
        dst_config_file_path = os.path.join(dst_config_dir, dst_config_file_name)
        dst_file_paths = []

        src_file_paths.append(src_config_file_path)
        dst_file_paths.append(dst_config_file_path)

        if "include_files" in src_config_info:
            for idx, src_file_name in enumerate(src_config_info["include_files"]):
                dst_file_name = src_file_name.replace(src_config_name_base, dst_config_name_base, 1)
                src_file_paths.append(os.path.join(src_config_dir, src_file_name))
                dst_file_paths.append(os.path.join(dst_config_dir, dst_file_name))

        cmake_include_file_names = self.get_cmake_include_file_names(src_config_dir, src_config_file_name)
        for src_file_name in cmake_include_file_names:
            dst_file_name = src_file_name.replace(src_config_name_base, dst_config_name_base, 1)
            src_file_paths.append(os.path.join(src_config_dir, src_file_name))
            dst_file_paths.append(os.path.join(dst_config_dir, dst_file_name))

        if (src_config_info is not None and
            (("app" in src_config_info and src_config_info["app"]) or
             ("doc" in src_config_info and src_config_info["doc"]) or
             ("include_sub_dir" in src_config_info and src_config_info["include_sub_dir"]))):
            src_config_app_path = os.path.join(src_config_dir, src_config_name_base)
            dst_config_app_path = os.path.join(dst_config_dir, dst_config_name_base)
            if os.path.exists(src_config_app_path):
                src_file_paths.append(src_config_app_path + "/")
                dst_file_paths.append(dst_config_app_path + "/")

        for idx in range(len(src_file_paths)):
            src_file_paths[idx] = pathlib.Path(src_file_paths[idx]).as_posix()
        for idx in range(len(dst_file_paths)):
            dst_file_paths[idx] = pathlib.Path(dst_file_paths[idx]).as_posix()

        return src_file_paths, dst_file_paths, src_config_name_base, dst_config_name

    def check_clone_dst_file_paths(self, dst_file_paths):
        is_valid = True

        for file_path in dst_file_paths:
            if os.path.exists(file_path):
                print("%s is already exists" % file_path)
                is_valid = False

        return is_valid

    def copy_config(self, make_file_path, src_config_dir, src_config_file_name, dst_config_dir, dst_config_name_base):
        src_file_paths, dst_file_paths, src_config_name_base, dst_config_name = self.get_clone_params(src_config_dir, src_config_file_name, dst_config_dir, dst_config_name_base)

        if debug_level >= 2:
            print(src_file_paths)
            print(dst_file_paths)
            print("")

        if not os.path.exists(dst_config_dir):
            os.mkdir(dst_config_dir)

        if self.check_clone_dst_file_paths(dst_file_paths):
            for idx, src_file_path in enumerate(src_file_paths):
                dst_file_path = dst_file_paths[idx]
                if os.path.isdir(src_file_path):
                    shutil.copytree(src_file_path, dst_file_path)
                else:
                    file = file_open(src_file_path, 'r')
                    lines = file.readlines()
                    file.close()
                    file = file_open(dst_file_path, 'w+')

                    for line in lines:
                        written = False

                        keyword = "ubinos_config_info"
                        k_idx = line.find(keyword)
                        if not written and k_idx > -1:
                            k_idx = k_idx + len(keyword)
                            config_info_idx = line[k_idx:].find("{")
                            tmp_config_info = json.loads(line[k_idx + config_info_idx:])
                            dst_config_info = self.copy_config_info(tmp_config_info, dst_config_name_base)
                            new_line = line[:k_idx] + " " + json.dumps(dst_config_info) + "\n"
                            file.write(new_line)
                            written = True

                        keyword = "set(APP__NAME"
                        k_idx = line.find(keyword)
                        if not written and k_idx > -1:
                            k_idx = k_idx + len(keyword)
                            new_line = line[:k_idx] + line[k_idx:].replace(src_config_name_base, dst_config_name_base, 1)
                            file.write(new_line)
                            written = True

                        keyword = "APP__NAME = "
                        k_idx = line.find(keyword)
                        if not written and k_idx > -1:
                            k_idx = k_idx + len(keyword)
                            new_line = line[:k_idx] + line[k_idx:].replace(src_config_name_base, dst_config_name_base, 1)
                            file.write(new_line)
                            written = True

                        keyword = "include(${CMAKE_CURRENT_LIST_DIR}"
                        k_idx = line.find(keyword)
                        if not written and k_idx > -1:
                            k_idx = k_idx + len(keyword)
                            new_line = line[:k_idx] + line[k_idx:].replace(src_config_name_base, dst_config_name_base, 1)
                            file.write(new_line)
                            written = True

                        keyword = ("${CMAKE_CURRENT_LIST_DIR}/%s" % src_config_name_base)
                        k_idx = line.find(keyword)
                        if not written and k_idx > -1:
                            new_line = line[:k_idx] + line[k_idx:].replace(src_config_name_base, dst_config_name_base, 1)
                            file.write(new_line)
                            written = True

                        if not written:
                            file.write(line)

                    file.close()

            self.select_config(make_file_path, dst_config_dir, dst_config_name)

            return True, ("%s cloned %s has been created successfully." % (dst_config_name, os.path.splitext(src_config_file_name)[0]))

        else:
            return False, "Files already exist."

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
            self.select_config(self.make_file_name, selection["dir"], selection["name"])

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
        result, message = self.copy_config(self.make_file_name, self.copy_dialog.src_config_dir, self.copy_dialog.src_config_file_name, self.copy_dialog.dst_config_dir, self.copy_dialog.dst_config_name_base)
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
        print_help()
    else:
        if sys.argv[1] == "--lib-absolute" and 4 <= len(sys.argv):
            prj_dir_base = sys.argv[2]
            lib_rel_dir = os.path.relpath(sys.argv[3], os.path.abspath(prj_dir_base))
        else:
            prj_dir_base = sys.argv[1]
            lib_rel_dir = sys.argv[2]

        csel = confsel(prj_dir_base, lib_rel_dir)
        csel.mainloop()

    # csel = confsel("..", "library")
    # csel.mainloop()
