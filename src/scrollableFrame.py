import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, bd=0, highlightthickness=0)

        self.onScroll = lambda *args, **kwargs: None

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.frame = ttk.Frame(self.canvas)

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onCanvasConfigure)

        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.onScrollCommand)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        self.canvas.itemconfigure(self.frame_id, width=event.width)

    def onScrollCommand(self, *args, **kwargs):
        self.onScroll()
        self.scrollbar.set(*args, **kwargs)