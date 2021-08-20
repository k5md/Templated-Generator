import os
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET
import shutil
from src.utils import extract_zip

class BaseTextExtension():
    def __init__(self, text = ''):
        self.text = text

    def __repr__(self):
        return f"{self.__class__.__name__}(\n{self.text}\n)"

class PlaintextExtension(BaseTextExtension):
    def __init__(self, file_path):
        super().__init__()
        with open(file_path, 'r', encoding='utf-8') as file:
            self.text = str(file.read())

class DocxExtension(BaseTextExtension):
    def __init__(self, file_path):
        super().__init__()
        temp_path = file_path + '_temp'
        extract_zip(file_path, temp_path)
        tree = ET.parse(os.sep.join([temp_path, 'word', 'document.xml']))
        xmlstr = ET.tostring(tree.getroot(), encoding='utf-8', method='xml')
        self.text = xmlstr
        shutil.rmtree(temp_path)

class XlsxExtension(BaseTextExtension):
    def __init__(self, file_path):
        super().__init__()
        temp_path = file_path + '_temp'
        extract_zip(file_path, temp_path)
        tree = ET.parse(os.sep.join([temp_path, 'xl', 'sharedStrings.xml']))
        xmlstr = ET.tostring(tree.getroot(), encoding='utf-8', method='xml')
        self.text = xmlstr
        shutil.rmtree(temp_path)

class OdfExtension(BaseTextExtension):
    def __init__(self, file_path):
        super().__init__()
        temp_path = file_path + '_temp'
        extract_zip(file_path, temp_path)
        tree = ET.parse(os.sep.join([temp_path, 'content.xml']))
        xmlstr = ET.tostring(tree.getroot(), encoding='utf-8', method='xml')
        self.text = xmlstr
        shutil.rmtree(temp_path)

ext_serializer_map = {
    '.docx': DocxExtension,
    '.xlsx': XlsxExtension,
    '.md': PlaintextExtension,
    '.txt': PlaintextExtension,
    '.odt': OdfExtension,
    '.ods': OdfExtension,
}