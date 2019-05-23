from device import DeviceDef, UdcMap
from dtf import DTF
import pandas as pd

mappings = pd.read_excel("docs/Book1.xlsx", sheet_name="Sheet1")
dd = DeviceDef("docs/CO1_delta0515.xml")
dtfxml = DTF("NGL_ET_AB_CIP_20190502_1318.dtf")

devices = mappings.device.unique()
for d in devices:
    dev_points = mappings.loc[mappings['device'] == d]
    dev_arr = dev_points.array.unique()
    facs = []
    for da in dev_arr:
        arr_points = dev_points.loc[dev_points['array'] == da]
        maps = []
        for i, p in arr_points.iterrows():
            udc = UdcMap(p["uniformdatacode"], p["indexed"], p["facilityid"])
            if dtfxml.check_dg_element(da, udc.data_id):
                maps.append(udc)
            else:
                print("{} not found in {} array".format(udc.data_id, da))
            facs.append(p["facilityid"]) if p["facilityid"] not in facs else None
        dd.add_maps(d, da, maps)
        dd.add_facs(facs, d)

dd.save("docs/CO1_delta0515_updated.xml")
