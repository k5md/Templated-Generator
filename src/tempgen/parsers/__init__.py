from . import docx
from . import xlsx
from . import plaintext
from . import ods
from . import odt

ext_parser_map = {
    '.docx': docx,
    '.xlsx': xlsx,
    '.md': plaintext,
    '.txt': plaintext,
    '.odt': odt,
    '.ods': ods,
}
