# -*- coding: utf-8 -*-
import os
import sys
import re
import itertools
import json
import datetime
import i18n

import tkinter.filedialog
import tkinter.font
import tkinter.ttk
import tkinter.messagebox
import tkinter as tk

from libs.scrollableFrame import ScrollableFrame
from libs.autocompleteEntry import AutocompleteEntry
from parsers import ext_parser_map
from transforms import name_transform_map
from utils import has, split_by_property_presense, copy_func

try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    approot = os.path.dirname(sys.executable)

LOCALES_PATH=os.path.join(approot, 'locales')
DEFAULT_TEMPLATE_FILENAME = 'template'

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        i18n.load_path.append(LOCALES_PATH)
        i18n.set('fallback', 'ru')

        ### FRAMES
        self.rootFrame = tk.ttk.Frame(self)
        self.default_font = tkinter.font.nametofont("TkDefaultFont")
        self.default_font.configure(size=10)
        self.rootFrame.option_add("*Font", self.default_font)
        self.fieldsFrame = tk.ttk.LabelFrame(self.rootFrame, text=i18n.t('translate.fieldsTitle'))
        self.controlsFrame = tk.ttk.LabelFrame(self.rootFrame, text=i18n.t('translate.controlsTitle'))

        self.rootFrame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.fieldsFrame.pack(side=tk.TOP, fill="both", expand=True)
        self.controlsFrame.pack(side=tk.BOTTOM, fill="x", pady=(10, 0))

        ### FIELDS FRAME ITEMS PACKING
        self.scrollableFrame = ScrollableFrame(self.fieldsFrame)
        self.scrollableFrame.pack(side="top", fill="both", anchor="nw", expand=True)

        ### OUTPUT FIELD ITEMS PACKING
        self.templateFrame = tk.ttk.Frame(self.controlsFrame)
        self.loadTemplateBtn = tk.ttk.Button(self.templateFrame, text = i18n.t('translate.loadTemplate'), command = self.add_template)
        self.clearTemplatesBtn = tk.ttk.Button(self.templateFrame, text = i18n.t('translate.clearTemplates'), command = self.resetTemplates)
        self.templatesTextBoxLabel = tk.ttk.Label(self.templateFrame, text=i18n.t('translate.loadedTemplates'))
        self.templatesTextBox = tk.ttk.Entry(self.templateFrame, background="grey")

        self.saveFrame = tk.ttk.Frame(self.controlsFrame)
        self.saveResultsBtn = tk.ttk.Button(self.saveFrame, text = i18n.t('translate.saveResults'), command = self.saveResults)
        self.saveFileLabel = tk.ttk.Label(self.saveFrame, text=i18n.t('translate.saveName'))
        self.saveFileStringVar = tk.StringVar()
        self.saveFileEntry = tk.ttk.Entry(self.saveFrame, textvariable=self.saveFileStringVar)
        
        self.saveFrame.pack(side=tk.TOP, fill="x", padx=5, pady=5)
        self.saveFileLabel.pack(side=tk.LEFT, fill="x")
        self.saveFileEntry.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.saveResultsBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))

        self.templatesTextBoxLabel.pack(side=tk.LEFT, fill="x")
        self.templatesTextBox.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.loadTemplateBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))
        self.clearTemplatesBtn.pack(side=tk.LEFT, fill="x", padx=(0, 5))
        self.templateFrame.pack(side=tk.TOP, fill="x", padx=5, pady=5)

        # MENU BAR

        self.menuBar = tk.Menu(self)

        self.settingsMenu = tk.Menu(self.menuBar, tearoff=0)

        self.rewriteTemplates = tk.BooleanVar(value=True)
        self.rewriteExternals = tk.BooleanVar(value=True)
        self.settingsMenu.add_checkbutton(label=i18n.t('translate.rewriteTemplates'), onvalue=True, offvalue=False, variable=self.rewriteTemplates)
        self.settingsMenu.add_checkbutton(label=i18n.t('translate.rewriteExternals'), onvalue=True, offvalue=False, variable=self.rewriteExternals)

        self.menuBar.add_cascade(label=i18n.t('translate.settings'), menu=self.settingsMenu)

        # WINDOW CONFIG
        self.config(menu=self.menuBar)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.update_idletasks()
        self.minsize(self.winfo_width(), self.winfo_height())
        self.winfo_toplevel().title("Templated generator")

        # INIT VALUES
        self.fields = {} # key - id, value - { id, title, __stringVar, __entry }
        self.rendered = {} # maps id from fields to { type: type of entity, widget: tk widget, var: tk variable }

        self.templates = [] # value - { path }
        
        for template in [os.path.abspath(path) for path in os.listdir(approot) if os.path.isfile(path) and DEFAULT_TEMPLATE_FILENAME in path]:
            self.add_template(template)

        date=datetime.datetime.today().strftime('%Y%m%d')[2:] + ' '
        rendered = date
        self.saveFileStringVar.set(rendered )
    
    def add_template(self, template_path = ''):
        if (not template_path):
            template_path = tk.filedialog.Open(self).show()
            if template_path == '':
                return
        if template_path in self.templates:
            return
        self.templates.append(template_path)
        self.loadTemplate(template_path)
        self.renderEntries(self.fields.values())
        self.renderTemplateBox()
    
    def renderTemplateBox(self):
        self.templatesTextBox.delete(0, tk.END)
        self.templatesTextBox.insert(0, ','.join(self.templates))
    
    def resetTemplates(self):
        self.clearTemplates()
        self.renderTemplateBox()
        self.renderEntries(self.fields.values())

    def saveResults(self):
        generatedFiles = [self.saveFileStringVar.get() + os.path.splitext(template)[1] for template in self.templates]
        filesInDirectory = [path for path in os.listdir(approot) if os.path.isfile(path)]
        for generatedFile in generatedFiles:
            if generatedFile in filesInDirectory:
                proceed = tk.messagebox.askyesno(title=i18n.t('translate.replaceTitle'), message=i18n.t('translate.replaceMessage'))
                if not proceed:
                    return
                break
        for template in self.templates:
            self.save_result(template, name, self.saveFileStringVar.get())
        if (self.rewriteTemplates.get()):
            for template in self.templates:
                self.save_template(template)

    ### ABOVE - GUI, BELOW - MODULE

    def findMatches(self, text):
        return re.findall(r'{{{.+?}}}+', text)

    def loadTemplate(self, template):      
        name, ext = os.path.splitext(template)
        if not (ext in ext_parser_map.keys()):
            return
        ext_parser_map[ext].parse(template, self.fields, self.parseEntry, self.findMatches)
        
    def clearTemplates(self):
        self.templates = []
        self.fields = {}

    def loadExternal(self, file_name):
        if file_name in os.listdir(approot) and os.path.isfile(file_name):
            file_path = os.path.abspath(file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                payload = json.loads(content)
                return payload
    
    def saveExternal(self, file_name, payload):
        if file_name in os.listdir(approot) and os.path.isfile(file_name):
            file_path = os.path.abspath(file_name)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(payload, file, ensure_ascii=False)

    def save_result(self, template_path, name):
        name, ext = os.path.splitext(template_path)
        if not (ext in ext_parser_map.keys()):
            return
        ext_parser_map[ext].replace(
            template_path,
            name + ext,
            self.computeMatch
        )

    def save_template(self, template):
        name, ext = os.path.splitext(template)
        if not (ext in ext_parser_map.keys()):
            return
        ext_parser_map[ext].replace(
            template,
            name + ext,
            self.computeUpdatedTemplate
        )


    # NOT CLASSIFIED
    def reloadExternals(self):
        for entry in self.fields.values():
            autocomplete = entry.get('autocomplete')
            if autocomplete:
                if type(autocomplete) is dict and autocomplete.get('external'):
                    external = self.loadExternal(autocomplete.get('external'))
                    self.fields[entry['id']]['autocomplete']['data'] = external
                    self.fields[entry['id']]['__entry'].suggestions = external
                    self.fields[entry['id']]['__entry'].update()

    def parseEntry(self, string):
        content = string[2:-2]
        payload = {}
        payload = json.loads(content)
        if 'getter' in payload:
            if payload['getter'] in name_transform_map:
                value = name_transform_map[payload['getter']](payload['value'])
                payload['value'] = str(value)
        autocomplete = payload.get('autocomplete')
        if autocomplete:
            if type(autocomplete) is dict and autocomplete.get('external'):
                external = self.loadExternal(autocomplete.get('external'))
                payload['autocomplete']['data'] = external
        return payload
    


    def computeMatch(self, text, to_replace): # find matches, populate to_replace, return to_replace
        matches = self.findMatches(text)
        for match in matches:
            payload = self.parseEntry(match)
            value = self.fields[payload['id']]['__stringVar'].get()
            if 'fn' in payload:
                if payload['fn'] in name_transform_map:
                    value = name_transform_map[payload['fn']](value)
            if 'monetary' in payload and payload['monetary']:
                value = "{:,.2f}".format(float(value)).replace(",", " ").replace('.', ',')
            if 'append' in payload:
                value = str(value) + payload['append']
            to_replace[match] = value
        return to_replace
    
    def computeUpdatedTemplate(self, text, to_replace): # find matches, populate to_replace, return to_replace
        matches = self.findMatches(text)
        for match in matches:
            payload = self.parseEntry(match)
            newValue = self.fields[payload['id']]['__stringVar'].get()
            payload['value'] = newValue
            if payload.get('autocomplete') and payload.get('autocomplete', {}).get('data'):
                if newValue not in payload['autocomplete']['data']:
                    payload['autocomplete']['data'].append(newValue) 
                    if (self.rewriteExternals.get()):
                        self.saveExternal(payload['autocomplete']['external'], payload['autocomplete']['data'])
                        self.reloadExternals()
                del payload['autocomplete']['data']
            to_replace[match] = '{{' + json.dumps(payload, ensure_ascii=False) + '}}'
        return to_replace




    
    def renderEntry(self, value):
        id = value['id']
        container = tk.ttk.Frame(self.scrollableFrame.frame)
        container.pack(side=tk.TOP, fill='both', expand=True, padx=5, pady=2.5)
        label = tk.ttk.Label(container, text=value.get('title', id))
        label.pack(side=tk.LEFT)
        self.fields[id]['__stringVar'] = tk.StringVar()
        self.fields[id]['__stringVar'].set(value.get('value', ''))

        autocomplete_suggestions = self.fields[id].get('autocomplete', {}).get('data')
        if (autocomplete_suggestions):
            self.fields[id]['__entry'] = AutocompleteEntry(
                container, autocomplete_suggestions, textvariable=self.fields[id]['__stringVar'],
                bounding_container=self.rootFrame,
                font=self.default_font,
                window=self.rootFrame
            )
            oldOnScroll = copy_func(self.scrollableFrame.onScroll)
            self.scrollableFrame.onScroll = lambda: (oldOnScroll() and False) or self.fields[id]['__entry'].destroyListBox()
            self.fields[id]['__entry'].pack(fill=tk.X)
        else:
            self.fields[id]['__entry'] = tk.ttk.Entry(container, textvariable=self.fields[id]['__stringVar'])
            self.fields[id]['__entry'].pack(side=tk.RIGHT, fill="x", expand=True)

    def renderEntries(self, fields):
        # clear entries container
        for child in self.scrollableFrame.frame.winfo_children():
            child.destroy()
        
        # remove scroll listeners
        self.scrollableFrame.onScroll = lambda: None

        # split fields by presense 'group' property into group_specified and group_not_specified
        group_specified, group_not_specified = split_by_property_presense(fields, 'group')
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

        # render groups separated with separator
        for group in group_specified:
            for value in group:
                self.renderEntry(value)
            separator = tk.ttk.Separator(self.scrollableFrame.frame, orient='horizontal')
            separator.pack(fill='x', pady=10)
        for value in group_not_specified_sorted:
            self.renderEntry(value)

if __name__ == "__main__":
    app = App()
    app.mainloop()
