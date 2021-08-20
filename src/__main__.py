import os
import sys
import argparse
import json
from tempgen_gui import App
from tempgen import Tempgen

if len(sys.argv) == 1:
    app = App()
    app.mainloop()

parser = argparse.ArgumentParser(description = 'Generate files from templates with template entries replaced')

parser.add_argument(
    '--input',
    dest='templates',
    nargs='+',
    help='absolute or relative paths to templates, e.g. --input template.docx template.md ... template.xlsx',
    required=True
)
parser.add_argument(
    '--output',
    dest='output',
    help='absolute or relative path to store generated files without extension, e.g. --output foo/bar/generated where "generated" will be the filename'
)
parser.add_argument(
    '--replacements',
    dest='replacements',
    type=json.loads,
    action='store',
    help='json dictionary with template entry ids as keys and desired string values, e.g. --replacements {\"receipt_number\":\"42\"}, note no spaces between key, colon and value and escape double quotes on Windows'
)

parser.add_argument(
    '--update-templates',
    dest='update_templates',
    action='store_true',
    help='update value field in each template entry'
)
parser.add_argument(
    '--update-externals',
    dest='update_externals',
    action='store_true',
    help='update external resources from template with new value from replacements'
)

args = parser.parse_args()

templates = [ os.sep.join([os.getcwd(), template]) if not os.path.isabs(template) else template for template in args.templates]
replacements = args.replacements or {}
actions = []
tempgen = Tempgen()

for template in templates:
    actions.append(lambda: tempgen.load_template(template))
    actions.append(lambda: tempgen.save_result(template, args.output, replacements))
    if args.update_templates:
        actions.append(lambda: tempgen.save_template(template, replacements, args.update_externals))
for action in actions:
    action()
