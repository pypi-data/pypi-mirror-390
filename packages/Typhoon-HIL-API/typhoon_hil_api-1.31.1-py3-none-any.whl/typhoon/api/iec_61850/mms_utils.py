import json
import os.path
import xml.etree.ElementTree as ET
from collections import OrderedDict

from typhoon.api.iec_61850.exceptions import MMSValidationException
from typhoon.api.schematic_editor.const import FLIP_VERTICAL, ITEM_COMPONENT, ITEM_PORT
from typhoon.api.schematic_editor.exception import SchApiException

TYPE_BORDER_VALUES = {
    "BOOLEAN": {"min": 0, "max": 1},
    "INT8": {"min": -128, "max": 127},
    "INT16": {"min": -32768, "max": 32767},
    "INT32": {"min": -2147483648, "max": 2147483647},
    "INT64": {"min": -9223372036854775808, "max": 9223372036854775807},
    "INT128": {"min": -(2**127), "max": 2**127 - 1},
    "INT8U": {"min": 0, "max": 255},
    "INT16U": {"min": 0, "max": 65535},
    "INT32U": {"min": 0, "max": 4294967295},
    "INT64U": {"min": 0, "max": 18446744073709551615},
    "FLOAT32": {"min": -(2 - 2 ** (-23)) * 2**127, "max": (2 - 2 ** (-23)) * 2**127},
    "FLOAT64": {"min": -(2 - 2 ** (-52)) * 2**1023, "max": (2 - 2 ** (-52)) * 2**1023},
}

default_DA_value = {
    "scaleFactor": 1.0,
}

Dbpos_values = ["0 - intermediate-state", "1 - off", "2 - on", "3 - bad-state"]

DATA_TYPES = [
    "BOOLEAN",
    "INT8",
    "INT16",
    "INT24",
    "INT32",
    "INT128",
    "INT8U",
    "INT16U",
    "INT24U",
    "INT32U",
    "FLOAT32",
    "FLOAT64",
    "ENUMERATED",
    "CODED ENUM",
    "OCTET STRING",
    "VISIBLE STRING",
    "UNICODE STRING",
]

SUPPORTED_DATA_TYPES = [
    "INT8U",
    "INT16U",
    "INT32U",
    "INT8",
    "INT16",
    "INT32",
    "FLOAT32",
    "FLOAT64",
    "Quality",
    "BOOLEAN",
    "Enum",
    "Dbpos",
]


def _get_attrib_val(obj, attrib_name):
    try:
        return obj.attrib[attrib_name]
    except KeyError:
        return ""


def _parse_scl_file(file_path=None):
    def _parse_DO_struct(
        root, do_name, do_type, struct, fc=None, dchg="", qchg="", dupd=""
    ):
        Type = root.find(
            scl_prefix
            + "DataTypeTemplates"
            + "/"
            + scl_prefix
            + f"DOType[@id='{do_type}']"
        )

        if Type:
            struct["cdc"] = _get_attrib_val(Type, "cdc")
        else:
            Type = root.find(
                scl_prefix
                + "DataTypeTemplates"
                + "/"
                + scl_prefix
                + f"DAType[@id='{do_type}']"
            )

        if not Type:
            Type = []

        for obj in Type:
            name = _get_attrib_val(obj, "name")
            _fc = _get_attrib_val(obj, "fc")
            bType = _get_attrib_val(obj, "bType")
            _dchg = _get_attrib_val(obj, "dchg")
            _qchg = _get_attrib_val(obj, "qchg")
            _dupd = _get_attrib_val(obj, "dupd")
            type_val = _get_attrib_val(obj, "type")

            # Make sure that the timestamp is represented by lowercase t
            if bType == "Timestamp" and name == "T":
                name = "t"

            struct[name] = {}
            struct[name]["type"] = type_val
            struct[name]["bType"] = bType
            struct[name]["fc"] = _fc if _fc else fc
            struct[name]["dchg"] = _dchg if _dchg else dchg
            struct[name]["qchg"] = _qchg if _qchg else qchg
            struct[name]["dupd"] = _dupd if _dupd else dupd
            struct[name]["list"] = False

            val_object = obj.find(scl_prefix + "Val")
            struct[name]["default_value"] = (
                val_object.text if (val_object is not None) else None
            )

            if type_val:
                if bType != "Enum":
                    # data attribute is a structure. Parse that structure
                    _parse_DO_struct(
                        root,
                        name,
                        type_val,
                        struct[name],
                        fc=struct[name]["fc"],
                        dchg=struct[name]["dchg"],
                        qchg=struct[name]["qchg"],
                        dupd=struct[name]["dupd"],
                    )
                else:
                    # data atribute is enumeration
                    struct[name]["enum_values"] = enum_types[type_val]
            else:
                # Leaf node
                count = _get_attrib_val(obj, "count")
                try:
                    # Try to convert count to integer. If count is '0' it should be
                    # treated as a scalar value, and not vector
                    count = int(count)
                except ValueError:
                    pass

                if count:
                    struct[name]["bType"] = f"{bType}[{count}]"
                    struct[name]["list"] = True
                    struct[name]["count"] = int(count)
                    # data attribute is leaf node of type list
                    for i in range(int(count)):
                        struct[name][f"[{i}]"] = {}
                        struct[name][f"[{i}]"]["bType"] = bType
                        struct[name][f"[{i}]"]["fc"] = fc
                        struct[name][f"[{i}]"]["value"] = None
                else:
                    # data attribute is leaf node
                    struct[name]["value"] = None

    def _parse_SDI_struct(node, scl_struct, ied_struct=None):
        SDIs = node.findall(scl_prefix + "SDI")
        for SDI in SDIs:
            SDI_name = SDI.attrib["name"]

            scl_struct[SDI_name] = {}
            _parse_SDI_struct(SDI, scl_struct[SDI_name], ied_struct[SDI_name])

        DAIs = node.findall(scl_prefix + "DAI")
        for DAI in DAIs:
            DAI_name = DAI.attrib["name"]
            try:
                value = DAI.find(scl_prefix + "Val").text

                if ied_struct[DAI_name]["bType"] == "Enum":
                    for enum_value in ied_struct[DAI_name]["enum_values"]:
                        if value in enum_value:
                            value = enum_value
                            break
                elif ied_struct[DAI_name]["bType"] == "Dbpos":
                    for enum_value in Dbpos_values:
                        if value in enum_value:
                            value = enum_value
                            break

                scl_struct[DAI_name] = {"value": value, "default_value": value}
            except AttributeError:
                pass

    if not file_path:
        return

    scl_tree = ET.parse(file_path)
    scl_root = scl_tree.getroot()

    root_tag = scl_root.tag
    scl_prefix = root_tag[: root_tag.find("}") + 1]

    scl = {}

    enum_types = {}
    EnumTypes = scl_root.findall(
        scl_prefix + "DataTypeTemplates" + "/" + scl_prefix + "EnumType"
    )
    for _i, EnumType in enumerate(EnumTypes):
        enum_name = _get_attrib_val(EnumType, "id")
        enum_types[enum_name] = []

        for EnumVal in EnumType:
            order_num = _get_attrib_val(EnumVal, "ord")
            value = EnumVal.text if EnumVal.text else ""

            enum_types[enum_name].append(order_num + " - " + value)

    # Parse initial IED structure
    ieds = scl_root.findall(scl_prefix + "IED")
    for ied in ieds:
        ied_name = _get_attrib_val(ied, "name")
        scl[ied_name] = {}

        AccessPoints = ied.findall(scl_prefix + "AccessPoint")
        for AccessPoint in AccessPoints:
            AccessPoint_name = AccessPoint.attrib["name"]
            scl[ied_name][AccessPoint_name] = {}

            LDevices = AccessPoint.findall(
                scl_prefix + "Server" + "/" + scl_prefix + "LDevice"
            )

            for LDevice in LDevices:
                LDevice_name = ied_name + LDevice.attrib["inst"]
                scl[ied_name][AccessPoint_name][LDevice_name] = {}

                for LNode in LDevice:
                    lnClass = _get_attrib_val(LNode, "lnClass")
                    inst = _get_attrib_val(LNode, "inst")
                    ln_type_id = _get_attrib_val(LNode, "lnType")
                    prefix = _get_attrib_val(LNode, "prefix")

                    scl[ied_name][AccessPoint_name][LDevice_name][
                        prefix + lnClass + inst
                    ] = {}
                    scl[ied_name][AccessPoint_name][LDevice_name][
                        prefix + lnClass + inst
                    ]["id"] = ln_type_id

    ied_data = {}
    for accessPoints in scl.values():
        for ldevices in accessPoints.values():
            for lnodes in ldevices.values():
                for lnode_data in lnodes.values():
                    lnode_type = lnode_data["id"]
                    ied_data[lnode_type] = {}

                    LNodeType = scl_root.find(
                        scl_prefix
                        + "DataTypeTemplates"
                        + "/"
                        + scl_prefix
                        + f"LNodeType[@id='{lnode_type}']"
                    )

                    DataObjects = LNodeType.findall(scl_prefix + "DO")

                    for DataObject in DataObjects:
                        do_name = _get_attrib_val(DataObject, "name")
                        do_type = _get_attrib_val(DataObject, "type")

                        ied_data[lnode_type][do_name] = {"type": do_type}
                        _parse_DO_struct(
                            scl_root, do_name, do_type, ied_data[lnode_type][do_name]
                        )

    # parse the rest of SCL structure
    ieds = scl_root.findall(scl_prefix + "IED")
    for ied in ieds:
        ied_name = _get_attrib_val(ied, "name")

        AccessPoints = ied.findall(scl_prefix + "AccessPoint")
        for AccessPoint in AccessPoints:
            AccessPoint_name = AccessPoint.attrib["name"]

            LDevices = AccessPoint.findall(
                scl_prefix + "Server" + "/" + scl_prefix + "LDevice"
            )

            for LDevice in LDevices:
                LDevice_name = ied_name + LDevice.attrib["inst"]

                for LNode in LDevice:
                    lnClass = _get_attrib_val(LNode, "lnClass")
                    inst = _get_attrib_val(LNode, "inst")
                    ln_type_id = _get_attrib_val(LNode, "lnType")
                    prefix = _get_attrib_val(LNode, "prefix")

                    # init_values
                    scl[ied_name][AccessPoint_name][LDevice_name][
                        prefix + lnClass + inst
                    ]["init_values"] = {}
                    # data sets
                    scl[ied_name][AccessPoint_name][LDevice_name][
                        prefix + lnClass + inst
                    ]["ds"] = {}
                    # reporting blocks
                    scl[ied_name][AccessPoint_name][LDevice_name][
                        prefix + lnClass + inst
                    ]["rp"] = {}

                    # Parse initial values
                    DOIs = LNode.findall(scl_prefix + "DOI")
                    for DOI in DOIs:
                        DOI_name = _get_attrib_val(DOI, "name")

                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["init_values"][DOI_name] = {}

                        _parse_SDI_struct(
                            DOI,
                            scl[ied_name][AccessPoint_name][LDevice_name][
                                prefix + lnClass + inst
                            ]["init_values"][DOI_name],
                            ied_data[ln_type_id][DOI_name],
                        )

                    # Parse Data sets
                    DataSets = LNode.findall(scl_prefix + "DataSet")
                    for DataSet in DataSets:
                        DataSet_name = _get_attrib_val(DataSet, "name")
                        DataSet_desc = _get_attrib_val(DataSet, "desc")
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["ds"][DataSet_name] = {}
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["ds"][DataSet_name]["fcda"] = []
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["ds"][DataSet_name]["desc"] = DataSet_desc

                        ln_ref = f"{LDevice_name}/{prefix}{lnClass}{inst}"
                        ds_ref = f"{ln_ref}${DataSet_name}"

                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["ds"][DataSet_name]["ds_reference"] = ds_ref

                        FCDAs = DataSet.findall(scl_prefix + "FCDA")
                        for FCDA in FCDAs:
                            _ldInst = _get_attrib_val(FCDA, "ldInst")
                            _prefix = _get_attrib_val(FCDA, "prefix")
                            _lnClass = _get_attrib_val(FCDA, "lnClass")
                            _lnInst = _get_attrib_val(FCDA, "lnInst")
                            _doName = _get_attrib_val(FCDA, "doName")
                            _daName = _get_attrib_val(FCDA, "daName")
                            _fc = _get_attrib_val(FCDA, "fc")

                            _daName.replace(".", "$")

                            fcda_ref = f"{ied_name}{_ldInst}/{_prefix}{_lnClass}{_lnInst}${_fc}${_doName}"
                            fcda_ref += f"${_daName}" if _daName else ""

                            scl[ied_name][AccessPoint_name][LDevice_name][
                                prefix + lnClass + inst
                            ]["ds"][DataSet_name]["fcda"].append(fcda_ref)

                    # Parse Reporting CB
                    ReportControls = LNode.findall(scl_prefix + "ReportControl")
                    for ReportControl in ReportControls:
                        ReportControl_name = _get_attrib_val(ReportControl, "name")
                        ReportControl_desc = _get_attrib_val(ReportControl, "desc")
                        ReportControl_dataSet = _get_attrib_val(ReportControl, "datSet")
                        ReportControl_intgPd = _get_attrib_val(ReportControl, "intgPd")
                        ReportControl_rptID = _get_attrib_val(ReportControl, "rptID")
                        ReportControl_confRev = _get_attrib_val(
                            ReportControl, "confRev"
                        )
                        ReportControl_buffered = _get_attrib_val(
                            ReportControl, "buffered"
                        )
                        ReportControl_bufTime = _get_attrib_val(
                            ReportControl, "bufTime"
                        )

                        ln_ref = f"{LDevice_name}/{prefix}{lnClass}{inst}"
                        rp_ref = f"{ln_ref}${ReportControl_name}"

                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name] = {}
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["desc"] = ReportControl_desc
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["datSet"] = ReportControl_dataSet
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["intgPd"] = ReportControl_intgPd
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["rptID"] = ReportControl_rptID
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["confRev"] = ReportControl_confRev
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["buffered"] = ReportControl_buffered
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["bufTime"] = ReportControl_bufTime
                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["rp_reference"] = rp_ref

                        TrgOps = ReportControl.find(scl_prefix + "TrgOps")
                        TrgOps_dchg = _get_attrib_val(TrgOps, "dchg")
                        TrgOps_qchg = _get_attrib_val(TrgOps, "qchg")
                        TrgOps_dupd = _get_attrib_val(TrgOps, "dupd")
                        TrgOps_period = _get_attrib_val(TrgOps, "period")

                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["TrgOps"] = {
                            "dchg": TrgOps_dchg,
                            "qchg": TrgOps_qchg,
                            "dupd": TrgOps_dupd,
                            "period": TrgOps_period,
                        }

                        OptFields = ReportControl.find(scl_prefix + "OptFields")
                        OptFields_seqNum = _get_attrib_val(OptFields, "seqNum")
                        OptFields_timeStamp = _get_attrib_val(OptFields, "timeStamp")
                        OptFields_dataSet = _get_attrib_val(OptFields, "dataSet")
                        OptFields_reasonCode = _get_attrib_val(OptFields, "reasonCode")
                        OptFields_dataRef = _get_attrib_val(OptFields, "dataRef")
                        OptFields_bufOvfl = _get_attrib_val(OptFields, "bufOvfl")
                        OptFields_entryID = _get_attrib_val(OptFields, "entryID")
                        OptFields_configRef = _get_attrib_val(OptFields, "configRef")
                        OptFields_segmentation = _get_attrib_val(
                            OptFields, "segmentation"
                        )

                        scl[ied_name][AccessPoint_name][LDevice_name][
                            prefix + lnClass + inst
                        ]["rp"][ReportControl_name]["OptFields"] = {
                            "seqNum": OptFields_seqNum,
                            "timeStamp": OptFields_timeStamp,
                            "dataSet": OptFields_dataSet,
                            "reasonCode": OptFields_reasonCode,
                            "dataRef": OptFields_dataRef,
                            "bufOvfl": OptFields_bufOvfl,
                            "entryID": OptFields_entryID,
                            "configRef": OptFields_configRef,
                            "segmentation": OptFields_segmentation,
                        }

    return scl, ied_data, enum_types


def _get_object(scl, ied_data, path):
    path_parts = path.split("$")

    _ied, _ap, _ld, _ln = (
        path_parts[0],
        path_parts[1],
        path_parts[2],
        path_parts[3],
    )
    ln_id = scl[_ied][_ap][_ld][_ln]["id"]

    # Backward compatibility code
    try:
        struct = ied_data[ln_id]
    except KeyError:
        struct = ied_data[_ln]

    for part in path_parts[4:]:
        try:
            struct = struct[part]
        except KeyError:
            return None

    return struct


def _get_object_type(scl, ied_data, path):
    try:
        return _get_object(scl, ied_data, path)["type"]
    except KeyError:
        return None


def _get_object_bType(scl, ied_data, path):
    try:
        return _get_object(scl, ied_data, path)["bType"]
    except KeyError:
        return None


def _get_include_widget_value(leaf_widgets, path):
    def get_include_widget(leaf_widgets, path):
        try:
            return leaf_widgets[path]["include"]
        except KeyError:
            return None

    widget = get_include_widget(leaf_widgets, path)
    if widget:
        return widget
    else:
        return None


def _get_object_fc(scl, ied_data, path):
    try:
        return _get_object(scl, ied_data, path)["fc"]
    except KeyError:
        return None


def _get_value_widget(path, leaf_widgets):
    try:
        return leaf_widgets[path]["value"]["value"]
    except KeyError:
        return None


def _find_parent_path(path):
    last = path.rfind("$")
    return path[:last]


def _get_object_dimension(scl, ied_data, path):
    obj = _get_object(scl, ied_data, path)
    if obj["list"]:
        return obj["count"]
    else:
        return 1


def _get_enum_value_list(config, path):
    path_parts = path.split("$")

    _ied, _ap, _ld, _ln = (
        path_parts[0],
        path_parts[1],
        path_parts[2],
        path_parts[3],
    )
    ln_id = config["scl"][_ied][_ap][_ld][_ln]["id"]

    # Backward compatibility code
    try:
        struct = config["ied_data"][ln_id]
    except KeyError:
        struct = config["ied_data"][_ln]

    for part in path_parts[4:]:
        try:
            struct = struct[part]
        except KeyError:
            return None

    try:
        return struct["enum_values"]
    except KeyError:
        return []


def _check_quality_string(string):
    if isinstance(string, str):
        if len(string) != 13:
            return False
        else:
            return all(c in ("0", "1") for c in string)
    else:
        return False


def _get_direction_widget(leaf_widgets, path):
    try:
        return leaf_widgets[path]["direction"]
    except KeyError:
        return None


def _get_alias_widget(leaf_widgets, path):
    try:
        return leaf_widgets[path]["alias"]
    except KeyError:
        return None


def _get_triggering_value(path, triggering_values):
    try:
        if triggering_values[path]:
            return {
                "dchg": "dchg" in triggering_values[path],
                "dupd": "dupd" in triggering_values[path],
                "qchg": "qchg" in triggering_values[path],
            }
        else:
            return {"dchg": False, "dupd": False, "qchg": False}
    except KeyError:
        return {"dchg": False, "dupd": False, "qchg": False}


def _get_values_from_scl_struct(config, path):
    obj = config["scl"]

    path_elements = path.split("$")
    path_elements.insert(4, "init_values")

    for el in path_elements:
        try:
            if el != path_elements[-1]:
                obj = obj[el]
            else:
                value = obj[el].get("value", None)
                default_value = obj[el].get("default_value", None)
                include = obj[el].get("include", None)
                direction = obj[el].get("direction", None)
                alias = obj[el].get("alias", None)

                enum_values = _get_enum_value_list(config, path)
                for enum_value in enum_values:
                    if str(default_value) in enum_value:
                        default_value = enum_value
                        break

                return value, default_value, include, direction, alias
        except KeyError:
            return None, None, None, None, None


def import_config(sch_model, item_handle):
    # --------------------------------------------------------------------------------
    # Description:
    #   This function reads property values from MMS Server schematic component and writes it to dictionary
    #
    # Inputs:
    #   sch_model:      schematic model
    #   item_handle:    MMS Server component
    #
    #
    # Outputs:
    #   mms_dict: dictionary that holds values from MMS Server component
    #   mms_dict = {
    #       "scl": dict,
    #       "ied_data": list,
    #       "enum_types": list,
    #       "ied_names" : list,
    #       "file_name": string,
    #       "file_path": string,
    #       "node_trees": dict,
    #       "leaf_widgets": dict,
    #       "included_leafs": dict,
    #       "triggering_values": dict,
    #       "path_type": string,
    #       "chosen_ied": string,
    #   }
    #
    # Author:
    #   Marko Boberic, December 2024
    # --------------------------------------------------------------------------------

    def _init_leaf_values():
        for leaf_path, leaf_widget in leaf_widgets.items():
            value, default_value, include, direction, alias = (
                _get_values_from_scl_struct(mms_dict, leaf_path)
            )

            # Use default value if there is not init value defined
            value = default_value if value is None else value

            if include:
                leaf_widget["include"] = include

            if direction:
                leaf_widget["direction"] = direction

            if alias:
                leaf_widget["alias"] = alias

            if value:
                leaf_bType = _get_object_bType(
                    mms_dict["scl"], mms_dict["ied_data"], leaf_path
                )

                if "INT" in leaf_bType:
                    leaf_widget.setdefault("value", {})["value"] = int(value)
                elif "FLOAT" in leaf_bType:
                    leaf_widget.setdefault("value", {})["value"] = float(value)
                elif leaf_bType == "BOOLEAN":
                    leaf_widget.setdefault("value", {})["value"] = bool(value)
                elif leaf_bType == "Enum":
                    enum_values = _get_enum_value_list(mms_dict, leaf_path)
                    for enum_value in enum_values:
                        if value in (enum_value, enum_value[4:]):
                            leaf_widget.setdefault("value", {})["value"] = value
                            break
                elif leaf_bType == "Dbpos":
                    for db_value in Dbpos_values:
                        if value in (db_value, db_value[4:]):
                            leaf_widget.setdefault("value", {})["value"] = Dbpos_values
                            break
                elif (
                    "String" in leaf_bType
                    or "Unicode" in leaf_bType
                    or "Octet" in leaf_bType
                    or leaf_bType == "Quality"
                ):
                    leaf_widget.setdefault("value", {})["value"] = str(value)

    def _get_default_DA_value(type_val, obj=None, enum_type=None):
        if obj:
            try:
                return default_DA_value[obj]
            except KeyError:
                if type_val.startswith("INT"):
                    return 0
                elif type_val.startswith("FLOAT"):
                    return 0.0
                elif type_val == "BOOLEAN":
                    return False
                elif type_val == "Quality":
                    return "0000000000000"
                elif (
                    "String" in type_val or "Unicode" in type_val or "Octet" in type_val
                ):
                    return ""
                elif type_val == "Enum":
                    return enum_types[enum_type][0]
                elif type_val == "Dbpos":
                    return Dbpos_values[0]
        else:
            if type_val.startswith("INT"):
                return 0
            elif type_val.startswith("FLOAT"):
                return 0.0
            elif type_val == "BOOLEAN":
                return False
            elif type_val == "Quality":
                return "0000000000000"
            elif "String" in type_val or "Unicode" in type_val or "Octet" in type_val:
                return ""
            elif type_val == "Enum":
                return enum_types[enum_type][0]
            elif type_val == "Dbpos":
                return Dbpos_values[0]

    def _init_ied_data_tree(node_path):
        def populate_branch(tree, path, data):
            for obj in data:
                object_path = path + "$" + obj

                try:
                    type_val = data[obj]["bType"]
                    if not type_val or type_val == "Struct":
                        type_val = data[obj]["type"]
                except KeyError:
                    type_val = data[obj]["type"]
                except TypeError:
                    continue

                try:
                    fc = data[obj]["fc"]
                    fc = f" [{fc}]" if fc else ""
                except KeyError:
                    fc = ""

                try:
                    dchg = data[obj]["dchg"]
                    qchg = data[obj]["qchg"]
                    dupd = data[obj]["dupd"]
                    triggering = ""
                    if dchg:
                        triggering += "dchg, "
                    if qchg:
                        triggering += "qchg, "
                    if dupd:
                        triggering += "dupd, "

                    if triggering:
                        triggering = triggering[:-2]
                        triggering_values[object_path] = triggering
                except KeyError:
                    triggering = ""

                list_type = bool(type_val.endswith("]"))

                if (obj.startswith("[") and obj.endswith("]")) or type_val.endswith(
                    "]"
                ):
                    list_item = True
                else:
                    list_item = False

                if (type_val in SUPPORTED_DATA_TYPES and not list_item) or list_type:
                    include = False
                    direction = "out"
                    alias_label = ""

                    # store widget reference to list
                    if object_path not in leaf_widgets:
                        leaf_widgets[object_path] = {
                            "include": include,
                            "direction": direction,
                            "alias": alias_label,
                        }

                if type_val and not list_type:
                    value_dict = {}

                    if type_val.startswith(("INT", "FLOAT")) or type_val == "BOOLEAN":
                        value_dict["value"] = _get_default_DA_value(type_val, obj)
                        value_dict["range"] = {
                            "min": TYPE_BORDER_VALUES[type_val]["min"],
                            "max": TYPE_BORDER_VALUES[type_val]["max"],
                        }
                    elif type_val == "Quality":
                        value_dict["value"] = _get_default_DA_value(type_val, obj)
                        value_dict["range"] = {
                            "min": "quality",
                            "max": "quality",
                        }
                    elif type_val == "Enum":
                        value_dict["value"] = data[obj]["enum_values"]
                        value_dict["range"] = {
                            "min": "enum",
                            "max": "enum",
                        }
                    elif (
                        "String" in type_val or "Unicode" in type_val
                    ):  # or "Octet" in type:
                        value_dict["value"] = _get_default_DA_value(type_val, obj)
                        value_dict["range"] = {
                            "min": "string",
                            "max": "string",
                        }
                    elif type_val == "Dbpos":
                        value_dict["value"] = _get_default_DA_value(type_val, obj)
                        value_dict["range"] = {
                            "min": "Dbpos",
                            "max": "Dbpos",
                        }

                    # store value widget reference to list
                    if value_dict:
                        if object_path not in leaf_widgets:
                            leaf_widgets[object_path] = {"value": value_dict}
                        else:
                            leaf_widgets[object_path]["value"] = value_dict

                populate_branch(tree, path + "$" + obj, data[obj])

        tree = node_trees[node_path]
        data = ied_data
        _ied, _ap, _ld, _ln = node_path.split("$")
        ln_id = scl[_ied][_ap][_ld][_ln]["id"]

        # Backward compatibility code
        try:
            ln_data = data[ln_id]
        except KeyError:
            ln_data = data[_ln]

        populate_branch(tree, node_path, ln_data)

    def _get_node_paths():
        node_paths = []
        for ied_name in scl:
            for access_point in scl[ied_name]:
                for ldevice_name in scl[ied_name][access_point]:
                    for lnode_name in scl[ied_name][access_point][ldevice_name]:
                        node_paths.append(
                            ied_name
                            + "$"
                            + access_point
                            + "$"
                            + ldevice_name
                            + "$"
                            + lnode_name
                        )

        return node_paths

    def _init_node_trees():
        if scl:
            node_path = _get_node_paths()

            for node in node_path:
                node_trees[node] = {
                    "Objects": "",
                    "Type": "",
                    "Trigering": "",
                    "Value": 0,
                    "Include": "",
                    "Direction": "",
                    "Alias": "",
                }
                _init_ied_data_tree(node)
            _init_leaf_values()
        else:
            raise Exception("init_node_trees fail : scl not valid!")

    def _get_supported_values(type_val, enum_type=None):
        if type_val.startswith("INT"):
            return "int"
        elif type_val.startswith("FLOAT"):
            return "float"
        elif type_val == "BOOLEAN":
            return "boolean"
        elif type_val == "Quality":
            return "quality"
        elif "String" in type_val or "Unicode" in type_val or "Octet" in type_val:
            return "string"
        elif type_val == "Enum":
            return enum_types[enum_type]
        elif type_val == "Dbpos":
            return Dbpos_values

    mms_dict = {}

    scl = {}
    enum_types = []
    ied_data = []
    node_trees = {}
    leaf_widgets = {}
    triggering_values = {}
    included_leafs = {}
    available_leafs = {}

    eth_port = sch_model.get_property_value(sch_model.prop(item_handle, "eth_port"))
    path_type = sch_model.get_property_value(sch_model.prop(item_handle, "path_type"))
    file_path = sch_model.get_property_value(sch_model.prop(item_handle, "file_path"))
    file_name = sch_model.get_property_value(sch_model.prop(item_handle, "file_name"))
    ied_names = eval(
        sch_model.get_property_value(sch_model.prop(item_handle, "ied_names")),
        {},
        {"OrderedDict": OrderedDict},
    )
    chosen_ied = sch_model.get_property_value(sch_model.prop(item_handle, "chosen_ied"))
    scl = eval(
        sch_model.get_property_value(sch_model.prop(item_handle, "scl")),
        {},
        {"OrderedDict": OrderedDict},
    )
    enum_types = eval(
        sch_model.get_property_value(sch_model.prop(item_handle, "enum_types")),
        {},
        {"OrderedDict": OrderedDict},
    )
    ied_data = eval(
        sch_model.get_property_value(sch_model.prop(item_handle, "ied_data")),
        {},
        {"OrderedDict": OrderedDict},
    )
    server_ip = sch_model.get_property_disp_value(
        sch_model.prop(item_handle, "server_ip")
    )
    server_netmask = sch_model.get_property_disp_value(
        sch_model.prop(item_handle, "server_netmask")
    )
    server_gateway_enable = sch_model.get_property_value(
        sch_model.prop(item_handle, "server_gateway_enable")
    )
    server_gateway = sch_model.get_property_disp_value(
        sch_model.prop(item_handle, "server_gateway")
    )
    execution_rate = str(
        sch_model.get_property_disp_value(sch_model.prop(item_handle, "execution_rate"))
    )
    vendor = sch_model.get_property_value(sch_model.prop(item_handle, "vendor"))
    model_name = sch_model.get_property_value(sch_model.prop(item_handle, "model_name"))
    revision = sch_model.get_property_value(sch_model.prop(item_handle, "revision"))

    network_prop = {
        "ip": server_ip,
        "gateway": server_gateway,
        "netmask": server_netmask,
        "gateway_enable": server_gateway_enable,
        "eth_port": eth_port,
        "execution_rate": execution_rate,
    }

    service_resp_prop = {
        "vendor": vendor,
        "model_name": model_name,
        "revision": revision,
    }

    mms_dict = {
        "scl": scl,
        "ied_data": ied_data,
        "enum_types": enum_types,
        "ied_names": ied_names,
        "file_name": file_name,
        "file_path": file_path,
        "path_type": path_type,
        "chosen_ied": chosen_ied,
        "network_prop": network_prop,
        "service_resp_prop": service_resp_prop,
    }

    _init_node_trees()

    for node_path in node_trees:
        leaf_path_subset = [path for path in leaf_widgets if node_path in path]

        for leaf_path in leaf_path_subset:
            type_val = _get_object_type(scl, ied_data, leaf_path)
            if not type_val:
                type_val = _get_object_bType(scl, ied_data, leaf_path)

            leaf_type = _get_object_bType(scl, ied_data, leaf_path)

            if leaf_type in ["Enum", "Dbpos"]:
                if leaf_type == "Enum":
                    supported_vals = _get_supported_values(
                        leaf_type, enum_type=type_val
                    )
                else:
                    supported_vals = _get_supported_values(leaf_type)
            else:
                supported_vals = _get_supported_values(leaf_type)
            leaf_value = _get_value_widget(leaf_path, leaf_widgets)
            parent_type = True
            path = leaf_path
            while parent_type:
                path = _find_parent_path(path)
                parent_type = _get_object_type(scl, ied_data, path)
                leaf_type += "/" + parent_type if parent_type else ""

            # get t path
            leaf_path_parts = leaf_path.split("$")
            t_path = leaf_path_parts[0]
            for part in leaf_path_parts[1:]:
                t_path += f"${part}"
            t_path += "$t"
            last_part = 1
            while not _get_object(scl, ied_data, t_path):
                t_path = leaf_path_parts[0]
                for part in leaf_path_parts[1:-last_part]:
                    t_path += f"${part}"
                t_path += "$t"
                # check if is the fourth element of t_path is 't'
                t_path_parts = t_path.split("$")
                if t_path_parts[3] == "t":
                    t_path = ""
                    break
                last_part += 1

            leaf_direction = _get_direction_widget(leaf_widgets, path)
            leaf_alias = (
                _get_alias_widget(leaf_widgets, path)
                if _get_alias_widget(leaf_widgets, path) is not None
                else ""
            )
            dimension = _get_object_dimension(scl, ied_data, leaf_path)
            triggering = _get_triggering_value(leaf_path, triggering_values)

            if dimension > 1:
                list_values = []
                for _i in range(dimension):
                    list_values.append(_get_default_DA_value(type_val))
            else:
                list_values = None

            available_leafs[leaf_path] = {
                "path": leaf_path,
                "fc": _get_object_fc(scl, ied_data, leaf_path),
                "type": leaf_type,
                "value": leaf_value,
                "direction": leaf_direction,
                "alias": leaf_alias,
                "dimension": dimension,
                "list_values": list_values,
                "triggering": triggering,
                "t_path": t_path,
                "supported_values": supported_vals,
            }

    for leaf_path, leaf_data in available_leafs.items():
        include = _get_include_widget_value(leaf_widgets, leaf_path)
        if include:
            included_leafs[leaf_path] = leaf_data

    mms_dict.update(
        {
            "node_trees": node_trees,
            "leaf_widgets": leaf_widgets,
            "available_leafs": available_leafs,
            "triggering_values": triggering_values,
            "included_leafs": included_leafs,
        }
    )

    return mms_dict


def load_config(absolute_file_path):
    # --------------------------------------------------------------------------------
    # Description:
    #   This function loads *.icd file and returns parsed dictionary
    #
    # Inputs:
    #   absolute_file_path: absolute path to *.icd file
    #
    #
    # Outputs:
    #   mms_dict: dictionary that holds parsed values from *.icd_file
    #   mms_dict = {
    #       "scl": dict,
    #       "ied_data": list,
    #       "enum_types": list,
    #       "ied_names" : list,
    #       "file_name": string,
    #       "file_path": string,
    #       "node_trees": dict,
    #       "leaf_widgets": dict,
    #       "included_leafs": dict,
    #       "triggering_values": dict,
    #       "path_type": string,
    #       "chosen_ied": string,
    #   }
    #
    # Author:
    #   Marko Boberic, December 2024
    # --------------------------------------------------------------------------------

    def _get_supported_values(type_val, enum_type=None):
        if type_val.startswith("INT"):
            return "int"
        elif type_val.startswith("FLOAT"):
            return "float"
        elif type_val == "BOOLEAN":
            return "boolean"
        elif type_val == "Quality":
            return "quality"
        elif "String" in type_val or "Unicode" in type_val or "Octet" in type_val:
            return "string"
        elif type_val == "Enum":
            return enum_types[enum_type]
        elif type_val == "Dbpos":
            return Dbpos_values

    def _init_leaf_values():
        for leaf_path, leaf_widget in leaf_widgets.items():
            value, default_value, include, direction, alias = (
                _get_values_from_scl_struct(mms_dict, leaf_path)
            )

            # Use default value if there is not init value defined
            value = default_value if value is None else value

            if include:
                leaf_widgets["include"] = include

            if direction:
                leaf_widgets["direction"] = direction

            if alias:
                leaf_widgets["alias"] = alias

            if value:
                leaf_bType = _get_object_bType(
                    mms_dict["scl"], mms_dict["ied_data"], leaf_path
                )

                if "INT" in leaf_bType:
                    leaf_widget.setdefault("value", {})["value"] = int(value)
                elif "FLOAT" in leaf_bType:
                    leaf_widget.setdefault("value", {})["value"] = float(value)
                elif leaf_bType == "BOOLEAN":
                    leaf_widget.setdefault("value", {})["value"] = bool(value)
                elif leaf_bType == "Enum":
                    enum_values = _get_enum_value_list(mms_dict, leaf_path)
                    for enum_value in enum_values:
                        if value in (enum_value, enum_value[4:]):
                            leaf_widget.setdefault("value", {})["value"] = value
                            break
                elif leaf_bType == "Dbpos":
                    for db_value in Dbpos_values:
                        if value in (db_value, db_value[4:]):
                            leaf_widget.setdefault("value", {})["value"] = Dbpos_values
                            break
                elif (
                    "String" in leaf_bType
                    or "Unicode" in leaf_bType
                    or "Octet" in leaf_bType
                    or leaf_bType == "Quality"
                ):
                    leaf_widget.setdefault("value", {})["value"] = str(value)

    def _get_default_DA_value(type_val, obj=None, enum_type=None):
        if obj:
            try:
                return default_DA_value[obj]
            except KeyError:
                if type_val.startswith("INT"):
                    return 0
                elif type_val.startswith("FLOAT"):
                    return 0.0
                elif type_val == "BOOLEAN":
                    return False
                elif type_val == "Quality":
                    return "0000000000000"
                elif (
                    "String" in type_val or "Unicode" in type_val or "Octet" in type_val
                ):
                    return ""
                elif type_val == "Enum":
                    return enum_types[enum_type][0]
                elif type_val == "Dbpos":
                    return Dbpos_values[0]
        else:
            if type_val.startswith("INT"):
                return 0
            elif type_val.startswith("FLOAT"):
                return 0.0
            elif type_val == "BOOLEAN":
                return False
            elif type_val == "Quality":
                return "0000000000000"
            elif "String" in type_val or "Unicode" in type_val or "Octet" in type_val:
                return ""
            elif type_val == "Enum":
                return enum_types[enum_type][0]
            elif type_val == "Dbpos":
                return Dbpos_values[0]

    def _get_node_paths():
        node_paths = []
        for ied_name in scl:
            for access_point in scl[ied_name]:
                for ldevice_name in scl[ied_name][access_point]:
                    for lnode_name in scl[ied_name][access_point][ldevice_name]:
                        node_paths.append(
                            ied_name
                            + "$"
                            + access_point
                            + "$"
                            + ldevice_name
                            + "$"
                            + lnode_name
                        )

        return node_paths

    def _init_node_trees():
        if scl:
            node_path = _get_node_paths()

            for node in node_path:
                node_trees[node] = {
                    "Objects": "",
                    "Type": "",
                    "Trigering": "",
                    "Value": 0,
                    "Include": "",
                    "Direction": "",
                    "Alias": "",
                }
                _init_ied_data_tree(node)
            _init_leaf_values()
        else:
            raise Exception("init_node_trees fail : scl not valid!")

    def _init_ied_data_tree(node_path):
        def populate_branch(tree, path, data):
            for obj in data:
                object_path = path + "$" + obj

                try:
                    type_val = data[obj]["bType"]
                    if not type_val or type_val == "Struct":
                        type_val = data[obj]["type"]
                except KeyError:
                    type_val = data[obj]["type"]
                except TypeError:
                    continue

                try:
                    fc = data[obj]["fc"]
                    fc = f" [{fc}]" if fc else ""
                except KeyError:
                    fc = ""

                try:
                    dchg = data[obj]["dchg"]
                    qchg = data[obj]["qchg"]
                    dupd = data[obj]["dupd"]
                    triggering = ""
                    if dchg:
                        triggering += "dchg, "
                    if qchg:
                        triggering += "qchg, "
                    if dupd:
                        triggering += "dupd, "

                    if triggering:
                        triggering = triggering[:-2]
                        triggering_values[object_path] = triggering
                except KeyError:
                    triggering = ""

                list_type = bool(type_val.endswith("]"))

                if (obj.startswith("[") and obj.endswith("]")) or type_val.endswith(
                    "]"
                ):
                    list_item = True
                else:
                    list_item = False

                if (type_val in SUPPORTED_DATA_TYPES and not list_item) or list_type:
                    include = False
                    direction = "out"
                    alias_label = ""

                    # store widget reference to list
                    if object_path not in leaf_widgets:
                        leaf_widgets[object_path] = {
                            "include": include,
                            "direction": direction,
                            "alias": alias_label,
                        }

                if type_val and not list_type:
                    value_dict = {}

                    if type_val.startswith(("INT", "FLOAT")) or type_val == "BOOLEAN":
                        value_dict["value"] = _get_default_DA_value(type_val, obj)
                        value_dict["range"] = {
                            "min": TYPE_BORDER_VALUES[type_val]["min"],
                            "max": TYPE_BORDER_VALUES[type_val]["max"],
                        }
                    elif type_val == "Quality":
                        value_dict["value"] = _get_default_DA_value(type_val, obj)
                        value_dict["range"] = {
                            "min": "quality",
                            "max": "quality",
                        }
                    elif type_val == "Enum":
                        value_dict["value"] = data[obj]["enum_values"]
                        value_dict["range"] = {
                            "min": "enum",
                            "max": "enum",
                        }
                    elif (
                        "String" in type_val or "Unicode" in type_val
                    ):  # or "Octet" in type:
                        value_dict["value"] = _get_default_DA_value(type_val, obj)
                        value_dict["range"] = {
                            "min": "string",
                            "max": "string",
                        }
                    elif type_val == "Dbpos":
                        value_dict["value"] = _get_default_DA_value(type_val, obj)
                        value_dict["range"] = {
                            "min": "Dbpos",
                            "max": "Dbpos",
                        }

                    # store value widget reference to list
                    if value_dict:
                        if object_path not in leaf_widgets:
                            leaf_widgets[object_path] = {"value": value_dict}
                        else:
                            leaf_widgets[object_path]["value"] = value_dict

                populate_branch(tree, path + "$" + obj, data[obj])

        tree = node_trees[node_path]
        data = ied_data
        _ied, _ap, _ld, _ln = node_path.split("$")
        ln_id = scl[_ied][_ap][_ld][_ln]["id"]

        # Backward compatibility code
        try:
            ln_data = data[ln_id]
        except KeyError:
            ln_data = data[_ln]

        populate_branch(tree, node_path, ln_data)

    mms_dict = {}

    scl = {}
    enum_types = []
    node_trees = {}
    ied_data = []
    leaf_widgets = {}
    triggering_values = {}
    available_leafs = {}

    if os.path.exists(absolute_file_path):
        # Parse scl file
        scl, ied_data, enum_types = _parse_scl_file(absolute_file_path)

        file_directory, file_name = os.path.split(absolute_file_path)

        ied_names = list(scl.keys())

        mms_dict = {
            "scl": scl,
            "ied_data": ied_data,
            "enum_types": enum_types,
            "ied_names": ied_names,
            "file_name": file_name,
            "file_path": absolute_file_path,
        }

        _init_node_trees()

        for node_path in node_trees:
            leaf_path_subset = [path for path in leaf_widgets if node_path in path]

            for leaf_path in leaf_path_subset:
                type_val = _get_object_type(scl, ied_data, leaf_path)
                if not type_val:
                    type_val = _get_object_bType(scl, ied_data, leaf_path)

                leaf_type = _get_object_bType(scl, ied_data, leaf_path)

                if leaf_type in ["Enum", "Dbpos"]:
                    leaf_value = _get_default_DA_value(leaf_type, enum_type=type_val)
                    if leaf_type == "Enum":
                        supported_vals = _get_supported_values(
                            leaf_type, enum_type=type_val
                        )
                    else:
                        supported_vals = _get_supported_values(leaf_type)
                else:
                    leaf_value = _get_default_DA_value(leaf_type)
                    supported_vals = _get_supported_values(leaf_type)

                parent_type = True
                path = leaf_path
                while parent_type:
                    path = _find_parent_path(path)
                    parent_type = _get_object_type(scl, ied_data, path)
                    leaf_type += "/" + parent_type if parent_type else ""

                # get t path
                leaf_path_parts = leaf_path.split("$")
                t_path = leaf_path_parts[0]
                for part in leaf_path_parts[1:]:
                    t_path += f"${part}"
                t_path += "$t"
                last_part = 1
                while not _get_object(scl, ied_data, t_path):
                    t_path = leaf_path_parts[0]
                    for part in leaf_path_parts[1:-last_part]:
                        t_path += f"${part}"
                    t_path += "$t"
                    # check if is the fourth element of t_path is 't'
                    t_path_parts = t_path.split("$")
                    if t_path_parts[3] == "t":
                        t_path = ""
                        break
                    last_part += 1

                leaf_direction = "out"
                leaf_alias = ""
                dimension = _get_object_dimension(scl, ied_data, leaf_path)
                triggering = _get_triggering_value(leaf_path, triggering_values)

                if dimension > 1:
                    list_values = []
                    for _i in range(dimension):
                        list_values.append(_get_default_DA_value(type_val))
                else:
                    list_values = None

                available_leafs[leaf_path] = {
                    "path": leaf_path,
                    "fc": _get_object_fc(scl, ied_data, leaf_path),
                    "type": leaf_type,
                    "value": leaf_value,
                    "direction": leaf_direction,
                    "alias": leaf_alias,
                    "dimension": dimension,
                    "list_values": list_values,
                    "triggering": triggering,
                    "t_path": t_path,
                    "supported_values": supported_vals,
                }

        mms_dict.update(
            {
                "node_trees": node_trees,
                "leaf_widgets": leaf_widgets,
                "available_leafs": available_leafs,
                "triggering_values": triggering_values,
                "path_type": "Absolute",
                "chosen_ied": "",
                "included_leafs": {},
            }
        )

        return mms_dict
    else:
        raise Exception("Error Configuration file not found!")


def export_config(config, file_name=None, file_path=None):
    # --------------------------------------------------------------------------------
    # Description:
    #   This function exports dictionary that holds *.icd file configuration for MMS Server
    #
    # Inputs:
    #   config: configuration dictionary
    #
    #
    # Outputs:
    #   leafs.json: dictionary printed in a json file
    #
    # Author:
    #   Marko Boberic, December 2024
    # --------------------------------------------------------------------------------

    # “w”: write mode, overwrites the file if it already exists or creates a new file if it does not exist
    if isinstance(config, dict):
        if file_path is not None and file_name is None:
            if config["file_name"].endswith(".icd"):
                parts_list = config["file_name"].split(".")
                file_name = parts_list[0] + ".json"
            else:
                file_name = config["file_name"] + ".json"
            full_path = os.path.normpath(os.path.join(file_path, file_name))
            with open(full_path, "w") as converted_file:
                converted_file.write(json.dumps(config["available_leafs"], indent=4))

        elif file_path is not None and file_name is not None:
            if file_name.endswith(".icd"):
                part_list = file_name.split(".")
                file_name = part_list[0] + ".json"
            else:
                file_name = file_name + ".json"
            full_path = os.path.normpath(os.path.join(file_path, file_name))
            with open(full_path, "w") as converted_file:
                converted_file.write(json.dumps(config["available_leafs"], indent=4))

        elif file_path is None and file_name is not None:
            if not file_name.endswith(".json"):
                file_name = file_name + ".json"
            with open(file_name, "w") as converted_file:
                converted_file.write(json.dumps(config["available_leafs"], indent=4))

        elif file_path is None and file_name is None:
            file_name = config["file_name"]
            if file_name.endswith(".icd"):
                parts_list = file_name.split(".")
                file_name = parts_list[0] + ".json"
            else:
                file_name = config["file_name"]
            with open(file_name, "w") as converted_file:
                converted_file.write(json.dumps(config["available_leafs"], indent=4))
    else:
        raise TypeError("config is not a dictionary!")


def set_leafs(
    config, ied, leafs_to_include, set_val_leafs, values, directions, aliases
):
    # --------------------------------------------------------------------------------
    # Description:
    #   This function includes chosen leafs, sets initial values for chosen leafs and sets directions and aliases for
    #   included leafs
    #
    # Inputs:
    #   config:             configuration dictionary
    #   ied:                IED to be selected
    #   leafs_to_include:   list of leafs to be included
    #   set_val_leafs:      list of values to set initial values for
    #   values:             list of values to set
    #   directions:         list of directions to set
    #   aliases;            list of aliases to set
    #
    #
    # Outputs:
    #   True if everything is valid, else False
    #
    # Author:
    #   Marko Boberic, December 2024
    # --------------------------------------------------------------------------------
    def _is_iso646_string(string):
        return all(ord(c) < 128 for c in string)

    def _is_unicode255_string(string):
        return all(ord(c) < 256 for c in string)

    def _is_octet_string(string):
        if string:
            try:
                tmp_string = "0x" + string if not string.startswith("0x") else string
                int(tmp_string, 16)
                return True
            except ValueError:
                return False
        else:
            return True

    if not isinstance(config, dict):
        raise MMSValidationException(
            "config is not a dictionary! Leafs can't be included!"
        )
    else:
        config["chosen_ied"] = ied

        # Clear all included leafs
        for leaf in list(config["included_leafs"].keys()):
            del config["included_leafs"][leaf]
            config["leaf_widgets"][leaf]["include"] = False

        # Include chosen and supported leafs
        for leaf_path in leafs_to_include:
            if (
                "Octet" in config["available_leafs"][leaf_path]["type"]
                or "VisString" in config["available_leafs"][leaf_path]["type"]
                or "Unicode" in config["available_leafs"][leaf_path]["type"]
            ):
                error_msg = (
                    "Octet, VisString and Unicode are not supported as inputs/outputs.\n"
                    "leaf: {leaf_path} cannot be included!"
                )
                raise MMSValidationException(error_msg)
            else:
                if leaf_path not in config["included_leafs"]:
                    config["included_leafs"].update(
                        {leaf_path: config["available_leafs"][leaf_path]}
                    )
                    config["leaf_widgets"][leaf_path]["include"] = True

        # Set directions for included leafs
        for direction in directions:
            if direction not in ["in", "out"]:
                raise MMSValidationException(
                    "Invalid direction! Valid directions are 'in' or 'out'"
                )

        if len(directions) != len(leafs_to_include):
            error_msg = "Directions list and leaf list must be the same length for directions to be set properly!"
            raise MMSValidationException(error_msg)

        for i, leaf in enumerate(leafs_to_include):
            config["included_leafs"][leaf]["direction"] = directions[i]
            config["leaf_widgets"][leaf]["direction"] = directions[i]

        # Set values for chosen leafs
        if len(set_val_leafs) != len(values):
            raise MMSValidationException(
                "To properly set values, leaf_list and value_list must be the same length!"
            )

        found = 0

        for i, leaf in enumerate(set_val_leafs):
            if values[i] is None:
                values[i] = values[i]
            else:
                if leaf not in config["available_leafs"]:
                    raise MMSValidationException(f"{leaf} is not available for access!")
                else:
                    if "Enum" in config["available_leafs"][leaf]["type"]:
                        if config["available_leafs"][leaf]["direction"] == "in":
                            error_msg = (
                                f"Cannot change value for leaf: {leaf}!\n"
                                "Type is Enum and direction is 'in'!"
                            )
                            raise MMSValidationException(error_msg)
                        else:
                            enum_values = _get_enum_value_list(config, leaf)
                            for enum_value in enum_values:
                                if values[i] in (enum_value, enum_value[4:]):
                                    config["available_leafs"][leaf]["value"] = values[i]
                                    config["leaf_widgets"][leaf]["value"]["value"] = (
                                        values[i]
                                    )
                                    found = 1
                                    if leaf in config["included_leafs"]:
                                        config["included_leafs"][leaf]["value"] = (
                                            values[i]
                                        )
                            if found != 1:
                                raise MMSValidationException(
                                    f"Invalid enum value for leaf {leaf}!"
                                )
                            else:
                                found = 0
                    elif "Quality" in config["available_leafs"][leaf]["type"]:
                        if not _check_quality_string(values[i]):
                            error_msg = (
                                f"Value for {leaf} is invalid.\n"
                                "Value must be 13 bits long wit 0 and 1 characters!"
                            )
                            raise MMSValidationException(error_msg)
                        else:
                            config["available_leafs"][leaf]["value"] = values[i]
                            config["leaf_widgets"][leaf]["value"]["value"] = values[i]
                            if leaf in config["included_leafs"]:
                                config["included_leafs"][leaf]["value"] = values[i]
                    elif "VisString" in config["available_leafs"][leaf]["type"]:
                        if isinstance(values[i], str):
                            if _is_iso646_string(values[i]):
                                config["available_leafs"][leaf]["value"] = values[i]
                                config["leaf_widgets"][leaf]["value"]["value"] = values[
                                    i
                                ]
                            else:
                                raise MMSValidationException(
                                    f"Invalid value for VisString leaf : {leaf}!"
                                )
                        else:
                            raise MMSValidationException(
                                f"Invalid value for VisString leaf : {leaf}!"
                            )
                    elif "Unicode" in config["available_leafs"][leaf]["type"]:
                        if isinstance(values[i], str):
                            if _is_unicode255_string(values[i]):
                                config["available_leafs"][leaf]["value"] = values[i]
                                config["leaf_widgets"][leaf]["value"]["value"] = values[
                                    i
                                ]
                            else:
                                raise MMSValidationException(
                                    f"Invalid value for Unicode leaf : {leaf}!"
                                )
                        else:
                            raise MMSValidationException(
                                f"Invalid value for Unicode leaf : {leaf}!"
                            )
                    elif "Octet" in config["included_leafs"][leaf]["type"]:
                        if isinstance(values[i], str):
                            if _is_octet_string(values[i]):
                                config["available_leafs"][leaf]["value"] = values[i]
                                config["leaf_widgets"][leaf]["value"]["value"] = values[
                                    i
                                ]
                            else:
                                raise MMSValidationException(
                                    f"Invalid value for Octet leaf : {leaf}!"
                                )
                        else:
                            raise MMSValidationException(
                                f"Invalid value for Octet leaf : {leaf}!"
                            )
                    elif "FLOAT" in config["included_leafs"][leaf]["type"]:
                        if isinstance(values[i], float):
                            config["included_leafs"][leaf]["value"] = values[i]
                            config["leaf_widgets"][leaf]["value"]["value"] = values[i]
                        else:
                            raise MMSValidationException(
                                f"Invalid float value for {leaf}!"
                            )
                    elif "INT" in config["included_leafs"][leaf]["type"]:
                        if isinstance(values[i], int):
                            config["available_leafs"][leaf]["value"] = values[i]
                            config["leaf_widgets"][leaf]["value"]["value"] = values[i]
                            if leaf in config["included_leafs"]:
                                config["included_leafs"][leaf]["value"] = values[i]
                        else:
                            raise MMSValidationException(
                                f"Invalid integer value for {leaf}!"
                            )
                    elif "BOOLEAN" in config["included_leafs"][leaf]["type"]:
                        if values[i] == 1 or values == 0:
                            config["available_leafs"][leaf]["value"] = values[i]
                            config["leaf_widgets"][leaf]["value"]["value"] = values[i]
                            if leaf in config["included_leafs"]:
                                config["included_leafs"][leaf]["value"] = values[i]
                        else:
                            raise MMSValidationException(
                                f"Invalid boolean value for {leaf}!"
                            )

        if len(aliases) != len(leafs_to_include):
            error_msg = "Aliases list and leaf list must be the same length for aliases to be set properly!"
            raise MMSValidationException(error_msg)

        for i, leaf in enumerate(leafs_to_include):
            config["included_leafs"][leaf]["alias"] = aliases[i]
            config["leaf_widgets"][leaf]["alias"] = aliases[i]
    return True


def write_leaf_props_to_mms(config, sch_model, item_handle):
    # --------------------------------------------------------------------------------
    # Description:
    #   This function sets dict properties of mms component
    #
    # Inputs:
    #   config:             configuration dictionary
    #   sch_model:          schematic model
    #   item_handle:        MMS Server schematic component
    #
    # Outputs:
    #
    # Author:
    #   Marko Boberic, December 2024
    # --------------------------------------------------------------------------------

    def _get_path_with_fc(path, fc):
        path_parts = path.split("$")

        try:
            path_with_fc = path_parts[3] + f"${fc}"
            for part in path_parts[4:]:
                path_with_fc += f"${part}"

            return path_with_fc
        except IndexError:
            return ""

    def _get_domain_name(path):
        path_parts = path.split("$")

        try:
            return path_parts[2]
        except IndexError:
            return ""

    def _get_casted_value(value, type_val):
        if type_val in ["Enum", "Dbpos"]:
            try:
                return int(value[0 : value.find("-")].strip())
            except ValueError:
                return int(value[0 : value.rfind("-")].strip())
        elif type_val.startswith("INT"):
            return int(value)
        elif type_val.startswith("FLOAT"):
            return float(value)
        elif type_val == "BOOLEAN":
            try:
                return int(value)
            except ValueError:
                return int(eval(value))
        elif type_val == "Quality":
            q0 = int(value[:8], 2)
            q1 = int(value[8:], 2)
            return [q0, q1]
        elif type_val.startswith(("VisString", "Octet", "Unicode")):
            return value
        else:
            print(f"Unsupported type {type_val}")

    def _get_casted_type(type_val):
        c_type_mappings = {
            "INT8": "signed char",
            "INT16": "signed short",
            "INT32": "int",
            "INT64": "long long int",
            "INT8U": "unsigned char",
            "INT16U": "unsigned short",
            "INT32U": "unsigned int",
            "INT64U": "unsigned long long int",
            "FLOAT32": "float",
            "FLOAT64": "double",
            "Enum": "signed char",
            "BOOLEAN": "char",
        }

        try:
            return c_type_mappings[type_val]
        except KeyError:
            return None

    def _get_default_DA_value(config, obj, type_val, enum_type=None):
        try:
            return default_DA_value[obj]
        except KeyError:
            if type_val.startswith("INT"):
                return 0
            elif type_val.startswith("FLOAT"):
                return 0.0
            elif type_val == "BOOLEAN":
                return False
            elif type_val == "Quality":
                return "0000000000000"
            elif "String" in type_val or "Unicode" in type_val or "Octet" in type_val:
                return ""
            elif type_val == "Enum":
                return config["enum_types"][enum_type][0]
            elif type_val == "Dbpos":
                return Dbpos_values[0]

    def _store_values_to_scl_struct(config, path, value, include, direction, alias):
        obj = config["scl"]

        path_elements = path.split("$")
        path_elements.insert(4, "init_values")
        for el in path_elements:
            try:
                if el != path_elements[-1]:
                    obj = obj[el]
                else:
                    _, default_value, _, _, _ = _get_values_from_scl_struct(
                        config, path
                    )
                    if default_value is None:
                        bType = _get_object_bType(
                            config["scl"], config["ied_data"], path
                        )
                        default_value = _get_default_DA_value(
                            config,
                            el,
                            bType,
                            enum_type=_get_object_type(
                                config["scl"], config["ied_data"], path
                            )
                            if bType in ["Enum", "Dbpos"]
                            else None,
                        )

                    obj[el] = {
                        "value": value,
                        "default_value": default_value,
                        "include": include,
                        "direction": direction,
                        "alias": alias,
                    }
            except KeyError:
                if el != path_elements[-1]:
                    obj[el] = {}
                    obj = obj[el]
                else:
                    _, default_value, _, _, _ = _get_values_from_scl_struct(
                        config, path
                    )
                    if default_value is None:
                        bType = _get_object_bType(
                            config["scl"], config["ied_data"], path
                        )
                        default_value = _get_default_DA_value(
                            config,
                            el,
                            bType,
                            enum_type=_get_object_type(
                                config["scl"], config["ied_data"], path
                            )
                            if bType == "Enum"
                            else None,
                        )

                    obj[el] = {
                        "value": value,
                        "default_value": default_value,
                        "include": include,
                        "direction": direction,
                        "alias": alias,
                    }

    def _get_widget_value(config, path, enum_type=None):
        if path in config["included_leafs"]:
            return config["included_leafs"][path]["value"]
        else:
            if enum_type:
                return config["enum_types"][enum_type][0]
            else:
                value = _get_value_widget(path, config["leaf_widgets"])
                return value

    def _create_terminals(sch_model, item_handle, included_leafs):
        type_mappings = {
            "INT8": "int",
            "INT16": "int",
            "INT32": "int",
            "INT8U": "uint",
            "INT16U": "uint",
            "INT32U": "uint",
            "FLOAT32": "real",
            "FLOAT64": "real",
            "Enum": "int",
            "Quality": "int",
            "BOOLEAN": "uint",
            "Dbpos": "int",
        }

        # get the existing terminal names
        all_terminals = sch_model.get_items(
            parent=item_handle, item_type=ITEM_COMPONENT
        )
        in_terminals = [
            sch_model.get_name(x)[:-3]
            for x in all_terminals
            if "in" in sch_model.get_name(x)
        ]
        out_terminals = [
            sch_model.get_name(x)[:-4]
            for x in all_terminals
            if "out" in sch_model.get_name(x)
        ]

        in_cnt = 0
        out_cnt = 0
        for leaf in included_leafs:
            terminal_name = _create_terminal_name(leaf)

            label = included_leafs[leaf]["alias"]
            if not label:
                label = terminal_name

            leaf_type = included_leafs[leaf]["type"]
            leaf_type = leaf_type.split("/")[0]
            if included_leafs[leaf]["dimension"] > 1:
                leaf_type = leaf_type.split("[")[0]

            if included_leafs[leaf]["direction"] == "in":
                # first delete out terminal with the same name
                comp = sch_model.get_item(
                    terminal_name + "_out", parent=item_handle, item_type=ITEM_COMPONENT
                )
                if comp:
                    sch_model.delete_item(comp)

                    port = sch_model.get_item(
                        terminal_name, parent=item_handle, item_type=ITEM_PORT
                    )
                    sch_model.delete_item(port)

                    del out_terminals[out_terminals.index(terminal_name)]

                # create input terminal
                if terminal_name not in in_terminals:
                    try:
                        input_port = sch_model.create_port(
                            name=terminal_name,
                            parent=item_handle,
                            kind="sp",
                            direction="in",
                            terminal_position=("left", "auto"),
                            position=(8000, 8000 + in_cnt * 100),
                        )

                        type_conversion = sch_model.create_component(
                            "core/Data Type Conversion",
                            name=terminal_name + "_conversion",
                            parent=item_handle,
                            position=(8250, 8000 + in_cnt * 100),
                        )

                        sp_input = sch_model.create_component(
                            "core/SP output",
                            name=terminal_name + "_in",
                            parent=item_handle,
                            position=(8500, 8000 + in_cnt * 100),
                        )

                        sch_model.set_property_value(
                            sch_model.prop(type_conversion, "output_type"),
                            type_mappings[leaf_type],
                        )

                        sch_model.set_terminal_dimension(
                            sch_model.term(sp_input, "in"), [1]
                        )

                        sch_model.create_connection(
                            input_port, sch_model.term(type_conversion, "in")
                        )
                        sch_model.create_connection(
                            sch_model.term(type_conversion, "out"),
                            sch_model.term(sp_input, "in"),
                        )

                        in_cnt += 1

                    except SchApiException:
                        input_port = sch_model.get_item(
                            terminal_name, parent=item_handle, item_type=ITEM_PORT
                        )

                    sch_model.set_port_properties(input_port, term_label=label)
                else:
                    del in_terminals[in_terminals.index(terminal_name)]

                    # update the terminal label
                    input_port = sch_model.get_item(
                        terminal_name, parent=item_handle, item_type=ITEM_PORT
                    )
                    sch_model.set_port_properties(input_port, term_label=label)

                    in_cnt += 1

            else:
                if terminal_name not in out_terminals:
                    try:
                        # first delete out terminal with the same name
                        comp = sch_model.get_item(
                            terminal_name + "_in",
                            parent=item_handle,
                            item_type=ITEM_COMPONENT,
                        )
                        if comp:
                            sch_model.delete_item(comp)
                            sch_model.delete_item(
                                sch_model.get_item(
                                    terminal_name,
                                    parent=item_handle,
                                    item_type=ITEM_PORT,
                                )
                            )
                            sch_model.delete_item(
                                sch_model.get_item(
                                    terminal_name + "_conversion",
                                    parent=item_handle,
                                    item_type=ITEM_COMPONENT,
                                )
                            )

                            del in_terminals[in_terminals.index(terminal_name)]

                        # create input terminal
                        output_port = sch_model.create_port(
                            name=terminal_name,
                            parent=item_handle,
                            kind="sp",
                            direction="out",
                            terminal_position=("right", "auto"),
                            flip=FLIP_VERTICAL,
                            position=(9000, 8000 + out_cnt * 100),
                        )

                        sp_output = sch_model.create_component(
                            "core/SP input",
                            name=terminal_name + "_out",
                            parent=item_handle,
                            flip=FLIP_VERTICAL,
                            position=(9500, 8000 + out_cnt * 100),
                        )

                        sch_model.set_terminal_sp_type(
                            sch_model.term(sp_output, "out"), type_mappings[leaf_type]
                        )
                        sch_model.set_property_value(
                            sch_model.prop(sp_output, "dimension"),
                            included_leafs[leaf]["dimension"],
                        )
                        sch_model.set_property_value(
                            sch_model.prop(sp_output, "execution_rate"),
                            "execution_rate",
                        )

                        sch_model.create_connection(
                            output_port, sch_model.term(sp_output, "out")
                        )

                        out_cnt += 1

                    except SchApiException:
                        output_port = sch_model.get_item(
                            terminal_name, parent=item_handle, item_type=ITEM_PORT
                        )

                    sch_model.set_port_properties(output_port, term_label=label)
                else:
                    del out_terminals[out_terminals.index(terminal_name)]

                    # update the terminal label
                    output_port = sch_model.get_item(
                        terminal_name, parent=item_handle, item_type=ITEM_PORT
                    )
                    sch_model.set_port_properties(output_port, term_label=label)

                    in_cnt += 1

        # delete excess terminals
        for terminal in in_terminals:
            port = sch_model.get_item(terminal, parent=item_handle, item_type=ITEM_PORT)
            if port:
                sch_model.delete_item(port)

            comp = sch_model.get_item(
                terminal + "_in", parent=item_handle, item_type=ITEM_COMPONENT
            )
            if comp:
                sch_model.delete_item(comp)

            comp = sch_model.get_item(
                terminal + "_conversion", parent=item_handle, item_type=ITEM_COMPONENT
            )
            if comp:
                sch_model.delete_item(comp)

        for terminal in out_terminals:
            port = sch_model.get_item(terminal, parent=item_handle, item_type=ITEM_PORT)
            if port:
                sch_model.delete_item(port)

            comp = sch_model.get_item(
                terminal + "_out", parent=item_handle, item_type=ITEM_COMPONENT
            )
            if comp:
                sch_model.delete_item(comp)

    def _create_terminal_name(path):
        path_parts = path.split("$")

        terminal_name = path_parts[2]
        for part in path_parts[3:]:
            terminal_name += f"_{part}"

        return terminal_name

    leaf_values = []
    # Write the initial values to scl structure
    for node_path in config["node_trees"]:
        leaf_path_subset = [
            path for path in config["leaf_widgets"] if node_path in path
        ]

        for leaf_path in leaf_path_subset:
            include = leaf_path in config["included_leafs"]
            direction = _get_direction_widget(config["leaf_widgets"], leaf_path)
            alias = _get_alias_widget(config["leaf_widgets"], leaf_path)
            type_val = _get_object_bType(config["scl"], config["ied_data"], leaf_path)

            value = _get_widget_value(
                config,
                leaf_path,
                enum_type=_get_object_type(config["scl"], config["ied_data"], leaf_path)
                if type_val == "Enum"
                else None,
            )

            _store_values_to_scl_struct(
                config,
                leaf_path,
                value,
                include,
                direction,
                alias,
            )

            _, default_value, _, _, _ = _get_values_from_scl_struct(config, leaf_path)

            if value:
                leaf_values.append(
                    {
                        "domain": _get_domain_name(leaf_path),
                        "name": _get_path_with_fc(
                            leaf_path,
                            _get_object_fc(
                                config["scl"], config["ied_data"], leaf_path
                            ),
                        ),
                        "casted_type": _get_casted_type(type_val),
                        "type": type_val,
                        "value": _get_casted_value(value, type_val),
                        "default_value": _get_casted_value(default_value, type_val),
                    }
                )

    sch_model.set_property_value(
        sch_model.prop(item_handle, "leaf_values"), leaf_values
    )
    sch_model.set_property_value(
        sch_model.prop(item_handle, "path_type"), config["path_type"]
    )
    sch_model.set_property_value(
        sch_model.prop(item_handle, "file_path"), config["file_path"]
    )
    sch_model.set_property_value(
        sch_model.prop(item_handle, "file_name"), config["file_name"]
    )
    sch_model.set_property_value(
        sch_model.prop(item_handle, "chosen_ied"), config["chosen_ied"]
    )
    sch_model.set_property_value(sch_model.prop(item_handle, "scl"), str(config["scl"]))
    sch_model.set_property_value(
        sch_model.prop(item_handle, "enum_types"), str(config["enum_types"])
    )
    sch_model.set_property_value(
        sch_model.prop(item_handle, "ied_data"), str(config["ied_data"])
    )
    sch_model.set_property_value(
        sch_model.prop(item_handle, "included_leafs"), str(config["included_leafs"])
    )

    # Create terminals for leaf nodes
    _create_terminals(sch_model, item_handle, config["included_leafs"])
