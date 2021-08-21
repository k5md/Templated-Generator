from odf import opendocument, text, teletype, element, table
import shutil
from functools import partial

class Parser():
    def parse(self, path, container, parse_entry, find_matches):
        doc = opendocument.load(path)
        paragraphs = doc.getElementsByType(text.P)
        for s in map(teletype.extractText, paragraphs):
            matches = find_matches(s)
            for match in matches:
                payload = parse_entry(match, path)
                container[payload['id']] = payload ## add check here for duplicates

    def replace(self, source_path, target_path, compute_match, replacements, update_external = False):
        doc = opendocument.load(source_path)
        for span in doc.getElementsByType(text.Span):
            s = teletype.extractText(span)
            local_to_replace = compute_match(s, {}, replacements, source_path, update_external)
            for match, value in local_to_replace.items():
                if s.find(match) != -1:
                    s = s.replace(match, value)
                    span._get_firstChild().data = s
        for cell in doc.getElementsByType(table.TableCell):
            for paragraph in cell.getElementsByType(text.P):
                s = teletype.extractText(paragraph)
                local_to_replace = compute_match(s, {}, replacements, source_path, update_external)
                for match, value in local_to_replace.items():
                    if s.find(match) != -1:
                        s = s.replace(match, value)
                        # TODO: first child won't do if there are forced multiple text entries separated by inserted self-closing span
                        paragraph._get_firstChild().data = s 
        doc.save(target_path)
