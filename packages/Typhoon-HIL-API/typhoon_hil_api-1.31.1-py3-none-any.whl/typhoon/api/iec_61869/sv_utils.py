import os.path
import xml.etree.ElementTree as ET
from typhoon.api.iec_61869.exceptions import IEC61869SVValidationException

VARIANTS = ["F4000S1", "F4800S1", "F4800S2", "F5760S1", "F12800S8", "F14400S6", "F15360S8"]

def get_attrib_val(obj, attrib_name):
    try:
        return obj.attrib[attrib_name]
    except KeyError:
        return ""

def parse_scl_file(file_path):
    if os.path.isfile(file_path) is False:
        raise IEC61869SVValidationException("Provided file path does not exists.")

    scl_tree = ET.parse(file_path)
    scl_root = scl_tree.getroot()

    root_tag = scl_root.tag
    scl_prefix = root_tag[: root_tag.find("}") + 1]

    scl = {}
    smv_dict = {}

    # Loop the 'Communication' section of the file, and parse all SMV blocks.
    # If the file does not have 'Communication' section (for example ICD files),
    # configuring the component this way is most likely to fail because network communication
    # info such as APP ID, destination MAC and VLAN settings are missing.
    communications = scl_root.findall(scl_prefix + "Communication")

    for communication in communications:
        subnetworks = communication.findall(scl_prefix + "SubNetwork")
        for subnetwork in subnetworks:
            connectedAPs = subnetwork.findall(scl_prefix + "ConnectedAP")
            for connectedAP in connectedAPs:
                iedName = get_attrib_val(connectedAP, "iedName")
                apName = get_attrib_val(connectedAP, "apName")
                smv_dict[(iedName, apName)] = {}

                smvs = connectedAP.findall(scl_prefix + "SMV")
                for smv in smvs:
                    ldInst = get_attrib_val(smv, "ldInst")
                    cbName = get_attrib_val(smv, "cbName")
                    smv_dict[(iedName, apName)][(ldInst, cbName)] = {}

                    addresses = smv.findall(scl_prefix + "Address")
                    for address in addresses:
                        ps = address.findall(scl_prefix + "P")
                        for p in ps:
                            type = get_attrib_val(p, "type")
                            smv_dict[(iedName, apName)][(ldInst, cbName)][type] = p.text


    # Loop all IEDs, and search for a device that contains 'SampledValueControl' block.
    ieds = scl_root.findall(scl_prefix + "IED")

    for ied in ieds:
        ied_name = get_attrib_val(ied, "name")
        scl[ied_name] = {}

        AccessPoints = ied.findall(scl_prefix + "AccessPoint")
        for AccessPoint in AccessPoints:
            AccessPoint_name = AccessPoint.attrib["name"]
            scl[ied_name][AccessPoint_name] = {}

            LDevices = AccessPoint.findall(
                scl_prefix + "Server" + "/" + scl_prefix + "LDevice"
            )

            for LDevice in LDevices:
                LDevice_name = LDevice.attrib["inst"]
                scl[ied_name][AccessPoint_name][LDevice_name] = {}

                LNodes = LDevice.findall(
                    scl_prefix + "LN0"
                )

                for LNode in LNodes:
                    lnClass = get_attrib_val(LNode, "lnClass")
                    inst = get_attrib_val(LNode, "inst")
                    ln_type_id = get_attrib_val(LNode, "lnType")
                    prefix = get_attrib_val(LNode, "prefix")

                    LNode_name = lnClass

                    scl[ied_name][AccessPoint_name][LDevice_name][LNode_name] = {}
                    scl[ied_name][AccessPoint_name][LDevice_name][LNode_name]["id"] = ln_type_id

                    DataSets = LNode.findall(scl_prefix + "DataSet")

                    for DataSet in DataSets:

                        DataSet_name = get_attrib_val(DataSet, "name")
                        DataSet_desc = get_attrib_val(DataSet, "desc")

                        scl[ied_name][AccessPoint_name][LDevice_name][LNode_name][DataSet_name] = {}
                        scl[ied_name][AccessPoint_name][LDevice_name][LNode_name][DataSet_name]["desc"] = DataSet_desc

                        FCDAs = DataSet.findall(scl_prefix + "FCDA")

                        scl[ied_name][AccessPoint_name][LDevice_name][LNode_name][DataSet_name]["FCDAs"] = []

                        for FCDA in FCDAs:
                            ldInst = get_attrib_val(FCDA, "ldInst")
                            prefix = get_attrib_val(FCDA, "prefix")
                            lnClass = get_attrib_val(FCDA, "lnClass")
                            lnInst = get_attrib_val(FCDA, "lnInst")
                            doName = get_attrib_val(FCDA, "doName")
                            daName = get_attrib_val(FCDA, "daName")
                            fc = get_attrib_val(FCDA, "fc")

                            FCDA_dict = {}

                            FCDA_dict["ldInst"] = ldInst
                            FCDA_dict["prefix"] = prefix
                            FCDA_dict["lnClass"] = lnClass
                            FCDA_dict["lnInst"] = lnInst
                            FCDA_dict["doName"] = doName
                            FCDA_dict["daName"] = daName
                            FCDA_dict["fc"] = fc

                            scl[ied_name][AccessPoint_name][LDevice_name][LNode_name][DataSet_name]["FCDAs"].append(FCDA_dict)


                    SampledValueControls = LNode.findall(scl_prefix + "SampledValueControl")

                    scl[ied_name][AccessPoint_name][LDevice_name][LNode_name]["SampledValueControl"] = []

                    for SampledValueControl in SampledValueControls:
                        svc = {}

                        datSet = get_attrib_val(SampledValueControl, "datSet")
                        confRev = get_attrib_val(SampledValueControl, "confRev")
                        smvID = get_attrib_val(SampledValueControl, "smvID")
                        multicast = get_attrib_val(SampledValueControl, "multicast")
                        smpRate = get_attrib_val(SampledValueControl, "smpRate")
                        nofASDU = get_attrib_val(SampledValueControl, "nofASDU")
                        smpMod = get_attrib_val(SampledValueControl, "smpMod")
                        svc_name = get_attrib_val(SampledValueControl, "name")

                        dataSet_dict = {}

                        dataSet_dict["datSet"] = datSet
                        dataSet_dict["confRev"] = confRev
                        dataSet_dict["smvID"] = smvID
                        dataSet_dict["multicast"] = multicast
                        dataSet_dict["smpRate"] = smpRate
                        dataSet_dict["nofASDU"] = nofASDU
                        dataSet_dict["smpMod"] = smpMod
                        dataSet_dict["svc_name"] = svc_name
                        try:
                            dataSet_dict["appID"] = smv_dict[(ied_name, AccessPoint_name)][(LDevice_name, svc_name)]["APPID"]
                            dataSet_dict["vlanID"] = smv_dict[(ied_name, AccessPoint_name)][(LDevice_name, svc_name)]["VLAN-ID"]
                            dataSet_dict["user_priority"] = smv_dict[(ied_name, AccessPoint_name)][(LDevice_name, svc_name)]["VLAN-PRIORITY"]
                            dataSet_dict["destination_mac"] = smv_dict[(ied_name, AccessPoint_name)][(LDevice_name, svc_name)]["MAC-Address"]
                        except KeyError:
                            if len(communications) == 0:
                                raise IEC61869SVValidationException(
                                    "Error while parsing configuration. No valid 'Communication' section found in the provided file.")
                            else:
                                raise IEC61869SVValidationException(
                                    "Error while parsing configuration. No valid 'SMV' block found in the 'Communication' section in the provided file.")

                        svc = dataSet_dict
                        svc["name"] = get_attrib_val(SampledValueControl, "name")


                        # Check the signal frequency, this is used if 'smpRate' is given as 'smpPerPeriod'.
                        # Signal frequency is located in the 'LN' section o
                        LNNodes = LDevice.findall(
                            scl_prefix + "LN"
                        )
                        frequencies = []
                        i_scales = []
                        v_scales = []
                        for LN in LNNodes:
                            DOIs = LN.findall(scl_prefix + "DOI")
                            for DOI in DOIs:
                                if get_attrib_val(DOI, "name") == "HzRtg":
                                    # Parse all signals frequencies
                                    SDIs = DOI.findall(scl_prefix + "SDI")
                                    for SDI in SDIs:
                                        if get_attrib_val(SDI, "name") == "setMag":
                                            DAIs = SDI.findall(scl_prefix + "DAI")
                                            for DAI in DAIs:
                                                if get_attrib_val(DAI, "name") == "f":
                                                    Val = DAI.find(scl_prefix + "Val")
                                                    frequencies.append(Val.text)

                                # Parse all AmpSv (current) scaling factors
                                if get_attrib_val(DOI, "name") == "AmpSv" or get_attrib_val(DOI, "name") == "Amp":
                                    SDIs = DOI.findall(scl_prefix + "SDI")
                                    for SDI in SDIs:
                                        if get_attrib_val(SDI, "name") == "sVC":
                                            DAIs = SDI.findall(scl_prefix + "DAI")
                                            for DAI in DAIs:
                                                if get_attrib_val(DAI, "name") == "scaleFactor":
                                                    Val = DAI.find(scl_prefix + "Val")
                                                    i_scales.append(Val.text)

                                # Parse all VolSv (voltage) scaling factors
                                if get_attrib_val(DOI, "name") == "VolSv" or get_attrib_val(DOI, "name") == "Vol":
                                    SDIs = DOI.findall(scl_prefix + "SDI")
                                    for SDI in SDIs:
                                        if get_attrib_val(SDI, "name") == "sVC":
                                            DAIs = SDI.findall(scl_prefix + "DAI")
                                            for DAI in DAIs:
                                                if get_attrib_val(DAI, "name") == "scaleFactor":
                                                    Val = DAI.find(scl_prefix + "Val")
                                                    v_scales.append(Val.text)

                        dataSet_dict["frequencies"] = frequencies
                        dataSet_dict["i_scales"] = i_scales
                        dataSet_dict["v_scales"] = v_scales

                        scl[ied_name][AccessPoint_name][LDevice_name][LNode_name]["SampledValueControl"].append(svc)

    return scl


def filter_scv(scl):
    """
    This function will filter the parsed SCL structure and return only the items containing SampledValueControl block.
    """
    filtered_scl = {}

    for ied in scl:
        for ap in scl[ied]:
            for ld in scl[ied][ap]:
                for ln in scl[ied][ap][ld]:
                    ln_data = scl[ied][ap][ld][ln]
                    if ln_data.get("SampledValueControl"):
                        filtered_scl.setdefault(ied, {}).setdefault(ap, {}).setdefault(ld, {})[ln] = ln_data

    return filtered_scl


def save_scl_configuration(mdl, item_handle, configuration):
    """
    This function will save provided configuration.
    If this change needs to be permanent, model.save() must be called after the call to this function.

    'configuration' : a dictionary containing following keys:
        'scl', 'ied_name', 'access_point', 'l_device', 'svc', 'svc_index', 'file_path'
    """
    
    mask_handle = mdl.get_mask(item_handle)

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_scl"), configuration["scl"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'scl' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_ied"), configuration["ied_name"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'ied_name' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_access_point"), configuration["access_point"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'access_point' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_l_device"), configuration["l_device"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'l_device' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_svc"), configuration["svc"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'svc' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_svc_index"), configuration["svc_index"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'svc_index' key in the provided dictionary.")

    try:
        mdl.set_property_value(mdl.prop(mask_handle, "saved_file_path"), configuration["file_path"])
    except KeyError:
        raise IEC61869SVValidationException("Error while saving configuration. No 'file_path' key in the provided dictionary.")

def set_configuration_from_file(mdl, item_handle, file_path, svc):
    """
    This function parses the file located at the 'file_path', and configures the component
    referred to by 'item_handle' with values associated with 'svc' in the file.

    'mdl' : model handle
    'item_handle' : IEC 61869 SV Publisher component item handle
    'file_path' : valid absolute path to the configuration file
    'svc' : a string in the format: "IED_name/AccessPoint_name/LDevice_name/SampledValueControl_name"
        For example: "TEMPLATE/S1/MU01/MSVCB01"


    If successful it will return a dictionary with keys:
    'appID', 'vlanID', 'user_priority', 'destination_mac', 'confRev', 'smvID', 'variant', 'i_count', 'v_count', 'i_scaling', 'v_scaling'
    If 'i_scaling' or 'v_scaling' were not configured, the value returned is 'None'.
    """

    scl = parse_file(file_path)

    path_splits = svc.split("/")

    if len(path_splits) != 4:
        raise IEC61869SVValidationException(f"Provided SampledValueControl path '{svc}' not valid.")

    IED = path_splits[0]
    AccessPoint = path_splits[1]
    LDevice = path_splits[2]
    SampledValueControl = path_splits[3]
    LN = "LLN0"

    try:
        SVCs = scl[IED][AccessPoint][LDevice][LN]["SampledValueControl"]
    except KeyError:
        raise IEC61869SVValidationException(f"Provided 'scl' dictionary does not contain {svc} elements.")

    configuration = None
    svc_index = 0
    for i, SVC in enumerate(SVCs):
        if SVC["name"] == SampledValueControl:
            svc_index = i
            configuration = SVC

    if configuration is None:
        raise IEC61869SVValidationException(f"Provided SampledValueControl {SampledValueControl} does not exist in the provided 'scl' dictionary.")

    dataSet = {}
    datSet_name = configuration["datSet"]
    try:
        dataSet[datSet_name] = scl[IED][AccessPoint][LDevice][LN][datSet_name]
    except KeyError:
        raise IEC61869SVValidationException(f"No data set name '{datSet_name}' found in provided 'scl' dictionary.")

    save_dict = {
        "scl" : scl,
        "ied_name": IED,
        "access_point" : AccessPoint,
        "l_device" : LDevice,
        "svc" : configuration["name"],
        "svc_index" : svc_index,
        "file_path" : file_path,
    }

    configured_values = set_configuration(mdl, item_handle, configuration, dataSet, save_dict)
    return configured_values


def set_configuration(mdl, item_handle, configuration, datasets, save_dict):
    """
    Set the provided configuration to the provided item in the model.

    'configuration' : dictionary containing following keys:
        'appID', 'vlanID', 'user_priority', 'destination_mac', confRev', 'smvID', 'smpMod', 'smpRate', 'nofASDU', 'datSet', 'frequencies', 'i_scales', 'v_scales'

        For this purpose it is recommended to use the function 'parse_scl_file', as it returns the dictionary containing items of this structure.

    'datasets' : this can be either an item of a dictionary or a dictionary.
        If it's an item, it must be the handle of the dataSet item which is called the same as
        the value of configuration["datSet"].
        If it's a dictionary, function will search for configuration["datSet"] key in that dictionary.

    'save_dict' : this is a dictionary containing following keys:
        'scl', 'ied_name', 'access_point', 'l_device', 'svc', 'svc_index', 'file_path'


    If successful it will return a dictionary with keys:
    'appID', 'vlanID', 'user_priority', 'destination_mac', 'confRev', 'smvID', 'variant', 'i_count', 'v_count', 'i_scaling', 'v_scaling'
    If 'i_scaling' or 'v_scaling' were not configured, the value returned is 'None'.
    """

    try:
        appID = str(configuration["appID"])

        try:
            appID = int(appID, 16)
        except ValueError:
            raise IEC61869SVValidationException("Invalid appID value.")

        appID = hex(appID)
    except KeyError:
        raise IEC61869SVValidationException("No 'appID' in the provided dictionary.")

    try:
        vlanID = int(configuration["vlanID"])
    except KeyError:
        raise IEC61869SVValidationException("No 'vlanID' in the provided dictionary.")

    try:
        user_priority = int(configuration["user_priority"])
    except KeyError:
        raise IEC61869SVValidationException("No 'user_priority' in the provided dictionary.")

    try:
        destination_mac = configuration["destination_mac"].replace("-", ":")
    except KeyError:
        raise IEC61869SVValidationException("No 'destination_mac' in the provided dictionary.")

    try:
        confRev = int(configuration["confRev"])
    except KeyError:
        raise IEC61869SVValidationException("No 'confRev' in the provided dictionary.")


    try:
        smvID = configuration["smvID"]
    except KeyError:
        raise IEC61869SVValidationException("No 'smvID' in the provided dictionary.")


    try:
        smpMod = configuration["smpMod"]
    except KeyError:
        raise IEC61869SVValidationException("No 'smpMod' in the provided dictionary.")

    # If 'smpMod' is missing, it is assumed that the default value is 'SmpPerPeriod'
    # According to Siemens SIPROTEC 5 Process Bus manual
    if smpMod == "":
        smpMod = "SmpPerPeriod"

    try:
        smpRate = configuration["smpRate"]
    except KeyError:
        raise IEC61869SVValidationException("No 'smpRate' in the provided dictionary.")

    try:
        nofASDU = configuration["nofASDU"]
    except KeyError:
        raise IEC61869SVValidationException("No 'nofASDU' in the provided dictionary.")


    try:
        frequencies = configuration["frequencies"]
    except KeyError:
        frequencies = []

    if smpMod.lower() == "SmpPerPeriod".lower():
        if frequencies is not None:
            freq_set = set(frequencies)
            if len(freq_set) == 0:
                raise IEC61869SVValidationException(
                    "No signal frequency value was parsed. No way to determine the SV variant.")
            elif len(freq_set) == 1:
                freq = float(freq_set.pop())
                smpRate = int(int(smpRate) * freq)
            else:
                raise IEC61869SVValidationException(
                    "More than one signal frequency value was parsed. No way to determine the SV variant.")

        else:
            raise IEC61869SVValidationException(
                "No signal frequency value was parsed. No way to determine the SV variant.")


    variant = "F" + str(smpRate) + "S" + str(nofASDU)
    if variant not in VARIANTS:
        raise IEC61869SVValidationException(f"Variant {variant} not supported by IEC 61869 SV Publisher.")


    try:
        datSet = configuration["datSet"]
    except KeyError:
        datSet = ""


    if datasets is None or datSet == "":
        raise IEC61869SVValidationException("Non valid dataSet provided.")

    else:
        try:
            i_count, v_count = _get_count_in_dataset(datasets[datSet])
        except KeyError:
            raise IEC61869SVValidationException("Non valid dataSet provided.")

    try:
        i_scales = configuration["i_scales"]
    except KeyError:
        i_scales = []

    try:
        v_scales = configuration["v_scales"]
    except KeyError:
        v_scales = []

    # Set components properties
    mask_handle = mdl.get_mask(item_handle)

    mdl.set_property_value(mdl.prop(mask_handle, "appID"), appID)
    mdl.set_property_value(mdl.prop(mask_handle, "vlanID"), vlanID)
    mdl.set_property_value(mdl.prop(mask_handle, "user_priority"), user_priority)
    mdl.set_property_value(mdl.prop(mask_handle, "destination_mac"), destination_mac)
    mdl.set_property_value(mdl.prop(mask_handle, "confRev"), confRev)
    mdl.set_property_value(mdl.prop(mask_handle, "svID"), smvID)
    mdl.set_property_value(mdl.prop(mask_handle, "variant"), variant)
    mdl.set_property_value(mdl.prop(mask_handle, "i_count"), i_count)
    mdl.set_property_value(mdl.prop(mask_handle, "v_count"), v_count)

    if i_scales:
        # Check if there is more than one scaling factor value in the list
        i_scale_set = set(i_scales)
        if len(i_scale_set) == 1:
            i_scaling = float(i_scale_set.pop())
            mdl.set_property_value(mdl.prop(mask_handle, "i_scaling"), i_scaling)
        else:
            raise IEC61869SVValidationException("More than one current scale factor value was parsed. No way to determine the exact scaling factor.")
    else:
        # If i_scales list is empty, no scaling factor was parsed from the file
        # In this case, do nothing and leave i_scaling value as default or as already set
        i_scaling = None


    if v_scales:
        # Check if there is more than one scaling factor value in the list
        v_scale_set = set(v_scales)
        if len(v_scale_set) == 1:
            v_scaling = float(v_scale_set.pop())
            mdl.set_property_value(mdl.prop(mask_handle, "v_scaling"), v_scaling)
        else:
            raise IEC61869SVValidationException(
                "More than one voltage scale factor value was parsed. No way to determine the exact scaling factor.")
    else:
        # If v_scales list is empty, no scaling factor was parsed from the file
        # In this case, do nothing and leave v_scaling value as default or as already set
        v_scaling = None


    configured_values = {
        "appID": appID,
        "vlanID": vlanID,
        "user_priority": user_priority,
        "destination_mac": destination_mac,
        "confRev": confRev,
        "svID": smvID,
        "variant": variant,
        "i_count": i_count,
        "v_count": v_count,
        "i_scaling": i_scaling,
        "v_scaling": v_scaling,
    }

    save_scl_configuration(mdl, item_handle, save_dict)

    return configured_values


def parse_file(file_path):
    """
    This function loads an SCL file located on the provided path, parses it, filters it and returns a dictionary.

    file_path must be an absolute path.
    """

    if os.path.isabs(file_path) is False:
        raise IEC61869SVValidationException(f"Provided file path {file_path} is not an absolute path.")

    scl = parse_scl_file(file_path)
    filtered_scl = filter_scv(scl)

    return filtered_scl


def get_IEDs(scl):
    return list(scl.keys())


def get_AccessPoints(scl):
    return list(scl.keys())


def get_LDevices(scl):
    return list(scl.keys())


def get_LNodes(scl):
    return list(scl.keys())


def get_SampledValueControls(scl):
    return list(scl["SampledValueControl"])


def get_DataSets(scl):
    return {key: value for key, value in scl.items() if key != "SampledValueControl"}


def _get_count_in_dataset(datSet):
    i_count = 0
    v_count = 0

    try:
        FCDAs = datSet["FCDAs"]
    except KeyError:
        raise IEC61869SVValidationException("Non valid dataSet provided.")

    for instance in FCDAs:
        doName = str(instance["doName"])
        if doName.startswith("AmpSv") and instance["daName"] != "q":
            i_count += 1

        if doName.startswith("VolSv") and instance["daName"] != "q":
            v_count += 1

    return i_count, v_count

