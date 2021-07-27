## by Miguel Ángel Alarcos Torrecillas on Thu, 6 Sep 2012 (MIT) 

import tkinter as tk
from tkinter import ttk
import re

class AutocompleteEntry(ttk.Entry):
    def __init__(self, container, window, suggestions, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.suggestions = suggestions
        self.lb_up = False
        self.window = window

        self.var = tk.StringVar()
        self.var.trace('w', self.changed)
        self.entry = tk.Entry(self, textvariable=self.var)
        self.entry.pack(fill=tk.BOTH, expand=True)
        
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        self.bind("<Configure>", self.configure)

        # frame used to place bounding frame arbitrarily
        self.listBoxPlacingFrame = tk.Frame(container, borderwidth = 1, relief=tk.RIDGE, bg="Green")



        # frame used to specify dimensions of list box arbitrarily
        self.listBoxBoundingFrame = tk.Frame(self.listBoxPlacingFrame, borderwidth = 1, relief=tk.RIDGE, bg="Red")
        self.listBoxBoundingFrame.grid(row=0, column=1)
        self.listBoxBoundingFrame.columnconfigure(0, weight=10)
        self.listBoxBoundingFrame.grid_propagate(False)

        self.positionListBox()

    def changed(self, name, index, mode):  
        if self.var.get() == '' and self.lb_up:
            self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:            
                if not self.lb_up:
                    self.listBoxScrollbarFrame = tk.Frame(self.listBoxBoundingFrame, borderwidth = 1, relief=tk.RIDGE, bg='Blue')
                    scrollbar = tk.Scrollbar(self.listBoxScrollbarFrame, orient="vertical")
                    self.lb = tk.Listbox(self.listBoxScrollbarFrame, yscrollcommand=scrollbar.set)
                    scrollbar.config(command=self.lb.yview)
                    scrollbar.pack(side="right", fill="y")
                    self.lb.pack(side="left",fill="both", expand=True)

                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    
                    self.lb_up = True
                    
                    self.positionListBox()
                    
                    
                self.lb.delete(0, tk.END)
                for w in words:
                    self.lb.insert(tk.END,w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False
        
    def selection(self, event):
        if self.lb_up:
            self.var.set(self.lb.get(tk.ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(tk.END)

    def up(self, event):
        if self.lb_up:
            index = '0' if self.lb.curselection() == () else self.lb.curselection()[0]
            if index != '0':                
                self.lb.selection_clear(first=index)
                index = str(int(index)-1)                
                self.lb.selection_set(first=index)
                self.lb.activate(index) 

    def down(self, event):
        if self.lb_up:
            index = '0' if self.lb.curselection() == () else self.lb.curselection()[0]
            if index != tk.END:                        
                self.lb.selection_clear(first=index)
                index = str(int(index)+1)        
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def comparison(self):
        pattern = re.compile('.*' + self.var.get() + '.*')
        return [w for w in self.suggestions if re.match(pattern, w)]
    
    def configure(self, event):
        print('frame dimensions', self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height())
        print('window dimensions', self.window.winfo_x(), self.window.winfo_y(), self.window.winfo_width(), self.window.winfo_height())
        self.min_height = self.winfo_height()
        self.max_height = self.min_height * 4
        self.positionListBox()
    
    # one can not simply set list box widget width and height or position it directly
    def positionListBox(self):
        if not self.lb_up:
            return
        x, y, width, height = self.computeListBoxConfig()
        print('list dimensions', x, y, width, height)
        self.listBoxPlacingFrame.place(x=x, y=y)
        self.listBoxPlacingFrame.configure(width=width, height=height)
        self.listBoxBoundingFrame.configure(width=width, height=height)
        self.listBoxScrollbarFrame.grid(sticky=tk.W+tk.E+tk.N+tk.S)
        self.listBoxScrollbarFrame.configure(width=width, height=height)
        self.lb.config(width=0,height=4)

    def computeListBoxConfig(self):
        # place below
        if self.winfo_y() + self.winfo_height() + self.min_height < self.window.winfo_height():
            overflow = self.window.winfo_height() - self.winfo_y() - self.winfo_height() - self.max_height
            height = self.max_height + overflow if overflow < 0 else self.max_height
            return self.winfo_x(), self.winfo_y() + self.winfo_height(), self.winfo_width(), height
        # place above
        if self.winfo_y() - self.min_height > 0:
            overflow = self.winfo_y() - self.max_height
            height = self.max_height + overflow if overflow < 0 else self.max_height
            return self.winfo_x(), self.winfo_y() - height, self.winfo_width(), height
        # place over
        return self.winfo_x(), self.winfo_y(), self.winfo_width(), self.min_height
        
