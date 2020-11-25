import time
import json
import rest, files, platforms
import urllib3

urllib3.disable_warnings()

omm = mms = omm_username = omm_password = mms_username = mms_password = ...


def main():
    global omm
    global mms
    global omm_username
    global omm_password
    global mms_username
    global mms_password
    tme = time.localtime()
    with open("log.txt", 'w') as logfile:
        logfile.write(f'{time.strftime("%m/%d/%y %H:%M:%S", tme)} setFlatCM started\n')
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)

        omm = config_data['servers'][0]['ip'][0]
        print(f'{config_data["servers"][0]["name"]}: {omm}')
        mms = config_data['servers'][1]['ip'][0]
        print(f'{config_data["servers"][1]["name"]}: {mms}')
        mms = f'https://{mms}'
        omm_username = config_data['servers'][0]['credentials'][0]['username']
        # print(omm_username)
        omm_password = config_data['servers'][0]['credentials'][0]['password']
        # print(omm_password)
        mms_username = config_data['servers'][1]['credentials'][0]['username']
        # print(mms_username)
        mms_password = config_data['servers'][1]['credentials'][0]['password']
        # print(mms_password)
        if config_data['rollback'] == 'yes':
            platforms.rollback('platform_test_extended')
    return omm, mms, omm_username, omm_password, mms_username, mms_password


if __name__ == "__main__":
    main()


def module_from_midtype(midtype):
    midtypes = {"0x000": "BUS", "0x002": "OMM", "0x003": "TTS", "0x006": "RES", "0x007": "SCAQI", "0x011": "DPA",
                "0x012": "CPA", "0x013": "IPA", "0x030": "STG", "0x034": "STA", "0x080": "MDP", "0x201": "BSAN",
                "0x211": "TTSNew", "0x212": "MDPI", "0x5EE": "SEE", "0xED5": "EDP"}
    if midtype in midtypes:
        new = midtype.replace()
    elif midtype is None:
        new = 'SEE'
    else:
        new = 'Wrong midtype'
    return new.lower()


def midtype_from_module(module):
    modules = dict(BUS="0x000", OMM="0x002", TTS="0x003", RES="0x006", SCAQI="0x007", DPA="0x011", CPA="0x012",
                   IPA="0x013", STG="0x030", STA="0x034", MDP="0x080", BSAN="0x201", TTSNew="0x211", MDPI="0x212",
                   SEE="0x5ee", EDP="0xed5")
    if module in modules:
        new = module.replace(module, f"{modules[module]}")
    elif module is None:
        new = 'SEE'
    else:
        new = 'Wrong module'
    return new.lower()
