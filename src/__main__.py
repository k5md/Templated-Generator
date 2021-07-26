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
import locale
import time
import calendar
from tkinter.messagebox import askyesno
import itertools
import operator

availableParsers = {
    '.docx': parsers.docx,
    '.xlsx': parsers.xlsx,
}

try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    approot = os.path.dirname(sys.executable)


def ru_dmy():
    month_names = ['', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    now = datetime.today()
    return ' '.join([str(x) for x in [now.day, month_names[now.month], now.year]]) + 'г.'

LOCALES_PATH=os.path.join(approot, 'locales')
DEFAULT_TEMPLATE_FILENAME = 'template'
TRANSFORMS = {
    'num2text': lambda x: decimal2text(x,
        int_units=((u'рубль', u'рубля', u'рублей'), 'm'),
        exp_units=((u'копейка', u'копейки', u'копеек'), 'f')
    ).capitalize(),
    'inverted_date': lambda x: datetime.today().strftime('%Y%m%d')[2:],
    'ru_dmy': lambda x: ru_dmy()
}

def has(arr , key, value):
    for x in arr:
        if x[key] == value:
            return True

def split_by_property_presense(array, property):
    present, missing = [], []
    for item in array:
        present.append(item) if property in item else missing.append(item)
    return present, missing  

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
        self.templatesTextBoxLabel = tk.Label(self.templateFrame, text=i18n.t('translate.loadedTemplates'))
        self.templatesTextBox = tk.Text(self.templateFrame, wrap='word', height=1, background="gray")

        self.saveFrame = tk.Frame(self.controlsFrame)
        self.saveResultsBtn = tk.Button(self.saveFrame, text = i18n.t('translate.saveResults'), command = self.saveResults)
        self.saveFileLabel = tk.Label(self.saveFrame, text=i18n.t('translate.saveName'))
        self.saveFileStringVar = tk.StringVar()
        self.saveFileEntry = tk.Entry(self.saveFrame, textvariable=self.saveFileStringVar)
        
        self.saveFrame.pack(side=tk.TOP, fill="x", padx=5, pady=5)
        self.saveFileLabel.pack(side=tk.LEFT, fill="x")
        self.saveFileEntry.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.saveResultsBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))

        self.templatesTextBoxLabel.pack(side=tk.LEFT, fill="x")
        self.templatesTextBox.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.loadTemplateBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))
        self.clearTemplatesBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))
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
        
        self._templates = [{'path': os.path.abspath(path) } for path in os.listdir(approot) if os.path.isfile(path) and DEFAULT_TEMPLATE_FILENAME in path]
        for template in self._templates:
            self.loadTemplate(template)

        date=datetime.today().strftime('%Y%m%d')
        rendered = date[2:]
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
        self.renderEntries()
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
                key = key.strip()[1:-1]
                value = value.strip()[1:-1]
                payload[key] = value
        if 'getter' in payload:
            if payload['getter'] in TRANSFORMS:
                value = TRANSFORMS[payload['getter']](payload['default'])
                payload['default'] = str(value)
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
        generatedFiles = [self.saveFileStringVar.get() + os.path.splitext(template['path'])[1] for template in self._templates]
        filesInDirectory = [path for path in os.listdir(approot) if os.path.isfile(path)]
        for generatedFile in generatedFiles:
            if generatedFile in filesInDirectory:
                proceed = askyesno(title=i18n.t('translate.replaceTitle'), message=i18n.t('translate.replaceMessage'))
                if not proceed:
                    return
                break

        for template in self._templates:
            name, ext = os.path.splitext(template['path'])
            if not (ext in availableParsers.keys()):
                return
            availableParsers[ext].replace(
                template['path'],
                self.saveFileStringVar.get() + ext,
                self.computeMatch
            )
    
    def renderEntry(self, key, value):
        container = tk.Frame(self.scrollableFrame.frame)
        container.pack(side=tk.TOP, fill='both', expand=True)
        label = tk.Label(container, text=value['title'] if 'title' in value else key)
        label.pack(side=tk.LEFT)
        self._fields[key]['__stringVar'] = tk.StringVar()
        self._fields[key]['__stringVar'].set(value['default'] if 'default' in value else '')
        self._fields[key]['__entry'] = tk.Entry(container, textvariable=self._fields[key]['__stringVar'])
        self._fields[key]['__entry'].pack(side=tk.RIGHT, fill="x", expand=True)

    def renderEntries(self):
        for child in self.scrollableFrame.frame.winfo_children():
            child.destroy()

        # split fields by presense 'group' property into group_specified and group_not_specified
        group_specified, group_not_specified = split_by_property_presense(self._fields.values(), 'group')
        # sort fields with no 'group' specified by 'title' property
        group_not_specified_sorted = sorted(group_not_specified, key=lambda i: i['title'])
        # group fields with 'group' specified by 'group' property value
        group_specified_dict = { p: list(g) for p, g in itertools.groupby(group_specified, lambda i: i['group']) }

        # sort each group entries by entry 'order' property, entries with missing 'order' property are sorted by title
        # and place in the end
        group_specified_dict_items_sorted = {}
        for group, entries in group_specified_dict.items():
            order_specified, order_not_specified = split_by_property_presense(entries, 'order')
            order_not_specified = sorted(order_not_specified, key=lambda i: i['title'])
            order_specified = sorted(order_specified, key=lambda i: int(i['order']))
            group_specified_dict_items_sorted[group] = order_specified + order_not_specified

        # group_specified_dict_items_sorted -> array of entries, entries groups are sorted by group name
        group_specified = [v for k, v in sorted(group_specified_dict_items_sorted.items(), key=lambda e: e[0])]

        for group in group_specified:
            for value in group:
                self.renderEntry(value['id'], value)
            separator = tk.ttk.Separator(self.scrollableFrame.frame, orient='horizontal')
            separator.pack(fill='x', pady=10)
        for value in group_not_specified_sorted:
            self.renderEntry(value['id'], value)

    def processTemplate(self, template):
        name, ext = os.path.splitext(template['path'])
        if not (ext in availableParsers.keys()):
            return
        availableParsers[ext].parse(template['path'], self._fields, self.parseEntry)
        
        

if __name__ == "__main__":
    app = App()
    app.mainloop()
