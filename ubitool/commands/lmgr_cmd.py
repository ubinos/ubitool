#! /usr/bin/python

#
# Copyright (c) 2024 Sung Ho Park and CSOS
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
import subprocess
import platform

from tkinter import ttk
from tkinter import Toplevel
from tkinter import messagebox

from ttkwidgets import CheckboxTreeview

from collections import Counter

debug_level = 0

true_string = "O"
false_string = "X"
unknown_string = "-"

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

class run_dialog(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.runable = True
        self.running = False

        self.title("Ubinos library command")

        set_dialog_geometry_center(parent, self, 1100, 600)

        self.transient(self.parent)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.columnconfigure(0, weight=1)

        self.bind("<Key>", self.key_pressed)

        ##
        self.command_text_var = ""

        frame_command_text = tk.Frame(self)
        frame_command_text.grid(row=0, column=0, sticky="nsew")
        frame_command_text.rowconfigure(0, weight=1)
        frame_command_text.columnconfigure(0, weight=1)

        self.command_text = tk.Text(frame_command_text, height=1)
        self.command_text.grid(row=0, column=0, sticky="nsew")
        self.command_text.config(state=tk.DISABLED)

        sb = tk.Scrollbar(frame_command_text, orient=tk.VERTICAL)
        sb.grid(row=0, column=1, sticky="ns")
        self.command_text.config(yscrollcommand=sb.set)
        sb.config(command=self.command_text.yview)

        ##
        self.result_text_var = ""

        frame_result_text = tk.Frame(self)
        frame_result_text.grid(row=1, column=0, sticky="nsew")
        frame_result_text.rowconfigure(0, weight=1)
        frame_result_text.columnconfigure(0, weight=1)

        self.result_text = tk.Text(frame_result_text, height=1)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        self.result_text.config(state=tk.DISABLED)

        sb = tk.Scrollbar(frame_result_text, orient=tk.VERTICAL)
        sb.grid(row=0, column=1, sticky="ns")
        self.result_text.config(yscrollcommand=sb.set)
        sb.config(command=self.result_text.yview)

        ##
        frame_bt = tk.Frame(self)
        frame_bt.grid(row=2, column=0, sticky="nsew", padx=10, pady=20)

        self.run_button = tk.Button(frame_bt, text="Run", command=self.parent.press_run_dialog_run)
        self.run_button.pack(side=tk.LEFT, padx=10, pady=0)

        self.close_button = tk.Button(frame_bt, text="Close", command=self.parent.press_run_dialog_close)
        self.close_button.pack(side=tk.RIGHT, padx=10, pady=0)

        ##
        self.update_command_text(True)
        self.update_result_text(True)
        self.update_buttons(True)

    def key_pressed(self, event):
        # print(event.keysym)
        if event.keysym == "Escape":
            self.close()

    def close(self):
        if not self.running:
            self.parent.press_run_dialog_close()

    def update_command_text(self, init=False):
        self.command_text.config(state=tk.NORMAL)
        self.command_text.delete(1.0, tk.END)
        self.command_text.insert(tk.END, self.command_text_var)
        last_line_index = self.command_text.index("end-1c linestart")
        self.command_text.see(last_line_index)
        self.command_text.config(state=tk.DISABLED)
        self.update()

    def update_result_text(self, init=False):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, self.result_text_var)
        last_line_index = self.result_text.index("end-1c linestart")
        self.result_text.see(last_line_index)
        self.result_text.config(state=tk.DISABLED)
        self.update()

    def update_buttons(self, init=False):
        if not self.runable or self.running:
            self.run_button.config(state=tk.DISABLED)
        else:
            self.run_button.config(state=tk.NORMAL)

        if self.running:
            self.close_button.config(state=tk.DISABLED)
        else:
            self.close_button.config(state=tk.NORMAL)
        self.update()

    def set_command(self, commands):
        for cmd in commands:
            self.command_text_var += (cmd + "\n")
        self.update_command_text()

    def clear_result(self):
        self.result_text_var = ""
        self.update_result_text()

    def append_result(self, result):
        self.result_text_var += result
        self.update_result_text()

    def set_runable(self, runable):
        self.runable = runable
        self.update_buttons()

    def set_running(self, running):
        self.running = running
        self.update_buttons()

class libmgr(tk.Tk):
    def __init__(self, prj_dir_base, lib_rel_dir):
        super().__init__()

        self.prj_dir_base = prj_dir_base
        self.lib_rel_dir = lib_rel_dir
        self.lib_list_default_file_name = "liblist_default.json"
        self.lib_list_default_file_rel_dir = os.path.join(lib_rel_dir, "ubinos", "make")
        self.lib_list_custom_file_name = "liblist.json"
        self.lib_list_custom_file_rel_dir = "make"

        self.lib_items = []
        self.lib_items_updatable = []
        self.lib_item_idx = 0
        self.lib_item_idx_prev = 0
        self.git_commands = []

        self.hide_checkbutton_value = tk.StringVar(value=false_string)

        self.run_command_type = ""

        if debug_level >= 1:
            print("Ubinos library manager")
            print("    base dir : %s" % self.prj_dir_base)
            print("    library dir : %s" % self.lib_rel_dir)
            print("")

        self.title("Ubinos library manager")

        set_geometry_center(self, win_width, win_height)

        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.bind("<Key>", self.key_pressed)

        ##
        frame_tv = tk.Frame(self)
        frame_tv.grid(row=0, column=0, sticky="nsew")
        frame_tv.rowconfigure(0, weight=1)
        frame_tv.columnconfigure(0, weight=1)

        self.tv = CheckboxTreeview(frame_tv)
        self.tv["columns"] = ("I", "M", "U", "S", "L", "Name", "URL", "Branch", "Tags", "Commit")
        self.tv.pack(fill="both", expand=True)
        self.tv.grid(row=0, column=0, sticky="nsew")
        self.tv.tag_configure("selected", background="palegoldenrod")
        self.tv.tag_configure("checked", foreground="red")

        sb = tk.Scrollbar(frame_tv, orient=tk.VERTICAL)
        sb.grid(row=0, column=1, sticky="ns")
        self.tv.config(yscrollcommand=sb.set)
        sb.config(command=self.tv.yview)

        self.tv.bind("<ButtonRelease-1>", self.button_release_1)

        self.tv.heading("#0", text="Index") # Index
        self.tv.column("#0", width=60)
        self.tv.heading("I", text="I", anchor=tk.CENTER) # Installed
        self.tv.column("I", width=20, anchor=tk.CENTER)
        self.tv.heading("M", text="M", anchor=tk.CENTER) # Modified
        self.tv.column("M", width=20, anchor=tk.CENTER)
        self.tv.heading("U", text="U", anchor=tk.CENTER) # Updatable
        self.tv.column("U", width=20, anchor=tk.CENTER)
        self.tv.heading("S", text="S", anchor=tk.CENTER) # Switchable
        self.tv.column("S", width=20, anchor=tk.CENTER)
        self.tv.heading("L", text="L", anchor=tk.CENTER) # Listed
        self.tv.column("L", width=20, anchor=tk.CENTER)
        self.tv.heading("Name", text="Name")
        self.tv.column("Name", width=200)
        self.tv.heading("URL", text="URL")
        self.tv.column("URL", width=370)
        self.tv.heading("Branch", text="Branch")
        self.tv.column("Branch", width=100)
        self.tv.heading("Tags", text="Tags")
        self.tv.column("Tags", width=80)
        self.tv.heading("Commit", text="Commit")
        self.tv.column("Commit", width=70)

        #
        frame_description_text = tk.Frame(self)
        frame_description_text.grid(row=1, column=0, sticky="nsew")
        frame_description_text.rowconfigure(0, weight=1)
        frame_description_text.columnconfigure(0, weight=1)

        self.description_text = tk.Text(frame_description_text, height=1)
        self.description_text.grid(row=0, column=0, sticky="nsew")
        self.description_text.config(state=tk.DISABLED)

        sb = tk.Scrollbar(frame_description_text, orient=tk.VERTICAL)
        sb.grid(row=0, column=1, sticky="ns")
        self.description_text.config(yscrollcommand=sb.set)
        sb.config(command=self.description_text.yview)

        ##
        frame_labels = tk.Frame(self)
        frame_labels.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        self.labels = tk.Label(frame_labels, text="I: Installed,  M: Modified,  U: Updatable,  S: Switchable,  L: Listed in liblist.json,  O: True,  X: False,  -: Unknown")
        self.labels.pack(side=tk.LEFT, padx=4, pady=0)

        ##
        frame_bt1 = tk.Frame(self)
        frame_bt1.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        self.hide_checkbutton = ttk.Checkbutton(frame_bt1,
                                                text="Hide ubinos default library list",
                                                command=self.hide_checkbutton_changed,
                                                variable=self.hide_checkbutton_value,
                                                onvalue=true_string,
                                                offvalue=false_string)
        self.hide_checkbutton.pack(side=tk.LEFT, padx=4, pady=0)

        ##
        frame_bt2 = tk.Frame(self)
        frame_bt2.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

        self.install_button = tk.Button(frame_bt2, text="Install", command=self.press_install)
        self.install_button.pack(side=tk.LEFT, padx=4, pady=0)

        self.uninstall_button = tk.Button(frame_bt2, text="Uninstall", command=self.press_uninstall)
        self.uninstall_button.pack(side=tk.LEFT, padx=4, pady=0)

        self.reset_button = tk.Button(frame_bt2, text="Reset", command=self.press_reset)
        self.reset_button.pack(side=tk.LEFT, padx=4, pady=0)

        self.update_button = tk.Button(frame_bt2, text="Update", command=self.press_update)
        self.update_button.pack(side=tk.LEFT, padx=4, pady=0)

        self.switch_button = tk.Button(frame_bt2, text="switch", command=self.press_switch)
        self.switch_button.pack(side=tk.LEFT, padx=4, pady=0)

        self.close_button = tk.Button(frame_bt2, text="Close", command=quit)
        self.close_button.pack(side=tk.RIGHT, padx=4, pady=0)

        self.check_all_button = tk.Button(frame_bt2, text="Fetch and check for update all", command=self.press_check)
        self.check_all_button.pack(side=tk.RIGHT, padx=40, pady=0)

        self.update_lib_items()

    def update_lib_items(self):
        exist_lib_items = []
        temp_lib_items = []

        exist_lib_list = self.get_exist_lib_list()
        for lib in exist_lib_list:
            if not "upstreams" in lib:
                lib["upstreams"] = []
            if not "description" in lib:
                lib["description"] = ""
            lib["installed"] = true_string if self.is_git_repo(lib["name"]) else unknown_string
            lib["modified"] = self.git_check_modified(lib["name"])
            lib["listed"] = false_string
            if lib["name"] == "ubinos":
                lib["uninstallable"] = false_string
            elif self.is_git_repo(lib["name"]):
                lib["uninstallable"] = true_string
            else:
                lib["uninstallable"] = unknown_string
            lib["installable"] = false_string
            lib["switchable"] = false_string
            lib["updatable"] = self.get_updatable(lib)
            exist_lib_items.append(lib)

        lib_list = []

        hide_checkbutton_value_string = self.hide_checkbutton_value.get()
        if hide_checkbutton_value_string != true_string:
            lib_list_default_file_path = os.path.join(self.prj_dir_base, self.lib_list_default_file_rel_dir, self.lib_list_default_file_name)
            if os.path.exists(lib_list_default_file_path):
                lib_list = self.load_lib_list(lib_list_default_file_path)

        lib_list_custom_file_path = os.path.join(self.prj_dir_base, self.lib_list_custom_file_rel_dir, self.lib_list_custom_file_name)
        if os.path.exists(lib_list_custom_file_path):
            lib_list_custom = self.load_lib_list(lib_list_custom_file_path)
            if lib_list_custom != None:
                lib_list += lib_list_custom

        for item in lib_list:
            is_exist = False
            lib = {}
            lib["name"] = item["name"]
            lib["url"] = item["url"]
            lib["branch"] = ""
            lib["tags"] = [""]
            lib["commit"] = ""
            lib["upstreams"] = []
            lib["description"] = ""
            if item["branch_tag_commit"]["type"] == "branch":
                lib["branch"] = item["branch_tag_commit"]["name"]
            elif item["branch_tag_commit"]["type"] == "tag":
                lib["tags"] = [item["branch_tag_commit"]["name"]]
            elif item["branch_tag_commit"]["type"] == "commit":
                lib["commit"] = item["branch_tag_commit"]["name"]
            if "upstreams" in item:
                lib["upstreams"] = item["upstreams"]
            if "description" in item:
                lib["description"] = item["description"]

            for exist_lib in exist_lib_items:
                if self.is_equal_lib(lib, exist_lib):
                    exist_lib["listed"] = true_string
                    exist_lib["description"] = lib["description"]
                    is_exist = True
                    break
            if is_exist:
                continue
            else:
                lib["installed"] = false_string
                lib["modified"] = unknown_string
                lib["listed"] = true_string
                lib["uninstallable"] = false_string
                lib["installable"] = true_string
                for eitm in exist_lib_items:
                    if eitm["name"] == lib["name"]:
                            lib["installable"] = false_string
                            break
                lib["switchable"] = false_string
                for eitm in exist_lib_items:
                    if (eitm["name"] == lib["name"] and eitm["url"] == lib["url"]):
                        if (eitm["installed"] == true_string):
                            lib["switchable"] = true_string
                lib["updatable"] = unknown_string
                temp_lib_items.append(lib)

        temp_lib_items += exist_lib_items
        self.lib_items = sorted(temp_lib_items, key=lambda x:
                                (x["name"], x["url"], x["branch"], x["commit"]))

        self.tv.delete(*self.tv.get_children())
        for index, lib_item in enumerate(self.lib_items):
            lib_item["index"] = index
            self.tv.insert(parent="", index=index, iid=index,
                            text=f"{index + 1}",
                            values=(
                                lib_item["installed"],
                                lib_item["modified"],
                                lib_item["updatable"],
                                lib_item["switchable"],
                                lib_item["listed"],
                                lib_item["name"],
                                lib_item["url"],
                                lib_item["branch"],
                                ", ".join(lib_item["tags"]),
                                lib_item["commit"]
                                )
                            )

        if debug_level >= 3:
            for lib in self.lib_items:
                print(lib)
            print("")

        self.update_selection()

    def update_selection(self):
        lib_items_last_index = len(self.lib_items) - 1
        if self.lib_item_idx > lib_items_last_index:
            self.lib_item_idx = lib_items_last_index
        if self.lib_item_idx_prev > lib_items_last_index:
            self.lib_item_idx_prev = lib_items_last_index

        include_modified = False
        include_not_modified = False
        include_installable = False
        include_not_installable = False
        include_uninstallable = False
        include_not_uninstallable = False
        include_updatable = False
        include_not_updatable = False
        include_switchable = False
        include_not_switchable = False
        checked_items_indexs = self.tv.get_checked()

        for index in checked_items_indexs:
            item = self.lib_items[int(index)]

            if item["modified"] == true_string:
                include_modified = True
            else:
                include_not_modified = True

            if item["installable"] == true_string:
                include_installable = True
            else:
                include_not_installable = True

            if item["uninstallable"] == true_string:
                include_uninstallable = True
            else:
                include_not_uninstallable = True

            if item["updatable"] == true_string:
                include_updatable = True
            else:
                include_not_updatable = True

            if item["switchable"] == true_string:
                include_switchable = True
            else:
                include_not_switchable = True

        if include_installable and not include_not_installable:
            self.install_button.config(state=tk.NORMAL)
        else:
            self.install_button.config(state=tk.DISABLED)

        if include_uninstallable and not include_not_uninstallable:
            self.uninstall_button.config(state=tk.NORMAL)
        else:
            self.uninstall_button.config(state=tk.DISABLED)

        if include_modified and not include_not_modified:
            self.reset_button.config(state=tk.NORMAL)
        else:
            self.reset_button.config(state=tk.DISABLED)

        if include_updatable and not include_not_updatable:
            self.update_button.config(state=tk.NORMAL)
        else:
            self.update_button.config(state=tk.DISABLED)

        if include_switchable and not include_not_switchable:
            self.switch_button.config(state=tk.NORMAL)
        else:
            self.switch_button.config(state=tk.DISABLED)

        self.check_all_button.config(state=tk.NORMAL)

        index = self.lib_item_idx_prev
        tags = self.tv.item(index, "tag")
        if "selected" in tags:
            self.tv.tag_del(index, "selected")

        index = self.lib_item_idx
        tags = self.tv.item(index, "tag")
        if not "selected" in tags:
            self.tv.tag_add(index, "selected")
        self.tv.selection_set(index)
        self.tv.see(index)
        self.tv.see(index) # There are times when this function should not be called once. If you call it twice, it always works normally. It was assumed to be a library bug.

        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, self.lib_items[self.lib_item_idx]["description"])
        self.description_text.config(state=tk.DISABLED)
        self.update()

    def load_lib_list(self, file_path):
        lib_list = []
        try:
            with file_open(file_path, "r") as file:
                lib_list = json.load(file)
        except Exception as e:
            print(f"Exception occurred when reading {file_path} .", e)
        return lib_list

    def get_exist_lib_list(self):
        lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
        exist_lib_list = []
        for name in os.listdir(lib_dir):
            if os.path.isdir(os.path.join(lib_dir, name)):
                url, upstreams = self.git_local_url(name)
                branch, tags, commit = self.git_local_branch_tag_commit(name)
                lib = {
                    "name": name,
                    "url": url,
                    "branch": branch,
                    "tags": tags,
                    "commit": commit,
                    "upstreams": upstreams,
                    "description": ""
                    }
                if debug_level >= 3:
                    print(lib)
                exist_lib_list.append(lib)
        return exist_lib_list

    def is_equal_lib(self, lib1, lib2):
        equal = False
        if lib1["name"] == lib2["name"] and lib1["url"] == lib2["url"]:
            while True:
                if lib1["branch"] != "" and lib2["branch"] != "":
                    if lib1["branch"] == lib2["branch"]:
                        equal = True
                    break
                if lib1["commit"] != "" and lib2["commit"] != "":
                    if lib1["commit"] == lib2["commit"]:
                        equal = True
                    break

                if set(lib1["tags"]).intersection(lib2["tags"]):
                    equal = True
                break
        return equal

    def is_checked_multiple(self):
        checked_items_indexs = self.tv.get_checked()
        multiple_check_items = []
        for idx1 in checked_items_indexs:
            itm1 = self.lib_items[int(idx1)]
            for idx2 in checked_items_indexs:
                itm2 = self.lib_items[int(idx2)]
                if idx1 != idx2 and itm1["name"] == itm2["name"]:
                    if not itm1["name"] in multiple_check_items:
                        multiple_check_items.append(itm1["name"])

        if len(multiple_check_items) > 0:
            message = "Libraries with the same name were checked multiple times.\n"
            for i, name in enumerate(multiple_check_items):
                if i == 0:
                    message += f"({name}"
                else:
                    message += f", {name}"
            message += ")"
            messagebox.showinfo(
                title="Error",
                message=message,
            )
            return True
        else:
            return False

    def get_updatable(self, lib):
        for item in self.lib_items_updatable:
            if self.is_equal_lib(lib, item):
                return item["updatable"]
        return unknown_string

    def print_selection(self):
        selection = self.lib_items[self.lib_item_idx]
        print(selection)
        print("")

    def select_item(self, index):
        self.lib_item_idx_prev = self.lib_item_idx
        self.lib_item_idx = index
        self.update_selection()
        if debug_level >= 3:
            self.print_selection()

    def button_release_1(self, event):
        item = self.tv.focus()
        if item != "":
            self.select_item(int(item))

    def key_pressed(self, event):
        # print(event.keysym)
        if event.keysym == "Escape":
            self.quit()
        elif event.keysym == "Up":
            self.tv.focus_set()
            if self.lib_item_idx > 0:
                self.select_item(self.lib_item_idx - 1)
        elif event.keysym == "Down":
            self.tv.focus_set()
            if self.lib_item_idx < (len(self.lib_items) - 1):
                self.select_item(self.lib_item_idx + 1)
        elif event.keysym == "space":
            tags = self.tv.item(self.lib_item_idx, "tag")
            if "checked" in tags:
                self.tv.tag_del(self.lib_item_idx, "checked")
                self.tv.tag_add(self.lib_item_idx, "unchecked")
            elif "unchecked" in tags:
                self.tv.tag_del(self.lib_item_idx, "unchecked")
                self.tv.tag_add(self.lib_item_idx, "checked")
            self.update_selection()

    def hide_checkbutton_changed(self):
        self.update_lib_items()

    def press_install(self):
        if len(self.lib_items) > 0:
            if debug_level >= 1:
                print("Install library\n")
                self.print_selection()

            if self.is_checked_multiple():
                return

            checked_items_indexs = self.tv.get_checked()
            if len(checked_items_indexs) > 0:
                lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
                self.run_command_type = "install"
                self.git_commands = []
                for index in checked_items_indexs:
                    selection = self.lib_items[int(index)]
                    target_dir = os.path.join(lib_dir, selection["name"])
                    source_url = selection["url"]
                    source_branch = selection["branch"]
                    source_tag = selection["tags"][0]
                    source_commit = selection["commit"]
                    if source_branch != "":
                        self.git_commands.append(f"git submodule add -f -b {source_branch} {source_url} {target_dir}")
                    elif source_tag != "":
                        self.git_commands.append(f"git submodule add -f {source_url} {target_dir}")
                        self.git_commands.append(f"cd {target_dir} && git checkout -f {source_tag}")
                    elif source_commit != "":
                        self.git_commands.append(f"git submodule add -f {source_url} {target_dir}")
                        self.git_commands.append(f"cd {target_dir} && git checkout -f {source_commit}")
                    else:
                        self.git_commands.append(f"git submodule add -f {source_url} {target_dir}")
                    for upstream in selection["upstreams"]:
                        uname = upstream["name"]
                        uurl = upstream["url"]
                        self.git_commands.append(f"cd {target_dir} && git remote add {uname} {uurl}")
                self.run_dialog = run_dialog(self)
                self.run_dialog.title("Install library commands")
                self.run_dialog.set_command(self.git_commands)
                self.run_dialog.grab_set()

    def get_platform_rmdir_command(self, dir):
        platform_rmdir_command = ""
        if platform.system() == "Windows":
            platform_rmdir_command = f"if exist {dir} rmdir /s /q {dir}"
        elif platform.system() == "Linux":
            platform_rmdir_command = f"rm -rf {dir}"
        elif platform.system() == "Darwin":
            platform_rmdir_command = f"rm -rf {dir}"
        return platform_rmdir_command

    def press_uninstall(self):
        if len(self.lib_items) > 0:
            if debug_level >= 1:
                print("Uninstall library\n")
                self.print_selection()

            if self.is_checked_multiple():
                return

            checked_items_indexs = self.tv.get_checked()
            if len(checked_items_indexs) > 0:
                lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
                self.run_command_type = "uninstall"
                self.git_commands = []
                for index in checked_items_indexs:
                    selection = self.lib_items[int(index)]
                    target_dir = os.path.join(lib_dir, selection["name"])
                    dot_git_dir = os.path.join(self.prj_dir_base, ".git", "modules", self.lib_rel_dir, selection["name"])
                    if  self.is_git_repo(selection["name"]):
                        self.git_commands.append(f"git submodule deinit -f {target_dir}")
                        self.git_commands.append(self.get_platform_rmdir_command(dot_git_dir))
                        self.git_commands.append(f"git rm -f {target_dir}")
                        self.git_commands.append(self.get_platform_rmdir_command(target_dir))
                        # dot_gitmodule_path = os.path.join(self.prj_dir_base, ".gitmodules")
                        # target_base_name = os.path.basename(target_dir)
                        # self.git_commands.append(f"git config -f {dot_gitmodule_path} --remove-section submodule.{target_base_name} || true")
                    else:
                        self.git_commands.append(self.get_platform_rmdir_command(dot_git_dir))
                        self.git_commands.append(self.get_platform_rmdir_command(target_dir))
                self.run_dialog = run_dialog(self)
                self.run_dialog.title("Uninstall library commands")
                self.run_dialog.set_command(self.git_commands)
                self.run_dialog.grab_set()

    def press_switch(self):
        if len(self.lib_items) > 0:
            if debug_level >= 1:
                print("Switch library\n")
                self.print_selection()

            if self.is_checked_multiple():
                return

            checked_items_indexs = self.tv.get_checked()
            if len(checked_items_indexs) > 0:
                lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
                self.run_command_type = "switch"
                self.git_commands = []
                for index in checked_items_indexs:
                    selection = self.lib_items[int(index)]
                    target_dir = os.path.join(lib_dir, selection["name"])
                    source_btc_name = ""
                    if selection["branch"] != "":
                        source_btc_name = selection["branch"]
                    if selection["tags"][0] != "":
                        source_btc_name = selection["tags"][0]
                    if selection["commit"] != "":
                        source_btc_name = selection["commit"]
                    if source_btc_name != "":
                        self.git_commands.append(f"cd {target_dir} && git checkout -f {source_btc_name}")
                self.run_dialog = run_dialog(self)
                self.run_dialog.title("Switch library commands")
                self.run_dialog.set_command(self.git_commands)
                self.run_dialog.grab_set()

    def press_reset(self):
        if len(self.lib_items) > 0:
            if debug_level >= 1:
                print("Reset library\n")
                self.print_selection()

            if self.is_checked_multiple():
                return

            checked_items_indexs = self.tv.get_checked()
            if len(checked_items_indexs) > 0:
                lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
                self.run_command_type = "reset"
                self.git_commands = []
                for index in checked_items_indexs:
                    selection = self.lib_items[int(index)]
                    target_dir = os.path.join(lib_dir, selection["name"])
                    self.git_commands.append(f"cd {target_dir} && git reset --hard HEAD")
                    self.git_commands.append(f"cd {target_dir} && git clean -fd")
                self.run_dialog = run_dialog(self)
                self.run_dialog.title("Reset library commands")
                self.run_dialog.set_command(self.git_commands)
                self.run_dialog.grab_set()

    def press_check(self):
        if len(self.lib_items) > 0:
            if debug_level >= 1:
                print("Check library updatable all\n")
                self.print_selection()

            self.lib_items_updatable = []
            for lib_item in self.lib_items:
                if lib_item["installed"] == true_string:
                    item_updatable = {"name": lib_item["name"], "url": lib_item["url"],
                                      "branch": lib_item["branch"], "tags": lib_item["tags"], "commit": lib_item["commit"]}
                    if debug_level >= 2:
                        print(item_updatable)
                    if self.git_check_updatable(lib_item["name"]):
                        item_updatable["updatable"] = true_string
                    else:
                        item_updatable["updatable"] = false_string
                    self.lib_items_updatable.append(item_updatable)

            if debug_level >= 2:
                print(self.lib_items_updatable)

            messagebox.showinfo(
                title="Result",
                message="Done",
            )

            self.update_lib_items()

    def press_update(self):
        if len(self.lib_items) > 0:
            if debug_level >= 1:
                print("Update library\n")
                self.print_selection()

            if self.is_checked_multiple():
                return

            checked_items_indexs = self.tv.get_checked()
            if len(checked_items_indexs) > 0:
                lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
                self.run_command_type = "update"
                self.git_commands = []
                for index in checked_items_indexs:
                    selection = self.lib_items[int(index)]
                    target_dir = os.path.join(lib_dir, selection["name"])
                    self.git_commands.append(f"cd {target_dir} && git pull")
                self.run_dialog = run_dialog(self)
                self.run_dialog.title("Update library commands")
                self.run_dialog.set_command(self.git_commands)
                self.run_dialog.grab_set()

    def press_run_dialog_close(self):
        self.run_command_type = ""
        self.run_dialog.destroy()
        self.deiconify()

    def press_run_dialog_run(self):
        self.run_dialog.set_running(True)
        self.run_dialog.clear_result()

        result = True
        for cmd in self.git_commands:
            run_result = self.run_git_command_with_dialog(cmd)
            if not run_result:
                result = False
                if self.run_command_type != "uninstall":
                    break

        if result:
            messagebox.showinfo(
                title="Result",
                message="Succeeded",
            )
        else:
            messagebox.showinfo(
                title="Result",
                message="Failed",
            )

        self.run_dialog.set_running(False)
        self.run_dialog.set_runable(False)

        if self.run_command_type == "update":
            self.press_check()

        self.update_lib_items()

        self.run_command_type = ""

    def run_git_command_with_dialog(self, command):
        result = False
        self.run_dialog.append_result(command + "\n")
        try:
            if debug_level >= 3:
                new_env = os.environ.copy()
                # new_env["GIT_TRACE"] = "1"
                # new_env["GIT_SSH_COMMAND"] = "ssh -vvv"
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=1, universal_newlines=True, env=new_env)
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=1, universal_newlines=True)
            for line in process.stdout:
                self.run_dialog.append_result(line)
            for line in process.stderr:
                self.run_dialog.append_result(line)
            process.wait()

            if process.returncode == 0:
                result = True
        except Exception as e:
            print("Exception occurred.", e)

        return result

    def run_git_command(self, directory, command):
        result = None

        try:
            result = subprocess.run(command, cwd=directory, capture_output=True, text=True, check=True, encoding='utf-8')
        except Exception as e:
            if debug_level >= 1:
                print("Exception occurred.", e)

        return result

    def is_git_repo(self, name):
        lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
        target_dir = os.path.join(lib_dir, name)
        if os.path.exists(os.path.join(target_dir, ".git")):
            return True
        else:
            return False


    def git_checkout_branch(self, name, branch):
        lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
        target_dir = os.path.join(lib_dir, name)
        if self.is_git_repo(name):
            git_command = ["git", "checkout", "-f", branch]
            result = self.run_git_command(target_dir, git_command)
            if debug_level >= 2:
                print(result)

            if result != None and result.returncode == 0:
                return True
        return False

    def git_check_updatable(self, name):
        lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
        target_dir = os.path.join(lib_dir, name)
        if self.is_git_repo(name):
            git_command = ["git", "fetch"]
            result = self.run_git_command(target_dir, git_command)
            if debug_level >= 2:
                print(result)

            branch, _, _ = self.git_local_branch_tag_commit(name)
            if branch == "":
                return False

            git_command = ["git", "log", f"{branch}..origin/{branch}"]
            result = self.run_git_command(target_dir, git_command)
            if debug_level >= 2:
                print(result)

            if result != None and result.stdout.strip():
                return True
            else:
                return False

    def git_check_modified(self, name):
        lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
        target_dir = os.path.join(lib_dir, name)
        if self.is_git_repo(name):
            git_command = ["git", "status", "--porcelain"]
            result = self.run_git_command(target_dir, git_command)
            if debug_level >= 2:
                print(result)
            if result != None and result.stdout.strip():
                return true_string
            else:
                return false_string
        return unknown_string

    def git_local_branch_tag_commit(self, name):
        lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
        target_dir = os.path.join(lib_dir, name)
        branch = ""
        tags = []
        commit = ""
        if self.is_git_repo(name):
            git_command = ["git", "symbolic-ref", "--quiet", "HEAD"]
            result = self.run_git_command(target_dir, git_command)
            if debug_level >= 2:
                print(result)
            if result != None and result.returncode == 0:
                git_command = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
                result = self.run_git_command(target_dir, git_command)
                if debug_level >= 2:
                    print(result)
                if result != None:
                   branch = result.stdout.strip()

            git_command = ["git", "tag", "--points-at", "HEAD"]
            result = self.run_git_command(target_dir, git_command)
            if debug_level >= 2:
                print(result)
            if result != None and result.returncode == 0:
                tags = result.stdout.strip().split('\n')

            git_command = ["git", "rev-parse", "--verify", "HEAD"]
            result = self.run_git_command(target_dir, git_command)
            if debug_level >= 2:
                print(result)
            if result != None and result.returncode == 0:
                commit = result.stdout.strip()

        return branch, tags, commit

    def git_local_url(self, name):
        lib_dir = os.path.join(self.prj_dir_base, self.lib_rel_dir)
        target_dir = os.path.join(lib_dir, name)
        url = unknown_string
        upstreams = []
        if self.is_git_repo(name):
            git_command = ["git", "remote", "-v"]
            result = self.run_git_command(target_dir, git_command)
            if debug_level >= 2:
                print(result)
            if result != None:
                output_lines = result.stdout.splitlines()
                for line in output_lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        if (parts[0] == "origin" and parts[2] == "(fetch)"):
                            url = parts[1]
                for line in output_lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        if (parts[0] != "origin" and parts[2] == "(fetch)"):
                            upstreams.append([parts[0], parts[1]])
        return url, upstreams

if __name__ == "__main__":
    if 3 > len(sys.argv):
        print_help()
    else:
        if sys.argv[1] == "--lib-absolute" and 4 <= len(sys.argv):
            prj_dir_base = sys.argv[2]
            lib_rel_dir = os.path.relpath(sys.argv[3], os.path.abspath(prj_dir_base))
        else:
            prj_dir_base = sys.argv[1]
            lib_rel_dir = sys.argv[2]

        csel = libmgr(prj_dir_base, lib_rel_dir)
        csel.mainloop()

    # csel = libmgr("..", "library")
    # csel.mainloop()
