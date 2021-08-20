import pytest
import os
import os
from collections import defaultdict
from syrupy.extensions.single_file import SingleFileSnapshotExtension
from tempgen.tempgen_mod import Tempgen
from tempgen.parsers import ext_parser_map
from tempgen.tests.helpers import ext_serializer_map

tests_dir = os.path.dirname(os.path.abspath(__file__))
fixture_dir = os.path.join(tests_dir, 'fixtures')
fixture_name = 'test_template'
generated_name = 'generated'

extensions = ext_parser_map.keys()
serializers = ext_serializer_map

@pytest.fixture(autouse=True)
def tempgen_instance():
    return Tempgen()

@pytest.mark.parametrize('extension', extensions)
def test_load_template(extension, tempgen_instance, snapshot):
    template = os.path.join(fixture_dir, fixture_name + extension)
    tempgen_instance.load_template(template)
    assert template in tempgen_instance.get_templates()
    assert tempgen_instance.get_fields() == snapshot

@pytest.mark.parametrize('extension', extensions)
def test_save_result(extension, tempgen_instance, snapshot):
    template = os.path.join(fixture_dir, fixture_name + extension)
    tempgen_instance.load_template(template)
    replacements = { key: value['value'] for key, value in tempgen_instance.get_fields().items() }
    replacements['doer'] = 'Петров П.П.'
    replacements['itn'] = '987654321098'
    save_path = os.path.join(fixture_dir, generated_name)
    tempgen_instance.save_result(template, save_path, replacements)
    assert ext_serializer_map[extension](save_path + extension) == snapshot
    os.remove(save_path + extension)
