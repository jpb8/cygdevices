from xml.etree.ElementTree import SubElement, ElementTree
import xml.etree.ElementTree as ET


class DTF:
    # TODO : Create Parent class that parses supplied xml
    def __init__(self, dtf_filepath):
        self.xml = None
        self.device_xml_path = dtf_filepath
        self.create_xml()

    def create_xml(self):
        tree = ET.parse(self.device_xml_path)
        root = tree.getroot()
        self.xml = root

    def find_dg_element(self, array_type, element):
        return self.xml.find('dataGroups/{}/dgElements/{}'.format(array_type, element))

    def check_dg_element(self, array_type, element):
        return True if self.find_dg_element(array_type, element) is not None else False
