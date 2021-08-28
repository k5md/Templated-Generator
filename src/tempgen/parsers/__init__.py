from . import docx
from . import xlsx
from . import plaintext
from . import ods
from . import odt

class Parsers():
    """Class contains dictionary of extensions as keys and parser instances as values, providing tools for text extraction and replacement

    Attributes
    ----------
    ext_parser_map : Dict[str, AbstractParser]
        Dictionary containing supported file extensions, uses extension name as key
        and instance of class implementing AbstractParser interface as value
    """
    def __init__(self):
        self.ext_parser_map = {
            '.docx': docx.Parser(),
            '.xlsx': xlsx.Parser(),
            '.md': plaintext.Parser(),
            '.txt': plaintext.Parser(),
            '.odt': odt.Parser(),
            '.ods': ods.Parser(),
        }
