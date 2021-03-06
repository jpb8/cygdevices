from lxml import etree
from lxml.etree import SubElement
import pandas as pd


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

    def export_data(self):
        """
        Export all UIS mappings for easy validation
        :return: Pandas DF of all UIS mappings
        """
        devs_dict = {
            "dev_id": [],
            "comm_id": [],
            "desc": [],
            "dg_type": [],
            "deid": [],
            "last_char": [],
            "fac": [],
            "udc": []
        }
        for elem in self.xml:
            dev_id = elem.get("device_id")
            comm_id = elem.find("DeviceAttributes/CommunicationId1").text
            for data_group in elem.find("DataGroups"):
                desc = data_group.find("DataGroupAttributes/Description").text
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    devs_dict["dev_id"].append(dev_id)
                    devs_dict["comm_id"].append(comm_id)
                    devs_dict["desc"].append(desc)
                    devs_dict["dg_type"].append(dg_type)
                    devs_dict["deid"].append(m.get("data_element_id"))
                    devs_dict["last_char"].append(m.get("data_element_id")[-2:])
                    devs_dict["fac"].append(m.get("facility"))
                    devs_dict["udc"].append(m.get("UDC"))
        return pd.DataFrame(data=devs_dict)

    def uis_commands(self):
        """
        Format DDS XML to a usable Excel dataframe to for mapping validation
        Every component will have single line
        :return: Pandas DataFrame of all components in the xml
        """
        def _dg_type(s_cmd):
            s_cmd["dev_id"] = dev_id
            s_cmd["comm_id"] = comm_id
            s_cmd["desc"] = cmd_decs
            s_cmd["UIS_fac"] = fac
            s_cmd["cmd_name"] = cmd_name
            s_cmd["comp_type"] = c_type
            s_cmd["comp_pos"] = c.get("position")
            s_cmd["DGORD"] = c.find("Param[@key='DGORD']").get("value")
            s_cmd["DGTYPE"] = c.find("Param[@key='DGTYPE']").get("value")
            xpath = c.xpath("Param[starts-with(@key,'L')]")[0] if len(
                c.xpath("Param[starts-with(@key,'L')]")) != 0 else None
            if xpath is not None:
                s_cmd["LD"] = xpath.get("key")
                s_cmd["Value"] = xpath.get("value")
            append_cmd(s_cmd)

        def _cyupdtpt(s_cmd):
            s_cmd["dev_id"] = dev_id
            s_cmd["comm_id"] = comm_id
            s_cmd["desc"] = cmd_decs
            s_cmd["UIS_fac"] = fac
            s_cmd["cmd_name"] = cmd_name
            s_cmd["comp_type"] = c_type
            s_cmd["comp_pos"] = c.get("position")
            for param in c:
                s_cmd[param.get("key")] = param.get("value")
            append_cmd(s_cmd)

        def append_cmd(cmd_sing):
            for k, v in cmd_sing.items():
                cmd_dict[k].append(v)

        cmd_dict = {
            "dev_id": [],
            "comm_id": [],
            "desc": [],
            "UIS_fac": [],
            "cmd_name": [],
            "comp_type": [],
            "comp_pos": [],
            "DGORD": [],
            "DGTYPE": [],
            "LD": [],
            "Fac": [],
            "FOnErr": [],
            "Serv": [],
            "Site": [],
            "UDC": [],
            "UType": [],
            "Value": [],
        }
        for elem in self.xml:
            dev_id = elem.get("device_id")
            comm_id = elem.find("DeviceAttributes/CommunicationId1").text
            for uis in elem.find("UisCommands"):
                cmd_name = uis.find('CommandAttributes/Name').text
                cmd_decs = uis.find('CommandAttributes/Description').text
                fac = uis.find('CommandAttributes/Facility').text
                for c in uis.find("CommandComponents"):
                    _cmd = {
                        "dev_id": "",
                        "comm_id": "",
                        "desc": "",
                        "UIS_fac": "",
                        "cmd_name": "",
                        "comp_type": "",
                        "comp_pos": "",
                        "DGORD": "",
                        "DGTYPE": "",
                        "LD": "",
                        "Fac": "",
                        "FOnErr": "",
                        "Serv": "",
                        "Site": "",
                        "UDC": "",
                        "UType": "",
                        "Value": "",
                    }
                    c_type = c.get("type")
                    if c_type == "DG_T_DEV" or c_type == "DG_F_DEV":
                        _dg_type(_cmd)
                    elif c_type == "CYUPDTPT":
                        _cyupdtpt(_cmd)
        return pd.DataFrame(data=cmd_dict)

    def mapped_fac_check(self):
        """
        :return: A list and their devices that are not mapped correctly
        """
        unmapped = []
        for elem in self.xml:
            facs = []
            dev_id = elem.get("device_id")
            for data_group in elem.find("DataGroups"):
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    facs.append(m.get("facility")) if m.get("facility") not in facs else None
            for f in facs:
                fac_link = elem.find("FacilityLinks/FacilityLink[@id='{}']".format(f))
                unmapped.append({
                    "facility": fac_link,
                    "device": dev_id
                })
        return unmapped

    def fac_exists_check(self, facs):
        """
        :param facs:
        :return: A list of facilities and their device that do no exist in the supplied Facility list
        """
        dne = []
        for elem in self.xml:
            dev_id = elem.get("device_id")
            for f in elem.find("FacilityLinks"):
                dne.append({
                    "device": dev_id,
                    "facility": f.get("id")
                })
        return dne

    def correct_dev_check(self):
        """
        Check the first 4 letters in every facility and check that it matches with the first 4 of the device
        :return: List of all Points that do not match
        """
        non_matches = []
        for elem in self.xml:
            dev_id = elem.get("device_id").split("_")[0]
            dev_full = elem.get("device_id")
            for data_group in elem.find("DataGroups"):
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    if m.get("facility").split("_")[0] != dev_id:
                        non_matches.append({
                            "deid": m.get("data_element_id"),
                            "facility": m.get("facility"),
                            "udc": m.get("UDC"),
                            "dg_type": dg_type,
                            "device": dev_full,
                        })
        return non_matches

    def find_orphans(self, dtf):
        orphans = {
            "device": [],
            "array": [],
            "deid": []
        }
        for elem in self.xml:
            dev_id = elem.get("device_id")
            for data_group in elem.find("DataGroups"):
                dg_type = data_group.find("DataGroupAttributes/DataGroupType").text
                for m in data_group.find("UdcMappings"):
                    chck = dtf.check_dg_element(dg_type, m.get("data_element_id"))
                    if not chck:
                        orphans['device'].append(dev_id)
                        orphans['array'].append(dg_type)
                        orphans['deid'].append(m.get("data_element_id"))
        return orphans

    def export_mappings(self, file_name):
        df_pnt = self.export_data()
        df_cmd = self.uis_commands()
        writer = pd.ExcelWriter(file_name, engine="xlsxwriter")
        df_pnt.to_excel(writer, sheet_name="PNTS")
        df_cmd.to_excel(writer, sheet_name="CMDS")
        writer.save()


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
