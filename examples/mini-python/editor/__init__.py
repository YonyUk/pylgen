import sys
import threading
from queue import Queue
import tkinter as tk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox
from typing import Callable
from cupcake import Editor,Languages
from datetime import datetime

from pylgen.lexer import Lexer
from pylgen.parser import Parser
from pylgen.analysis import Context,ASTWalker,ErrorType,Error
from pylgen.visual import draw_ast,draw_parse_tree_from_parser,set_cache_file

class TerminalOutputBridge:

    def __init__(self,text_widget:tk.Text,update_interval=100) -> None:
        self._widget = text_widget
        self._queue = Queue()
        self._interval = update_interval

    def write(self,text:str) -> None:
        if not text:
            return

        done = threading.Event()

        def do_write():
            try:
                self._widget.configure(state=tk.NORMAL)
                if text == '\033c':
                    self._widget.delete(1.0, tk.END)
                else:
                    self._widget.insert(tk.END, text)
                    self._widget.see(tk.END)
                self._widget.configure(state=tk.DISABLED)
            finally:
                done.set()

        self._widget.after(0, do_write)
        done.wait()

    def flush(self):
        pass

class TerminalInputBridge:

    def __init__(
            self,
            queue:Queue,
            editor:tk.Widget,
            callback:Callable[[str],None],
            editor_set_writable_callback:Callable[[],None]
        ) -> None:
        self._queue = queue
        self._callback = callback
        self._e_w_callback = editor_set_writable_callback
        self._editor = editor

    def readline(self,prompt=""):

        def setup():
            self._callback(prompt)
            self._e_w_callback()

        self._editor.after(0,setup)
        line = self._queue.get()
        return f'{line}\n'

class Popup(tk.Toplevel):

    def __init__(self, master,title:str,callback:Callable[[str],None],on_cancel_callback:Callable|None=None,*args,**kwargs) -> None:
        super().__init__(master,*args,**kwargs)
        self.title(title)
        self._callback = callback
        if on_cancel_callback:
            self.wm_protocol('WM_DELETE_WINDOW',on_cancel_callback)
        self._on_cancel_callback = on_cancel_callback
        self.geometry('300x100')

        text_panel = tk.Frame(self)
        text_panel.pack(side=tk.TOP)
        label = tk.Label(text_panel,text='Please, provide a name for the HTML file result:')
        label.pack(side=tk.TOP)

        control_panel = tk.Frame(self)
        control_panel.pack(side=tk.BOTTOM)
        self._text_var = tk.StringVar(control_panel)
        text_input = tk.Entry(control_panel,textvariable=self._text_var)
        text_input.pack(side=tk.TOP)

        buttons_panel = tk.Frame(control_panel)
        buttons_panel.pack(side=tk.BOTTOM,pady=3,fill=tk.X,expand=True)

        self.btn_accept = tk.Button(buttons_panel,text='Accept',command=lambda:self._accept())
        self.btn_cancel = tk.Button(buttons_panel,text='Cancel',command=lambda:self._cancel())

        self.btn_accept.pack(side=tk.LEFT,padx=5)
        self.btn_cancel.pack(side=tk.RIGHT,padx=5)

    def _accept(self):
        text = self._text_var.get()
        if text.strip() == '':
            messagebox.showwarning('Empty Text','A non-empty name must be provided')
        else:
            self.grab_release()
            self._callback(text)
            self.after(0,self.destroy)

    def _cancel(self):
        if self._on_cancel_callback:
            self._on_cancel_callback()
        self.grab_release()
        self.after(0,self.destroy)

class PythonEditor(Editor):

    def __init__(
            self,
            lexer:Lexer,
            parser:Parser,
            context:Context, 
            collector:ASTWalker,
            checker:ASTWalker,
            evaluator:ASTWalker,
            *args,
            **kwargs
        ) -> None:
        super().__init__(tk.Tk(), language=Languages.PYTHON, *args, **kwargs)
        self.master.title('Python Subset Interpreter') # type: ignore
        self.master.wm_state('zoomed') # type: ignore
        self._lexer = lexer
        self._lexer.initialize()
        self._parser = parser
        self._context = context
        self._collector = collector
        self._checker = checker
        self._evaluator = evaluator

        control_panel = tk.Frame(self.master)
        control_panel.pack(expand=True,fill=tk.BOTH,padx=1,pady=1)

        self.btn_run = tk.Button(control_panel,text='Run',command=lambda:self._execute())
        self.btn_run.pack(side=tk.LEFT,padx=1)
        self.btn_draw_ast = tk.Button(control_panel,text='Draw AST',command=lambda:self._draw_ast())
        self.btn_draw_ast.pack(side=tk.LEFT,padx=1)
        self.btn_draw_parse_tree = tk.Button(control_panel,text='Draw Parse Tree',command=lambda:self._draw_parse_tree())
        self.btn_draw_parse_tree.pack(side=tk.LEFT,padx=1)
        self.btn_load_cache = tk.Button(control_panel,text='Load Cache',command=lambda:self._load_cache())
        self.btn_load_cache.pack(side=tk.LEFT,padx=1)

        upper = tk.Frame(self.master)
        upper.pack(expand=True,fill=tk.BOTH,pady=2)
        self.pack(expand=True,fill=tk.BOTH)

        lower = tk.Frame(self.master)
        lower.pack(expand=True,fill=tk.BOTH,pady=2)
        terminal_font = font.Font(family='Consolas',size=12,weight='normal')
        self.terminal = tk.Text(lower,state=tk.DISABLED,font=terminal_font)
        sys.stdout = TerminalOutputBridge(self.terminal)
        self._input_queue = Queue()
        sys.stdin = TerminalInputBridge(self._input_queue,self,self._input_callback,self._editor_set_writable_callback)
        self.terminal.configure(bg='black',fg='white',insertbackground='white',state=tk.DISABLED)
        self.terminal.pack(expand=True,fill=tk.BOTH)

        self.content.tag_config("error",background='red',foreground='black') # type: ignore
        self._input_start = '1.0'
        self._waiting_input = False
        self._cache_option = False

        self._config_keyboard_events()

        self.master.mainloop()

    def _clear_error_highlights(self):
        try:
            self.content.tag_remove("error",1.0,tk.END) # type: ignore
        except Exception:
            pass

    def _highlight_error(self,error:Error):
        line = error.line
        column = error.column
        err_index = f'{line}.{column}'
        start_idx = f'{line}.0'
        end_idx = f'{line}.end'
        self.content.tag_add("error",start_idx,end_idx) # type: ignore
        self.content.mark_set(tk.INSERT,err_index) # type: ignore
        self.content.see(err_index) # type: ignore
        self.content.focus_set()

    def _input_callback(self,prompt):
        self.terminal.configure(state=tk.NORMAL)
        self.terminal.insert(tk.END,prompt)
        self.terminal.see(tk.END)

    def _editor_set_writable_callback(self):
        self._input_start = self.terminal.index(tk.END + '-1c')
        self._waiting_input = True
        self.terminal.mark_set(tk.INSERT,tk.END)
        self.terminal.see(tk.END)
        self.terminal.focus_set()

    def _config_keyboard_events(self):
        self.terminal.bind('<Key>',self._on_key)
        self.terminal.bind('<BackSpace>',self._on_backspace)
        self.terminal.bind('<Delete>',self._on_delete)
        self.terminal.bind('<Left>',self._on_left)
        self.terminal.bind('<Up>',self._on_up)
        self.terminal.bind('<Home>',self._on_home)
        self.terminal.bind('<Button-1>',self._on_click)

    def _on_key(self,event:tk.Event):
        if not self._waiting_input:
            return 'break'
        if event.keysym == 'Return':
            if not self._waiting_input:
                return 'break'
            text = self.terminal.get(self._input_start,tk.END).strip()
            self.terminal.insert(tk.END,'\n')
            self._input_start = self.terminal.index(tk.END + '-1c')
            self._waiting_input = False
            self.terminal.configure(state=tk.DISABLED)
            self._waiting_input = False
            self._input_queue.put(text)
            return 'break'
        if self.terminal.compare(tk.INSERT,'<',self._input_start):
            self.terminal.mark_set(tk.INSERT,tk.END)
        return None

    def _on_backspace(self,event:tk.Event):
        if not self._waiting_input:
            return 'break'
        if self.terminal.tag_ranges(tk.SEL):
            sel_start = self.terminal.index(tk.SEL_FIRST)
            if self.terminal.compare(sel_start,'<',self._input_start):
                return 'break'
        if self.terminal.compare(tk.INSERT,'<=',self._input_start):
            return 'break'
        return None

    def _on_delete(self,event:tk.Event):
        if not self._waiting_input:
            return 'break'
        if self.terminal.compare(tk.INSERT,'<',self._input_start):
            return 'break'
        return None

    def _on_left(self,event:tk.Event):
        if not self._waiting_input:
            return 'break'
        if self.terminal.compare(tk.INSERT,'<=',self._input_start):
            return 'break'
        return None

    def _on_up(self,event:tk.Event):
        return 'break'

    def _on_home(self,event:tk.Event):
        if not self._waiting_input:
            return 'break'
        if self.terminal.compare(tk.INSERT,'<=',self._input_start):
            return 'break'
        return None

    def _on_click(self,event:tk.Event):
        if not self._waiting_input:
            return 'break'
        index = self.terminal.index(f"@{event.x},{event.y}")
        if self.terminal.compare(index,'<',self._input_start):
            self.terminal.mark_set(tk.INSERT,tk.END)
            return 'break'
        return None

    def _load_cache(self):
        cache_file = filedialog.askopenfilename()
        set_cache_file(cache_file)
        self._cache_option = True

    def _draw_ast(self):
        self._lexer.clear_errors()
        self._parser.reset()
        self._context.reset()
        code = self.content.text.get_all_text() # type: ignore
        if code.strip() == '':
            return
        self._lexer.load_text(code)
        ast = self._parser.parse(self._lexer.tokens)

        def get_name(text):
            draw_ast(ast,filename=text,show=True,cache=self._cache_option)

        popup = Popup(self,'Filename?',get_name)
        popup.grab_set()
        popup.focus_set()
        popup.wait_window()

    def _draw_parse_tree(self):
        self._lexer.clear_errors()
        self._parser.reset()
        self._context.reset()
        code = self.content.text.get_all_text() # type: ignore
        if code.strip() == '':
            return
        self._parser.set_draw_parse_tree_flag(True)
        self._lexer.load_text(code)
        _ = self._parser.parse(self._lexer.tokens)

        def _on_cancel():
            self._parser.set_draw_parse_tree_flag(False)

        def get_name(text):
            draw_parse_tree_from_parser(self._parser,filename=text,show=True,cache=self._cache_option)
            self._parser.set_draw_parse_tree_flag(False)

        popup = Popup(self,'Filename?',get_name,_on_cancel)
        popup.grab_set()
        popup.focus_set()
        popup.wait_window()

    def _execute(self):
        self.terminal.configure(state=tk.NORMAL)
        self.terminal.delete(1.0,tk.END)
        self.terminal.configure(state=tk.DISABLED)
        self._input_start = '1.0'
        self._waiting_input = False
        self._lexer.clear_errors()
        self._parser.reset()
        self._context.reset()
        self._clear_error_highlights()

        thread = threading.Thread(target=self._run_code,daemon=True)
        thread.start()

    def _run_code(self):

        def make_normal():
            self.terminal.configure(state=tk.NORMAL)

        def make_disabled():
            self.terminal.configure(state=tk.DISABLED)

        def insert(text):
            self.terminal.insert(tk.END,text)

        def see():
            self.terminal.see(tk.END)

        def lock_btns():
            self.btn_run.configure(state=tk.DISABLED)
            self.btn_draw_ast.configure(state=tk.DISABLED)
            self.btn_draw_parse_tree.configure(state=tk.DISABLED)
            self.btn_load_cache.configure(state=tk.DISABLED)

        def unlock_btns():
            self.btn_run.configure(state=tk.NORMAL)
            self.btn_draw_ast.configure(state=tk.NORMAL)
            self.btn_draw_parse_tree.configure(state=tk.NORMAL)
            self.btn_load_cache.configure(state=tk.NORMAL)

        self.btn_run.after(0,lock_btns)

        code = self.content.text.get_all_text() # type: ignore
        if code.strip() == '':
            self.btn_run.after(0,unlock_btns)
            return
        
        t = datetime.now()
        self._lexer.load_text(code)
        ast = self._parser.parse(self._lexer.tokens)
        errors = list(self._lexer.errors) + self._parser.errors
        no_sintax_errors = list(filter(lambda error:error.type != ErrorType.SEMANTIC,errors))
        if no_sintax_errors:
            self.terminal.after(0,make_normal)
            for error in no_sintax_errors:
                self.terminal.after(0,insert,f'{error}\n')
                self.after(0,self._highlight_error,error)
            self.terminal.after(0,see)
            self.terminal.after(0,make_disabled)
            self.btn_run.after(0,unlock_btns)
            return
        self._collector.walk(ast)
        self._checker.walk(ast)
        errors.extend(self._context.errors)
        if errors:
            self.terminal.after(0,make_normal)
            for error in errors:
                self.terminal.after(0,insert,f'{error}\n')
                self.after(0,self._highlight_error,error)
            self.terminal.after(0,see)
            self.terminal.after(0,make_disabled)
            self.btn_run.after(0,unlock_btns)
            return

        self._evaluator.walk(ast)
        errors.extend(self._context.errors)
        if errors:
            self.terminal.after(0,make_normal)
            for error in errors:
                self.terminal.after(0,insert,f'{error}\n')
                self.after(0,self._highlight_error,error)
            self.terminal.after(0,see)
            self.terminal.after(0,make_disabled)
            self.btn_run.after(0,unlock_btns)
            return

        self.terminal.after(0,make_normal)
        val = self._context.last_instruction_result # type: ignore
        if not val is None:
            self.terminal.after(0,insert,f'{val}\n')
        self.terminal.after(0,insert,f'\nexecution time: {datetime.now() - t}')
        self.terminal.after(0,see)
        self.terminal.after(0,make_disabled)
        self.btn_run.after(0,unlock_btns)