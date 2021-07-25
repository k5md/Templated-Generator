import sys
import re
import docx
from utils.docx_replace import replace as docx_replace

def parse(path, container, parseEntry):
    doc = docx.Document(path)
    for p in doc.paragraphs:
        matches = re.findall(r'{{.+?}}', p.text)
        for match in matches:
            payload = parseEntry(match)
            container[payload['id']] = payload ## add check here for duplicates
    for table in doc.tables:
        for col in table.columns:
            for cell in col.cells:
                for p in cell.paragraphs:
                    matches = re.findall(r'{{.+?}}', p.text)
                    for match in matches:
                        payload = parseEntry(match)
                        container[payload['id']] = payload ## add check here for duplicates

def replace(sourcePath, targetPath, computeMatch):
    doc = docx.Document(sourcePath)
    to_replace = {}
    for p in doc.paragraphs:
        computeMatch(p.text, to_replace)
        docx_replace(p, to_replace)
    for table in doc.tables:
        for col in table.columns:
            for cell in col.cells:
                for p in cell.paragraphs:
                    computeMatch(p.text, to_replace)
                    docx_replace(p, to_replace)
    doc.save(targetPath)