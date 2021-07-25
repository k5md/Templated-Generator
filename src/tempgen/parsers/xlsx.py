import os
import re
import pyexcel
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET
import shutil

def parse(path, container, parseEntry):
  sheet = pyexcel.get_sheet(file_name=path)
  for row in sheet:
      for cell in row:
          matches = re.findall(r'{{.+?}}', str(cell))
          for match in matches:
              payload = parseEntry(match)
              container[payload['id']] = payload ## add check here for duplicates

def replace(sourcePath, targetPath, computeMatch):
    tempPath = sourcePath + '_temp'
    with ZipFile(sourcePath, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        for fileName in listOfFileNames:
            zipObj.extract(fileName, tempPath)
        
    ET.register_namespace('','http://schemas.openxmlformats.org/spreadsheetml/2006/main')
    tree = ET.parse('\\'.join([tempPath, 'xl', 'sharedStrings.xml']))
    root = tree.getroot()
    for si in root:
        for t in si:
            text = t.text
            local_to_replace = computeMatch(t.text, {})
            for match, value in local_to_replace.items():
                text = text.replace(match, value)
            t.text = text
    tree.write('\\'.join([tempPath, 'xl', 'sharedStrings.xml']))
    zipf = ZipFile(targetPath, 'w', ZIP_DEFLATED)
    for folderName, subfolders, filenames in os.walk(tempPath):
        for filename in filenames:
            filepath = os.path.join(folderName, filename)
            zipf.write(filepath, arcname='\\'.join(filepath.split('\\')[1:]))
    zipf.close()
    shutil.rmtree(tempPath)