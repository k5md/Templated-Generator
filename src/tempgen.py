# -*- coding: utf-8 -*-
import os
import sys
import re
import json

from parsers import ext_parser_map
from transforms import name_transform_map

try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    approot = os.path.dirname(sys.executable)

class Tempgen():
    def __init__(self):
        # INIT VALUES
        self.fields = {} # key - id, value - { id, title, __stringVar, __entry }
        self.templates = [] # value - { path }

    def findMatches(self, text):
        return re.findall(r'{{{.+?}}}+', text)

    def loadTemplate(self, template):
        if template in self.templates:
            return
        name, ext = os.path.splitext(template)
        if not (ext in ext_parser_map.keys()):
            return
        ext_parser_map[ext].parse(template, self.fields, self.parseEntry, self.findMatches)
        self.templates.append(template)
        
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

    def save_result(self, template_path, target_name, replacements):
        name, ext = os.path.splitext(template_path)
        if not (ext in ext_parser_map.keys()):
            return
        ext_parser_map[ext].replace(
            template_path,
            target_name + ext,
            self.computeMatch,
            replacements
        )

    def save_template(self, template, replacements, updateExternals):
        name, ext = os.path.splitext(template)
        if not (ext in ext_parser_map.keys()):
            return
        ext_parser_map[ext].replace(
            template,
            name + ext,
            self.computeUpdatedTemplate,
            replacements,
            updateExternals
        )

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

    def computeMatch(self, text, to_replace, replacements, *args, **kwargs): # find matches, populate to_replace, return to_replace
        matches = self.findMatches(text)
        for match in matches:
            payload = self.parseEntry(match)
            value = replacements[payload['id']]
            if 'fn' in payload:
                if payload['fn'] in name_transform_map:
                    value = name_transform_map[payload['fn']](value)
            if 'monetary' in payload and payload['monetary']:
                value = "{:,.2f}".format(float(value)).replace(",", " ").replace('.', ',')
            if 'append' in payload:
                value = str(value) + payload['append']
            to_replace[match] = value
        return to_replace

    def computeUpdatedTemplate(self, text, to_replace, replacements, updateExternals): # find matches, populate to_replace, return to_replace
        matches = self.findMatches(text)
        for match in matches:
            payload = self.parseEntry(match)
            newValue = replacements[payload['id']]
            payload['value'] = newValue
            if (updateExternals):
                if payload.get('autocomplete') and payload.get('autocomplete', {}).get('data'):
                    if newValue not in payload['autocomplete']['data']:
                        payload['autocomplete']['data'].append(newValue) 
                        self.saveExternal(payload['autocomplete']['external'], payload['autocomplete']['data'])
                    del payload['autocomplete']['data']
            to_replace[match] = '{{' + json.dumps(payload, ensure_ascii=False) + '}}'
        return to_replace  

    def reload_externals(self):
        for entry in self.fields.values():
            autocomplete = entry.get('autocomplete')
            if autocomplete:
                if type(autocomplete) is dict and autocomplete.get('external'):
                    external = self.loadExternal(autocomplete.get('external'))
                    self.fields[entry['id']]['autocomplete']['data'] = external
