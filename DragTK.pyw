# DragTK
# Copyright (c) 2025 Marcus Douglas
# Licensed under the MIT License. See LICENSE file for details.
# Last Updated: 2025-08-13
# Version 1.0.0


# Imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import tempfile
import subprocess
import sys
import os
from collections import defaultdict
import re
import keyword
import builtins
import tkinter.font as tkfont
import traceback
import datetime

# Number of pixels dragged canvas elements snap by
GRID_SIZE = 10  # pixels

# Redundant (one reference to COLOR_BLACK)
DARK_MODE = False
COLOR_BLACK = 'black'
COLOR_WHITE = 'white'


# --- Utility functions -----------------------------------------------------

# Increments name of elements as they are added to canvas e.g. button1, button2, etc
def next_name(counter, base):
    counter[base] += 1
    return f"{base}{counter[base]}"

# --- Main Application -----------------------------------------------------

class GUIBuilderApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("DragTK")
        self.geometry("1200x800")
        self.minsize(900, 600)
        try:
            self.iconbitmap('resources/logo.ico')
        except Exception as e:
            print("resources/logo.ico was not found")

        # state
        self.counters = defaultdict(int)  # for naming
        self.elements = {}  # name -> metadata
        self.selected = None
        self.mode = tk.StringVar(value="light")

        self.canvas_width_var = tk.StringVar(value="800")
        self.canvas_height_var = tk.StringVar(value="600")
        self.canvas_title_var = tk.StringVar(value="Generated GUI")

        # Have changes been made to the current project / code
        self.dirty = False
        self.current_save_path = None

        # Function when closing app
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Stores group names for radio button widgets
        self.radio_groups = {}

        # Create UI, apply themes (dark vs light mode), generate code
        self._create_ui()
        self._apply_theme()
        self.generate_code()

    def _create_ui(self):

        # Visual style
        self.style = ttk.Style()
        self.style.theme_use('clam') # Clam theme (more editable than leaving as default)

        big_font = ("Calibri", 11)
        self.style.configure("Big.TButton", font=("Calibri", 11))

        # File, options, run, help (menu bar along top of window)
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Create File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        # Create Options menu
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)

        # Create Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)

        # Add menu commands
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Save Project           <Ctrl + s>", command=self.save_project)
        file_menu.add_command(label="Save Project As     <Ctrl + shift + s>", command=self.save_project_as)
        file_menu.add_command(label="Export as .py", command=self.export_code)
        file_menu.add_separator()
        file_menu.add_command(label="Load Project", command=self.load_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        #file_menu.add_separator()
        options_menu.add_command(label="Toggle Dark/Light    <Ctrl + t>", command=self.toggle_theme)

        # Add Run menu commands
        run_menu.add_command(label="Check and Run", command=self.verify_code)
        run_menu.add_command(label="Run <f5>", command=self.run_code)

        # --- Add Help menu ---
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About DragTK", command=self.show_about)
        

        # main panes: HORIZONTAL - properties (left) | canvas (middle) | right pane (code + errors)
        main_pane = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=(10, 10), pady=(20, 0))

        self.style.configure("My.TLabelframe.Label", font=("Calibri", 12))
        

        # LEFT: Widgets buttons frame (new)
        widgets_frame = ttk.LabelFrame(main_pane, text="Add Widgets", style="My.TLabelframe")
        widgets_frame.config(width=120)
        main_pane.add(widgets_frame, weight=0)

        # Add buttons vertically in widgets_frame
        btn_params = {'side': tk.TOP, 'fill': tk.X, 'padx': 4, 'pady': 2}

        self.add_label_btn = ttk.Button(widgets_frame, text="Label", command=lambda: self.add_element('Label'))
        self.add_label_btn.pack(**btn_params)
        self.add_button_btn = ttk.Button(widgets_frame, text="Button", command=lambda: self.add_element('Button'))
        self.add_button_btn.pack(**btn_params)
        self.add_entry_btn = ttk.Button(widgets_frame, text="Entry", command=lambda: self.add_element('Entry'))
        self.add_entry_btn.pack(**btn_params)
        self.add_tree_btn = ttk.Button(widgets_frame, text="Treeview", command=lambda: self.add_element('Treeview'))
        self.add_tree_btn.pack(**btn_params)
        self.add_check_btn = ttk.Button(widgets_frame, text="Checkbutton", command=lambda: self.add_element('Checkbutton'))
        self.add_check_btn.pack(**btn_params)
        self.add_radio_btn = ttk.Button(widgets_frame, text="Radiobutton", command=lambda: self.add_element('Radiobutton'))
        self.add_radio_btn.pack(**btn_params)
        self.add_textarea_btn = ttk.Button(widgets_frame, text="Text Area", command=lambda: self.add_element('TextArea'))
        self.add_textarea_btn.pack(**btn_params)
        self.add_listbox_btn = ttk.Button(widgets_frame, text="Listbox", command=lambda: self.add_element('Listbox'))
        self.add_listbox_btn.pack(**btn_params)
        self.add_combobox_btn = ttk.Button(widgets_frame, text="Combobox", command=lambda: self.add_element('Combobox'))
        self.add_combobox_btn.pack(**btn_params)

        # LEFT: Properties
        prop_frame = ttk.LabelFrame(main_pane, text="Properties", width=250, style="My.TLabelframe")
        main_pane.add(prop_frame, weight=1)

        container = ttk.Frame(prop_frame)
        container.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)

        ttk.Label(container, text="ID:", font=big_font).grid(row=0, column=0, sticky=tk.W, padx=(0,4), pady=2)
        self.prop_id = ttk.Entry(container, font=big_font)
        self.prop_id.grid(row=0, column=1, sticky=tk.EW, pady=2, ipady=4)

        ttk.Label(container, text="Type:", font=big_font).grid(row=1, column=0, sticky=tk.W, padx=(0,4), pady=2)
        self.prop_type = ttk.Label(container, text="-", font=big_font)
        self.prop_type.grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(container, text="Text:", font=big_font).grid(row=2, column=0, sticky=tk.W, padx=(0,4), pady=2)
        self.prop_text = ttk.Entry(container, font=big_font)
        self.prop_text.grid(row=2, column=1, sticky=tk.EW, pady=2, ipady=4)

        ttk.Label(container, text="X:", font=big_font).grid(row=3, column=0, sticky=tk.W, padx=(0,4), pady=2)
        self.prop_x = ttk.Entry(container, font=big_font)
        self.prop_x.grid(row=3, column=1, sticky=tk.EW, pady=2, ipady=4)

        ttk.Label(container, text="Y:", font=big_font).grid(row=4, column=0, sticky=tk.W, padx=(0,4), pady=2)
        self.prop_y = ttk.Entry(container, font=big_font)
        self.prop_y.grid(row=4, column=1, sticky=tk.EW, pady=2, ipady=4)

        ttk.Label(container, text="Width:", font=big_font).grid(row=5, column=0, sticky=tk.W, padx=(0,4), pady=2)
        self.prop_w = ttk.Entry(container, font=big_font)
        self.prop_w.grid(row=5, column=1, sticky=tk.EW, pady=2, ipady=4)

        ttk.Label(container, text="Height:", font=big_font).grid(row=6, column=0, sticky=tk.W, padx=(0,4), pady=2)
        self.prop_h = ttk.Entry(container, font=big_font)
        self.prop_h.grid(row=6, column=1, sticky=tk.EW, pady=2, ipady=4)

        self.apply_btn = ttk.Button(container, text="Apply", command=self.apply_properties)
        self.apply_btn.grid(row=7, column=0, columnspan=2, pady=8)

        prop_frame.columnconfigure(0, weight=1)
        prop_frame.rowconfigure(0, weight=1)

        # MIDDLE: Canvas area
        canvas_frame = ttk.LabelFrame(main_pane, text="Canvas", width=600, style="My.TLabelframe")
        main_pane.add(canvas_frame, weight=3)

        # Canvas (where widgets are added)
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.hbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.vbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(
            xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
            scrollregion=(0, 0, int(self.canvas_width_var.get()), int(self.canvas_height_var.get()))
        )

        # Canvas settings controls BELOW the canvas
        canvas_settings_frame = ttk.Frame(canvas_frame)
        canvas_settings_frame.pack(side=tk.TOP, fill=tk.X, pady=(4,8), padx=4)

        ttk.Label(canvas_settings_frame, text="Canvas Title:", font=big_font).pack(side=tk.LEFT, padx=(0,4))
        self.canvas_title_var = tk.StringVar(value="Generated GUI")
        self.canvas_title_entry = ttk.Entry(canvas_settings_frame, textvariable=self.canvas_title_var, width=20, font=big_font)
        self.canvas_title_entry.pack(side=tk.LEFT, padx=(0,12))

        ttk.Label(canvas_settings_frame, text="Width:", font=big_font).pack(side=tk.LEFT, padx=(0,4))
        self.canvas_width_var = tk.StringVar(value="800")
        self.canvas_width_entry = ttk.Entry(canvas_settings_frame, width=6, textvariable=self.canvas_width_var, font=big_font)
        self.canvas_width_entry.pack(side=tk.LEFT, padx=(0,8))

        ttk.Label(canvas_settings_frame, text="Height:", font=big_font).pack(side=tk.LEFT, padx=(0,4))
        self.canvas_height_var = tk.StringVar(value="600")
        self.canvas_height_entry = ttk.Entry(canvas_settings_frame, width=6, textvariable=self.canvas_height_var, font=big_font)
        self.canvas_height_entry.pack(side=tk.LEFT, padx=(0,8))

        self.apply_size_btn = ttk.Button(canvas_settings_frame, text="Apply Canvas Settings", command=self.apply_canvas_size)
        self.apply_size_btn.pack(side=tk.LEFT)


        # Binds
        self.canvas.bind('<Button-1>', self.canvas_click)
        # Bind F5 to run_code function
        self.bind('<F5>', lambda event: self.run_code())
        self.bind('<Delete>', lambda event: self.delete_selected())
        # Bind Ctrl+S to Save
        self.bind_all("<Control-s>", lambda event: self.save_project())
        # Bind Ctrl+Shift+S to Save As
        self.bind_all("<Control-S>", lambda event: self.save_project_as())
        # Bind Ctrl+T to toggle dark/light mode
        self.bind_all("<Control-t>", lambda event: self.toggle_theme())


        # RIGHT: Code editor + syntax output
        right_pane = ttk.Panedwindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(right_pane, weight=2)

        # Create a single frame for both buttons + code editor
        editor_container = ttk.Frame(right_pane)
        right_pane.add(editor_container, weight=3)

        # Buttons row inside container
        editor_buttons_frame = ttk.Frame(editor_container)
        editor_buttons_frame.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.run_btn = ttk.Button(editor_buttons_frame, text="Run <f5>", command=self.run_code)
        self.run_btn.pack(side=tk.RIGHT, padx=2)
        self.verify_btn = ttk.Button(editor_buttons_frame, text="Check and Run", command=self.verify_code)
        self.verify_btn.pack(side=tk.RIGHT, padx=2)

        # Code editor frame inside container
        code_frame = ttk.LabelFrame(editor_container, text="Code Editor", style="My.TLabelframe")
        code_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.setup_code_editor(parent=code_frame)

        # Error log frame
        output_frame = ttk.LabelFrame(right_pane, text="Error Log", style="My.TLabelframe")
        right_pane.add(output_frame, weight=1)
        

        # Text widget for error output
        self.syntax_output = tk.Text(output_frame, height=6, wrap="word", fg="red", font=("Consolas", 12))
        self.syntax_output.insert("1.0", "Use the 'Check and Run' button to check code for errors.")
        self.syntax_output.pack(fill=tk.BOTH, expand=True)


    # Function to open about window
    def show_about(self):
        
        about_win = tk.Toplevel(self)
        about_win.title("About DragTK")
        about_win.geometry("400x450")
        
        try:
            about_win.iconbitmap('resources/logo.ico')
        except Exception as e:
            print("resources/logo.ico was not found")
        about_win.resizable(False, False)

        # --- Top section ---
        top_frame = ttk.Frame(about_win, padding=10)
        top_frame.pack(fill="x")

        # Logo
        try:
            logo_img = tk.PhotoImage(file="resources/logo.png")  # adjust path as needed
            logo_img = logo_img.subsample(10, 10)  # shrink to 1/4 size in both dimensions
            logo_label = ttk.Label(top_frame, image=logo_img)
            logo_label.image = logo_img  # keep reference
            logo_label.pack()
        except Exception as e:
            ttk.Label(top_frame, text="[Logo missing]", font=("Arial", 10, "italic")).pack()

        ttk.Label(top_frame, text="DragTK", font=("Arial", 16, "bold")).pack(pady=(5, 0))
        ttk.Label(top_frame, text="A simple GUI Builder for Tkinter and Python", font=("Arial", 10)).pack()
        ttk.Label(top_frame, text="Contact: marcus.douglas@cullodenacademy.org.uk", font=("Arial", 9)).pack()

        # --- Bottom section ---
        bottom_frame = ttk.Frame(about_win, padding=10)
        bottom_frame.pack(fill="x", pady=(20, 0))

        def show_text_file(title, path):
            win = tk.Toplevel(self)
            win.title(title)
            win.geometry("500x400")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except FileNotFoundError:
                content = f"{title} file not found."
            text_widget = tk.Text(win, wrap="word")
            text_widget.insert("1.0", content)
            text_widget.config(state="disabled")
            text_widget.pack(fill="both", expand=True)

        ttk.Button(bottom_frame, text="License", 
                   command=lambda: show_text_file("License", "LICENSE.txt")).pack(fill="x", pady=2)
        ttk.Button(bottom_frame, text="Copyright", 
                   command=lambda: show_text_file("Copyright", "COPYRIGHT.txt")).pack(fill="x", pady=2)
        ttk.Button(bottom_frame, text="README", 
                   command=lambda: show_text_file("README", "README.txt")).pack(fill="x", pady=2)



    # Draws the red boundard of the canvas area
    def _draw_canvas_boundary(self):
        
        # Remove old boundary if it exists
        if hasattr(self, '_canvas_boundary_id'):
            self.canvas.delete(self._canvas_boundary_id)

        w = getattr(self, 'canvas_width', 800)
        h = getattr(self, 'canvas_height', 600)

        # Draw a rectangle border with dashed lines
        self._canvas_boundary_id = self.canvas.create_rectangle(
            0, 0, w, h,
            outline='red',
            dash=(4, 2),
            width=2
        )


    # Updates canvas to new size set by user
    def apply_canvas_size(self):
        try:
            w = int(self.canvas_width_var.get())
            h = int(self.canvas_height_var.get())
            if w <= 0 or h <= 0:
                raise ValueError("Dimensions must be positive integers.")
        except ValueError as e:
            messagebox.showerror("Invalid Size", f"Invalid canvas size: {e}")
            return

        # Update canvas size and scrollregion
        self.canvas.config(width=w, height=h)
        self.canvas.config(scrollregion=(0, 0, w, h))

        # Store current size for save/load persistence
        self.canvas_width = w
        self.canvas_height = h
        self._draw_canvas_boundary()
        self.generate_code()


    # Runs on Check and Run button
    # Used to check code for errors before execution
    def verify_code(self):
        
        if getattr(self, 'show_verify_warning', True):
            self.show_verify_warning = not self.show_warning_dialog()

        code_text = self.code_text.get("1.0", tk.END)
        self.syntax_output.delete("1.0", tk.END)
        self.code_text.tag_remove("error_highlight", "1.0", tk.END)

        try:
            compiled_code = compile(code_text, "<string>", "exec")
        except SyntaxError as e:
            self.syntax_output.config(fg="red")
            self.syntax_output.insert(
                tk.END,
                f"❌ Syntax Error on line {e.lineno}, column {e.offset}:\n"
                f"{e.text.strip()}\n{e.msg}\n"
            )
            self._highlight_error_line(e.lineno)
            return

        try:
            self.syntax_output.config(fg="green")
            self.syntax_output.insert(tk.END, "✅ No syntax or runtime errors since last verification.\n")
            
            # Store and display timestamp
            self.last_verified = datetime.datetime.now()
            self.syntax_output.insert(
                tk.END,
                f"Last verified: {self.last_verified.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            exec(compiled_code, {"__builtins__": __builtins__})

        except Exception as e:
            self.syntax_output.delete('1.0', tk.END)
            tb = e.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            lineno = tb.tb_lineno
            self.syntax_output.config(fg="red")
            self.syntax_output.insert(
                tk.END,
                f"⚠️ {type(e).__name__} on line {lineno}:\n{e}\n"
            )
            self._highlight_error_line(lineno)


    # Shows warning message when using check and run button
    # Just to say main purpose of check and run is checking for errors
    # Better to use just the Run button once no errors for app to run fully
    def show_warning_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("!! Attention !!")
        dialog.geometry("350x150")
        dialog.transient(self)
        dialog.grab_set()
        try:
            dialog.iconbitmap('resources/logo.ico')
        except Exception as e:
            print("resources/logo.ico was not found")

        # Center the dialog over the parent window
        self.update_idletasks()  # Make sure geometry info is up to date

        # Get the parent window position and size
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        # Calculate position for the dialog
        dialog_width = 350
        dialog_height = 250

        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        wrn_msg = ("Attenntion!\n\nThe primary purpose of this button is to check that your code contains no errors."
                   + " You may find some features of your app don't work as expected when testing your app through this method."
                   + " If the Error Log shows there were no errors, it is recommended you launch your app using the dedicated 'Run' button.")

        msg = tk.Label(dialog, text=wrn_msg, wraplength=320)
        msg.pack(padx=20, pady=10)

        dont_show_var = tk.BooleanVar()

        cb = tk.Checkbutton(dialog, text="Don't show this message again", variable=dont_show_var)
        cb.pack(pady=5)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        def on_ok():
            dialog.destroy()

        ok_btn = tk.Button(btn_frame, text="OK", width=10, command=on_ok)
        ok_btn.pack()

        self.wait_window(dialog)

        return dont_show_var.get()



    # Highlights line with errors in the code editor when an error is found
    def _highlight_error_line(self, lineno):
        """Highlight a specific line number in the code editor."""
        # Add highlight tag style
        self.code_text.tag_configure("error_highlight", background="#ffcccc")
        # Highlight the whole line
        self.code_text.tag_add(
            "error_highlight",
            f"{lineno}.0",
            f"{lineno}.0 lineend"
        )
        # Scroll to the line
        self.code_text.see(f"{lineno}.0")


    # Sets code as dirty (meaning a change has been made so project needs saved)
    def _on_code_modified(self, event):
        self.dirty = True
    

    # Setup code editor
    def setup_code_editor(self, parent):

        # Helper to make tab = to 4 spaces (just tab spaces had weird results)
        def insert_tab(event):
            event.widget.insert('insert', '    ')  # Insert 4 spaces
            return "break"

        # Auto indents when hitting return after e.g. for loops, function definitions, etc
        def auto_indent(event):
            """Handle indentation when pressing Enter."""
            # Get current line index
            current_line_index = self.code_text.index("insert linestart")
            current_line_text = self.code_text.get(current_line_index, f"{current_line_index} lineend")

            # Determine leading whitespace
            leading_spaces = len(current_line_text) - len(current_line_text.lstrip(' '))
            indent = ' ' * leading_spaces

            # Check if line should increase indent (ends with a colon)
            if current_line_text.strip().endswith(':'):
                indent += '    '  # Add one extra indent level

            # Insert newline + indent
            self.code_text.insert("insert", "\n" + indent)
            return "break"

        # Create a frame to hold line numbers and text widget
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(
            editor_frame,
            width=5, padx=4, takefocus=0, border=1,
            background='lightgrey', state='disabled',
            wrap='none', font=('Consolas', 12)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.code_text = tk.Text(
            editor_frame, wrap=tk.NONE, undo=True,
            bg=COLOR_WHITE, fg=COLOR_BLACK, tabs=('1c')
        )
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        font = tkfont.Font(family="Consolas", size=12)
        self.code_text.config(font=font)
        self.code_text.bind('<Tab>', insert_tab)
        self.code_text.bind('<Return>', auto_indent)  # ← Auto-indent binding

        y_scroll = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self._on_scroll)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_text.config(yscrollcommand=y_scroll.set)
        self.line_numbers.config(yscrollcommand=y_scroll.set)

        self.code_text.bind('<KeyRelease>', self._update_line_numbers, add="+")
        self.code_text.bind('<MouseWheel>', self._update_line_numbers)
        self.code_text.bind('<Button-4>', self._update_line_numbers)
        self.code_text.bind('<Button-5>', self._update_line_numbers)
        self.code_text.bind('<BackSpace>', self._update_line_numbers)

        self._update_line_numbers()
        self.code_text.bind("<KeyRelease>", self.highlight_syntax, add="+")
        self.code_text.bind("<KeyRelease>", self._on_code_modified, add="+")



    def _on_scroll(self, *args):
        self.code_text.yview(*args)
        self.line_numbers.yview(*args)


    # Update line numbers for each line in code editor
    def _update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')

        line_count = int(self.code_text.index('end-1c').split('.')[0])
        line_numbers_str = "\n".join(str(i) for i in range(1, line_count + 1)) + '\n'

        self.line_numbers.insert('1.0', line_numbers_str)
        self.line_numbers.config(state='disabled')


    # Marks key Python syntax with colored text
    def highlight_syntax(self, event=None):
        self.code_text.tag_remove("keyword", "1.0", tk.END)
        self.code_text.tag_remove("comment", "1.0", tk.END)
        self.code_text.tag_remove("string", "1.0", tk.END)
        self.code_text.tag_remove("builtin", "1.0", tk.END)

        text = self.code_text.get("1.0", tk.END)

        comment_pattern = re.compile(r"#.*")
        string_pattern = re.compile(r"(\".*?\"|\'.*?\')")

        for match in comment_pattern.finditer(text):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.code_text.tag_add("comment", start, end)

        for match in string_pattern.finditer(text):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.code_text.tag_add("string", start, end)

        # Keywords
        for kw in keyword.kwlist:
            for match in re.finditer(rf"\b{kw}\b", text):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                if not any(self.code_text.tag_names(start)):
                    self.code_text.tag_add("keyword", start, end)

        # Built-in functions like print, len, etc.
        builtins_list = dir(builtins)
        for bi in builtins_list:
            for match in re.finditer(rf"\b{bi}\b", text):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                if not any(self.code_text.tag_names(start)):
                    self.code_text.tag_add("builtin", start, end)

    # ------------------- Element management ---------------------------------
    
    # Called when user clicked an add widget button.
    # First function which is called when adding a widget to the canvas
    def add_element(self, eltype):
        name = next_name(self.counters, eltype.lower())
        # default properties
        props = {
            'type': eltype,
            'name': name,
            'text': eltype,
            'x': 50 + len(self.elements)*20,
            'y': 50 + len(self.elements)*20,
            'w': 100,
            'h': 30,
        }

        if eltype == "Entry":
            props = {
            'type': eltype,
            'name': name,
            'text': "",
            'x': 50 + len(self.elements)*20,
            'y': 50 + len(self.elements)*20,
            'w': 100,
            'h': 30,
        }
        elif eltype == "TextArea":
            props['text'] = ""
            props['w'] = 200  # wider by default
            props['h'] = 100  # taller by default

        elif eltype == "Listbox":
            props['text'] = ""  # Not really used, but keeps data structure consistent
            props['w'] = 120
            props['h'] = 80  # taller by default

        elif eltype == "Combobox":
            props['text'] = ""  # starting selection
            props['w'] = 120
            props['h'] = 30

        
        self.elements[name] = props
        self._create_visual(props)
        self.generate_code()
        


    # For making sure when copy and pasting in the code editor
    # it does not result in copy and pasting in the canvas
    def _conditional_copy(self, event, name):
        focused = self.focus_get()
        
        if focused == self.code_text or (hasattr(focused, 'winfo_class') and focused.winfo_class() in ['Text', 'Entry']):
            # Let text widget handle it normally
            return
        else:
            self.copy_element(name)

    # For making sure when copy and pasting in the code editor
    # it does not result in copy and pasting in the canvas
    def _conditional_paste(self, event, name):
        focused = self.focus_get()
        if focused == self.code_text or (hasattr(focused, 'winfo_class') and focused.winfo_class() in ['Text', 'Entry']):
            return
        else:
            self.paste_element(name)

    # Copy an element (widget)
    def copy_element(self, name):

        self.select_element(name)
        element = self.elements.get(name)
        if not element:
            return

        if name in self.elements:
            # store a copy of the properties
            self.copied_element = self.elements[name].copy()


    # Paste an element (widget)
    def paste_element(self, name):
        
        if not hasattr(self, "copied_element") or not self.copied_element:
            return  # nothing copied

        eltype = self.copied_element['type']

        # Generate next name like button15, label3, etc.
        new_name = next_name(self.counters, eltype.lower())

        # Create a new props dict from copied one
        new_props = self.copied_element.copy()
        new_props['name'] = new_name

        # Shift position a bit so it doesn't sit directly on top
        new_props['x'] += 20
        new_props['y'] += 20

        # Add to elements and draw
        self.elements[new_name] = new_props
        self._create_visual(new_props)
        self.generate_code()



    # Called in apply_properties() at the bottom
    # Updates elements with property changes
    def _update_element(self, name=None):
        """
        Update the visual widget and bindings for element 'name'.
        If name is None, use self.selected.
        """
        if name is None:
            name = self.selected
        if not name or name not in self.elements:
            return
        
        props = self.elements[name]
        widget = props.get('_widget')
        frame = props.get('_frame')

        # Update text/value on widget
        text = props.get('text', '')
        if widget:
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, text)
            elif props['type'] == 'Checkbutton':
                var = props.get('_var')
                if var is not None:
                    # No text update for var, update widget text separately
                    widget.config(text=text)
            elif props['type'] == 'Radiobutton':
                var = props.get('_radio_group_var')
                # Radiobutton text update
                widget.config(text=text, value=text)
                # No need to update var here (shared across group)
            else:
                try:
                    widget.config(text=text)
                except Exception:
                    pass

        # Update canvas position and size
        if props.get('_window_id'):
            self.canvas.coords(props['_window_id'], props['x'], props['y'])
            self.canvas.itemconfigure(props['_window_id'], width=props['w'], height=props['h'])

        # Update canvas tags if the element was renamed
        self.canvas.itemconfig(props['_window_id'], tags=(name,))

        # Rebind events to new name to avoid stale closures on lambdas
        if frame:
            # Unbind previous? Tkinter doesn't provide easy unbind for lambdas, so just rebind
            frame.bind('<Button-1>', lambda e, n=name: self._on_mouse_down(e, n))
            frame.bind('<B1-Motion>', lambda e, n=name: self._on_mouse_move(e, n))
            frame.bind('<ButtonRelease-1>', lambda e, n=name: self._on_mouse_up(e, n))
            frame.bind('<Motion>', lambda e, n=name: self._update_cursor(e, n))

        if widget:
            widget.bind('<Button-1>', lambda e, n=name: self._on_mouse_down(e, n))
            widget.bind('<B1-Motion>', lambda e, n=name: self._on_mouse_move(e, n))
            widget.bind('<ButtonRelease-1>', lambda e, n=name: self._on_mouse_up(e, n))
            widget.bind('<Motion>', lambda e, n=name: self._update_cursor(e, n))
            self.bind("<Control-c>", lambda e, n=name: self._conditional_copy(e, name))
            self.bind("<Control-v>", lambda e, n=name: self._conditional_paste(e, name))


        

    # Creates the actual widget onto the canvas. Called in add_element() and paste_element()
    def _create_visual(self, props):
        
        # create a tkinter widget and put it on the canvas
        eltype = props['type']
        name = props['name']
        text = props.get('text', name)
        x, y, w, h = props['x'], props['y'], props['w'], props['h']

        frame = tk.Frame(self.canvas)
        widget = None
        
        if eltype == 'Label':
            widget = ttk.Label(frame, text=text)
        elif eltype == 'Button':
            widget = ttk.Button(frame, text=text, command=lambda n=name: self._on_builder_button_click(n))
        elif eltype == 'Entry':
            widget = ttk.Entry(frame)
            widget.insert(0, text)
        elif eltype == 'TextArea':
            widget = tk.Text(frame, width=20, height=5)

        elif eltype == 'Listbox':
            widget = tk.Listbox(frame)
            widget.insert(tk.END, "Item 1")
            widget.insert(tk.END, "Item 2")
            widget.insert(tk.END, "Item 3")

        elif eltype == 'Combobox':
            widget = ttk.Combobox(frame, values=["Option 1", "Option 2", "Option 3"])
            widget.set(text)

        elif eltype == 'Treeview':
            widget = ttk.Treeview(frame, columns=('c1',), show='headings', height=3)
            widget.heading('c1', text='Column')
            widget.insert('', 'end', values=(text,))

        elif eltype == 'Checkbutton':
            var = tk.BooleanVar(value=False)
            widget = ttk.Checkbutton(frame, text=text, variable=var, onvalue=True, offvalue=False)
            props['_var'] = var
        elif eltype == 'Radiobutton':
            # Get all existing radio group variable names from self.elements
            existing_groups = sorted({
                p.get('_radio_group_name')
                for p in self.elements.values()
                if p['type'] == 'Radiobutton' and '_radio_group_name' in p
            })

            # Ask user if they want to create new or pick existing
            if existing_groups:
                choice = simpledialog.askstring(
                    "Radiobutton Group",
                    f"Enter group name or pick existing:\nExisting: {', '.join(existing_groups)}"
                )
            else:
                choice = simpledialog.askstring(
                    "Radiobutton Group",
                    "Enter new group name for this radiobutton:"
                )

            if not choice:
                return  # Cancel creation if no name provided

            # Store group name in props
            props['_radio_group_name'] = choice

            # Reuse same StringVar for group
            if choice not in self.radio_groups:
                self.radio_groups[choice] = tk.StringVar(value='')
            var = self.radio_groups[choice]

            props['_radio_group_var'] = var

            widget = ttk.Radiobutton(frame, text=text, variable=var, value=text)
        else:
            widget = ttk.Label(frame, text=f"{eltype}")

        widget.pack(fill=tk.BOTH, expand=True)

        # place on canvas
        window_id = self.canvas.create_window(x, y, window=frame, anchor='nw', width=w, height=h, tags=(name,))
        props['_window_id'] = window_id
        props['_frame'] = frame
        props['_widget'] = widget

        # bind events for selection, drag, and resize
        frame.bind('<Button-1>', lambda e, n=name: self._on_mouse_down(e, n))
        widget.bind('<Button-1>', lambda e, n=name: self._on_mouse_down(e, n))
        frame.bind('<B1-Motion>', lambda e, n=name: self._on_mouse_move(e, n))
        widget.bind('<B1-Motion>', lambda e, n=name: self._on_mouse_move(e, n))
        frame.bind('<ButtonRelease-1>', lambda e, n=name: self._on_mouse_up(e, n))
        widget.bind('<ButtonRelease-1>', lambda e, n=name: self._on_mouse_up(e, n))
        frame.bind('<Motion>', lambda e, n=name: self._update_cursor(e, n))
        widget.bind('<Motion>', lambda e, n=name: self._update_cursor(e, n))

        # Bind double-click on the widget itself
        widget.bind('<Double-1>', lambda e, n=name: self.widget_double_click(e, name))
        self.bind("<Control-c>", lambda e, n=name: self._conditional_copy(e, name))
        self.bind("<Control-v>", lambda e, n=name: self._conditional_paste(e, name))


        # right-click menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label='Properties', command=lambda n=name: self.select_element(n))
        menu.add_command(label='Copy', command=lambda n=name: self.copy_element(n))
        menu.add_command(label='Paste', command=lambda n=name: self.paste_element(n))
        menu.add_command(label='Delete', command=lambda n=name: self._delete_element(n))

        # right-click menu
        menu2 = tk.Menu(self, tearoff=0)
        menu2.add_command(label='Paste', command=lambda n=name: self.paste_element(n))
        self.canvas.bind('<Button-3>', lambda e, m=menu2: m.tk_popup(e.x_root, e.y_root))

        frame.bind('<Button-3>', lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))
        widget.bind('<Button-3>', lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))



    # Used for when loading widgets from existing project rather than creating
    # (this may have become redundant an _create_visual() might be doing the same job after refinements?)
    def _create_visual_loaded(self, props):
        
        # create a tkinter widget and put it on the canvas
        eltype = props['type']
        name = props['name']
        text = props.get('text', name)
        x, y, w, h = props['x'], props['y'], props['w'], props['h']

        frame = tk.Frame(self.canvas)
        widget = None
        
        if eltype == 'Label':
            widget = ttk.Label(frame, text=text)
        elif eltype == 'Button':
            widget = ttk.Button(frame, text=text, command=lambda n=name: self._on_builder_button_click(n))
        elif eltype == 'Entry':
            widget = ttk.Entry(frame)
            widget.insert(0, text)
        elif eltype == 'Listbox':
            widget = tk.Listbox(frame)
            widget.insert(tk.END, "Item 1")
            widget.insert(tk.END, "Item 2")
            widget.insert(tk.END, "Item 3")
        elif eltype == 'Combobox':
            widget = ttk.Combobox(frame, values=["Option 1", "Option 2", "Option 3"])
            widget.set(text)
        elif eltype == 'TextArea':
            widget = tk.Text(frame, width=20, height=5)
        elif eltype == 'Treeview':

            widget = ttk.Treeview(frame, columns=('c1',), show='headings', height=3)
            widget.heading('c1', text='Column')
            widget.insert('', 'end', values=(text,))

        elif eltype == 'Checkbutton':
            var = tk.BooleanVar(value=False)
            widget = ttk.Checkbutton(frame, text=text, variable=var, onvalue=True, offvalue=False)
            props['_var'] = var
        elif eltype == 'Radiobutton':
            # Use the saved group name if available, else ask user (for manual creation)
            choice = props.get('_radio_group_name')
            if not choice:
                # fallback to asking user if no group name saved
                existing_groups = sorted({
                    p.get('_radio_group_name')
                    for p in self.elements.values()
                    if p['type'] == 'Radiobutton' and '_radio_group_name' in p
                })

                if existing_groups:
                    choice = simpledialog.askstring(
                        "Radiobutton Group",
                        f"Enter group name or pick existing:\nExisting: {', '.join(existing_groups)}"
                    )
                else:
                    choice = simpledialog.askstring(
                        "Radiobutton Group",
                        "Enter new group name for this radiobutton:"
                    )

                if not choice:
                    return  # Cancel creation if no name provided

                props['_radio_group_name'] = choice

            # Reuse or create StringVar for this group
            if choice not in self.radio_groups:
                self.radio_groups[choice] = tk.StringVar(value='')
            var = self.radio_groups[choice]

            props['_radio_group_var'] = var

            widget = ttk.Radiobutton(frame, text=text, variable=var, value=text)

        else:
            widget = ttk.Label(frame, text=f"{eltype}")

        widget.pack(fill=tk.BOTH, expand=True)

        # place on canvas
        window_id = self.canvas.create_window(x, y, window=frame, anchor='nw', width=w, height=h, tags=(name,))
        props['_window_id'] = window_id
        props['_frame'] = frame
        props['_widget'] = widget

        # bind events for selection, drag, and resize
        frame.bind('<Button-1>', lambda e, n=name: self._on_mouse_down(e, n))
        widget.bind('<Button-1>', lambda e, n=name: self._on_mouse_down(e, n))
        frame.bind('<B1-Motion>', lambda e, n=name: self._on_mouse_move(e, n))
        widget.bind('<B1-Motion>', lambda e, n=name: self._on_mouse_move(e, n))
        frame.bind('<ButtonRelease-1>', lambda e, n=name: self._on_mouse_up(e, n))
        widget.bind('<ButtonRelease-1>', lambda e, n=name: self._on_mouse_up(e, n))
        frame.bind('<Motion>', lambda e, n=name: self._update_cursor(e, n))
        widget.bind('<Motion>', lambda e, n=name: self._update_cursor(e, n))

        # Bind double-click on the widget itself
        widget.bind('<Double-1>', lambda e, n=name: self.widget_double_click(e, name))
        self.bind("<Control-c>", lambda e, n=name: self._conditional_copy(e, name))
        self.bind("<Control-v>", lambda e, n=name: self._conditional_paste(e, name))


        # right-click menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label='Properties', command=lambda n=name: self.select_element(n))
        menu.add_command(label='Copy', command=lambda n=name: self.copy_element(n))
        menu.add_command(label='Paste', command=lambda n=name: self.paste_element(n))
        menu.add_command(label='Delete', command=lambda n=name: self._delete_element(n))

        # right-click menu
        menu2 = tk.Menu(self, tearoff=0)
        menu2.add_command(label='Paste', command=lambda n=name: self.paste_element(n))
        self.canvas.bind('<Button-3>', lambda e, m=menu2: m.tk_popup(e.x_root, e.y_root))

        frame.bind('<Button-3>', lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))
        widget.bind('<Button-3>', lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))




    # Double clicking a widget opens a dialog to let the user set the text value for the widget
    def widget_double_click(self, event, name):
        print(f"Double clicked on widget: {name}")
        self.select_element(name)
        # Open a simpledialog to edit the 'text' property
        element = self.elements.get(name)
        if not element:
            return
        old_text = element.get('text', '')
        new_text = simpledialog.askstring("Edit Text", f"Enter new text for {name}:", initialvalue=old_text)
        if new_text is not None:
            element['text'] = new_text
            # Update widget text live
            widget = element.get('_widget')
            if widget:
                if isinstance(widget, (ttk.Label, ttk.Button, ttk.Checkbutton, ttk.Radiobutton)):
                    widget.config(text=new_text)
                    self.generate_code()


    # Changes the mouse cursor to directional arrows
    # when near the corner or sides of a widget to indicate
    # the widget can be resized with click and drag
    def _update_cursor(self, event, name):
        props = self.elements[name]
        w = props['w']
        h = props['h']
        x = event.x
        y = event.y
        border_threshold = 8

        cursor = ''

        near_left = (0 <= x <= border_threshold)
        near_right = (w - border_threshold <= x <= w)
        near_top = (0 <= y <= border_threshold)
        near_bottom = (h - border_threshold <= y <= h)

        if near_left and near_top:
            cursor = 'top_left_corner'
        elif near_right and near_top:
            cursor = 'top_right_corner'
        elif near_left and near_bottom:
            cursor = 'bottom_left_corner'
        elif near_right and near_bottom:
            cursor = 'bottom_right_corner'
        elif near_top:
            cursor = 'top_side'
        elif near_bottom:
            cursor = 'bottom_side'
        elif near_left:
            cursor = 'left_side'
        elif near_right:
            cursor = 'right_side'
        else:
            cursor = ''  # default

        frame = props['_frame']
        if cursor:
            frame.config(cursor=cursor)
        else:
            frame.config(cursor='')


    # Function for resizing widgets or dragging them around canvas
    def _on_mouse_down(self, event, name):
        props = self.elements[name]
        self.selected = name
        self.select_element(name)

        # Calculate mouse position relative to element
        x = event.x
        y = event.y
        w = props['w']
        h = props['h']

        border_threshold = 8  # pixels near edge to start resize

        resizing = None
        # Check if near right edge
        if w - border_threshold <= x <= w:
            resizing = 'right'
        # Check if near bottom edge
        if h - border_threshold <= y <= h:
            if resizing:
                resizing = 'corner'  # bottom-right corner
            else:
                resizing = 'bottom'
        # Check if near left edge
        if 0 <= x <= border_threshold:
            resizing = 'left'
        # Check if near top edge
        if 0 <= y <= border_threshold:
            if resizing in ('right', 'corner'):
                resizing = 'top-right'
            elif resizing == 'bottom':
                resizing = 'top-bottom'  # for now just 'top' alone is fine
            else:
                resizing = 'top'

        if resizing:
            self._resize_mode = resizing
            self._resize_start = (event.x_root, event.y_root)
            self._resize_orig = (props['x'], props['y'], props['w'], props['h'])
        else:
            # dragging mode
            self._resize_mode = None
            self._drag_start = (event.x_root, event.y_root)
            self._drag_orig = (props['x'], props['y'])


    # Either resizes widgets or moves them over the canvas
    def _on_mouse_move(self, event, name):
        props = self.elements[name]

        if hasattr(self, '_resize_mode') and self._resize_mode:
            # resizing logic
            dx = event.x_root - self._resize_start[0]
            dy = event.y_root - self._resize_start[1]
            x0, y0, w0, h0 = self._resize_orig

            new_x, new_y, new_w, new_h = x0, y0, w0, h0
            min_size = 20
            grid_size = 10  # snap size for resizing

            mode = self._resize_mode
            if mode == 'right':
                new_w = max(min_size, w0 + dx)
            elif mode == 'bottom':
                new_h = max(min_size, h0 + dy)
            elif mode == 'corner':
                new_w = max(min_size, w0 + dx)
                new_h = max(min_size, h0 + dy)
            elif mode == 'left':
                new_x = x0 + dx
                new_w = max(min_size, w0 - dx)
                if new_w == min_size:
                    new_x = x0 + (w0 - min_size)
            elif mode == 'top':
                new_y = y0 + dy
                new_h = max(min_size, h0 - dy)
                if new_h == min_size:
                    new_y = y0 + (h0 - min_size)
            elif mode == 'top-right':
                new_y = y0 + dy
                new_h = max(min_size, h0 - dy)
                if new_h == min_size:
                    new_y = y0 + (h0 - min_size)
                new_w = max(min_size, w0 + dx)

            # Snap width/height to nearest 10px
            new_w = round(new_w / grid_size) * grid_size
            new_h = round(new_h / grid_size) * grid_size

            # Also snap x/y if adjusting from left or top
            new_x = round(new_x / grid_size) * grid_size
            new_y = round(new_y / grid_size) * grid_size

            props['x'], props['y'], props['w'], props['h'] = int(new_x), int(new_y), int(new_w), int(new_h)

            self.canvas.coords(props['_window_id'], props['x'], props['y'])
            self.canvas.itemconfig(props['_window_id'], width=props['w'], height=props['h'])
            if self.selected == name:
                self._highlight_selected()
                self.prop_x.delete(0, tk.END); self.prop_x.insert(0, props['x'])
                self.prop_y.delete(0, tk.END); self.prop_y.insert(0, props['y'])
                self.prop_w.delete(0, tk.END); self.prop_w.insert(0, props['w'])
                self.prop_h.delete(0, tk.END); self.prop_h.insert(0, props['h'])
                self.apply_properties()

        elif hasattr(self, '_drag_start'):
            # dragging logic
            dx = event.x_root - self._drag_start[0]
            dy = event.y_root - self._drag_start[1]
            new_x = self._drag_orig[0] + dx
            new_y = self._drag_orig[1] + dy

            # Snap to grid (10px increments)
            grid_size = 10
            new_x = round(new_x / grid_size) * grid_size
            new_y = round(new_y / grid_size) * grid_size

            props['x'], props['y'] = int(new_x), int(new_y)
            self.canvas.coords(props['_window_id'], props['x'], props['y'])

            if self.selected == name:
                self._highlight_selected()
                self.prop_x.delete(0, tk.END); self.prop_x.insert(0, props['x'])
                self.prop_y.delete(0, tk.END); self.prop_y.insert(0, props['y'])
                self.apply_properties()

    # Reset on mouse up
    def _on_mouse_up(self, event, name):
        # reset drag/resize states
        self._resize_mode = None
        self._drag_start = None


    # I forget what I planned for this?
    def _on_builder_button_click(self, name):
        pass

    # Identify selected element
    # (Do I actually need to call apply properties at the bottom? Forget why this was done?)
    def select_element(self, name):

        if name not in self.elements:
            return
        self.selected = name
        props = self.elements[name]

        self.prop_id.delete(0, tk.END)
        self.prop_id.insert(0, props['name'])
        self.prop_type.config(text=props['type'])
        self.prop_text.delete(0, tk.END)
        self.prop_text.insert(0, props.get('text', ''))
        self.prop_x.delete(0, tk.END)
        self.prop_x.insert(0, str(props.get('x', 0)))
        self.prop_y.delete(0, tk.END)
        self.prop_y.insert(0, str(props.get('y', 0)))
        self.prop_w.delete(0, tk.END)
        self.prop_w.insert(0, str(props.get('w', 0)))
        self.prop_h.delete(0, tk.END)
        self.prop_h.insert(0, str(props.get('h', 0)))

        self._highlight_selected()
        self.apply_properties()


    # Highlights the selected canvas element (mispelt select as selrect - lol?) It's an easter egg now
    def _highlight_selected(self):
        # remove existing highlight
        self.canvas.delete('selrect')
        if not self.selected: return
        props = self.elements[self.selected]
        wid = props.get('_window_id')
        if not wid: return
        bbox = self.canvas.bbox(wid)
        if not bbox: return
        x1, y1, x2, y2 = bbox
        rect = self.canvas.create_rectangle(x1-2, y1-2, x2+2, y2+2, outline='red', width=2, tags='selrect')
        self.canvas.tag_lower(rect)

    # Also for dragging widgets
    # (I think I apply properties so the property window and code updates as it moves?)
    # Should have added comments as I was building **sighs in lazy developer**
    def _drag_event(self, event, name):
        # move the window anchored to cursor
        x = self.canvas.canvasx(event.x_root - self.canvas.winfo_rootx())
        y = self.canvas.canvasy(event.y_root - self.canvas.winfo_rooty())
        props = self.elements[name]
        props['x'] = int(x)
        props['y'] = int(y)
        self.canvas.coords(props['_window_id'], props['x'], props['y'])
        if self.selected == name:
            self._highlight_selected()
            self.prop_x.delete(0, tk.END); self.prop_x.insert(0, props['x'])
            self.prop_y.delete(0, tk.END); self.prop_y.insert(0, props['y'])
            self.apply_properties()


    # Clear selected element if clicking empty space
    def canvas_click(self, event):
        # deselect if clicked empty area
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        items = self.canvas.find_overlapping(x, y, x, y)
        # find topmost that is a window
        selected = None
        for it in reversed(items):
            tags = self.canvas.gettags(it)
            if tags:
                selected = tags[0]
                break
        if selected is None:
            self.selected = None
            self.canvas.delete('selrect')
            # clear props
            self.prop_id.delete(0, tk.END); self.prop_type.config(text='-'); self.prop_text.delete(0, tk.END)
            self.prop_x.delete(0, tk.END); self.prop_y.delete(0, tk.END)
            self.prop_w.delete(0, tk.END); self.prop_h.delete(0, tk.END)
        


    def apply_properties(self):

        existing_code = self.code_text.get('1.0', tk.END)

        # Not required??? Re-enable if issues with ID changing + saving function names / code
        """preserved_handlers = getattr(self, 'preserved_handlers', {})

        # Re-extract function bodies to preserve edits (optional, for your bookkeeping)
        pattern = r"def\s+(on_\w+_click|get_\w+_data|load_\w+_options)\s*\(\):\n((?:\s{4}.*\n)*)"
        for match in re.finditer(pattern, existing_code):
            func_name = match.group(1)
            body = match.group(2)
            preserved_handlers[func_name] = body.rstrip("\n")"""

        if not self.selected:
            return

        props = self.elements[self.selected]
        old_name = self.selected
        new_name = self.prop_id.get().strip()

        # Validate new_name
        if not new_name:
            messagebox.showerror("Invalid Name", "ID cannot be empty.")
            self.prop_id.delete(0, tk.END)
            self.prop_id.insert(0, self.selected)
            return
        if not new_name.isidentifier():
            messagebox.showerror("Invalid Name", f"'{new_name}' is not a valid identifier.")
            self.prop_id.delete(0, tk.END)
            self.prop_id.insert(0, self.selected)
            return
        if keyword.iskeyword(new_name):
            messagebox.showerror("Invalid Name", f"'{new_name}' is a reserved Python keyword.")
            self.prop_id.delete(0, tk.END)
            self.prop_id.insert(0, self.selected)
            return
        if new_name != old_name and new_name in self.elements:
            messagebox.showerror("Invalid Name", f"An element with ID '{new_name}' already exists.")
            self.prop_id.delete(0, tk.END)
            self.prop_id.insert(0, self.selected)
            return

        # If name changed, update function names in the editor code text
        # IMPORTANT BIT OF CODE
        # When element ID is changed, this makes sure any associated functions
        # receive an update function name matching the new element ID
        # Otherwise, custom written code for the function would be lost
        if new_name != old_name:
            # Patterns of function names to rename
            func_patterns = [
                (f"on_{old_name}_click", f"on_{new_name}_click"),
                (f"get_{old_name}_data", f"get_{new_name}_data"),
                (f"load_{old_name}_options", f"load_{new_name}_options"),
            ]

            updated_code = existing_code
            for old_func, new_func in func_patterns:
                updated_code = re.sub(rf"\b{re.escape(old_func)}\b", new_func, updated_code)

            # Update the code text widget with replaced function names
            self.code_text.delete('1.0', tk.END)
            self.code_text.insert('1.0', updated_code)

            # Rename element dict key and update UI bindings as before
            self.elements[new_name] = self.elements.pop(old_name)
            props = self.elements[new_name]
            props['name'] = new_name

            if '_window_id' in props:
                self.canvas.itemconfig(props['_window_id'], tags=(new_name,))

            frame = props.get('_frame')
            widget = props.get('_widget')
            if frame:
                frame.bind('<Button-1>', lambda e, n=new_name: self._on_mouse_down(e, n))
                frame.bind('<B1-Motion>', lambda e, n=new_name: self._on_mouse_move(e, n))
                frame.bind('<ButtonRelease-1>', lambda e, n=new_name: self._on_mouse_up(e, n))
                frame.bind('<Motion>', lambda e, n=new_name: self._update_cursor(e, n))
            if widget:
                widget.bind('<Button-1>', lambda e, n=new_name: self._on_mouse_down(e, n))
                widget.bind('<B1-Motion>', lambda e, n=new_name: self._on_mouse_move(e, n))
                widget.bind('<ButtonRelease-1>', lambda e, n=new_name: self._on_mouse_up(e, n))
                widget.bind('<Motion>', lambda e, n=new_name: self._update_cursor(e, n))
                widget.bind('<Double-1>', lambda e, n=new_name: self.widget_double_click(e, new_name))

            self.selected = new_name

        # Update properties: text, x, y, w, h
        props['text'] = self.prop_text.get()
        try:
            props['x'] = int(self.prop_x.get())
            props['y'] = int(self.prop_y.get())
            props['w'] = int(self.prop_w.get())
            props['h'] = int(self.prop_h.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Position and size must be integers.")
            return

        self._update_element(self.selected)
        self.generate_code()



    # Deletes an element (widget)
    def _delete_element(self, name):
        
        if name not in self.elements: return
        props = self.elements.pop(name)
        wid = props.get('_window_id')
        if wid:
            self.canvas.delete(wid)
        if self.selected == name:
            self.selected = None
            self.canvas.delete('selrect')
        self.generate_code()

    # Delets an element (widget)
    def delete_selected(self):
        if not self.selected: return
        self._delete_element(self.selected)

    # ------------------- Code generation & running --------------------------

    # Extracts user custom code which should be written between start and end markers
    # Code not written between these spaces may be lost
    def extract_custom_code(self, code_text):
        start_marker = '# !!!!!!!!!!!! INSERT YOUR CODE BELOW THIS COMMENT !!!!!!!!!!!! #'
        end_marker = '# !!!!!!!!!!!! INSERT YOUR CODE ABOVE THIS COMMENT !!!!!!!!!!!! #'

        start_idx = code_text.find(start_marker)
        end_idx = code_text.find(end_marker)

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            # Extract everything between start and end markers
            return code_text[start_idx + len(start_marker):end_idx].strip('\n')
        elif start_idx != -1:
            # If no end_marker found, return everything after start_marker
            return code_text[start_idx + len(start_marker):].strip('\n')
        else:
            return ""


    # This function builds the project code
    # Main sections are:
    # - Imports (the default hardcoded ones)
    # - Users custom code (to go between start and end marker comments)
    #   - User can add additional imports at the top of their section if they like of course
    # - Special generated functions for buttons, treeviews, listboxes, and comboboxes are loaded
    #   - There are in part auto generated
    # - GUI element code is appended at the bottom
    def generate_code(self):

        self.dirty = True
        self._draw_canvas_boundary()
    
        existing_code = self.code_text.get('1.0', tk.END)
        
        # Extract custom user code below marker
        custom_code = getattr(self, 'custom_code', '') or self.extract_custom_code(existing_code)

        
        # Preserve button + treeview functions + combos / lists
        preserved_handlers = getattr(self, 'preserved_handlers', {})

        # Match on this pattern to find functions
        pattern = r"def\s+(on_\w+_click|get_\w+_data|load_\w+_options)\s*\(\):\n((?:\s{4}.*\n)*)"
        for match in re.finditer(pattern, existing_code):
            func_name = match.group(1)
            body = match.group(2)
            preserved_handlers[func_name] = body.rstrip("\n")


        # Start appending the code
        lines = []
        lines.append('import tkinter as tk')
        lines.append('from tkinter import ttk, messagebox, simpledialog')
        lines.append('')

        # Insert marker and preserved user custom code here:
        lines.append('# !!!!!!!!!!!! INSERT YOUR CODE BELOW THIS COMMENT !!!!!!!!!!!! #\n\n')
        if custom_code:
            lines.append(custom_code.rstrip('\n'))
        lines.append('')

        lines.append('\n# !!!!!!!!!!!! INSERT YOUR CODE ABOVE THIS COMMENT !!!!!!!!!!!! #\n')

        lines.append('\n\n\n####################### SPECIAL FUNCTIONS #######################\n')
        lines.append('# In this section, functions are automatically generated for widgets you add')
        lines.append('# to your canvas such as buttons, comboboxes, listboxes, and treeviews.')
        lines.append('\n# These functions should not be manually renamed.')
        lines.append('# Changing the ID of the element in the properties panel will automatically update the function name.')
        lines.append('# You can add code underneath each function.')
        lines.append('# Any code not properly indented into a function will be lost.')

        # --- Button functions ---
        lines.append('\n# --- BUTTON FUNCTIONS ---\n')
        for name, p in self.elements.items():
            if p['type'] == 'Button':
                func_name = f"on_{name}_click"
                if func_name in preserved_handlers:
                    lines.append(f"def {func_name}():")
                    lines.append(preserved_handlers[func_name])
                else:
                    lines.append(f"def {func_name}():")
                    lines.append(f"    # Code for {func_name}")
                    lines.append(f"    pass")
                lines.append('')


        # --- COMBOBOX OPTION LOADER FUNCTIONS ---
        lines.append('\n# --- COMBOBOX OPTION LOADER FUNCTIONS ---\n')
        for name, p in self.elements.items():
            if p['type'] == 'Combobox':
                func_name = f"load_{name}_options"
                if func_name in preserved_handlers:
                    lines.append(f"def {func_name}():")
                    lines.append(preserved_handlers[func_name])
                else:
                    lines.append(f"def {func_name}():")
                    lines.append(f"    # Return the list of options for {name}")
                    lines.append(f"    return ['Option 1', 'Option 2', 'Option 3']")
                lines.append('')

        # --- LISTBOX OPTION LOADER FUNCTIONS ---
        lines.append('\n# --- LISTBOX OPTION LOADER FUNCTIONS ---\n')
        for name, p in self.elements.items():
            if p['type'] == 'Listbox':
                func_name = f"load_{name}_options"
                if func_name in preserved_handlers:
                    lines.append(f"def {func_name}():")
                    lines.append(preserved_handlers[func_name])
                else:
                    lines.append(f"def {func_name}():")
                    lines.append(f"    # Return the list of items for {name}")
                    lines.append(f"    return ['Item 1', 'Item 2', 'Item 3']")
                lines.append('')



        # --- Treeview data functions ---
        lines.append('\n# --- TREEVIEW FUNCTIONS ---\n')
        for name, p in self.elements.items():
            if p['type'] == 'Treeview':
                func_name = f"get_{name}_data"

                if func_name in preserved_handlers:
                    lines.append(f"def {func_name}():")
                    lines.append(preserved_handlers[func_name])
                else:
                    lines.append(f"def {func_name}():")
                    lines.append(f"    # Replace this sample data with your own code.")
                    lines.append("    headers = (\"Name\", \"Age\", \"Job\")")
                    lines.append("    sample_data = [")
                    lines.append("        (\"Alice\", \"25\", \"Teacher\"),")
                    lines.append("        (\"Bob\", \"30\", \"Engineer\"),")
                    lines.append("        (\"Charlie\", \"35\", \"Designer\")")
                    lines.append("    ]")
                    lines.append("    return headers, sample_data")
                lines.append('')

        lines.append('\n######################## AUTO GENERATED GUI ELEMENTS CODE #######################\n')
        lines.append('\n# This code is automatically generated.')
        lines.append('# Any changes you make to the below code manually will be overwritten and lost.\n')
        lines.append('root = tk.Tk()')
        title = getattr(self, 'canvas_title_var', None)
        if title:
            canvas_title = self.canvas_title_var.get()
        else:
            canvas_title = "Generated GUI"
        lines.append(f'root.title({json.dumps(canvas_title)})')

        width = getattr(self, 'canvas_width', 800)
        height = getattr(self, 'canvas_height', 600)
        lines.append(f'root.geometry("{width}x{height}")')
        lines.append('')


        # --- Special variables ---
        radio_groups_done = set()
        for name, p in self.elements.items():
            if p['type'] == 'Checkbutton':
                lines.append(f"{name}_var = tk.BooleanVar()")
            elif p['type'] == 'Radiobutton':
                group_name = p.get('_radio_group_name', name)
                if group_name not in radio_groups_done:
                    lines.append(f"{group_name}_var = tk.StringVar()")
                    radio_groups_done.add(group_name)

                
        lines.append('')
        

        # --- Widget creation ---
        for name, p in self.elements.items():
            t = p['type']
            if t == 'Label':
                lines.append(f"{name} = ttk.Label(root, text={json.dumps(p.get('text',''))})")
            elif t == 'Button':
                func_name = f"on_{name}_click"
                lines.append(f"{name} = ttk.Button(root, text={json.dumps(p.get('text',''))}, command={func_name})")
            elif t == 'Entry':
                lines.append(f"{name} = ttk.Entry(root)")
                if p.get('text'):
                    lines.append(f"{name}.insert(0, {json.dumps(p.get('text'))})")
            elif t == 'TextArea':
                lines.append(f"{name} = tk.Text(root, wrap='word')")
                if p.get('text'):
                    lines.append(f"{name}.insert('1.0', {json.dumps(p.get('text'))})")
            elif t == 'Treeview':
                func_name = p.get('_data_func', f"get_{name}_data")
                lines.append(f"headers, rows = {func_name}()")
                lines.append(f"{name} = ttk.Treeview(root, columns=headers, show='headings')")
                lines.append(f"for col in headers:")
                lines.append(f"    {name}.heading(col, text=col)")
                lines.append(f"    {name}.column(col, width=max(len(str(col)), 10) * 10)")
                lines.append(f"for row in rows:")
                lines.append(f"    {name}.insert('', 'end', values=row)")
            elif t == 'Checkbutton':
                lines.append(f"{name} = ttk.Checkbutton(root, text={json.dumps(p.get('text',''))}, variable={name}_var)")
            elif t == 'Radiobutton':
                group_name = p.get('_radio_group_name', name)
                lines.append(
                    f"{name} = ttk.Radiobutton(root, "
                    f"text={json.dumps(p.get('text',''))}, "
                    f"variable={group_name}_var, "
                    f"value={json.dumps(p.get('text',''))})"
                )
            elif t == 'Listbox':
                func_name = f"load_{name}_options"
                lines.append(f"{name} = tk.Listbox(root)")
                lines.append(f"for item in {func_name}():")
                lines.append(f"    {name}.insert(tk.END, item)")


            elif t == 'Combobox':
                func_name = f"load_{name}_options"
                lines.append(f"{name} = ttk.Combobox(root, values={func_name}())")
                if p.get('text'):
                    lines.append(f"{name}.set({json.dumps(p.get('text'))})")


            else:
                lines.append(f"# Unsupported type: {t}")

            lines.append(f"{name}.place(x={p['x']}, y={p['y']}, width={p['w']}, height={p['h']})")
            lines.append('')

        lines.append("root.mainloop()")
        lines.append("")

        code = '\n'.join(lines)
        self.code_text.delete('1.0', tk.END)
        self.code_text.insert('1.0', code)
        self.highlight_syntax()
        self._update_line_numbers()
        return code


    # Called when clicking the run button.
    # Opens a subprocess to run the users built GUI app
    def run_code(self):
        
        # write code_text content to a temp file and execute it in new process
        code = self.code_text.get('1.0', tk.END)
        
        # basic safety check: disallow certain risky tokens (simple)
        # I have disabled this because meh but could be enabled
        """banned = ['__import__', 'os.system', 'subprocess', 'eval(', 'exec(']
        for b in banned:
            if b in code:
                if not messagebox.askokcancel('Warning', f'Your code contains "{b}" which may be unsafe. Continue?'):
                    return"""
        
        tf = tempfile.NamedTemporaryFile(delete=False, suffix='.py', mode='w', encoding='utf-8')
        tf.write(code)
        tf.flush(); tf.close()
        
        # Try ti run
        try:
            if sys.platform.startswith('win'):
                # detach in windows
                subprocess.Popen([sys.executable, tf.name], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, tf.name])
        except Exception as e:
            messagebox.showerror('Run Error', str(e))

    # ------------------- Theme, Save/Load ----------------------------------

    # Toggling light and dark theme
    def toggle_theme(self):
        self.mode.set('dark' if self.mode.get() == 'light' else 'light')
        self._apply_theme()

    # Apply light or dark theme
    def _apply_theme(self):
        global DARK_MODE

        self.style.configure('Light.TEntry', fieldbackground='white', foreground='black',insertcolor='black')
        self.style.configure('Dark.TEntry', fieldbackground='black', foreground='white',insertcolor='white')
        
        if self.mode.get() == 'dark':
            bg = '#2e2e2e'
            fg = 'white'
            canvas_bg = '#1e1e1e'
            btn_bg = '#000000'
            btn_fg = '#FFFFFF'
            btn_active_bg = '#222222'
            DARK_MODE = True

            self.prop_id.config(style='Dark.TEntry')
            self.prop_text.config(style='Dark.TEntry')
            self.prop_x.config(style='Dark.TEntry')
            self.prop_y.config(style='Dark.TEntry')
            self.prop_w.config(style='Dark.TEntry')
            self.prop_h.config(style='Dark.TEntry')
            self.canvas_title_entry.config(style='Dark.TEntry')
            self.canvas_width_entry.config(style='Dark.TEntry')
            self.canvas_height_entry.config(style='Dark.TEntry')

            # Define tags for syntax highlighting in code editor
            self.code_text.tag_configure("keyword", foreground="orange")
            self.code_text.tag_configure("builtin", foreground="orange")
            self.code_text.tag_configure("comment", foreground="grey")
            self.code_text.tag_configure("string", foreground="green")

            self.code_text.config(insertbackground='white')
            
        else:
            bg = 'white'
            fg = 'black'
            canvas_bg = 'white'
            btn_bg = '#FFFFFF'
            btn_fg = '#000000'
            btn_active_bg = '#CCCCCC'
            DARK_MODE = False
            
            self.prop_id.config(style='Light.TEntry')
            self.prop_text.config(style='Light.TEntry')
            self.prop_x.config(style='Light.TEntry')
            self.prop_y.config(style='Light.TEntry')
            self.prop_w.config(style='Light.TEntry')
            self.prop_h.config(style='Light.TEntry')
            self.canvas_title_entry.config(style='Light.TEntry')
            self.canvas_width_entry.config(style='Light.TEntry')
            self.canvas_height_entry.config(style='Light.TEntry')

            # Define tags for syntax highlighting in code editor
            self.code_text.tag_configure("keyword", foreground="blue")
            self.code_text.tag_configure("builtin", foreground="purple")
            self.code_text.tag_configure("comment", foreground="red")
            self.code_text.tag_configure("string", foreground="green")

            self.code_text.config(insertbackground='black')


        # Configure ttk button style
        self.style.configure('Custom.TButton',
                             background=btn_bg,
                             foreground=btn_fg,
                             borderwidth=1,
                             font=("Calibri", 11))
        self.style.map('Custom.TButton',
                       background=[('active', btn_active_bg)],
                       foreground=[('active', btn_fg)])


        self.style.configure('ProjectMenu.TMenubutton',
                     background=btn_bg,
                     foreground=btn_fg,
                     font=("Consolas", 11))

        #self.project_menu_btn.config(style='ProjectMenu.TMenubutton')

        
        # Apply style to buttons
        for btn in [
            #self.project_menu_btn,
            self.add_label_btn,
            self.add_button_btn,
            self.add_entry_btn,
            self.add_tree_btn,
            self.add_check_btn,
            self.add_radio_btn,
            #self.delete_btn,
            #self.gen_code_btn,
            #self.export_btn,
            self.run_btn,
            self.verify_btn,
            #self.theme_btn,
            #self.save_btn,
            #self.load_btn,
            self.apply_size_btn,
            #self.new_project_btn,
            self.add_textarea_btn,
            self.add_listbox_btn,
            self.add_combobox_btn,
            self.apply_btn
        ]:
            btn.config(style='Custom.TButton')

        
        # Attempt to set theme colors where possible
        try:
            self.configure(bg=bg)
            self.style.configure('.', background=bg, foreground=fg)
            self.style.configure('TLabel', background=bg, foreground=fg)
            self.style.configure('TFrame', background=bg)
            self.style.configure('TButton', background=bg)
            self.code_text.config(bg=canvas_bg, fg = fg)
            self.syntax_output.config(bg=bg)
            self.line_numbers.config(bg=canvas_bg, fg = fg)
            
        except Exception:
            pass
        self.canvas.config(bg=canvas_bg)
        
        self.highlight_syntax()


    # Function for saving project as
    def save_project_as(self):
        
        # Always ask for a new save location (Save As)
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON Files', '*.json')])
        if not path:
            return  # user cancelled

        self.current_save_path = path

        # Call save logic but force saving to this new path
        self._save_to_path(path)

    # Saving logic function
    def _save_to_path(self, path):
        export = {
            'elements': {},
            'custom_code': '',
            'preserved_handlers': {}
        }

        # Save elements
        for name, p in self.elements.items():
            element_data = {k: v for k, v in p.items() if not k.startswith('_')}
            if '_radio_group_name' in p:
                element_data['_radio_group_name'] = p['_radio_group_name']
            export['elements'][name] = element_data

        export['canvas_width'] = getattr(self, 'canvas_width', 800)
        export['canvas_height'] = getattr(self, 'canvas_height', 600)
        export['canvas_title'] = self.canvas_title_var.get()

        existing_code = self.code_text.get('1.0', tk.END)
        export['custom_code'] = self.extract_custom_code(existing_code)

        pattern = r"def\s+(on_\w+_click|get_\w+_data|load_\w+_options)\s*\(\):\n((?:\s{4}.*\n)*)"
        for match in re.finditer(pattern, existing_code):
            func_name = match.group(1)
            body = match.group(2)
            export['preserved_handlers'][func_name] = body.rstrip("\n")

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(export, f, indent=2)

        self.dirty = False
        self.update_window_title_with_path(path)
        messagebox.showinfo('Saved', f'Project saved to {path}')



    # Save function (not save as)
    def save_project(self):
        if self.current_save_path is None:
            path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON Files', '*.json')])
            if not path:
                return
            self.current_save_path = path
        else:
            path = self.current_save_path

        self._save_to_path(path)


    # Updates window title with path of saved project / file (file opened and being edited in the app)
    def update_window_title_with_path(self, path):
        base_title = self.canvas_title_entry.get()  # or however you want it
        self.title(f"{base_title} - {path}")


    # Load a saved project (as json)
    def load_project(self):
        self.code_text.delete("1.0", tk.END)
        
        path = filedialog.askopenfilename(filetypes=[('JSON Files', '*.json')])
        if not path:
            return

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self._clear_canvas()

        # Restore elements
        for name, p in data.get('elements', {}).items():
            base = p['type'].lower()
            try:
                num = int(''.join(filter(str.isdigit, name[len(base):])))
                if num > self.counters[base]:
                    self.counters[base] = num
            except Exception:
                pass
            self.elements[name] = p
            self._create_visual_loaded(p)

        # Restore canvas size and apply it
        self.canvas_width = data.get('canvas_width', 800)
        self.canvas_height = data.get('canvas_height', 600)
        canvas_title = data.get('canvas_title', 'Generated GUI')
        self.canvas_title_var.set(canvas_title)
        self.canvas_width_var.set(str(self.canvas_width))
        self.canvas_height_var.set(str(self.canvas_height))
        self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)

        # Restore custom code + preserved handlers
        self.custom_code = data.get('custom_code', '')
        self.preserved_handlers = data.get('preserved_handlers', {})

        # Re-generate code using loaded code and handlers
        self.generate_code()

        self.dirty = False
        self.current_save_path = path  # the loaded file path
        self.update_window_title_with_path(path)

    # Function to support closing the app
    # Used to warn user about unsaved changes
    def on_close(self):
        if self.dirty:
            result = messagebox.askyesnocancel("Unsaved Changes",
                "You have unsaved changes. Would you like to save before exiting?")
            if result is True:
                # User chose yes, save first
                self.save_project()
                # Then close
                self.destroy()
            elif result is False:
                # User chose no, just close without saving
                self.destroy()
            else:
                # Cancel, do nothing
                return
        else:
            self.destroy()


    # For exporting code in the code editor to a .py file
    def export_code(self):
        """Export the code editor contents as a .py file."""
        from tkinter import filedialog, messagebox

        # Ask where to save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
            title="Export Python Code"
        )

        if not file_path:
            return  # User cancelled

        try:
            code_content = self.code_text.get("1.0", tk.END).strip()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_content)
            messagebox.showinfo("Export Successful", f"Code exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred:\n{e}")

    # Create a new project
    # Warns user any unsaved changes will be lost
    def new_project(self):
        # Ask for confirmation
        if not messagebox.askyesno("Confirm New Project", 
                                   "Are you sure you want to start a new project?\nAll unsaved work will be lost."):
            return  # user cancelled

        # Clear properties input fields
        self.prop_id.delete(0, tk.END)
        self.prop_text.delete(0, tk.END)
        self.prop_x.delete(0, tk.END)
        self.prop_y.delete(0, tk.END)
        self.prop_w.delete(0, tk.END)
        self.prop_h.delete(0, tk.END)

        # Clear the code editor text
        self.code_text.delete('1.0', tk.END)

        # Reset selected element
        self.selected = None

        # Clear preserved handlers if present
        if hasattr(self, 'preserved_handlers'):
            self.preserved_handlers.clear()

        # Clear custom code
        self.custom_code = ''

        # Reset elements and related state
        self.elements = {}  # name -> metadata
        self.radio_groups = {}
        self.counters = defaultdict(int)  # for naming

        # Clear canvas visuals
        self.canvas.delete("all")

        # Update existing StringVars
        self.canvas_width_var.set("800")
        self.canvas_height_var.set("600")
        self.canvas_title_var.set("Generated GUI")

        # Update canvas config to reflect new sizes
        self.canvas.config(
            scrollregion=(0, 0, int(self.canvas_width_var.get()), int(self.canvas_height_var.get())),
            width=int(self.canvas_width_var.get()),
            height=int(self.canvas_height_var.get())
        )

        # Apply canvas size changes
        self.apply_canvas_size()

        # Regenerate code to clear the editor properly
        self.generate_code()


    # Clear the canvas
    def _clear_canvas(self):
        # Delete all canvas items
        self.canvas.delete("all")
        
        # Clear element references and selection
        self.elements.clear()
        self.selected = None



if __name__ == '__main__':
    app = GUIBuilderApp()
    app.mainloop()
