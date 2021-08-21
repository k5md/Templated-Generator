# -*- coding: utf-8 -*-
import os
import sys
import re
import json

from tempgen.parsers import Parsers
from tempgen.transforms import Transforms

try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    approot = os.path.dirname(sys.executable)

class Tempgen():
    def __init__(self):
        # INIT VALUES
        self.fields = {} # key - id, value - { id, title, __stringVar, __entry }
        self.templates = [] # value - { path }
        self.parsers = Parsers().ext_parser_map
        self.transforms = Transforms().name_transform_map

    def find_matches(self, text):
        return re.findall(r'{{{.+?}}}+', text)

    def load_template(self, template):
        if template in self.templates:
            return
        name, ext = os.path.splitext(template)
        if not (ext in self.parsers.keys()):
            return
        self.parsers[ext].parse(template, self.fields, self.parse_entry, self.find_matches)
        self.templates.append(template)
        
    def clear_templates(self):
        self.templates = []
        self.fields = {}

    def load_external(self, file_name, template_path):
        template_dir, _ = os.path.split(template_path)
        file_path = os.path.join(template_dir, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                payload = json.loads(content)
                return payload
    
    def save_external(self, file_name, payload, template_path):
        template_dir, _ = os.path.split(template_path)
        file_path = os.path.join(template_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(payload, file, ensure_ascii=False)

    def save_result(self, template_path, target_name, replacements):
        name, ext = os.path.splitext(template_path)
        if not (ext in self.parsers.keys()):
            return
        self.parsers[ext].replace(
            template_path,
            target_name + ext,
            self.compute_match,
            replacements
        )

    def save_template(self, template, replacements, update_externals):
        name, ext = os.path.splitext(template)
        if not (ext in self.parsers.keys()):
            return
        self.parsers[ext].replace(
            template,
            name + ext,
            self.compute_updated_template,
            replacements,
            update_externals
        )

    def parse_entry(self, string, template_path):
        content = string[2:-2]
        payload = {}
        payload = json.loads(content)
        if 'getter' in payload:
            if payload['getter'] in self.transforms:
                value = self.transforms[payload['getter']](payload['value'])
                payload['value'] = str(value)
        autocomplete = payload.get('autocomplete')
        if autocomplete:
            if type(autocomplete) is dict and autocomplete.get('external'):
                external = self.load_external(autocomplete.get('external'), template_path)
                payload['autocomplete']['data'] = external
        return payload

    def compute_match(self, text, to_replace, replacements, template_path, *args, **kwargs): # find matches, populate to_replace, return to_replace
        matches = self.find_matches(text)
        for match in matches:
            payload = self.parse_entry(match, template_path)
            value = replacements.get(payload['id'], payload['value'])
            if 'fn' in payload:
                if payload['fn'] in self.transforms:
                    value = self.transforms[payload['fn']](value)
            if 'monetary' in payload and payload['monetary']:
                value = "{:,.2f}".format(float(value)).replace(",", " ").replace('.', ',')
            if 'append' in payload:
                value = str(value) + payload['append']
            to_replace[match] = value
        return to_replace

    def compute_updated_template(self, text, to_replace, replacements, template_path, update_externals): # find matches, populate to_replace, return to_replace
        matches = self.find_matches(text)
        for match in matches:
            payload = self.parse_entry(match, template_path)
            newValue = replacements.get(payload['id'], payload['value'])
            payload['value'] = newValue
            if (update_externals):
                if payload.get('autocomplete') and payload.get('autocomplete', {}).get('data'):
                    if newValue not in payload['autocomplete']['data']:
                        payload['autocomplete']['data'].append(newValue)
                        self.save_external(payload['autocomplete']['external'], payload['autocomplete']['data'], template_path)
                    del payload['autocomplete']['data']
            to_replace[match] = '{{' + json.dumps(payload, ensure_ascii=False) + '}}'
        return to_replace  

    def reload_externals(self, template_path):
        for entry in self.fields.values():
            autocomplete = entry.get('autocomplete')
            if autocomplete:
                if type(autocomplete) is dict and autocomplete.get('external'):
                    external = self.load_external(autocomplete.get('external'), template_path)
                    self.fields[entry['id']]['autocomplete']['data'] = external

    def get_templates(self):
        return self.templates
    
    def get_fields(self):
        return self.fields

    def set_fields(self, fields):
        self.fields = fields
