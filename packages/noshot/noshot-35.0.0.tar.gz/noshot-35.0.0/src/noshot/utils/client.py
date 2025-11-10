import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
import os
import sys
import threading
import json
import websockets
import asyncio
from datetime import datetime
import requests
import hashlib
import argparse

def log_message(message, quiet_mode=True):
    if not quiet_mode:
        print(message)

if sys.platform == 'win32':
    try:
        from ctypes import windll
        myappid = 'oneshotcoding.noshot.notepad.1.0'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

class FinalStealthNotepad:
    def __init__(self, root, server_ip="localhost", server_port=8765, http_port=5000, username=None, password=None):
        self.root = root
        self.root.title("Untitled - Notepad")
        self.root.geometry("900x700")
        self.root.configure(bg="#f3f3f3")
        
        self.websocket = None
        self.connected = False
        self.username = username
        self.server_ip = server_ip
        self.server_port = server_port
        self.http_port = http_port
        self.shared_files = []
        
        self.chat_mode = False
        self.input_active = False
        self.saved_content = ""
        self.unread_messages = 0
        self.total_messages = 0
        self.message_sent = False
        self.displayed_message_ids = set()
        
        self.all_messages = []
        self.recent_messages = []
        
        self.input_lines = 1
        self.max_input_height = 80
        
        self.status_message_timeout = None
        self.status_message_duration = 3000
        
        self.chat_font_size = 10
        self.default_font_size = 11
        self.text_visibility = 75
        
        self.MENU_FONT = ("Segoe UI", 9)
        self.TEXT_FONT = ("Consolas", 11)
        self.STATUS_FONT = ("Segoe UI", 9)
        self.CHAT_FONT = ("Segoe UI", 10)
        self.INPUT_FONT = ("Segoe UI", 9)
        
        self.loop = asyncio.new_event_loop()
        
        self.setup_ui()
        self.setup_chat_connection()
        
    def setup_ui(self):
        menubar = tk.Frame(self.root, bg="#f3f3f3", relief="flat", height=30)
        menubar.pack(fill=tk.X, side=tk.TOP)
        
        self.menu_buttons = {}
        
        menu_labels = ["File", "Edit", "Format", "View", "Help"]
        for label in menu_labels:
            btn = tk.Label(
                menubar,
                text=label,
                bg="#f3f3f3",
                fg="#000000",
                padx=14,
                pady=6,
                font=self.MENU_FONT,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=0)
            
            if label == "Help":
                self.help_button = btn
                btn.bind("<Button-1>", self.show_help_menu)
            
            def on_enter(e, b=btn):
                b.config(bg="#e5e5e5")
            
            def on_leave(e, b=btn):
                b.config(bg="#f3f3f3")
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        text_container = tk.Frame(self.root, bg="#ffffff", bd=0)
        text_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.scrollbar = ttk.Scrollbar(text_container, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(
            text_container,
            wrap="word",
            font=self.TEXT_FONT,
            undo=True,
            relief="flat",
            bg="#ffffff",
            fg="#000000",
            insertbackground="#000000",
            selectbackground="#0078d4",
            selectforeground="#ffffff",
            padx=4,
            pady=4,
            bd=0,
            highlightthickness=0
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_area.yview)
        
        self.text_area.bind("<Button-3>", self.disable_context_menu)
        
        self.status_bar = tk.Frame(self.root, bg="#f3f3f3", height=24)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, anchor='s')
        
        self.status_text = tk.Label(
            self.status_bar,
            text="Ln 1, Col 1",
            anchor="w",
            font=self.STATUS_FONT,
            bg="#f3f3f3",
            fg="#000000",
            relief="flat",
            padx=12,
            pady=0
        )
        self.status_text.pack(side=tk.LEFT)
        
        self.create_status_tooltip()
        
        self.input_frame = tk.Frame(self.status_bar, bg="#f3f3f3", height=24)
        self.input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_frame.pack_propagate(False)
        
        self.hidden_input = tk.Text(
            self.input_frame,
            font=self.INPUT_FONT,
            bg="#f3f3f3",
            fg="#000000",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=20,
            height=1,
            wrap="word",
            insertbackground="#000000",
            padx=10,
            pady=1,
            state=tk.DISABLED
        )
        self.hidden_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.input_scrollbar = ttk.Scrollbar(
            self.input_frame,
            orient="vertical",
            command=self.hidden_input.yview
        )
        self.hidden_input.config(yscrollcommand=self.input_scrollbar.set)
        
        self.message_indicator = tk.Label(
            self.status_bar,
            text="0%",
            font=("Segoe UI", 9),
            bg="#f3f3f3",
            fg="#000000",
            relief="flat",
            padx=12,
            pady=0
        )
        self.message_indicator.pack(side=tk.RIGHT)
        
        self.create_message_indicator_tooltip()
        
        self.upload_indicator = tk.Label(
            self.status_bar,
            text="UTF-8",
            font=("Segoe UI", 9),
            bg="#f3f3f3",
            fg="#000000",
            relief="flat",
            padx=12,
            pady=0,
            cursor="arrow"
        )
        self.upload_indicator.pack(side=tk.RIGHT)
        self.upload_indicator.bind("<Button-1>", self.upload_multiple_files)
        
        self.connection_indicator = tk.Label(
            self.status_bar,
            text="Windows (CRLF)",
            font=("Segoe UI", 9),
            bg="#f3f3f3",
            fg="#000000",
            relief="flat",
            padx=12,
            pady=0
        )
        self.connection_indicator.pack(side=tk.RIGHT)
        
        self.create_upload_tooltip()
        
        self.setup_hover_effects()
        self.setup_keyboard_shortcut()
        
        self.add_welcome_content()
        
    def show_help_menu(self, event=None):
        menu_x = self.help_button.winfo_rootx()
        menu_y = self.help_button.winfo_rooty() + self.help_button.winfo_height()
        
        self.help_menu = tk.Toplevel(self.root)
        self.help_menu.wm_overrideredirect(True)
        self.help_menu.wm_geometry(f"+{menu_x}+{menu_y}")
        self.help_menu.wm_attributes("-topmost", True)
        self.help_menu.configure(bg="#f0f0f0", relief="solid", borderwidth=1)
        
        toggle_text = "Help" if not self.chat_mode else "Notepad"
        toggle_btn = tk.Label(
            self.help_menu,
            text=f"{toggle_text}",
            bg="#f0f0f0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=20,
            pady=8,
            cursor="hand2",
            width=25,
            anchor="w",
            bd=0,
            highlightthickness=0
        )
        toggle_btn.pack(fill=tk.X)
        toggle_btn.bind("<Button-1>", lambda e: self.menu_toggle_mode())
        toggle_btn.bind("<Enter>", lambda e: toggle_btn.config(bg="#0078d7", fg="#ffffff"))
        toggle_btn.bind("<Leave>", lambda e: toggle_btn.config(bg="#f0f0f0", fg="#000000"))
        
        separator1 = tk.Frame(self.help_menu, bg="#c0c0c0", height=1)
        separator1.pack(fill=tk.X, padx=0, pady=2)
        
        font_size_frame = tk.Frame(self.help_menu, bg="#f0f0f0", height=28)
        font_size_frame.pack(fill=tk.X, padx=0, pady=0)
        font_size_frame.pack_propagate(False)
        
        font_size_label = tk.Label(
            font_size_frame,
            text="Font Size:",
            bg="#f0f0f0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=20,
            pady=6,
            anchor="w",
            width=12
        )
        font_size_label.pack(side=tk.LEFT)
        
        font_controls_frame = tk.Frame(font_size_frame, bg="#f0f0f0")
        font_controls_frame.pack(side=tk.RIGHT, padx=15, pady=2)
        
        font_decrease_btn = tk.Label(
            font_controls_frame,
            text=" - ",
            bg="#f0f0f0",
            fg="#000000",
            font=("Segoe UI", 10, "bold"),
            width=3,
            cursor="hand2",
            relief="raised",
            bd=1
        )
        font_decrease_btn.pack(side=tk.LEFT, padx=(0, 2))
        font_decrease_btn.bind("<Button-1>", lambda e: self.decrease_font_size())
        font_decrease_btn.bind("<Enter>", lambda e: font_decrease_btn.config(bg="#e1e1e1"))
        font_decrease_btn.bind("<Leave>", lambda e: font_decrease_btn.config(bg="#f0f0f0"))
        
        font_increase_btn = tk.Label(
            font_controls_frame,
            text=" + ",
            bg="#f0f0f0",
            fg="#000000",
            font=("Segoe UI", 10, "bold"),
            width=3,
            cursor="hand2",
            relief="raised",
            bd=1
        )
        font_increase_btn.pack(side=tk.LEFT, padx=(2, 0))
        font_increase_btn.bind("<Button-1>", lambda e: self.increase_font_size())
        font_increase_btn.bind("<Enter>", lambda e: font_increase_btn.config(bg="#e1e1e1"))
        font_increase_btn.bind("<Leave>", lambda e: font_increase_btn.config(bg="#f0f0f0"))
        
        separator2 = tk.Frame(self.help_menu, bg="#c0c0c0", height=1)
        separator2.pack(fill=tk.X, padx=0, pady=2)
        
        visibility_frame = tk.Frame(self.help_menu, bg="#f0f0f0", height=28)
        visibility_frame.pack(fill=tk.X, padx=0, pady=0)
        visibility_frame.pack_propagate(False)
        
        visibility_label = tk.Label(
            visibility_frame,
            text="Chat Visibility:",
            bg="#f0f0f0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=20,
            pady=6,
            anchor="w",
            width=12
        )
        visibility_label.pack(side=tk.LEFT)
        
        visibility_controls_frame = tk.Frame(visibility_frame, bg="#f0f0f0")
        visibility_controls_frame.pack(side=tk.RIGHT, padx=15, pady=2)
        
        visibility_decrease_btn = tk.Label(
            visibility_controls_frame,
            text=" - ",
            bg="#f0f0f0",
            fg="#000000",
            font=("Segoe UI", 10, "bold"),
            width=3,
            cursor="hand2",
            relief="raised",
            bd=1
        )
        visibility_decrease_btn.pack(side=tk.LEFT, padx=(0, 2))
        visibility_decrease_btn.bind("<Button-1>", lambda e: self.decrease_visibility())
        visibility_decrease_btn.bind("<Enter>", lambda e: visibility_decrease_btn.config(bg="#e1e1e1"))
        visibility_decrease_btn.bind("<Leave>", lambda e: visibility_decrease_btn.config(bg="#f0f0f0"))
        
        visibility_increase_btn = tk.Label(
            visibility_controls_frame,
            text=" + ",
            bg="#f0f0f0",
            fg="#000000",
            font=("Segoe UI", 10, "bold"),
            width=3,
            cursor="hand2",
            relief="raised",
            bd=1
        )
        visibility_increase_btn.pack(side=tk.LEFT, padx=(2, 0))
        visibility_increase_btn.bind("<Button-1>", lambda e: self.increase_visibility())
        visibility_increase_btn.bind("<Enter>", lambda e: visibility_increase_btn.config(bg="#e1e1e1"))
        visibility_increase_btn.bind("<Leave>", lambda e: visibility_increase_btn.config(bg="#f0f0f0"))
        
        separator3 = tk.Frame(self.help_menu, bg="#c0c0c0", height=1)
        separator3.pack(fill=tk.X, padx=0, pady=2)
        
        reset_btn = tk.Label(
            self.help_menu,
            text="Reset to Default",
            bg="#f0f0f0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=20,
            pady=8,
            cursor="hand2",
            width=25,
            anchor="w",
            bd=0,
            highlightthickness=0
        )
        reset_btn.pack(fill=tk.X)
        reset_btn.bind("<Button-1>", lambda e: self.reset_all_settings())
        reset_btn.bind("<Enter>", lambda e: reset_btn.config(bg="#0078d7", fg="#ffffff"))
        reset_btn.bind("<Leave>", lambda e: reset_btn.config(bg="#f0f0f0", fg="#000000"))
        
        self.help_menu.bind("<FocusOut>", lambda e: self.help_menu.destroy())
        self.root.bind("<Button-1>", self.close_help_menu, add="+")
        self.root.bind("<Configure>", lambda e: self.close_all_menus())
        
        self.help_menu.focus_force()
        
    def reset_all_settings(self):
        self.chat_font_size = 10
        self.text_visibility = 70
        if self.chat_mode:
            self.update_font_size()
            self.update_chat_visibility()
        self.close_all_menus()

    def close_all_menus(self):
        if hasattr(self, 'help_menu') and self.help_menu.winfo_exists():
            self.help_menu.destroy()
            self.root.unbind("<Button-1>")
                
    def close_help_menu(self, event=None):
        if hasattr(self, 'help_menu') and self.help_menu.winfo_exists():
            if (event.widget != self.help_menu and 
                not isinstance(event.widget, tk.Label) or 
                (event.widget not in self.help_menu.winfo_children())):
                self.close_all_menus()
                
    def menu_toggle_mode(self):
        self.close_all_menus()
        self.toggle_mode()

    def create_message_indicator_tooltip(self):
        self.message_tooltip = tk.Toplevel(self.root)
        self.message_tooltip.wm_overrideredirect(True)
        self.message_tooltip.wm_withdraw()
        self.message_tooltip.wm_attributes("-topmost", True)
        
        self.message_tooltip_label = tk.Label(
            self.message_tooltip,
            text="Unread messages: 0",
            background="#ffffff",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 8),
            padx=4,
            pady=2
        )
        self.message_tooltip_label.pack()
        
        self.message_indicator.bind("<Enter>", self.show_message_indicator_tooltip)
        self.message_indicator.bind("<Leave>", self.hide_message_indicator_tooltip)
        
    def show_message_indicator_tooltip(self, event=None):
        tooltip_text = f"Unread messages: {self.unread_messages}"
        self.message_tooltip_label.config(text=tooltip_text)
        
        x = self.message_indicator.winfo_rootx() + 10
        y = self.message_indicator.winfo_rooty() - 30
        self.message_tooltip.wm_geometry(f"+{x}+{y}")
        self.message_tooltip.deiconify()
        
    def hide_message_indicator_tooltip(self, event=None):
        self.message_tooltip.wm_withdraw()
        
    def create_status_tooltip(self):
        self.status_tooltip = tk.Toplevel(self.root)
        self.status_tooltip.wm_overrideredirect(True)
        self.status_tooltip.wm_withdraw()
        self.status_tooltip.wm_attributes("-topmost", True)
        
        self.status_tooltip_label = tk.Label(
            self.status_tooltip,
            text="Messages: 0\nUsers: 0",
            background="#ffffff",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 8),
            padx=4,
            pady=2,
            justify=tk.LEFT
        )
        self.status_tooltip_label.pack()
        
        self.status_text.bind("<Enter>", self.show_status_tooltip)
        self.status_text.bind("<Leave>", self.hide_status_tooltip)
        
    def show_status_tooltip(self, event=None):
        if self.chat_mode:
            message_count = len([msg for msg in self.all_messages if msg.get('type') != 'system'])
            user_count = len(getattr(self, 'current_users', [])) if hasattr(self, 'current_users') else 1
            
            tooltip_text = f"Messages: {message_count}\nUsers: {user_count}"
            self.status_tooltip_label.config(text=tooltip_text)
            
            x = self.status_text.winfo_rootx() + 10
            y = self.status_text.winfo_rooty() - 40
            self.status_tooltip.wm_geometry(f"+{x}+{y}")
            self.status_tooltip.deiconify()
            
    def hide_status_tooltip(self, event=None):
        self.status_tooltip.wm_withdraw()
        
    def create_upload_tooltip(self):
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_withdraw()
        self.tooltip.wm_attributes("-topmost", True)
        
        self.tooltip_label = tk.Label(
            self.tooltip,
            text="Upload File",
            background="#ffffff",
            foreground="#000000",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 8),
            padx=4,
            pady=2
        )
        self.tooltip_label.pack()
        
        self.upload_indicator.bind("<Enter>", self.show_tooltip)
        self.upload_indicator.bind("<Leave>", self.hide_tooltip)
        
    def show_tooltip(self, event=None):
        if self.connected and self.chat_mode:
            x = self.upload_indicator.winfo_rootx() + 10
            y = self.upload_indicator.winfo_rooty() - 25
            self.tooltip.wm_geometry(f"+{x}+{y}")
            self.tooltip.deiconify()
            
    def hide_tooltip(self, event=None):
        self.tooltip.wm_withdraw()
        
    def show_status_message(self, message, duration=3000):
        if self.status_message_timeout:
            self.root.after_cancel(self.status_message_timeout)
            
        if not hasattr(self, 'original_connection_text'):
            self.original_connection_text = self.connection_indicator.cget("text")
            
        self.connection_indicator.config(text=message)
        
        self.status_message_timeout = self.root.after(duration, self.revert_connection_text)
        
    def revert_connection_text(self):
        if hasattr(self, 'original_connection_text'):
            self.connection_indicator.config(text=self.original_connection_text)
        else:
            self.connection_indicator.config(text="Windows (CRLF)")
        self.status_message_timeout = None
        
    def disable_context_menu(self, event=None):
        if self.chat_mode:
            return "break"
        return None
        
    def setup_hover_effects(self):
        self.input_frame.bind("<Enter>", self.on_input_frame_enter)
        self.input_frame.bind("<Leave>", self.on_input_frame_leave)
        self.hidden_input.bind("<Enter>", self.on_input_enter)
        self.hidden_input.bind("<Leave>", self.on_input_leave)
        
        self.hidden_input.bind("<Return>", self.handle_return_key)
        self.hidden_input.bind("<Shift-Return>", self.handle_shift_return)
        self.hidden_input.bind("<Escape>", self.deactivate_input)
        self.hidden_input.bind("<KeyRelease>", self.update_input_height)
        
        self.hidden_input.bind("<FocusOut>", self.on_input_focus_out)
        
        self.root.bind("<Escape>", self.deactivate_input_global)
        
    def deactivate_input_global(self, event=None):
        if self.input_active and self.chat_mode:
            self.deactivate_input()
        return "break"
        
    def on_input_frame_enter(self, event=None):
        if self.chat_mode and self.connected:
            self.input_frame.config(cursor="xterm")
            self.input_frame.config(bg="#e8e8e8")
            self.hidden_input.config(bg="#e8e8e8")
            
    def on_input_frame_leave(self, event=None):
        if not self.input_active:
            self.input_frame.config(cursor="")
            self.input_frame.config(bg="#f3f3f3")
            self.hidden_input.config(bg="#f3f3f3")
            
    def on_input_enter(self, event=None):
        if self.chat_mode and self.connected:
            self.hidden_input.config(cursor="xterm")
            self.hidden_input.config(bg="#e8e8e8")
            
    def on_input_leave(self, event=None):
        if not self.input_active:
            self.hidden_input.config(cursor="")
            self.hidden_input.config(bg="#f3f3f3")
            
    def on_input_focus_out(self, event=None):
        if self.chat_mode and not self.hidden_input.focus_get():
            self.deactivate_input()
            
    def setup_keyboard_shortcut(self):
        self.root.bind("<Control-Shift-c>", self.toggle_mode)
        self.root.bind("<Control-Shift-C>", self.toggle_mode)
        self.text_area.bind("<Control-Shift-c>", self.toggle_mode)
        self.text_area.bind("<Control-Shift-C>", self.toggle_mode)
        self.hidden_input.bind("<Control-Shift-c>", self.toggle_mode)
        self.hidden_input.bind("<Control-Shift-C>", self.toggle_mode)
        
        self.root.bind("<Control-u>", self.upload_multiple_files)
        self.root.bind("<Control-U>", self.upload_multiple_files)
        self.text_area.bind("<Control-u>", self.upload_multiple_files)
        self.text_area.bind("<Control-U>", self.upload_multiple_files)
        self.hidden_input.bind("<Control-u>", self.upload_multiple_files)
        self.hidden_input.bind("<Control-U>", self.upload_multiple_files)
        
    def toggle_mode(self, event=None):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Not connected to chat server!")
            return "break"
            
        if not self.chat_mode:
            self.activate_chat_mode()
        else:
            self.activate_notepad_mode()
            
        return "break"
        
    def activate_chat_mode(self):
        log_message("Activating chat mode")
        self.saved_content = self.text_area.get("1.0", "end-1c")
        self.chat_mode = True
        
        new_font = ("Segoe UI", self.chat_font_size)
        self.text_area.config(font=new_font)
        
        self.update_chat_visibility()
        
        self.text_area.config(state=tk.DISABLED)
        self.text_area.config(cursor="arrow")
        
        self.text_area.bind("<Button-1>", self.disable_selection)
        self.text_area.bind("<Control-c>", self.disable_copy)
        self.text_area.bind("<Control-v>", self.disable_paste)
        self.text_area.bind("<Control-x>", self.disable_cut)
        self.text_area.bind("<Button-3>", self.disable_context_menu)
        
        self.text_area.bind("<Control-a>", self.disable_select_all)
        
        self.text_area.bind("<ButtonPress-1>", self.disable_text_selection)
        self.text_area.bind("<B1-Motion>", self.disable_text_selection)
        self.text_area.bind("<Shift-ButtonPress-1>", self.disable_text_selection)
        self.text_area.bind("<Shift-B1-Motion>", self.disable_text_selection)
        
        self.text_area.bind("<Key>", self.disable_text_selection)
        
        self.refresh_chat_display()
        
        self.upload_indicator.config(cursor="hand2", fg="#000000")
        
        self.activate_input()
        
        self.unread_messages = 0
        self.update_indicators()
        
    def activate_notepad_mode(self):
        log_message("Activating notepad mode")
        self.chat_mode = False
        
        self.text_area.config(font=self.TEXT_FONT)
        
        self.text_area.config(fg="#000000", insertbackground="#000000")
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.config(cursor="xterm")
        
        self.text_area.unbind("<Button-1>")
        self.text_area.unbind("<Control-c>")
        self.text_area.unbind("<Control-v>")
        self.text_area.unbind("<Control-x>")
        self.text_area.unbind("<Control-a>")
        self.text_area.unbind("<ButtonPress-1>")
        self.text_area.unbind("<B1-Motion>")
        self.text_area.unbind("<Shift-ButtonPress-1>")
        self.text_area.unbind("<Shift-B1-Motion>")
        self.text_area.unbind("<Key>")
        
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", self.saved_content)
        
        self.upload_indicator.config(cursor="", fg="#000000")
        self.hide_tooltip()
        
        self.deactivate_input()
        self.hidden_input.config(state=tk.DISABLED)
        self.input_frame.config(cursor="")
        self.hidden_input.config(cursor="")
        
        self.update_indicators()
        
    def disable_text_selection(self, event=None):
        if self.chat_mode:
            return "break"
        return None
        
    def disable_selection(self, event=None):
        if self.chat_mode:
            self.text_area.mark_set(tk.INSERT, tk.END)
            self.text_area.see(tk.END)
            return "break"
        return None
        
    def disable_copy(self, event=None):
        if self.chat_mode:
            return "break"
        return None
        
    def disable_paste(self, event=None):
        if self.chat_mode:
            return "break"
        return None
        
    def disable_cut(self, event=None):
        if self.chat_mode:
            return "break"
        return None
        
    def disable_select_all(self, event=None):
        if self.chat_mode:
            return "break"
        return None
        
    def activate_input(self):
        if not self.input_active:
            self.input_active = True
            self.hidden_input.config(height=1, state=tk.NORMAL)
            self.input_lines = 1
            self.input_scrollbar.pack_forget()
            self.hidden_input.focus()
            
    def deactivate_input(self, event=None):
        if self.input_active:
            self.input_active = False
            self.hidden_input.delete("1.0", "end")
            self.hidden_input.config(height=1)
            self.input_lines = 1
            self.input_frame.config(height=24)
            self.input_scrollbar.pack_forget()
            self.text_area.focus_set()
            self.text_area.mark_set(tk.INSERT, tk.END)
            
        return "break"
        
    def handle_return_key(self, event=None):
        if self.chat_mode and self.connected:
            message = self.hidden_input.get("1.0", "end-1c").strip()
            
            if message and not self.message_sent:
                self.message_sent = True
                log_message(f"Sending message: '{message}'")
                self.send_message(message)
                self.hidden_input.delete("1.0", "end")
                self.update_input_height()
                self.root.after(100, lambda: setattr(self, 'message_sent', False))
                return "break"
                
        return None
        
    def handle_shift_return(self, event=None):
        if self.chat_mode:
            self.update_input_height()
            return None
        return "break"
        
    def update_input_height(self, event=None):
        if not self.chat_mode:
            return
            
        content = self.hidden_input.get("1.0", "end-1c")
        lines = content.count('\n') + 1
        
        if lines > 1:
            lines = min(lines, 3)
            if lines != self.input_lines:
                self.input_lines = lines
                self.hidden_input.config(height=lines)
                new_height = 18 + (lines - 1) * 16
                new_height = min(new_height, 60)
                self.input_frame.config(height=new_height)
                self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.input_lines = 1
            self.hidden_input.config(height=1)
            self.input_frame.config(height=24)
            self.input_scrollbar.pack_forget()
        
    def send_message(self, message):
        if message and self.connected and self.websocket:
            self.send_to_server(message)
            
            self.hidden_input.delete("1.0", "end")
            self.update_input_height()
        
    def send_to_server(self, message):
        if not self.websocket:
            log_message("WebSocket not connected!")
            return
            
        msg_data = {
            'type': 'message',
            'content': message,
            'target': 'public'
        }
        
        try:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(msg_data)),
                self.loop
            )
            log_message(f"Message sent to server: {message}")
        except Exception as e:
            log_message(f"Error sending message: {e}")
        
    def display_message(self, message_data, from_history=False):
        if message_data.get('type') == 'system':
            return
            
        content = message_data.get('content', '')
        username = message_data.get('username', '')
        timestamp = message_data.get('timestamp', '')
        
        msg_id = f"recv_{username}_{timestamp}_{hash(content)}"
        
        if msg_id in self.displayed_message_ids:
            return
            
        if not self.chat_mode and not from_history:
            if not hasattr(self, 'recent_messages'):
                self.recent_messages = []
            self.recent_messages.append(message_data)
            self.unread_messages += 1
            self.update_indicators()
            return
            
        self.text_area.config(state=tk.NORMAL)
        
        if ':' in timestamp and timestamp.count(':') == 2:
            timestamp = timestamp.rsplit(':', 1)[0]
        
        if not hasattr(self, 'text_tags_created'):
            self.update_chat_text_tags()
            self.text_tags_created = True
        
        if message_data.get('type') == 'file_shared':
            file_info = message_data.get('file_info', {})
            
            if file_info.get('uploaded_by') == self.username:
                message_tag = "my_message"
            else:
                message_tag = "other_message"
            
            display_text = f"{username} shared: {file_info.get('original_name', 'file')} "
            self.text_area.insert(tk.END, display_text, message_tag)
            
            download_text = " ↓"
            self.text_area.insert(tk.END, download_text, "download_link")
            
            timestamp_text = f"     {timestamp}"
            self.text_area.insert(tk.END, timestamp_text, "timestamp")
            self.text_area.insert(tk.END, "\n")
            
            line_start = self.text_area.index("end-2l")
            download_start = len(display_text)
            download_end = download_start + len(download_text)
            
            download_start_idx = f"{line_start}+{download_start}c"
            download_end_idx = f"{line_start}+{download_end}c"
            
            unique_tag = f"download_{file_info.get('filename', 'file')}"
            
            self.text_area.tag_add(unique_tag, download_start_idx, download_end_idx)
            self.text_area.tag_config(unique_tag, foreground="#D0D0D0")
            self.text_area.tag_bind(unique_tag, "<Button-1>", 
                                  lambda e, fi=file_info: self.download_file(fi))
            self.text_area.tag_bind(unique_tag, "<Enter>", 
                                  lambda e, tag=unique_tag: self.on_download_hover_enter(e, tag))
            self.text_area.tag_bind(unique_tag, "<Leave>", 
                                  lambda e, tag=unique_tag: self.on_download_hover_leave(e, tag))
        else:
            if username == self.username:
                display_text = f"{username}: {content}"
                self.text_area.insert(tk.END, display_text, "my_message")
            else:
                display_text = f"{username}: {content}"
                self.text_area.insert(tk.END, display_text, "other_message")
            
            timestamp_text = f"     {timestamp}"
            self.text_area.insert(tk.END, timestamp_text, "timestamp")
            self.text_area.insert(tk.END, "\n")
        
        self.displayed_message_ids.add(msg_id)
        self.total_messages = len([msg for msg in self.all_messages if msg.get('type') != 'system'])
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        
        if self.chat_mode:
            online_users = len(getattr(self, 'current_users', [])) if hasattr(self, 'current_users') else 1
            self.status_text.config(text=f"Ln {self.total_messages}, Col {online_users}")
    
    def on_download_hover_enter(self, event, tag):
        self.text_area.config(cursor="hand2")
        
    def on_download_hover_leave(self, event, tag):
        self.text_area.config(cursor="arrow")
        
    def display_message_direct(self, message_data):
        if message_data.get('type') == 'system':
            return
            
        content = message_data.get('content', '')
        username = message_data.get('username', '')
        timestamp = message_data.get('timestamp', '')
        
        if ':' in timestamp and timestamp.count(':') == 2:
            timestamp = timestamp.rsplit(':', 1)[0]
        
        if not hasattr(self, 'text_tags_created'):
            self.update_chat_text_tags()
            self.text_tags_created = True
        
        if message_data.get('type') == 'file_shared':
            file_info = message_data.get('file_info', {})
            
            if file_info.get('uploaded_by') == self.username:
                message_tag = "my_message"
            else:
                message_tag = "other_message"
            
            display_text = f"{username} shared: {file_info.get('original_name', 'file')} "
            self.text_area.insert(tk.END, display_text, message_tag)
            
            download_text = " ↓"
            self.text_area.insert(tk.END, download_text, "download_link")
            
            timestamp_text = f"     {timestamp}"
            self.text_area.insert(tk.END, timestamp_text, "timestamp")
            self.text_area.insert(tk.END, "\n")
            
            line_start = self.text_area.index("end-2l")
            download_start = len(display_text)
            download_end = download_start + len(download_text)
            
            download_start_idx = f"{line_start}+{download_start}c"
            download_end_idx = f"{line_start}+{download_end}c"
            
            unique_tag = f"download_{file_info.get('filename', 'file')}"
            
            self.text_area.tag_add(unique_tag, download_start_idx, download_end_idx)
            self.text_area.tag_config(unique_tag, foreground="#D0D0D0")
            self.text_area.tag_bind(unique_tag, "<Button-1>", 
                                  lambda e, fi=file_info: self.download_file(fi))
            self.text_area.tag_bind(unique_tag, "<Enter>", 
                                  lambda e, tag=unique_tag: self.on_download_hover_enter(e, tag))
            self.text_area.tag_bind(unique_tag, "<Leave>", 
                                  lambda e, tag=unique_tag: self.on_download_hover_leave(e, tag))
        else:
            if username == self.username:
                display_text = f"{username}: {content}"
                self.text_area.insert(tk.END, display_text, "my_message")
            else:
                display_text = f"{username}: {content}"
                self.text_area.insert(tk.END, display_text, "other_message")
            
            timestamp_text = f"     {timestamp}"
            self.text_area.insert(tk.END, timestamp_text, "timestamp")
            self.text_area.insert(tk.END, "\n")
    
    def upload_multiple_files(self, event=None):
        if not self.connected or not self.chat_mode:
            return "break" if event else None
            
        filenames = filedialog.askopenfilenames(
            title="Select files to share",
            filetypes=[("All files", "*.*")]
        )
        
        if filenames:
            log_message(f"Uploading {len(filenames)} files")
            self.show_status_message(f"Uploading {len(filenames)} files...")
            
            for filename in filenames:
                threading.Thread(
                    target=self.upload_to_server,
                    args=(filename,),
                    daemon=True
                ).start()
            
        return "break" if event else None
            
    def upload_to_server(self, filepath):
        try:
            url = f"http://{self.server_ip}:{self.http_port}/upload"
            filename = os.path.basename(filepath)
            log_message(f"Uploading to: {url}")
            
            with open(filepath, 'rb') as f:
                files = {
                    'file': (filename, f, 'application/octet-stream')
                }
                data = {
                    'username': self.username,
                    'original_name': filename
                }
                
                log_message(f"Sending upload request for: {filename}")
                response = requests.post(url, files=files, data=data, timeout=30)
                log_message(f"Upload response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        file_info = result.get('file_info', {})
                        file_size = file_info.get('size', 0)
                        size_str = self.format_file_size(file_size)
                        self.show_status_message(f"Uploaded: {filename} ({size_str})")
                        log_message(f"File shared: {filename} ({size_str})")
                    else:
                        self.show_status_message(f"Upload failed: {filename}")
                        log_message(f"Upload failed: {result.get('message')}")
                else:
                    self.show_status_message(f"Upload failed: {filename}")
                    log_message(f"Upload failed with status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            error_msg = f"Upload timeout: {filename}"
            self.show_status_message(error_msg)
            log_message(error_msg)
        except Exception as e:
            error_msg = f"Upload error: {filename} - {e}"
            self.show_status_message(error_msg)
            log_message(error_msg)
            
    def format_file_size(self, bytes):
        if bytes == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"
            
    def download_file(self, file_info):
        try:
            filename = file_info.get('filename', '')
            if not filename:
                log_message("No filename provided in file_info")
                return
                
            url = f"http://{self.server_ip}:{self.http_port}/download/{filename}"
            original_name = file_info.get('original_name', 'download')
            
            file_extension = os.path.splitext(original_name)[1]
            if not file_extension:
                file_extension = os.path.splitext(filename)[1]
            
            log_message(f"Downloading from: {url}")
            self.show_status_message(f"Downloading: {original_name}")
            
            save_filename = original_name
            
            save_path = filedialog.asksaveasfilename(
                title="Save file",
                initialfile=save_filename,
                defaultextension=file_extension,
                filetypes=[("All files", "*.*")]
            )
            
            if save_path:
                log_message(f"Saving to: {save_path}")
                if file_extension and not save_path.lower().endswith(file_extension.lower()):
                    save_path += file_extension
                    log_message(f"Added extension to save path: {save_path}")
                
                if os.path.exists(save_path):
                    log_message(f"File exists, overwriting: {save_path}")
                
                threading.Thread(
                    target=self.download_thread,
                    args=(url, save_path, file_info),
                    daemon=True
                ).start()
            else:
                log_message("Download cancelled by user")
                
        except Exception as e:
            error_msg = f"Download error: {e}"
            self.show_status_message(error_msg)
            log_message(error_msg)
            
    def download_thread(self, url, save_path, file_info):
        try:
            log_message(f"Starting download: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            file_size = self.format_file_size(downloaded)
            success_msg = f"Downloaded: {os.path.basename(save_path)} ({file_size})"
            self.show_status_message(success_msg)
            log_message(f"Download completed: {save_path} ({downloaded} bytes)")
                
        except Exception as e:
            error_msg = f"Download failed: {e}"
            self.show_status_message(error_msg)
            log_message(f"Download thread error: {e}")
            
    def add_welcome_content(self):
        welcome_text = """Name
Reg no
Roll no
Section
Date
Time
Course Code
Course Name
"""
        self.text_area.insert("1.0", welcome_text)
        
    def setup_chat_connection(self):
        self.chat_thread = threading.Thread(target=self.run_chat_client, daemon=True)
        self.chat_thread.start()
        
    def run_chat_client(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.chat_client())
        finally:
            self.loop.close()
        
    async def chat_client(self):
        uri = f"ws://{self.server_ip}:{self.server_port}"
        log_message(f"Connecting to: {uri}")
        
        retry_delay = 3
        
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    self.connected = True
                    log_message("Connected to chat server!")
                    
                    self.root.after(0, self.update_connection_status, True)
                    self.show_status_message("Connected to chat server")
                    
                    log_message(f"Auto-login as: {self.username}")
                    
                    login_msg = {
                        'type': 'login',
                        'username': self.username
                    }
                    await websocket.send(json.dumps(login_msg))
                    log_message(f"Login message sent: {self.username}")
                    
                    retry_delay = 3
                    
                    async for message in websocket:
                        data = json.loads(message)
                        self.root.after(0, self.handle_websocket_message, data)
                        
            except Exception as e:
                log_message(f"Connection error: {e}")
                self.connected = False
                self.websocket = None
                self.root.after(0, self.update_connection_status, False)
                
                self.root.after(0, lambda: self.show_status_message("Reconnecting..."))
                
                log_message(f"Retrying connection in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                
                retry_delay = min(retry_delay * 1.5, 30)
            
    def handle_websocket_message(self, data):
        log_message(f"Received message type: {data.get('type')}")
        
        if data['type'] == 'message_history':
            new_messages = data.get('messages', [])
            log_message(f"Received {len(new_messages)} messages from server history")
            
            self.all_messages = new_messages.copy()
            
            self.displayed_message_ids.clear()
            
            log_message(f"Stored {len(self.all_messages)} messages in local history")
            
            if self.chat_mode:
                self.refresh_chat_display()
            
        elif data['type'] == 'message':
            message_data = data.get('message', {})
            log_message(f"Processing message from {message_data.get('username')}: {message_data.get('content')}")
            
            if not hasattr(self, 'all_messages'):
                self.all_messages = []
            
            msg_id = f"recv_{message_data.get('username')}_{message_data.get('timestamp')}_{hash(message_data.get('content', ''))}"
            if msg_id not in self.displayed_message_ids:
                self.all_messages.append(message_data)
                log_message(f"Added message to history, total: {len(self.all_messages)}")
            
            self.display_message(message_data)
            
        elif data['type'] == 'user_list':
            self.current_users = data.get('users', [])
            log_message(f"Users online: {self.current_users}")
            if self.chat_mode:
                message_count = len([msg for msg in self.all_messages if msg.get('type') != 'system'])
                self.status_text.config(text=f"Ln {message_count}, Col {len(self.current_users)}")
            
        elif data['type'] == 'file_shared':
            log_message(f"File shared: {data.get('original_name')}")
            
            file_msg = {
                'type': 'file_shared',
                'content': f"shared file: {data.get('original_name')}",
                'username': data.get('uploaded_by', 'User'),
                'timestamp': data.get('timestamp', ''),
                'file_info': data
            }
            
            if not hasattr(self, 'all_messages'):
                self.all_messages = []
            
            msg_id = f"recv_{file_msg.get('username')}_{file_msg.get('timestamp')}_{hash(file_msg.get('content', ''))}"
            if msg_id not in self.displayed_message_ids:
                self.all_messages.append(file_msg)
                log_message(f"Added file message to history, total: {len(self.all_messages)}")
            
            self.display_message(file_msg)
            
        elif data['type'] == 'file_list':
            files = data.get('files', [])
            log_message(f"Received file list with {len(files)} files")
            
            for file_info in files:
                file_msg = {
                    'type': 'file_shared',
                    'content': f"shared file: {file_info.get('original_name')}",
                    'username': file_info.get('uploaded_by', 'User'),
                    'timestamp': file_info.get('timestamp', ''),
                    'file_info': file_info
                }
                
                msg_id = f"recv_{file_msg.get('username')}_{file_msg.get('timestamp')}_{hash(file_msg.get('content', ''))}"
                if msg_id not in self.displayed_message_ids:
                    self.all_messages.append(file_msg)
                    log_message(f"Added file from file list to history: {file_info.get('original_name')}")
            
            if self.chat_mode:
                self.refresh_chat_display()
            
    def refresh_chat_display(self):
        if not self.chat_mode:
            return
            
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        
        log_message(f"Refreshing chat display with {len(self.all_messages)} messages")
        
        self.displayed_message_ids.clear()
        
        for msg in self.all_messages:
            self.display_message_direct(msg)
            
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        
        message_count = len([msg for msg in self.all_messages if msg.get('type') != 'system'])
        online_users = len(getattr(self, 'current_users', [])) if hasattr(self, 'current_users') else 1
        self.status_text.config(text=f"Ln {message_count}, Col {online_users}")
            
    def update_connection_status(self, connected):
        self.connected = connected
        self.update_indicators()
        
    def update_indicators(self):
        if self.connected:
            if not self.chat_mode and self.unread_messages > 0:
                message_percent = min(self.unread_messages, 10)
                self.message_indicator.config(text=f"{message_percent}%")
            else:
                self.message_indicator.config(text="0%")
        else:
            self.message_indicator.config(text="0%")
            
    def update_status(self, event=None):
        cursor_pos = self.text_area.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        
        if not self.chat_mode:
            self.status_text.config(text=f"Ln {line}, Col {int(col) + 1}")

    def increase_font_size(self):
        self.chat_font_size = min(self.chat_font_size + 1, 24)
        if self.chat_mode:
            self.update_font_size()
        
    def decrease_font_size(self):
        self.chat_font_size = max(self.chat_font_size - 1, 8)
        if self.chat_mode:
            self.update_font_size()
        
    def update_font_size(self):
        if self.chat_mode:
            new_font = ("Segoe UI", self.chat_font_size)
            self.text_area.config(font=new_font)
        
    def increase_visibility(self):
        self.text_visibility = min(self.text_visibility - 5, 100)
        if self.chat_mode:
            self.update_chat_visibility()
        
    def decrease_visibility(self):
        self.text_visibility = max(self.text_visibility + 5, 0)
        if self.chat_mode:
            self.update_chat_visibility()
        
    def update_chat_visibility(self):
        if self.chat_mode:
            self.update_chat_text_tags()
    
    def update_chat_text_tags(self):
        self.text_visibility = max(0, min(self.text_visibility, 100))
        
        base_darkness = int(255 * (self.text_visibility) / 100)
        
        base_darkness = max(0, min(base_darkness, 255))
        
        my_msg_darkness = min(base_darkness + 50, 255)
        other_msg_darkness = min(base_darkness + 50, 255)
        timestamp_darkness = min(base_darkness + 60, 255)
        download_darkness = min(base_darkness + 25, 255)
        
        my_msg_darkness = max(0, min(my_msg_darkness, 255))
        other_msg_darkness = max(0, min(other_msg_darkness, 255))
        timestamp_darkness = max(0, min(timestamp_darkness, 255))
        download_darkness = max(0, min(download_darkness, 255))
        
        my_msg_color = f"#{my_msg_darkness:02x}{my_msg_darkness:02x}{my_msg_darkness:02x}"
        other_msg_color = f"#{other_msg_darkness:02x}{other_msg_darkness:02x}{other_msg_darkness:02x}"
        timestamp_color = f"#{timestamp_darkness:02x}{timestamp_darkness:02x}{timestamp_darkness:02x}"
        download_color = f"#{download_darkness:02x}{download_darkness:02x}{download_darkness:02x}"
        
        self.text_area.tag_configure("my_message", foreground=my_msg_color)
        self.text_area.tag_configure("other_message", foreground=other_msg_color)
        self.text_area.tag_configure("timestamp", font=("Segoe UI", 6), foreground=timestamp_color)
        self.text_area.tag_configure("download_link", foreground=download_color)

def run_notepad(server_ip="localhost", server_port=8765, http_port=5000, username=None, password=None, quiet_mode=False):
    expected_md5 = "8ddcff3a80f4189ca1c9d4d902c3c909"
    provided_md5 = hashlib.md5(password.encode()).hexdigest()
    if provided_md5 != expected_md5:
        if not quiet_mode:
            print("Invalid password! Client terminating.")
        sys.exit(1)
    if not quiet_mode:
        print("Password validated successfully")
    
    root = tk.Tk()
    try:
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "storage", "assets", "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass
    
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 900) // 2
    y = (root.winfo_screenheight() - 600) // 3
    root.geometry(f"900x700+{x}+{y}")
    
    app = FinalStealthNotepad(root, server_ip, server_port, http_port, username, password)
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description='Stealth Notepad with Chat Functionality')
    parser.add_argument('-s', '--server-ip', default='localhost', help='Chat server IP address (default: localhost)')
    parser.add_argument('-p', '--server-port', type=int, default=8765, help='WebSocket server port (default: 8765)')
    parser.add_argument('-H', '--http-port', type=int, default=5000, help='HTTP server port for file uploads (default: 5000)')
    parser.add_argument('-u', '--username', required=True, help='Username for chat (required)')
    parser.add_argument('-P', '--password', required=True, help='Password for authentication (must be 88888888)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode - no terminal output')
    
    args = parser.parse_args()
    
    run_notepad(
        server_ip=args.server_ip,
        server_port=args.server_port,
        http_port=args.http_port,
        username=args.username,
        password=args.password,
        quiet_mode=args.quiet
    )

if __name__ == "__main__":
    main()