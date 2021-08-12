from . import docx
from . import xlsx
from . import plaintext

ext_parser_map = {
    '.docx': docx,
    '.xlsx': xlsx,
    '.md': plaintext,
    '.txt': plaintext,
}