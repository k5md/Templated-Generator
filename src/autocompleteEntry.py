## by Miguel Ángel Alarcos Torrecillas on Thu, 6 Sep 2012 (MIT) 

import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import re
import math

MAX_LINES = 16

def traverseUp(widget, function, initializer = None):
    return function(widget, traverseUp(widget.master, function, initializer) if hasattr(widget, 'master') else initializer)

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
        self.entry = tk.Entry(self, textvariable=self.var)
        self.entry.pack(fill=tk.X, expand=True)
        self.font = tk.font.Font(font=font)
 
        self.bind("<Configure>", self.configure)
        #self.bind('<FocusIn>', lambda _: self.changed())
        self.bind('<FocusOut>', self.focusOut )
    
    def focusOut(self, event):
        print('focus out')
        if not self.lb_up:
            return
        print(str(self.focus_get()), repr(str(self.lb)))
        if repr(str(self.focus_get())) == repr(str(self.lb)):
            return
        self.destroyListBox()

    def createListBox(self):
        # frame used to place bounding frame arbitrarily


        # frame containing scrollable listbox
        #self.listBoxScrollbarFrame = tk.Frame(self.bounding_container)

        self.lb = tk.Listbox(self.bounding_container, relief=tk.RAISED, highlightthickness=1)
        self.lb.bind("<Double-Button-1>", self.selection)
        self.lb.bind("<Return>", self.selection)
        self.lb.bind('<FocusOut>', self.focusOut )

        #self.scrollbar = tk.Scrollbar(self.listBoxScrollbarFrame)
        #self.scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        #self.lb.config(yscrollcommand = self.scrollbar.set)
        #self.scrollbar.config(command = self.lb.yview)

        self.lb_up = True
    
    def destroyListBox(self):
        if not self.lb_up:
            return
        self.lb.destroy()
        self.lb_up = False

    # one can not simply set list box widget width and height or position it directly
    def positionListBox(self):
        if not self.lb_up:
            return
        x, y, width, height = self.computeListBoxConfig()
        print({'x': x, 'y': y, 'width': width, 'height': height})
        print(self.entry.winfo_y())

        #self.lb.pack(fill="both", expand=True)
        self.lb.configure(height=math.floor(height / self.min_height))
        print(math.floor(height / self.min_height))

        self.lb.place(in_=self.bounding_container, x=x, y=y, width=width)
        

    def computeListBoxConfig(self):
        # self.max_height must be multiple of self.min_height
        # returned height must be a multiple of min_height, that is, of one-row text entry widget height
        # otherwise outer frames will either be too long or too short to display list box
        print('self', {'x': self.winfo_x(), 'y': self.winfo_y(), 'width': self.winfo_width(), 'height': self.winfo_height()})
        print('container', {'x': self.container.winfo_x(), 'y': self.container.winfo_y(), 'width': self.container.winfo_width(), 'height': self.container.winfo_height()})
        print('bounding_container', {'x': self.bounding_container.winfo_x(), 'y': self.bounding_container.winfo_y(), 'width': self.bounding_container.winfo_width(), 'height': self.bounding_container.winfo_height()})
        print('window', {'x': self.window.winfo_x(), 'y': self.window.winfo_y(), 'width': self.window.winfo_width(), 'height': self.window.winfo_height()})
        #print('scrollbar', {'x': self.scrollbar.winfo_x(), 'y': self.scrollbar.winfo_y(), 'width': self.scrollbar.winfo_width(), 'height': self.scrollbar.winfo_height()})
        # place below if distance between lowest points of container and bounding container is more than minimal listbox height
        bounding_y = traverseUp(self.bounding_container, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, 0)
        container_y = traverseUp(self.container, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, 0)
        distance = bounding_y + self.bounding_container.winfo_height() - container_y - self.container.winfo_height()
        if distance > self.min_height:
            overflow = distance - self.max_height
            height = math.floor((self.max_height + overflow if overflow < 0 else self.max_height) / self.min_height) * self.min_height
            # NOTE: investigate, why just setting height results in widget overflowing bounding container
            #height = height - self.min_height * 2 if height - self.min_height * 2 > self.min_height else height
            
            return (
                traverseUp(self, lambda widget, acc: widget.winfo_x() + acc if widget and widget.master else acc, 0),
                traverseUp(self, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, self.winfo_height()),
                self.winfo_width(),
                height
            )
        # place above
        distance = self.container.winfo_y() - self.bounding_container.winfo_y()
        if distance > self.min_height:
            overflow = distance - self.max_height
            height =  math.floor((self.max_height + overflow if overflow < 0 else self.max_height) / self.min_height) * self.min_height
            return (
                traverseUp(self, lambda widget, acc: widget.winfo_x() + acc if widget and widget.master else acc, 0),
                traverseUp(self, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, -height),
                self.winfo_width(),
                height
            )

    def changed(self, *args):
        print('changed')
        
        if self.var.get() == '' and self.lb_up:
            self.destroyListBox()
            return
        #if self.lb_up: self.lb.event_generate("<<FocusIn>>")
        words = self.comparison()
        if words:
            if not self.lb_up:
                self.createListBox()
            self.lb.delete(0, tk.END)
            for w in words:
                self.lb.insert(tk.END,w)
            self.max_height = min(self.min_height * MAX_LINES, self.min_height * len(words))
            self.positionListBox()
        else:
            self.destroyListBox()
        
    def selection(self, event):
        if not self.lb_up:
            return
        self.lb.get(tk.ACTIVE)
        self.var.set(self.lb.get(tk.ACTIVE))
        self.destroyListBox()
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
        # self.bounding_container.winfo_height() yields height of entry with 1-row
        # since we can not get text entry, listbox height directly (they yield height in rows), we take this self.bounding_container.winfo_height()
        # and use it to calculate possible height in rows
        self.min_height = self.winfo_height()
        self.positionListBox()