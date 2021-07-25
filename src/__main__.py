# -*- coding: utf-8 -*-
import os
import sys
import json
import tkinter.filedialog
import tkinter.font
import tkinter as tk
from scrollableFrame import ScrollableFrame
import re
from num2t4ru import decimal2text
from datetime import datetime
import i18n
import parsers.docx
import parsers.xlsx

availableParsers = {
    '.docx': parsers.docx,
    '.xlsx': parsers.xlsx,
}

try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    approot = os.path.dirname(sys.executable)

LOCALES_PATH=os.path.join(approot, 'locales')
DEFAULT_TEMPLATE_FILENAME = 'template'
TRANSFORMS = {
    'num2text': lambda x: decimal2text(x,
        int_units=((u'рубль', u'рубля', u'рублей'), 'm'),
        exp_units=((u'копейка', u'копейки', u'копеек'), 'f')
    ).capitalize(),
}

def has(arr , key, value):
    for x in arr:
        if x[key] == value:
            return True

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        i18n.load_path.append(LOCALES_PATH)
        i18n.set('fallback', 'ru')

        ### FRAMES
        self.rootFrame = tk.Frame(self)
        default_font = tkinter.font.nametofont("TkDefaultFont")
        default_font.configure(size=12)
        self.rootFrame.option_add("*Font", default_font)
        self.fieldsFrame = tk.LabelFrame(self.rootFrame, text=i18n.t('translate.fieldsTitle'))
        self.controlsFrame = tk.LabelFrame(self.rootFrame, text=i18n.t('translate.controlsTitle'))

        self.rootFrame.pack(fill=tk.BOTH, expand=True)
        self.fieldsFrame.pack(side=tk.TOP, fill="both", expand=True)
        self.controlsFrame.pack(side=tk.BOTTOM, fill="x", pady=(10, 0))

        ### FIELDS FRAME ITEMS PACKING
        self.scrollableFrame = ScrollableFrame(self.fieldsFrame)
        self.scrollableFrame.pack(side="top", fill="both", anchor="nw", expand=True)

        ### OUTPUT FIELD ITEMS PACKING
        self.templateFrame = tk.Frame(self.controlsFrame)
        self.loadTemplateBtn = tk.Button(self.templateFrame, text = i18n.t('translate.loadTemplate'), command = self.loadTemplate)
        self.clearTemplatesBtn = tk.Button(self.templateFrame, text = i18n.t('translate.clearTemplates'), command = self.clearTemplates)
        self.templatesTextBox = tk.Text(self.templateFrame, wrap='word', height=1, background="gray")

        self.saveFrame = tk.Frame(self.controlsFrame)
        self.saveFileStringVar = tk.StringVar()
        self.saveFileEntry = tk.Entry(self.saveFrame, textvariable=self.saveFileStringVar)
        self.saveResultsBtn = tk.Button(self.saveFrame, text = i18n.t('translate.saveResults'), command = self.saveResults)
        
        self.saveFrame.pack(side=tk.TOP, fill="x", padx=5, pady=5)
        self.saveResultsBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))
        self.saveFileEntry.pack(side=tk.RIGHT, fill="x", expand=True, padx=(0, 5))

        self.loadTemplateBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))
        self.clearTemplatesBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))
        self.templatesTextBox.pack(side=tk.RIGHT, fill="x", expand=True, padx=(0, 5))
        self.templateFrame.pack(side=tk.TOP, fill="x", padx=5, pady=5)

        # WINDOW CONFIG
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.update_idletasks()
        self.minsize(self.winfo_width(), self.winfo_height())
        self.winfo_toplevel().title("Templated generator")

        # INIT VALUES
        self._fields = {} # key - id, value - { id, title, __stringVar, __entry }

        self._templates = [] # value - { path }
        self._templates = [{'path': path } for path in os.listdir() if os.path.isfile(path) and DEFAULT_TEMPLATE_FILENAME in path]
        for template in self._templates:
            self.loadTemplate(template)

        date=datetime.today().strftime('%Y%m%d')
        rendered = date[2:4] + date[4:]
        self.saveFileStringVar.set(rendered + ' ')

    def loadTemplate(self, providedTemplate = None):
        template = None
        if (not providedTemplate):
            path = tk.filedialog.Open(self).show()
            if path == '' or has(self._templates, 'path', path):
                return
            template = { 'path': path }
            self._templates.append(template)
        else:
            template = providedTemplate
        
        self.processTemplate(template)
        self.templatesTextBox.delete(1.0, "end")
        self.templatesTextBox.insert("1.0", ','.join(t['path'] for t in self._templates))
    
    def clearTemplates(self):
        self._templates = []
        self._fields = {}
        self.templatesTextBox.delete(1.0, "end")
        for child in self.scrollableFrame.frame.winfo_children():
            child.destroy()

    def parseEntry(self, string):
        content = string[1:-1]
        parsable = re.sub(r'[“”]', '"', content)
        payload = {}
        try:
            payload = json.loads(parsable)
        except:
            payload = {}
            entry = parsable.strip('{').strip('}')
            pairs = [pair.strip() for pair in entry.split(',')]
            for pair in pairs:
                key, value = pair.split(':')
                key = key.replace(r'(^[^a-zA-Z0-9А-Яа-я]|[^a-zA-Z0-9А-Яа-я]$)', '')
                value = value.replace(r'(^[^a-zA-Z0-9А-Яа-я]|[^a-zA-Z0-9А-Яа-я]$)', '')
                payload[key.strip('"')] = value
        return payload

    def computeMatch(self, text, to_replace): # find matches, populate to_replace, return to_replace
        matches = re.findall(r'{{.+?}}', text)
        for match in matches:
            payload = self.parseEntry(match)
            value = self._fields[payload['id']]['__stringVar'].get()
            if 'fn' in payload:
                if payload['fn'] in TRANSFORMS:
                    value = TRANSFORMS[payload['fn']](value)
            if 'monetary' in payload and payload['monetary']:
                value = "{:,.2f}".format(float(value)).replace(",", " ").replace('.', ',')
            if 'append' in payload:
                value = str(value) + payload['append']
            to_replace[match] = value
        return to_replace

    def saveResults(self):
        for template in self._templates:
            name, ext = os.path.splitext(template['path'])

            if not (ext in availableParsers.keys()):
                return
            availableParsers[ext].replace(
                template['path'],
                self.saveFileStringVar.get() + ext,
                self.computeMatch
            )

    def processTemplate(self, template):
        name, ext = os.path.splitext(template['path'])
        if not (ext in availableParsers.keys()):
            return
        availableParsers[ext].parse(template['path'], self._fields, self.parseEntry)
        
        for child in self.scrollableFrame.frame.winfo_children():
            child.destroy()

        for key, value in self._fields.items():
            container = tk.Frame(self.scrollableFrame.frame)
            container.pack(side=tk.TOP, fill='both', expand=True)
            label = tk.Label(container, text=value['title'] if 'title' in value else key)
            label.pack(side=tk.LEFT)
            self._fields[key]['__stringVar'] = tk.StringVar()
            self._fields[key]['__stringVar'].set(value['default'] if 'default' in value else '')
            self._fields[key]['__entry'] = tk.Entry(container, textvariable=self._fields[key]['__stringVar'])
            self._fields[key]['__entry'].pack(side=tk.RIGHT, fill="x", expand=True)
            

if __name__ == "__main__":
    app = App()
    app.mainloop()
