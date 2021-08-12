import os
import re
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET
import shutil

def parse(path, container, parse_entry, find_matches):
    temp_path = path + '_temp'
    with ZipFile(path, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        for fileName in listOfFileNames:
            zipObj.extract(fileName, temp_path)
        
    ET.register_namespace('','http://schemas.openxmlformats.org/spreadsheetml/2006/main')
    tree = ET.parse('\\'.join([temp_path, 'xl', 'sharedStrings.xml']))
    root = tree.getroot()
    for si in root:
        for t in si:
            text = t.text
            matches = find_matches(str(text))
            for match in matches:
                payload = parse_entry(match, path)
                container[payload['id']] = payload ## add check here for duplicates
    shutil.rmtree(temp_path)

def replace(source_path, target_path, compute_match, replacements, update_external = False):
    temp_path = source_path + '_temp'
    try:
        shutil.rmtree(temp_path)
    except Exception as e:
        pass
    lastPortion = temp_path.split('\\')[-1] # relative path for zipf arcname construction
    with ZipFile(source_path, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        for fileName in listOfFileNames:
            zipObj.extract(fileName, temp_path)
        
    ET.register_namespace('','http://schemas.openxmlformats.org/spreadsheetml/2006/main')
    tree = ET.parse('\\'.join([temp_path, 'xl', 'sharedStrings.xml']))
    root = tree.getroot()
    for si in root:
        for t in si:
            text = t.text
            local_to_replace = compute_match(t.text, {}, replacements, source_path, update_external)
            for match, value in local_to_replace.items():
                text = text.replace(match, value)
            t.text = text
    tree.write(os.path.join(temp_path, 'xl', 'sharedStrings.xml'))
    zipf = ZipFile(target_path, 'w', ZIP_DEFLATED)
    for folderName, subfolders, filenames in os.walk(temp_path):
        for filename in filenames:
            filepath = os.path.join(folderName, filename)
            segments = filepath.split(os.sep)
            archivePath = segments[segments.index(lastPortion):]
            zipf.write(filepath, arcname=os.sep.join(archivePath[1:]))
    zipf.close()
    shutil.rmtree(temp_path)