from functools import partial

def wrap_widget(widget):
    def _onKeyRelease(self, event):
        ctrl = (event.state & 0x4) != 0
        if event.keycode==88 and ctrl and event.keysym.lower() != "x": 
            event.widget.event_generate("<<Cut>>")

        if event.keycode==86 and ctrl and event.keysym.lower() != "v": 
            event.widget.event_generate("<<Paste>>")

        if event.keycode==67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

    widget._onKeyRelease = partial(_onKeyRelease, widget)
    widget.bind_all("<Key>", widget._onKeyRelease, "+")
