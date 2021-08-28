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
    """Class that generates files from templates with template entries replaced

    Typical workflow is as follows:
    - call load_template, which parses template based on its extension using map from Parsers instance
    - change fields
    - call save_result with changed fields as replacements argument

    Attributes
    ----------
    fields : Dict[str, Dict[str, Any]]
        Dictionary, containing parsed entries from templates, entry id is used as key, value is a dictionary,
        containing full entry payload
    templates : List[str]
        List of absolute paths to each loaded template
    parsers : Dict[str, callable]
        Dictionary, containing supported document extensions (e.g. '.docx') as keys and handlers for text extraction and modification as values
    transforms : Dict[str, callable]
        Dictionary containing supported "functions" allowed in "pre" and "post" objects as "fn" property value in templates, uses function name as key and
        function itself as value
    """
    def __init__(self):
        """Initializes fields and templates, creates new instances of parsers and transforms"""
        self.fields = {}
        self.templates = []
        self.parsers = Parsers().ext_parser_map
        self.transforms = Transforms().name_transform_map

    def find_matches(self, text):
        """Function called on parsable's text to find entries (valid JSON objects stringified, enclosed by double curly brackets)

        Parameters
        ----------
        text : str
            Text to find entries in

        Returns
        -------
        List
            List of entries, extracted from text
        """
        return re.findall(r'{{{.+?}}}+', text)

    def load_template(self, template):
        """Parse template if possible and append it to templates list

        Parameters
        ----------
        template : str
            Absolute path to template file
        """
        if template in self.templates:
            return
        name, ext = os.path.splitext(template)
        if not (ext in self.parsers.keys()):
            return
        self.parsers[ext].parse(template, self.fields, self.parse_entry, self.find_matches)
        self.templates.append(template)
        
    def clear_templates(self):
        """Clear templates list and reset fields"""
        self.templates = []
        self.fields = {}

    def load_external(self, file_name, template_path):
        """Parse JSON from external (referenced in template entries) files

        Parameters
        ----------
        file_name : str
            Full file name (name and extension) of external resource that has to be in the same folder as template
        template_path : str
            Absolute path to the template, containing reference to resource to be parsed

        Returns
        -------
        Union[Dict, List]
            Object created from JSON from parsed external resource
        """
        template_dir, _ = os.path.split(template_path)
        file_path = os.path.join(template_dir, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                payload = json.loads(content)
                return payload
    
    def save_external(self, file_name, template_path, payload):
        """Save external resource as JSON

        Parameters
        ----------
        file_name : str
            Full file name (name and extension) of external resource that has to be in the same folder as template
        template_path : str
            Absolute path to the template containing reference to resource
        payload : Union[Dict, List]
            Contents to be stored as JSON in file
        """
        template_dir, _ = os.path.split(template_path)
        file_path = os.path.join(template_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(payload, file, ensure_ascii=False)

    def save_result(self, template_path, target_name, replacements):
        """Save generated file from template with entries replaced

        Parameters
        ----------
        template_path : str
            Absolute path to template file
        target_name : str
            Name (without extension) of file to save results
        replacements : Dict[str, str]
            Dictionary with entries ids as keys and their substitutions as values
        """
        name, ext = os.path.splitext(template_path)
        if not (ext in self.parsers.keys()):
            return
        self.parsers[ext].replace(
            template_path,
            target_name + ext,
            self.compute_match,
            replacements
        )

    def save_template(self, template_path, replacements, update_externals):
        """Update template file entries with new values from replacements

        Parameters
        ----------
        template_path : str
            Absolute path to template file
        replacements : Dict[str, str]
            Dictionary with entries ids as keys and their substitutions as values
        update_externals : bool
            Flag specifying whether external resources referenced from template should be updated with new values
        """
        name, ext = os.path.splitext(template_path)
        if not (ext in self.parsers.keys()):
            return
        self.parsers[ext].replace(
            template_path,
            template_path,
            self.compute_updated_template,
            replacements,
            update_externals
        )

    def parse_entry(self, string, template_path):
        """Transform raw entry from template to dictionary

        Parses JSON in entry, loads external resources, applies transforms to entry value specified in "pre" entry property

        Parameters
        ----------
        string : str
            Raw entry string, that is valid JSON object stringified and enclosed in double curly brackets (
                {{{"id": "foo", "title": "Foo", "value": "bar \"Baz\""}}}
            )
        template_path : str
            Absolute path to template file

        Returns
        -------
        Dict[str, Any]
            Entry representation
        """
        content = string[2:-2]
        payload = json.loads(content)
        pre = payload.get('pre', [])
        for entry in pre:
            fn = entry.get('fn')
            args = entry.get('args', [])
            if fn in self.transforms:
                payload['value'] = self.transforms[fn](payload['value'], *args)
        autocomplete = payload.get('autocomplete', {})
        autocomplete_external = autocomplete.get('external')
        if autocomplete_external:
            external = self.load_external(autocomplete_external, template_path)
            payload['autocomplete']['data'] = external
        return payload

    def compute_match(self, text, to_replace, replacements, template_path, *args, **kwargs):
        """Given replacements dict (id -> value), populate to_replace dict (raw entry string -> transformed replaced value) and return to_replace

        Find matches in text, apply transforms specified in "post" entry property to replacement value, populate to_replace and return it

        For instance, given text " {{{"id": "foo", "title": "Foo", "value": "bar \"Baz\"", "post": [{"fn": "append", "args": [" baz"]}]}}} ",
        empty to_replace dictionary and { "foo": "bar" } as replacements dictionary, function will populate to_replace and
        to_replace will be: { "{{{"id": "foo", "title": "Foo", "value": "bar \"Baz\""}}}": "bar baz" }

        Parameters
        ----------
        text : str
            Text containing raw entries
        to_replace : Dict[str, str]
            Dictionary mapping raw entry strings from template file text to values, provided in replacements dictionary by id
        replacements : Dict[str, str]
            Dictionary mapping entry id to its value
        template_path : str
            Absolute path to template file

        Returns
        -------
        Dict[str, str]
            Dictionary mapping raw entry string to its transformed value
        """
        matches = self.find_matches(text)
        for match in matches:
            payload = self.parse_entry(match, template_path)
            value = replacements.get(payload['id'], payload['value'])
            post = payload.get('post', [])
            for entry in post:
                fn = entry.get('fn')
                args = entry.get('args', [])
                if fn in self.transforms:
                    value = self.transforms[fn](value, *args)
            to_replace[match] = value
        return to_replace

    def compute_updated_template(self, text, to_replace, replacements, template_path, update_externals):
        """Given replacements dict (id -> value), populate to_replace dict (raw entry string -> raw entry string with replaced value) and return to_replace

        Find matches in text, generate raw entry string with replaced value for each raw entry string match,
        update external resources, referenced in template with replaced value (if update_externals is set to True),
        populate to_replace with them and return to_replace dictionary

        For instance, given text " {{{"id": "foo", "title": "Foo", "value": "bar \"Baz\"", "post": [{"fn": "append", "args": [" baz"]}]}}} ",
        empty to_replace dictionary and { "foo": "bar" } as replacements dictionary, function will populate to_replace and
        to_replace will be: { "{{{"id": "foo", "title": "Foo", "value": "bar \"Baz\"", "post": [{"fn": "append", "args": [" baz"]}]}}}": 
        "{{{"id": "foo", "title": "Foo", "value": "bar", "post": [{"fn": "append", "args": [" baz"]}]}}}"}

        Parameters
        ----------
        text : str
            Text containing raw entries
        to_replace : Dict[str, str]
            Dictionary mapping raw entry strings from template file text to raw entry strings with values, provided in replacements dictionary by id
        replacements : Dict[str, str]
            Dictionary mapping entry id to its value
        template_path : str
            Absolute path to template file
        update_externals : bool
            Flag specifying whether external resources referenced from template should be updated with new values
        Returns
        -------
        Dict[str, str]
            Dictionary mapping raw entry strings to raw entry strings with replaced value
        """
        matches = self.find_matches(text)
        for match in matches:
            payload = self.parse_entry(match, template_path)
            newValue = replacements.get(payload['id'], payload['value'])
            payload['value'] = newValue
            if (update_externals):
                if payload.get('autocomplete') and payload.get('autocomplete', {}).get('data'):
                    if newValue not in payload['autocomplete']['data']:
                        payload['autocomplete']['data'].append(newValue)
                        self.save_external(payload['autocomplete']['external'], template_path, payload['autocomplete']['data'])
                    del payload['autocomplete']['data']
            to_replace[match] = '{{' + json.dumps(payload, ensure_ascii=False) + '}}'
        return to_replace  

    def reload_externals(self, template_path):
        """Reload entry external resources data from template

        Parameters
        ----------
        template_path : str
            Absolute path to template file
        """
        for entry in self.fields.values():
            autocomplete = entry.get('autocomplete')
            if autocomplete:
                if type(autocomplete) is dict and autocomplete.get('external'):
                    external = self.load_external(autocomplete.get('external'), template_path)
                    self.fields[entry['id']]['autocomplete']['data'] = external


    def get_templates(self):
        """Get list of absolute paths to loaded templates
        
        Returns
        -------
        List[str]
                List of absolute paths to each loaded template
        """
        return self.templates
    
    def get_fields(self):
        """Get dictionary, mapping entry id to entry representation from loaded templates
        
        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary, containing parsed entries from templates, entry id is used as key, value is a dictionary,
            containing full entry payload
        """
        return self.fields

    def set_fields(self, fields):
        """Set new/updated entries representations
        
        Parameters
        ----------
        fields : Dict[str, Dict[str, Any]]
            Dictionary, containing parsed entries from templates, entry id is used as key, value is a dictionary,
            containing full entry payload
        """
        self.fields = fields
