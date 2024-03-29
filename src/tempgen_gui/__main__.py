# -*- coding: utf-8 -*-
import os
import sys
import itertools
import datetime
import i18n
import locale
import json

import tkinter.filedialog
import tkinter.font
import tkinter.ttk
import tkinter.messagebox
import tkinter as tk

from tempgen_gui.libs.scrollableFrame import ScrollableFrame
from tempgen_gui.libs.autocompleteEntry import AutocompleteEntry
from tempgen_gui.libs.controlSequences import wrap_widget
from tempgen.utils import split_by_key_presense, copy_func, make_path, fix_tk_file_path
from tempgen.module import Tempgen

locale.setlocale(locale.LC_ALL, '')

try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    approot = os.path.dirname(sys.executable)

LOCALES_PATH=os.path.join(approot, 'locales')
DEFAULT_TEMPLATE_FILENAME = 'template'
CONFIG_FILEPATH = os.path.join(approot, 'config.json')

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        i18n.load_path.append(LOCALES_PATH)
        i18n.set('fallback', 'en')
        i18n.set('locale', locale.getlocale()[0][0:2].lower())

        ### LOAD CONFIG
        self.settings = {
            'rewrite_templates_var': tk.BooleanVar(value=True),
            'rewrite_externals_var': tk.BooleanVar(value=True),
            'save_folder': tk.StringVar(value=approot)
        }
        self.load_settings(CONFIG_FILEPATH, self.settings)

        ### FRAMES
        self.root_frame = tk.ttk.Frame(self)
        self.default_font = tkinter.font.nametofont('TkDefaultFont')
        self.default_font.configure(size=10)
        self.root_frame.option_add('*Font', self.default_font)
        self.fields_frame = tk.ttk.LabelFrame(self.root_frame, text=i18n.t('translate.fieldsTitle'))
        self.controls_frame = tk.ttk.LabelFrame(self.root_frame, text=i18n.t('translate.controlsTitle'))

        self.root_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.fields_frame.pack(side=tk.TOP, fill='both', expand=True)
        self.controls_frame.pack(side=tk.BOTTOM, fill='x', pady=(10, 0))

        ### FIELDS FRAME ITEMS PACKING
        self.scrollable_frame = ScrollableFrame(self.fields_frame)
        self.scrollable_frame.pack(side='top', fill='both', anchor='nw', expand=True)

        ### OUTPUT FIELD ITEMS PACKING
        self.template_frame = tk.ttk.Frame(self.controls_frame)
        self.load_template_btn = tk.ttk.Button(self.template_frame, text = i18n.t('translate.loadTemplate'), command = self.ask_templates)
        self.clear_templates_btn = tk.ttk.Button(self.template_frame, text = i18n.t('translate.clearTemplates'), command = self.clear_template_list)
        self.templates_entry_label = tk.ttk.Label(self.template_frame, text=i18n.t('translate.loadedTemplates'))
        self.templates_entry = tk.ttk.Entry(self.template_frame, state='readonly', background='grey')

        self.save_frame = tk.ttk.Frame(self.controls_frame)
        self.save_folder_label = tk.ttk.Label(self.save_frame, text=i18n.t('translate.saveFolder'))
        self.save_folder_entry = tk.ttk.Entry(self.save_frame, textvariable=self.settings['save_folder'], state='readonly')
        self.save_folder_btn = tk.ttk.Button(self.save_frame, text = i18n.t('translate.select'), command = self.set_save_folder)
        self.save_file_label = tk.ttk.Label(self.save_frame, text=i18n.t('translate.saveName'))
        self.save_file_var = tk.StringVar(value=datetime.datetime.today().strftime('%Y%m%d')[2:] + ' ')
        self.save_file_entry = tk.ttk.Entry(self.save_frame, textvariable=self.save_file_var)
        self.save_results_btn = tk.ttk.Button(self.save_frame, text = i18n.t('translate.saveResults'), command = self.save_generated)
        
        self.save_frame.pack(side=tk.TOP, fill='x', padx=5, pady=5)
        self.save_folder_label.pack(side=tk.LEFT, fill='x', padx=(0, 5))
        self.save_folder_entry.pack(side=tk.LEFT, fill='x', padx=(0, 5), expand=True)
        self.save_folder_btn.pack(side=tk.LEFT, fill='x', padx=(0, 5))
        self.save_file_label.pack(side=tk.LEFT, fill='x', padx=(0, 5))
        self.save_file_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
        self.save_results_btn.pack(side=tk.LEFT, fill='x', padx=(0, 5))

        self.templates_entry_label.pack(side=tk.LEFT, fill='x')
        self.templates_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
        self.load_template_btn.pack(side=tk.LEFT, fill='x', padx=(0, 5))
        self.clear_templates_btn.pack(side=tk.LEFT, fill='x', padx=(0, 5))
        self.template_frame.pack(side=tk.TOP, fill='x', padx=5, pady=5)
        
        # MENU BAR
        self.menubar = tk.Menu(self)

        self.settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.settings_menu.add_checkbutton(label=i18n.t('translate.rewriteTemplates'), onvalue=True, offvalue=False, variable=self.settings['rewrite_templates_var'], command=self.save_settings)
        self.settings_menu.add_checkbutton(label=i18n.t('translate.rewriteExternals'), onvalue=True, offvalue=False, variable=self.settings['rewrite_externals_var'], command=self.save_settings)

        self.menubar.add_cascade(label=i18n.t('translate.settings'), menu=self.settings_menu)

        # WINDOW CONFIG
        self.config(menu=self.menubar)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.update_idletasks()
        self.minsize(self.winfo_width(), self.winfo_height())
        self.winfo_toplevel().title('Templated generator')
        wrap_widget(self) # NOTE: quick workaround for issue with cyrillic layouts control sequences

        # INIT VALUES
        self.tempgen = Tempgen()
        self.rendered = {}
        for template in [os.path.abspath(path) for path in os.listdir(approot) if os.path.isfile(path) and DEFAULT_TEMPLATE_FILENAME in path]:
            self.add_template(template)

    def ask_templates(self):
        template_paths = tk.filedialog.Open(self, multiple=True).show()
        if template_paths == '' or not len(template_paths):
            return
        for template_path in template_paths:
            self.add_template(fix_tk_file_path(template_path))

    def add_template(self, template_path = ''):
        self.tempgen.load_template(template_path)
        self.render_entries(self.tempgen.get_fields().values(), self.rendered)
        self.render_template_list()
    
    def render_template_list(self):
        self.templates_entry.config(state='normal')
        self.templates_entry.delete(0, tk.END)
        self.templates_entry.insert(0, ','.join(self.tempgen.get_templates()))
        self.templates_entry.config(state='readonly')
    
    def clear_template_list(self):
        self.tempgen.clear_templates()
        self.render_template_list()
        self.render_entries(self.tempgen.get_fields().values(), self.rendered)

    def save_generated(self):
        generated_files = [self.save_file_var.get() + os.path.splitext(template)[1] for template in self.tempgen.get_templates()]
        directory_files = [path for path in os.listdir(self.settings['save_folder'].get()) if os.path.isfile(os.path.join(self.settings['save_folder'].get(), path))]
        for generated_file in generated_files:
            if generated_file in directory_files:
                proceed = tk.messagebox.askyesno(title=i18n.t('translate.replaceTitle'), message=i18n.t('translate.replaceMessage'))
                if not proceed:
                    return
                break
        for template in self.tempgen.get_templates():
            self.tempgen.save_result(template, os.path.join(self.settings['save_folder'].get(), self.save_file_var.get()), { key: value['var'].get() for key, value in self.rendered.items() })
        if (self.settings['rewrite_templates_var'].get()):
            for template in self.tempgen.get_templates():
                self.tempgen.save_template(template, { key: value['var'].get() for key, value in self.rendered.items() }, self.settings['rewrite_externals_var'].get())
                self.reload_externals(template)
    
    def load_settings(self, file_path, container):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                payload = json.loads(content)
                for key in container.keys():
                    if key in payload:
                        container[key].set(payload[key])
        return container

    def save_settings(self, file_path = CONFIG_FILEPATH):
        payload = { k: v.get() for k, v in self.settings.items() }
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(payload, file, ensure_ascii=False)

    def reload_externals(self, template_path):
        self.tempgen.reload_externals(template_path)
        for entry in self.rendered.values():
            if self.tempgen.get_fields().get(entry['id'], {}).get('autocomplete', {}).get('data', None):
                entry['widget'].suggestions = self.tempgen.get_fields()[entry['id']]['autocomplete']['data']
                entry['widget'].update()

    def set_save_folder(self):
        save_folder = tk.filedialog.askdirectory()
        if save_folder == '':
            return
        self.settings['save_folder'].set(fix_tk_file_path(save_folder))
        self.save_settings()

    def render_entry(self, value, rendered):
        id = value['id']

        container = tk.ttk.Frame(self.scrollable_frame.frame)
        container.pack(side=tk.TOP, fill='both', expand=True, padx=5, pady=2)

        label = tk.ttk.Label(container, text=value.get('title', id))
        label.pack(side=tk.LEFT)

        make_path(rendered, id)
        rendered[id]['id'] = id
        rendered[id]['var'] = tk.StringVar()
        rendered[id]['var'].set(value.get('value', ''))

        autocomplete_suggestions = value.get('autocomplete', {}).get('data')
        if (autocomplete_suggestions):
            rendered[id]['widget'] = AutocompleteEntry(
                container, autocomplete_suggestions, textvariable=rendered[id]['var'],
                bounding_container=self.root_frame,
                font=self.default_font,
                window=self.root_frame
            )
            old_on_scroll = copy_func(self.scrollable_frame.on_scroll)
            self.scrollable_frame.on_scroll = lambda: (old_on_scroll() and False) or rendered[id]['widget'].destroy_list_box()
            rendered[id]['widget'].pack(fill=tk.X)
        else:
            rendered[id]['widget'] = tk.ttk.Entry(container, textvariable=rendered[id]['var'])
            rendered[id]['widget'].pack(side=tk.RIGHT, fill='x', expand=True)

    def render_entries(self, fields, rendered):
        # clear entries container
        for child in self.scrollable_frame.frame.winfo_children():
            child.destroy()
        
        # remove scroll listeners
        self.scrollable_frame.on_scroll = lambda: None

        # split fields by presense 'group' property into group_specified and group_not_specified
        group_specified, group_not_specified = split_by_key_presense(fields, 'group')
        # sort fields with no 'group' specified by 'title' property
        group_not_specified_sorted = sorted(group_not_specified, key=lambda i: i['title'] if 'title' in i else i['id'])
        # group fields with 'group' specified by 'group' property value
        group_specified_dict = { p: list(g) for p, g in itertools.groupby(group_specified, lambda i: i['group']) }

        # sort each group entries by entry 'order' property, entries with missing 'order' property are sorted by title
        # and place in the end
        group_specified_dict_items_sorted = {}
        for group, entries in group_specified_dict.items():
            order_specified, order_not_specified = split_by_key_presense(entries, 'order')
            order_not_specified = sorted(order_not_specified, key=lambda i: i['title'] if 'title' in i else i['id'])
            order_specified = sorted(order_specified, key=lambda i: int(i['order']))
            group_specified_dict_items_sorted[group] = order_specified + order_not_specified

        # group_specified_dict_items_sorted -> array of entries, entries groups are sorted by group name
        group_specified = [v for k, v in sorted(group_specified_dict_items_sorted.items(), key=lambda e: e[0])]

        # render groups separated with separator
        for group in group_specified:
            for value in group:
                self.render_entry(value, rendered)
            separator = tk.ttk.Separator(self.scrollable_frame.frame, orient='horizontal')
            separator.pack(fill='x', pady=10)
        for value in group_not_specified_sorted:
            self.render_entry(value, rendered)

app = App()
app.mainloop()
