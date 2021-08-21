from . import docx
from . import xlsx
from . import plaintext
from . import ods
from . import odt

class Parsers():
    def __init__(self):
        self.ext_parser_map = {
            '.docx': docx.Parser(),
            '.xlsx': xlsx.Parser(),
            '.md': plaintext.Parser(),
            '.txt': plaintext.Parser(),
            '.odt': odt.Parser(),
            '.ods': ods.Parser(),
        }
