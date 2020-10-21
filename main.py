import requests
import json
import paramiko
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


def download(ip, filename, path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="root", password="strom")
    sftp = ssh.open_sftp()
    sftp.get(path+filename, filename, callback=lambda x, y: print(f'{filename} transferred: {x/y*100:.0f}%'))
    sftp.close()
    ssh.close()


MMS = 'https://10.240.151.78'
