import os
import xml.etree.ElementTree as ET
import shutil
from utils import extract_zip, make_zip

def parse(path, container, parse_entry, find_matches):
    temp_path = path + '_temp'
    extract_zip(path, temp_path)
    ET.register_namespace('','http://schemas.openxmlformats.org/spreadsheetml/2006/main')
    tree = ET.parse(os.sep.join([temp_path, 'xl', 'sharedStrings.xml']))
    root = tree.getroot()
    for si in root:
        for t in si:
            text = t.text
            matches = find_matches(str(text))
            for match in matches:
                payload = parse_entry(match, path)
                container[payload['id']] = payload ## TODO: add check here for duplicates
    shutil.rmtree(temp_path)

def replace(source_path, target_path, compute_match, replacements, update_external = False):
    temp_path = source_path + '_temp'
    try:
        shutil.rmtree(temp_path)
    except Exception as e:
        pass
    extract_zip(source_path, temp_path)
        
    ET.register_namespace('','http://schemas.openxmlformats.org/spreadsheetml/2006/main')
    tree = ET.parse(os.sep.join([temp_path, 'xl', 'sharedStrings.xml']))
    root = tree.getroot()
    for si in root:
        for t in si:
            text = t.text
            local_to_replace = compute_match(t.text, {}, replacements, source_path, update_external)
            for match, value in local_to_replace.items():
                text = text.replace(match, value)
            t.text = text
    tree.write(os.path.join(temp_path, 'xl', 'sharedStrings.xml'))
    make_zip(temp_path, target_path)
    shutil.rmtree(temp_path)