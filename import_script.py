from device import DeviceDef, UdcMap
from dtf import DTF
import pandas as pd


def create_udc(dtfxml, row, da):
    _udc = None
    err = None
    if row["type"] == "A":
        deid = dtfxml.get_analog_deid(da, row["indexed"], str(int(row["bit"])))
        if deid:
            _udc = UdcMap(row["uniformdatacode"], deid, row["facilityid"])
        else:
            err = "*DEID Not found* tagname: {}[{}], Array: {}, UDC: {} FAC: {}".format(
                row["indexed"], row["bit"], da,
                row["uniformdatacode"],
                row["facilityid"]
            )
    elif row["type"] == "D":
        deid_check = dtfxml.check_dg_element(row["array"], row["deid"])
        if deid_check:
            _udc = UdcMap(row["uniformdatacode"], row["deid"], row["facilityid"])
        else:
            err = "*DEID Not found* DEID: {}, Array {}, UDC: {} FAC: {}".format(
                row["deid"],
                da,
                row["uniformdatacode"],
                row["facilityid"]
            )
    return _udc, err


def dds_excel_import(mappings, dd, dtfxml):
    devices = mappings.device.unique()
    errs = []
    for d in devices:
        dev_points = mappings.loc[mappings['device'] == d]
        dev_arr = dev_points.array.unique()
        facs = []
        if dd.check_device(d):
            for da in dev_arr:
                arr_points = dev_points.loc[dev_points['array'] == da]
                maps = []
                for i, p in arr_points.iterrows():
                    udc, pnt_err = create_udc(dtfxml, p, da)
                    maps.append(udc) if udc is not None else errs.append(pnt_err)
                    facs.append(p["facilityid"]) if p["facilityid"] not in facs else None
                map_log = dd.add_maps(d, da, maps)
                fac_log = dd.add_facs(facs, d)
                errs = errs + map_log + fac_log
        else:
            errs.append("Device {} is not in XML".format(d))

    dd.save("docs/deviceDefinitions_20190530_updated.xml")
    with open('docs/errorLog.txt', 'w') as f:
        for e in errs:
            f.write("{}\n".format(e))




if __name__ == '__main__':
    # mappings = pd.read_excel("docs/C15_delta0530.xlsx", sheet_name="Sheet1")
    facs = pd.read_excel("docs/CRD2_allFacs.xlsx", sheet_name="Sheet1")
    all_facs = facs["id"].to_list()
    dd = DeviceDef("docs/dds_CRD2_20190606.xml")
    dd.correct_dev_check()
    # dtfxml = DTF("docs/NGL_ET_AB_CIP_20190605.dtf")
    # dtfxml.create_array_excel("docs/arrays.xlsx", "docs/deids_NGL_ET_AB_CIP_20190605.xlsx")
    # dds_excel_import(mappings, dd, dtfxml)
    # dd.export_mappings("docs/dds_NGLC15_dds_export_20190605.xlsx")
    # orphans = dd.find_orphans(dtfxml)
    # df = pd.DataFrame(orphans)
    # df.to_excel("docs/orphans_20190605.xlsx")
