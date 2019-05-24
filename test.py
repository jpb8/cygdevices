from device import DeviceDef, UdcMap
from dtf import DTF
import pandas as pd

mappings = pd.read_excel("docs/Book2.xlsx", sheet_name="Sheet1")
dd = DeviceDef("docs/dds_C15_MHR6_to_MID2.xml")
dtfxml = DTF("docs/NGL_ET_AB_CIP_20190502-1318.dtf")


def create_udc(dtfxml, row):
    _udc = None
    if row["type"] == "A":
        deid = dtfxml.get_analog_deid(da, row["indexed"], str(int(row["bit"])))
        if deid:
            _udc = UdcMap(row["uniformdatacode"], deid, row["facilityid"])
    elif row["type"] == "D":
        deid_check = dtfxml.check_dg_element(row["array"], row["deid"])
        if deid_check:
            _udc = UdcMap(row["uniformdatacode"], row["deid"], row["facilityid"])
    return _udc


devices = mappings.device.unique()
for d in devices:
    dev_points = mappings.loc[mappings['device'] == d]
    dev_arr = dev_points.array.unique()
    facs = []
    if dd.check_device(d):
        for da in dev_arr:
            arr_points = dev_points.loc[dev_points['array'] == da]
            maps = []
            for i, p in arr_points.iterrows():
                udc = create_udc(dtfxml, p)
                maps.append(udc) if udc is not None else print(
                    "{} Not in {} Array".format(p["deid"], p["array"]))
                facs.append(p["facilityid"]) if p["facilityid"] not in facs else None
            dd.add_maps(d, da, maps)
            dd.add_facs(facs, d)
    else:
        print("Device {} is not in XML".format(d))

dd.save("docs/C15_updated.xml")
