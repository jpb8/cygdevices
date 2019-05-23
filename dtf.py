import xml.etree.ElementTree as ET
import pandas as pd


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

    def create_array_excel(self, array_file_name, deid_file_name):
        data_groups = self.xml.find('dataGroups')
        arrs = {"id": [], "niceName": []}
        dg_elems = {"deid": [], "array_id": [], "tagName": [], "niceName": [], "desc": []}
        for elem in data_groups:
            arrs["id"].append(elem.tag)
            arrs["niceName"].append(elem.get("niceName"))
            print(elem.tag, elem.get("niceName"))
            for died in elem.find("dgElements"):
                print(died.tag, died.get("niceName"), died.get("tagname"), died.get("desc"))
                dg_elems["deid"].append(died.tag)
                dg_elems["array_id"].append(elem.tag)
                dg_elems["tagName"].append(died.get("tagname"))
                dg_elems["niceName"].append(died.get("niceName"))
                dg_elems["desc"].append(died.get("desc"))
        df = pd.DataFrame(data=arrs)
        df2 = pd.DataFrame(data=dg_elems)
        df.to_excel(array_file_name)
        df2.to_excel(deid_file_name)
