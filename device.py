from xml.etree.ElementTree import SubElement, ElementTree
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
        dgs = self.device_dgs_element(device_id)
        if dgs.find('./DataGroup/DataGroupAttributes/[DataGroupType="{}"].../UdcMappings'.format(array_type)) is None:
            dg = DataGroup(device_id, device_id, array_type)
            dgs.append(dg.dg_element)
            print("appended {} {} DataGroup".format(device_id, array_type))
        return dgs.find('./DataGroup/DataGroupAttributes/[DataGroupType="{}"].../UdcMappings'.format(array_type))

    def add_maps(self, device_id, array_type, maps):
        mappings = self.device_dg_mappings(device_id, array_type)
        for m in maps:
            if mappings.find(".//UdcMapping[@UDC='{}'][@data_element_id='{}'][@facility='{}']".format(
                    m.udc,
                    m.data_id,
                    m.fac)
            ) is None:
                SubElement(mappings, "UdcMapping", {
                    "UDC": m.udc,
                    "data_element_id": m.data_id,
                    "facility": m.fac
                })
            else:
                print("{} {} {} mapping already exists".format(m.udc, m.data_id, m.fac))

    def add_facs(self, facs, device_id):
        fac_elem = self.device_facs_element(device_id)
        for f in facs:
            if fac_elem.find("./FacilityLink[@id='{}']".format(f)) is None:
                SubElement(fac_elem, "FacilityLink", {"id": f, "ordinal": str(len(fac_elem))})
                print("{} was linkded".format(f))

    def save(self, xml_file):
        et = ElementTree(self.xml)
        file = open(xml_file, "wb")
        et.write(file)
        file.close()


class DataGroup:
    def __init__(self, description, fac_id, dg_type):
        self.description = description
        self.fac_id = fac_id
        self.dg_type = dg_type
        self.dg_element = None
        self.create_element()

    def create_element(self):
        tree = ET.parse("utils/DataGroup.xml")
        root = tree.getroot()
        root.find("DataGroupAttributes/Description").text = self.description
        root.find("DataGroupAttributes/FacilityId").text = self.fac_id
        root.find("DataGroupAttributes/DataGroupType").text = self.dg_type
        self.dg_element = root

    @property
    def udc_maps(self):
        return self.dg_element.find("UdcMappings")


class UdcMap:
    def __init__(self, udc, data_id, fac):
        self.udc = udc
        self.data_id = data_id
        self.fac = fac
