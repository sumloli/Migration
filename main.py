import os
import time
import requests
import json
import paramiko
import xmltodict
from pprint import pprint
import urllib3
urllib3.disable_warnings()



def main():
    tme = time.localtime()
    with open("log.txt", 'w') as logfile:
        logfile.write(f'{time.strftime("%m/%d/%y %H:%M:%S", tme)} setFlatCM started\n')


def jprint(obj):
    text = json.dumps(json.loads(obj), sort_keys=False, indent=4)
    print(text)


def make_request(method, base, path, headers=None, params=None, body=None):
    try:
        auth = requests.request('POST', f'{MMS}/global/activeusers', auth=('dmytro', 'dmytro'), verify=False)
        if auth.status_code == 201:
            print('Successfully authorized')
        auth.raise_for_status()
        headers = {'Authorization': f'Bearer {auth.headers["X-Token"]}'}
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    if params:
        print(f'{method, path, params}:')
    else:
        print(f'{method, path}:')
    try:
        response = requests.request(method, f'{base + path}', headers=headers, params=params, data=body, verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        response = None
    return [response, response.text, headers]


def download(ip, filename, remotepath, localpath=''):
    path = os.getcwd()
    if localpath != '':
        try:
            if not os.path.exists(path+localpath):
                os.makedirs(path+localpath)
        except OSError:
            print(f"Creation of the directory {path+localpath} failed")
        else:
            print(f"Directory {path+localpath}")
    else:
        localpath = '/'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username="root", password="strom")
    except Exception as e:
        print(e)
        print("It doesn't seem to be Prague's VM \nTrying to use RU credentials instead")
        ssh.connect(ip, username="dboriso", password="B52-a418-C949")
    sftp = ssh.open_sftp()
    sftp.get(remotepath+filename, path+localpath+filename, callback=lambda x, y: print(f'{filename} transferred: {x/y*100:.0f}%'))
    sftp.close()
    ssh.close()


def get_modules(omm_ip):
    try:
        download(ip=omm_ip, filename='module_registry.xml', remotepath='/opt/sts/omm/')
        print('DOWNLOADED SUCCESSFULLY')
    except Exception as e:
        print('"downloading module_registry.xml from OMM" FAILED')
        print(e)
    with open("module_registry.xml") as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()
        data = json.loads(json.dumps(data_dict['ModuleRegistry']['Modules']['BUS']))
        data_json = json.dumps(data_dict['ModuleRegistry']['Modules']['BUS'])
        with open("data.json", "w") as json_file:
            json_file.write(data_json)
            json_file.close()
    pprint(data)
    print('DATATYPE:'+str(type(data)))
    return data


def get_default_cfgs_list(ip, module):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username="root", password="strom")
    except Exception as e:
        print(e)
        print("It doesn't seem to be Prague's VM \nTrying to use RU credentials instead")
        ssh.connect(ip, username="dboriso", password="B52-a418-C949")
    sftp = ssh.open_sftp()
    try:
        list_of_cfgs = sftp.listdir(f'/opt/sts/{module}/defaultcfg')
        print(list_of_cfgs)
    except Exception as e:
        list_of_cfgs = {}
        print(e)
        tme = time.localtime()
        with open("log.txt", 'a') as logfile:
            logfile.write(f"{time.strftime('%m/%d/%y %H:%M:%S', tme)}   ------    {ip} module {module} doesn't have default configs\n")
        pass
    sftp.close()
    ssh.close()
    return list_of_cfgs


def get_actual_cfgs_list(ip, module):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username="root", password="strom")
    except Exception as e:
        print(e)
        print("It doesn't seem to be Prague's VM \nTrying to use RU credentials instead")
        ssh.connect(ip, username="dboriso", password="B52-a418-C949")
    sftp = ssh.open_sftp()
    list_of_files = sftp.listdir(f'/opt/sts/{module}')
    print(list_of_files)
    list_of_cfgs = [cfg for cfg in list_of_files if cfg.endswith(".xml")]
    print(list_of_cfgs)
    sftp.close()
    ssh.close()
    return list_of_cfgs


def module_from_midtype(midtype):
    if midtype in midtypes:
        new = midtype.replace()
    elif midtype is None:
        new = 'SEE'
    else:
        new = 'Wrong midtype'
    return new.lower()


def midtype_from_module(module):
    if module in modules:
        new = module.replace(module, f"{modules[module]}")
    elif module is None:
        new = 'SEE'
    else:
        new = 'Wrong module'
    return new.lower()


def download_cfgs(ip, module):
    if module != 'see':
        def_cfgs = get_default_cfgs_list(ip, module)
        if not def_cfgs:
            for cfg in get_actual_cfgs_list(ip, module):
                print(f'Trying to download {cfg}')
                download(ip=ip, filename=cfg, remotepath=f'/opt/sts/{module}/',
                         localpath=f'/platform/{module}[{ip}]/actualcfg/')
                print(f'Downloaded {cfg}')
        else:
            for cfg in def_cfgs:
                print(f'Trying to download {cfg}')
                download(ip=ip, filename=cfg, remotepath=f'/opt/sts/{module}/defaultcfg/',
                         localpath=f'/platform/{module}[{ip}]/defaultcfg/')
                print(f'Downloaded {cfg}')
            for cfg in get_actual_cfgs_list(ip, module):
                print(f'Trying to download {cfg}')
                download(ip=ip, filename=cfg, remotepath=f'/opt/sts/{module}/',
                         localpath=f'/platform/{module}[{ip}]/actualcfg/')
                print(f'Downloaded {cfg}')


def download_all_platform_cfgs(omm):
    for vm in get_modules(omm):
        print(vm)
        print(vm.get('@IP1'))
        if type(vm.get('Module')) == list:
            module = module_from_midtype(vm.get('Module', {})[0].get('@MIDType'))
            print(module)
        else:
            module = module_from_midtype(vm.get('Module', {}).get('@MIDType'))
            print(module)
        if module != 'see':
            download_cfgs(vm.get('@IP1'), 'bus')
            if type(vm.get('Module')) == list:
                for module in vm.get('Module'):
                    download_cfgs(vm.get('@IP1'), module_from_midtype(module.get('@MIDType')))
            else:
                download_cfgs(vm.get('@IP1'), module_from_midtype(vm.get('Module', {}).get('@MIDType')))
        else:
            tme = time.localtime()
            with open("log.txt", 'a') as logfile:
                logfile.write(f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------    {vm.get("@IP1")} is Windows\n')


def import_default_cfgs(platform):
    # platform is platform folder name after download
    folders_list = [f for f in os.listdir(platform) if not f.startswith('.')]
    print(folders_list)
    for folder in folders_list:
        print(f'Module: {folder}')
        print(f"{folder.split('[')[0].upper()}")
        for cfg in os.listdir(f"{platform}/{folder}/defaultcfg"):
            print('\n\n'+cfg)
            print('\n"POST defaultxml":')
            try:
                with open(f"{platform}/{folder}/defaultcfg/{cfg}", 'rb') as f:
                    body = f.read()
                    print(f'{platform}/{folder}/defaultcfg/{cfg}')
                    # print(f'opening cfg: {body}')
                add = make_request('POST', MMS, '/cm/cfgparams/defaultxmls',
                                   params={'moaftype': '1',
                                           'moduletype': midtype_from_module(folder.split('[')[0].upper()),
                                           'moduleconfigtype': cfg,
                                           'iversion': '001.00.00',
                                           'name': f'TESTMIGRATION_DEFAULT_{cfg}',
                                           'description': 'TESTMIGRATION_dmytro',
                                           'roleuser': 'Test'}, body=body)[1]
                print(json.loads(add))
                print(type(json.loads(add)))
                id = json.loads(add)['Id']
                print(f'id: {id}')
                print('SUCCESS')
            except Exception as e:
                print('"POST defaultxml" FAILED')
                print(e)
                tme = time.localtime()
                with open("log.txt", 'a') as logfile:
                    logfile.write(
                        f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------  {platform}/{folder}/defaultcfg/{cfg}  {e}\n')


def create_profile_import_xml(platform):
    folders_list = [f for f in os.listdir(platform) if not f.startswith('.')]
    print(folders_list)
    for folder in folders_list:
        print(f'Module: {folder}')
        print(f"{folder.split('[')[0].upper()}")
        for cfg in os.listdir(f"{platform}/{folder}/defaultcfg"):
            print('\n\n'+cfg)
            print('\n"Create and add xml to profile":')
            if os.path.isfile(f'{platform}/{folder}/actualcfg/{cfg}'):
                print('Actual cfg found!')
                try:
                    add_profile = make_request('POST', MMS, '/cm/profiles',
                                               params={
                                                   'name': f'TESTMIGRATION_ACTUAL_{cfg}',
                                                   'moaftype': '1',
                                                   'moduletype': midtype_from_module(folder.split('[')[0].upper()),
                                                   'moduleconfigtype': cfg,
                                                   'priority': '1',
                                                   'description': 'TESTMIGRATION_dmytro',
                                                   'roleuser': 'Test'})[1]
                    print(json.loads(add_profile))
                    print(type(json.loads(add_profile)))
                    id = json.loads(add_profile)['Result']['Id']
                    print(f'id: {id}')
                    print('SUCCESSFULLY CREATED PROFILE')
                    with open(f"{platform}/{folder}/actualcfg/{cfg}", 'rb') as f:
                        body = f.read()
                        print(body)
                    import_xml_to_profile = make_request('POST', MMS, '/cm/cfgparams/importxmls',
                                                         params={'profileid': id,
                                                                 'iversion': '001.00.00',
                                                                 'roleuser': 'Test'}, body=body)[1]
                    print(json.loads(import_xml_to_profile))
                    print(type(json.loads(import_xml_to_profile)))
                    print('SUCCESSFULLY ADDED XML TO PROFILE(ACTUAL)')
                except Exception as e:
                    print('"Create and add xml to profile" FAILED')
                    print(e)
                    tme = time.localtime()
                    with open("log.txt", 'a') as logfile:
                        logfile.write(
                            f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------  {platform}/{folder}/actualcfg/{cfg}  {e}\n')
            else:
                print('Actual cfg NOT found!')
                try:
                    add_profile = make_request('POST', MMS, '/cm/profiles',
                                               params={
                                                   'name': f'TESTMIGRATION_ACTUAL_{cfg}',
                                                   'moaftype': '1',
                                                   'moduletype': midtype_from_module(folder.split('[')[0].upper()),
                                                   'moduleconfigtype': cfg,
                                                   'priority': '1',
                                                   'description': 'TESTMIGRATION_dmytro',
                                                   'roleuser': 'Test'})[1]
                    print(json.loads(add_profile))
                    print(type(json.loads(add_profile)))
                    id = json.loads(add_profile)['Result']['Id']
                    print(f'id: {id}')
                    print('SUCCESSFULLY CREATED PROFILE')
                    with open(f"{platform}/{folder}/defaultcfg/{cfg}", 'rb') as f:
                        body = f.read()
                        print(body)
                    import_xml_to_profile = make_request('POST', MMS, '/cm/cfgparams/importxmls',
                                                         params={'profileid': id,
                                                                 'iversion': '001.00.00',
                                                                 'roleuser': 'Test'}, body=body)[1]
                    print(json.loads(import_xml_to_profile))
                    print(type(json.loads(import_xml_to_profile)))
                    print('SUCCESSFULLY ADDED XML TO PROFILE(DEFAULT)')
                except Exception as e:
                    print('"POST defaultxml" FAILED')
                    print(e)
                    tme = time.localtime()
                    with open("log.txt", 'a') as logfile:
                        logfile.write(
                            f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------  {platform}/{folder}/defaultcfg/{cfg}  {e}\n')


MMS = 'https://10.240.151.78'
omm = '10.240.206.111'
#omm = '10.240.250.149'
midtypes = {"0x000": "BUS", "0x002": "OMM", "0x003": "TTS", "0x006": "RES", "0x007": "SCAQI", "0x011": "DPA",
            "0x012": "CPA", "0x013": "IPA", "0x030": "STG", "0x034": "STA", "0x080": "MDP", "0x201": "BSAN",
            "0x211": "TTSNew", "0x212": "MDPI", "0x5EE": "SEE", "0xED5": "EDP"}
modules = {"BUS": "0x000", "OMM": "0x002", "TTS":"0x003", "RES":"0x006", "SCAQI": "0x007", "DPA": "0x011",
            "CPA": "0x012", "IPA": "0x013", "STG": "0x030", "STA": "0x034", "MDP": "0x080", "BSAN": "0x201",
            "TTSNew": "0x211", "MDPI": "0x212", "SEE": "0x5ee", "EDP": "0xed5"}