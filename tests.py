from main import *


print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "GET version":')
try:
    print(make_request('GET', MMS, '/global/versions'))
    print('SUCCESS')
except Exception as e:
    print('"GET version" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "GET db version":')
try:
    print(make_request('GET', MMS, '/global/versions', params={'id': 'db'}))
    print('SUCCESS')
except Exception as e:
    print('"GET db version" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "GET modules":')
try:
    jprint(make_request('GET', MMS, '/mr/module', params={'roleuser': 'Test'})[1])
    print('SUCCESS')
except Exception as e:
    print('"GET modules" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "POST defaultxml":')
try:
    with open('body.xml', 'r') as f:
        body = f.read()
    add = make_request('POST', MMS, '/cm/cfgparams/defaultxmls', params={'moaftype': '1', 'moduletype': '0x002',
                                                                         'moduleconfigtype': 'TEST_apisecuritydefaults.xml',
                                                                         'iversion': '001.00.00',
                                                                         'name': 'TEST_apisecuritydefaults',
                                                                         'description': 'TEST_dmytro',
                                                                         'roleuser': 'Test'}, body=body)[1]
    print(json.loads(add))
    print(type(json.loads(add)))
    id = json.loads(add)['Id']
    print(f'id: {id}')
    print('SUCCESS')
except Exception as e:
    print('"POST defaultxml" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "GET profile":')
try:
    get = make_request('GET', MMS, f'/cm/profiles/{id}', params={'roleuser': 'Test'})
    print(get)
    print('SUCCESS')
except Exception as e:
    print('"GET profile" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "DELETE profile":')
try:
    remove = make_request('DELETE', MMS, f'/cm/profiles/{id}', params={'roleuser': 'Test'})
    print(remove)
    print('SUCCESS')
except Exception as e:
    print('"DELETE profile" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "downloading file":')
try:
    download(ip='10.240.151.112', filename='tts.pcap', path='/opt/sts/')
    print('SUCCESS')
except Exception as e:
    print('"downloading file" FAILED')
    print(e)
print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "downloading module_registry.xml from OMM":')
try:
    download(ip='10.97.155.51', filename='module_registry.xml', path='/opt/sts/omm/')
    print('SUCCESS')
except Exception as e:
    print('"downloading module_registry.xml from OMM" FAILED')
    print(e)
print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "receiving modules list":')
try:
    for vm in get_modules(OMM):
        print(f"Modules at {vm.get('@IP1')}: {module_from_midtype(vm.get('Module', {}).get('@MIDType'))}")
    print('SUCCESS')
except Exception as e:
    print('"receiving modules list" FAILED')
    print(e)
