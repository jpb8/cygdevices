from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
import xml.etree.ElementTree as ET


class DeviceDef:
    def __init__(self, device_xml_path):
        self.xml = None
        self.device_xml_path = device_xml_path
        self.create_xml()

    def create_xml(self):
        tree = ET.parse(self.device_xml_path)
        root = tree.getroot()
        self.xml = root

    def get_device(self, device_id):
        return self.xml.find('./Device[@device_id="{}"]'.format(device_id))

    def device_dgs_element(self, device_id):
        return self.get_device(device_id).find("DataGroups")

    def device_facs_element(self, device_id):
        return self.get_device(device_id).find("FacilityLinks")

    def device_dg_mappings(self, device_id, array_type):
        # TODO : Create new DataGroup from xml template if one does not exist
        dgs = self.device_dgs_element(device_id)
        return dgs.find('./DataGroup/DataGroupAttributes/[DataGroupType="{}"].../UdcMappings'.format(array_type))

    def add_maps(self, device_id, array_type, maps):
        # TODO : Check of the mapping already exists
        # TODO : Check in DTF in the Data Element ID exists in that array
        mappings = self.device_dg_mappings(device_id, array_type)
        for m in maps:
            SubElement(mappings, "UdcMapping", {
                "UDC": m.udc,
                "data_element_id": m.data_id,
                "facility": m.fac
            })

    def add_facs(self, facs, device_id):
        fac_elem = self.device_facs_element(device_id)
        for f in facs:
            if fac_elem.find(".//*[@id='{}']".format(f)) is None:
                SubElement(fac_elem, "FacilityLink", {"id": f, "ordinal": str(len(fac_elem))})
                print("{} was linkded".format(f))

    def save(self, xml_file):
        et = ElementTree(self.xml)
        file = open(xml_file, "wb")
        et.write(file)
        file.close()


class DataGroup:
    def __init__(self, description, fac_id, dg_type):
        self.mappings = []
        self.description = description
        self.fac_id = fac_id
        self.dg_type = dg_type
        self.dg_element = None
        self.create_element()

    def create_element(self):
        tree = ET.parse("dataGroupShell.xml")
        root = tree.getroot()
        root.find("DataGroupAttributes/Description").text = self.description
        root.find("DataGroupAttributes/FacilityId").text = self.fac_id
        root.find("DataGroupAttributes/DataGroupType").text = self.dg_type
        self.dg_element = root

    @property
    def udc_maps(self):
        return self.dg_element.find("UdcMappings")

    def add_map(self, udc_map):
        self.mappings.append(udc_map)
        SubElement(self.udc_maps, "UdcMapping", {
            "UDC": udc_map.udc,
            "data_element_id": udc_map.data_id,
            "facility": udc_map.fac
        })


class UdcMap:
    def __init__(self, udc, data_id, fac):
        self.udc = udc
        self.data_id = data_id
        self.fac = fac
