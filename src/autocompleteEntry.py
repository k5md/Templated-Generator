## by Miguel Ángel Alarcos Torrecillas on Thu, 6 Sep 2012 (MIT) 

import tkinter as tk
from tkinter import ttk
import re
import math

MAX_LINES = 16

def traverseUp(widget, function, initializer = None):
    return function(widget, traverseUp(widget.master, function, initializer) if hasattr(widget, 'master') else initializer)

class AutocompleteEntry(ttk.Frame):
    def __init__(self, container, suggestions, textvariable=None, bounding_container=None, *args, **kwargs):
        super().__init__(container, *args, **kwargs)  
        self.lb_up = False

        self.bounding_container = bounding_container if bounding_container else self

        self.container = container
        self.suggestions = suggestions

        self.var = textvariable if textvariable else tk.StringVar()
        self.var.trace('w', self.changed)
        self.entry = tk.Entry(self, textvariable=self.var)
        self.entry.pack(fill=tk.X, expand=True)
        
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        self.bind("<Configure>", self.configure)
        self.bind('<FocusIn>', lambda _: self.changed())
        self.bind('<FocusOut>', lambda _: self.destroyListBox())

        # traditional FocusIn and FocusOut won't trigger when any of autocompleteEntry masters would be scrolled, so bind to root and check if clicked away from listbox
        # if not done, listbox would be in bounding container when its contents are scrolled
        #traverseUp(self.container, lambda widget, _: widget.bind('<Button>', lambda event: self.click_away(event)) if widget and not widget.master else None)
    
    def get_mouse_position(self, event):
        x = traverseUp(event.widget, lambda widget, acc: widget.winfo_x() + acc if widget and widget.master else acc, event.x)
        y = traverseUp(event.widget, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, event.y)
        return x, y

    def click_away(self, event):
        self.max_height = MAX_LINES * self.min_height
        print(event)
        #if (not self.lb_up):
        #    return True
        print('click')
        x, y, width, height = self.computeListBoxConfig()
        actual_x, actual_y = self.get_mouse_position(event)

        print({'actualx': actual_x, 'actualy': actual_y})
        print(x, y, width, height)
        
        inside = actual_x > x and actual_x < x + width and actual_y > y and actual_y < y + height
        print(inside)
        print()
        if (not inside):
            self.destroyListBox()

    def createListBox(self):
        # frame used to place bounding frame arbitrarily
        self.listBoxPlacingFrame = tk.Frame(self.bounding_container)

        # frame used to specify dimensions of list box arbitrarily
        self.listBoxBoundingFrame = tk.Frame(self.listBoxPlacingFrame)

        # frame containing scrollable listbox
        self.listBoxScrollbarFrame = tk.Frame(self.listBoxBoundingFrame)

        self.lb = tk.Listbox(self.listBoxScrollbarFrame)
        self.lb.bind("<Double-Button-1>", self.selection)
        self.lb.bind("<Right>", self.selection)

        scrollbar = tk.Scrollbar(self.listBoxScrollbarFrame)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        self.lb.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.lb.yview)

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
        #print({'x': x, 'y': y, 'width': width, 'height': height})

        self.lb.pack(fill="both", expand=True)
        self.lb.configure(height=math.floor(height / self.min_height))

        self.listBoxScrollbarFrame.place(in_=self.listBoxBoundingFrame, relx=0, rely=0, relheight=1, relwidth=1)
        self.listBoxBoundingFrame.place(in_=self.listBoxPlacingFrame, relx=0, rely=0, relheight=1, relwidth=1)
        self.listBoxPlacingFrame.place(in_=self.bounding_container, x=x, y=y)
        self.listBoxPlacingFrame.configure(width=width, height=height)

    def computeListBoxConfig(self):
        # self.max_height must be multiple of self.min_height
        # returned height must be a multiple of min_height, that is, of one-row text entry widget height
        # otherwise outer frames will either be too long or too short to display list box
        print('self', {'x': self.winfo_x(), 'y': self.winfo_y(), 'width': self.winfo_width(), 'height': self.winfo_height()})
        print('container', {'x': self.container.winfo_x(), 'y': self.container.winfo_y(), 'width': self.container.winfo_width(), 'height': self.container.winfo_height()})
        print('bounding_container', {'x': self.bounding_container.winfo_x(), 'y': self.bounding_container.winfo_y(), 'width': self.bounding_container.winfo_width(), 'height': self.bounding_container.winfo_height()})
        # place below if distance between lowest points of container and bounding container is more than minimal listbox height
        distance = (self.bounding_container.winfo_y() + self.bounding_container.winfo_height() - self.container.winfo_y() + self.container.winfo_height())
        if distance > self.min_height:
            overflow = distance - self.max_height
            height = math.floor((self.max_height + overflow if overflow < 0 else self.max_height) / self.min_height) * self.min_height
            
            return (
                traverseUp(self, lambda widget, acc: widget.winfo_x() + acc if widget and widget.master else acc, 0),
                traverseUp(self, lambda widget, acc: widget.winfo_y() + acc if widget and widget.master else acc, self.winfo_height()),
                self.winfo_width(),
                height - self.winfo_height() * 2 # NOTE: investigate, why just setting height results in widget overflowing bounding container
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
        if self.var.get() == '' and self.lb_up:
            self.destroyListBox()
            return
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
        # self.bounding_container.winfo_height() yields height of entry with 1-row
        # since we can not get text entry, listbox height directly (they yield height in rows), we take this self.bounding_container.winfo_height()
        # and use it to calculate possible height in rows
        self.min_height = self.winfo_height() 
        self.positionListBox()