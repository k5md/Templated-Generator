## by Miguel Ángel Alarcos Torrecillas on Thu, 6 Sep 2012 (MIT) 

import tkinter as tk
from tkinter import ttk
import re
import math

class AutocompleteEntry(ttk.Frame):
    def __init__(self, container, suggestions, *args, **kwargs):
        super().__init__(container, *args, **kwargs)  
        self.lb_up = False

        self.container = container
        self.suggestions = suggestions

        self.var = tk.StringVar()
        self.var.trace('w', self.changed)
        self.entry = tk.Entry(self, textvariable=self.var)
        self.entry.pack(fill=tk.X, expand=True)
        
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        self.bind("<Configure>", self.configure)

    def createListBox(self):
        # frame used to place bounding frame arbitrarily
        self.listBoxPlacingFrame = tk.Frame(self.container)

        # frame used to specify dimensions of list box arbitrarily
        self.listBoxBoundingFrame = tk.Frame(self.listBoxPlacingFrame)

        # frame containing scrollable listbox
        self.listBoxScrollbarFrame = tk.Frame(self.listBoxBoundingFrame)

        #self.scrollbar = tk.Scrollbar(self.listBoxScrollbarFrame, orient="vertical")
        #self.lb = tk.Listbox(self.listBoxScrollbarFrame, yscrollcommand=self.scrollbar.set)
        self.lb = tk.Listbox(self.listBoxScrollbarFrame)
        #self.scrollbar.config(command=self.lb.yview)
        self.lb.bind("<Double-Button-1>", self.selection)
        self.lb.bind("<Right>", self.selection)
        #self.scrollbar.pack(side="right", fill="y")
        #self.lb.pack(side="left",fill="both", expand=True)

        self.lb_up = True
    
    def destroyListBox(self):
        if not self.lb_up:
            return
        self.listBoxPlacingFrame.destroy()
        self.lb_up = False

    # one can not simply set list box widget width and height or position it directly
    def positionListBox(self):
        if not self.lb_up:
            return
        x, y, width, height = self.computeListBoxConfig()

        #self.lb.place(in_=self.listBoxScrollbarFrame, relx=0, rely=0)
        self.lb.pack(fill="both", expand=True)
        self.lb.configure(height=math.floor(height / self.min_height))
        self.lb.update()

        self.listBoxScrollbarFrame.place(in_=self.listBoxBoundingFrame, relx=0, rely=0, relheight=1, relwidth=1)
        #self.listBoxScrollbarFrame.configure(width=width, height=height)
        self.listBoxScrollbarFrame.update()

        self.listBoxBoundingFrame.place(in_=self.listBoxPlacingFrame, relx=0, rely=0, relheight=1, relwidth=1)
        #self.listBoxBoundingFrame.configure(width=width, height=height)
        self.listBoxBoundingFrame.update()

        self.listBoxPlacingFrame.place(in_=self.container, x=x, y=y)
        self.listBoxPlacingFrame.configure(width=width, height=height)
        self.listBoxPlacingFrame.update()

    def computeListBoxConfig(self):
        # self.max_height must be multiple of self.min_height
        # returned height must be a multiple of min_height, that is, of one-row text entry widget height
        # otherwise outer frames will either be too long or too short to display list box
        # place below
        if self.winfo_y() + self.winfo_height() + self.min_height < self.container.winfo_height():
            overflow = self.container.winfo_height() - self.winfo_y() - self.winfo_height() - self.max_height
            height = math.floor((self.max_height + overflow if overflow < 0 else self.max_height) / self.min_height) * self.min_height
            return self.winfo_x(), self.winfo_y() + self.winfo_height(), self.winfo_width(), height
        # place above
        if self.winfo_y() - self.min_height > 0:
            overflow = self.winfo_y() - self.max_height
            if overflow < 0:
                height =  math.floor((self.max_height - abs(overflow)) / self.min_height) * self.min_height
                print('overflow', height, self.max_height)
            else:
                height = self.max_height  
            return self.winfo_x(), self.winfo_y() - height, self.winfo_width(), height
        # place over
        return self.winfo_x(), self.winfo_y(), self.winfo_width(), self.min_height

    def changed(self, name, index, mode):  
        if self.var.get() == '' and self.lb_up:
            self.destroyListBox()
            return
        words = self.comparison()
        if words:            
            if not self.lb_up:
                self.createListBox()
                self.positionListBox()
            self.lb.delete(0, tk.END)
            for w in words:
                self.lb.insert(tk.END,w)
        else:
            self.destroyListBox()
        
    def selection(self, event):
        if not self.lb_up:
            return
        self.var.set(self.lb.get(tk.ACTIVE))
        self.destroyListBox()
        self.entry.icursor(tk.END)

    def up(self, event):
        if not self.lb_up:
            return
        index = '0' if self.lb.curselection() == () else self.lb.curselection()[0]
        if index == '0':
            return             
        self.lb.selection_clear(first=index)
        index = str(int(index)-1)                
        self.lb.selection_set(first=index)
        self.lb.activate(index)

    def down(self, event):
        if not self.lb_up:
            return
        index = '0' if self.lb.curselection() == () else self.lb.curselection()[0]
        if index == tk.END:
            return                      
        self.lb.selection_clear(first=index)
        index = str(int(index)+1)        
        self.lb.selection_set(first=index)
        self.lb.activate(index)

    def comparison(self):
        pattern = re.compile('.*' + self.var.get() + '.*')
        return [w for w in self.suggestions if re.match(pattern, w)]
    
    def configure(self, event):
        # self.winfo_height() yields height of entry with 1-row
        # since we can not get text entry, listbox height directly (they yield height in rows), we take this self.winfo_height()
        # and use it to calculate possible height in rows
        self.min_height = self.winfo_height() 
        self.max_height = self.min_height * 16
        self.positionListBox()