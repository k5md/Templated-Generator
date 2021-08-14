from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET
import shutil

class PlaintextExtension():
    def __init__(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.text = str(file.read())

    def __repr__(self):
        return f"{self.__class__.__name__}(\n{self.text}\n)"

class DocxExtension():
    def __init__(self, file_path):
        temp_path = file_path + '_temp'
        with ZipFile(file_path, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            for fileName in listOfFileNames:
                zipObj.extract(fileName, temp_path)
        
        tree = ET.parse('\\'.join([temp_path, 'word', 'document.xml']))
        xmlstr = ET.tostring(tree.getroot(), encoding='utf8', method='xml')
        root = tree.getroot()
        self.text = xmlstr
        shutil.rmtree(temp_path)

    def __repr__(self):
        return f"{self.__class__.__name__}(\n{self.text}\n)"

class XlsxExtension():
    def __init__(self, file_path):
        temp_path = file_path + '_temp'
        with ZipFile(file_path, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            for fileName in listOfFileNames:
                zipObj.extract(fileName, temp_path)
            
        ET.register_namespace('','http://schemas.openxmlformats.org/spreadsheetml/2006/main')
        tree = ET.parse('\\'.join([temp_path, 'xl', 'sharedStrings.xml']))
        xmlstr = ET.tostring(tree.getroot(), encoding='utf8', method='xml')
        root = tree.getroot()
        self.text = xmlstr
        shutil.rmtree(temp_path)

    def __repr__(self):
        return f"{self.__class__.__name__}(\n{self.text}\n)"

ext_serializer_map = {
    '.docx': DocxExtension,
    '.xlsx': XlsxExtension,
    '.md': PlaintextExtension,
    '.txt': PlaintextExtension,
}