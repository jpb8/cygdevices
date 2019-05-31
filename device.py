from lxml import etree
from lxml.etree import Element, SubElement, ElementTree


class DeviceDef:
    def __init__(self, device_xml_path):
        self.xml = None
        self.device_xml_path = device_xml_path
        self.create_xml()

    def create_xml(self):
        """
        Sets the xml prop to an ETREE root with the supplied xml file
        :return:
        """
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(self.device_xml_path, parser)
        root = tree.getroot()
        self.xml = root

    def check_device(self, device_id):
        """
        Check to see of the device exists in the xml by looking for the device_id attr in the device elements
        :param device_id:
        :return: True if exists, False if Not
        """
        return True if self.xml.find('./Device[@device_id="{}"]'.format(device_id)) is not None else None

    def get_device(self, device_id):
        """
        Gets device element
        :param device_id: Name of the device in CygNet
        :return: ETREE element for that device
        """
        return self.xml.find('./Device[@device_id="{}"]'.format(device_id))

    def device_dgs_element(self, device_id):
        return self.get_device(device_id).find("DataGroups") if self.get_device(device_id) is not None else None

    def device_facs_element(self, device_id):
        return self.get_device(device_id).find("FacilityLinks") if self.get_device(device_id) is not None else None

    def device_dg_mappings(self, device_id, array_type):
        """
        :param device_id: CygNet Device name
        :param array_type: The array name inside the device
        :return: Tuple of the DataGroup UdcMappings Element and Error message
        """
        dgs = self.device_dgs_element(device_id)
        if dgs is None:
            return None, "Device {} Not Found".format(device_id)
        if dgs.find('./DataGroup/DataGroupAttributes/[DataGroupType="{}"].../UdcMappings'.format(array_type)) is None:
            return None, "Array {} not found in Device {}".format(device_id, array_type)
            # dg = DataGroup(device_id, device_id, array_type)
            # dgs.append(dg.dg_element)
            # print("appended {} {} DataGroup".format(device_id, array_type))
        return dgs.find('./DataGroup/DataGroupAttributes/[DataGroupType="{}"].../UdcMappings'.format(array_type)), ""

    def add_maps(self, device_id, array_type, maps):
        """
        Maps all supplied UDCs the given Device's Array.
        Checks all UCDs to see they already exist
        :param device_id: CygNet Device name
        :param array_type: The array name inside the device
        :param maps: List of UDCs to be mapped
        :return: Any errors
        """
        mappings, err = self.device_dg_mappings(device_id, array_type)
        errs = []
        if mappings is None:
            errs.append(err)
            return errs
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
                errs.append("{} {} {} mapping already exists".format(m.udc, m.data_id, m.fac))
        return errs

    def add_facs(self, facs, device_id):
        """
        Addes all facs to the device's FacilityLinks Element
        :param facs: List of Facility names
        :param device_id: Device the facilities should be mapped too
        :return: Any errors
        """
        fac_elem = self.device_facs_element(device_id)
        log = []
        if fac_elem is not None:
            for f in facs:
                if fac_elem.find("./FacilityLink[@id='{}']".format(f)) is None:
                    SubElement(fac_elem, "FacilityLink", {"id": f, "ordinal": str(len(fac_elem))})
                    log.append("Facility {} was linkded to {} device".format(f, device_id))
        return log

    def save(self, xml_file):
        file = open(xml_file, "wb")
        file.write(etree.tostring(self.xml, pretty_print=True))
        file.close()


class DataGroup:
    def __init__(self, description, fac_id, dg_type):
        self.description = description
        self.fac_id = fac_id
        self.dg_type = dg_type
        self.dg_element = None
        self.create_element()

    def create_element(self):
        tree = etree.parse("utils/DataGroup.xml")
        root = tree.getroot()
        root.find("DataGroupAttributes/Description").text = self.description
        root.find("DataGroupAttributes/FacilityId").text = self.fac_id
        root.find("DataGroupAttributes/DataGroupType").text = self.dg_type
        self.dg_element = root

    @property
    def udc_maps(self):
        return self.dg_element.find("UdcMappings")


class UdcMap:
    """
    Used to build UdcMappings in the DeviceDef class
    """

    def __init__(self, udc, data_id, fac):
        self.udc = udc
        self.data_id = data_id
        self.fac = fac
