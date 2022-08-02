from pytest import fixture
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString

@fixture
def et():
    return ET.parse('tests/test_inputs/p23_def.xml').getroot()

@fixture
def dom():
    return parse('tests/test_inputs/p23_def.xml')    



def test_sched(dom):
    pass
