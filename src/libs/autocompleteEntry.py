import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import re
import math

MAX_LINES = 16

def traverse_up(widget, function, initializer = None):
    return function(widget, traverse_up(widget.master, function, initializer) if hasattr(widget, 'master') else initializer)

class AutocompleteEntry(ttk.Frame):
    def __init__(self, container, suggestions, textvariable=None, bounding_container=None, window=None, font=None, *args, **kwargs):
        super().__init__(container, *args, **kwargs)  
        self.lb_up = False

        self.bounding_container = bounding_container if bounding_container else self

        self.container = container
        self.suggestions = suggestions
        self.window = window

        self.var = textvariable if textvariable else tk.StringVar()
        self.var.trace('w', self.changed)
        self.entry = ttk.Entry(self, textvariable=self.var)
        self.entry.pack(fill=tk.X, expand=True)
 
        self.bind("<Configure>", self.configure)
        self.bind('<FocusOut>', self.focus_out )
    
    def focus_out(self, event):
        if not self.lb_up:
            return
        print(str(self.focus_get()), repr(str(self.lb)))
        if repr(str(self.focus_get())) == repr(str(self.lb)):
            return
        self.destroy_list_box()

    def create_list_box(self):
        self.lb = tk.Listbox(self.bounding_container, relief=tk.RAISED, highlightthickness=1, activestyle='none')
        self.lb.bind("<Double-Button-1>", self.selection)
        self.lb.bind("<Return>", self.selection)
        self.lb.bind('<FocusOut>', self.focus_out )
        self.lb_up = True
    
    def destroy_list_box(self):
        if not self.lb_up:
            return
        self.lb.destroy()
        self.lb_up = False

    def position_list_box(self):
        if not self.lb_up:
            return
        x, y, width, height = self.compute_list_box_config()
        self.lb.configure(height=math.floor(height / self.min_height))
        self.lb.place(in_=self.bounding_container, x=x - self.container.winfo_x(), y=y, width=width) # NOTE: somehow take paddings into consideration
        

    def compute_list_box_config(self):
        # place below if distance between lowest points of container and bounding container is more than minimal listbox height
        bounding_y = traverse_up(self.bounding_container, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, 0)
        container_y = traverse_up(self.container, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, 0)
        distance = bounding_y + self.bounding_container.winfo_height() - container_y - self.container.winfo_height()
        if distance > self.min_height:
            overflow = distance - self.max_height
            height = math.floor((self.max_height + overflow if overflow < 0 else self.max_height) / self.min_height) * self.min_height           
            return (
                traverse_up(self, lambda widget, acc: widget.winfo_x() + acc if widget and widget.master else acc, 0),
                traverse_up(self, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, self.winfo_height()),
                self.winfo_width(),
                height
            )
        # place above
        distance = self.container.winfo_y() - self.bounding_container.winfo_y()
        if distance > self.min_height:
            overflow = distance - self.max_height
            height =  math.floor((self.max_height + overflow if overflow < 0 else self.max_height) / self.min_height) * self.min_height
            return (
                traverse_up(self, lambda widget, acc: widget.winfo_x() + acc if widget and widget.master else acc, 0),
                traverse_up(self, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, -height),
                self.winfo_width(),
                height
            )

    def changed(self, *args):
        if self.var.get() == '' and self.lb_up:
            self.destroy_list_box()
            return
        words = self.comparison()
        if words:
            if not self.lb_up:
                self.create_list_box()
            self.lb.delete(0, tk.END)
            for w in words:
                self.lb.insert(tk.END,w)
            self.max_height = min(self.min_height * MAX_LINES, self.min_height * len(words))
            self.position_list_box()
        else:
            self.destroy_list_box()
        
    def selection(self, event):
        if not self.lb_up:
            return
        self.lb.get(tk.ACTIVE)
        self.var.set(self.lb.get(tk.ACTIVE))
        self.destroy_list_box()
        self.entry.icursor(tk.END)

    def up(self, event):
        if not self.lb_up:
            return
        index = '0' if self.lb.curselection() == () else self.lb.curselection()[0]
        self.lb.selection_clear(first=index)
        index = str(max(int(index)-1, 0))              
        self.lb.selection_set(first=index)
        self.lb.event_generate("<<ListboxSelect>>")

    def down(self, event):
        if not self.lb_up:
            return
        index = '0' if self.lb.curselection() == () else self.lb.curselection()[0]
        self.lb.selection_clear(first=index)
        index = str(min(int(index)+1, self.lb.size() - 1)) if index != '0' else '0'
        self.lb.selection_set(first=index)
        self.lb.event_generate("<<ListboxSelect>>")

    def comparison(self):
        pattern = re.compile('.*' + self.var.get() + '.*')
        return [w for w in self.suggestions if re.match(pattern, w)]
    
    def configure(self, event):
        self.min_height = self.winfo_height()
        self.position_list_box()