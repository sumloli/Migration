import os
import time
import requests
import json
import paramiko
import xmltodict
from pprint import pprint
import urllib3
urllib3.disable_warnings()


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
    list_of_cfgs = sftp.listdir(f'/opt/sts/{module}/defaultcfg')
    print(list_of_cfgs)
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
        new = midtype.replace(midtype, f"{midtypes['0x000']}(0x000), {midtypes[midtype]}({midtype})")
    elif midtype is None:
        new = f"{midtypes['0x000']}(0x000)"
    else:
        new = 'Wrong midtype'
    return new


def download_cfgs(ip, module):
    for cfg in get_default_cfgs_list(ip, module):
        print(f'Trying to download {cfg}')
        download(ip=ip, filename=cfg, remotepath=f'/opt/sts/{module}/defaultcfg/',
                 localpath=f'/platform/{module}[{ip}]/defaultcfg/')
        print(f'Downloaded {cfg}')
    for cfg in get_actual_cfgs_list(ip, module):
        print(f'Trying to download {cfg}')
        download(ip=ip, filename=cfg, remotepath=f'/opt/sts/{module}/',
                 localpath=f'/platform/{module}[{ip}]/actualtcfg/')
        print(f'Downloaded {cfg}')

MMS = 'https://10.240.151.78'
OMM = '10.97.155.51'
midtypes = {"0x000": "BUS", "0x002": "OMM", "0x003": "TTS", "0x006": "RES", "0x007": "SCAQI", "0x011": "DPA",
            "0x012": "CPA", "0x013": "IPA", "0x030": "STG", "0x034": "STA", "0x080": "MDP", "0x201": "BSAN",
            "0x211": "TTSNew", "0x212": "MDPI", "0x5EE": "SEE", "0xED5": "EDP"}
