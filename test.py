from device import DeviceDef, UdcMap, DataGroup
import pandas as pd
import os

mappings = pd.read_excel("Book1.xlsx", sheet_name="Sheet1")
dd = DeviceDef("CO1_delta0515.xml")

devices = mappings.device.unique()
for d in devices:
    dev_points = mappings.loc[mappings['device'] == d]
    dev_arr = dev_points.array.unique()
    for da in dev_arr:
        arr_points = dev_points.loc[dev_points['array'] == da]
        maps = []
        for i, p in arr_points.iterrows():
            udc = UdcMap(p["uniformdatacode"], p["indexed"], p["facilityid"])
            maps.append(udc)
        dd.add_maps(d, da, maps)
dd.save("CO1_delta0515_updated.xml")