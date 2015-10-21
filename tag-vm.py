# Author:   Dale Coghlan (www.sneaku.com)
# Date:     13th Aug 2015
# Version:  1.0.2
# Enable Remote AccessApply a atg to a VM based on VM Name

# ----------------------------------------------------------------------------
# Set some variables. No need to change anything else after this section

nsxraml_file = '/Users/dcoghlan/Documents/07-NSXRAML/Repositories/NSXRAML/nsxraml-master/nsxvapiv614.raml'

globalScopeId = 'globalroot-0'

# Uncomment the following line to hardcode the password. This will remove the
# password prompt.
nsxMgrPass = 'VMware1!'
nsxmgr = '10.10.128.123'

# ----------------------------------------------------------------------------

from nsxramlclient.client import NsxClient
import yaml         # Used for debugging purposes
import argparse     # Used to generate command arguments
import getpass      # Generates the password prompt

def f_load_arguments():

    global nsx_username
    global nsxmanager
    # global args
    global vmName
    global tagName
    global modeAdd
    global modeDelete
    global modeList
    global modeDebug

    parser = argparse.ArgumentParser(description='Enable remote access for a VM')
    parser.add_argument('--nsxmgr',\
        help = 'NSX Manager hostname, FQDN or IP address',\
        metavar = 'nsxmanager',\
        dest = 'nsxmanager',\
        type = str,\
        required = True)
    parser.add_argument('--user',\
        help = 'OPTIONAL - NSX Manager username (default: %(default)s)',\
        metavar = 'username',\
        dest = 'username',\
        nargs = '?',\
        const = 'admin')
    parser.add_argument('--vm',\
        help = 'Virtual Machine Name',\
        metavar = 'VM Name',\
        dest = 'vm',\
        type = str,\
        required = True)
    parser.add_argument('--tag',\
        help = 'OPTIONAL - Security Tag Name',\
        metavar = 'tag',\
        dest = 'tag',\
        nargs = '?',\
        const = 'tag')
    parser.set_defaults(username='admin')
    # parser.set_defaults(debug=False)

    delParser = argparse.ArgumentParser(add_help=False)
    delParser.add_argument('--del', help=argparse.SUPPRESS, dest='modeDelete', action='store_true')
    delParser.add_argument('-v', help=argparse.SUPPRESS, dest = 'debug', action='store_true')

    # Parser arguments for 'add' sub-parser defined below
    addParser = argparse.ArgumentParser(add_help=False)
    addParser.add_argument('--add', help=argparse.SUPPRESS, dest='modeAdd', action='store_true')
    addParser.add_argument('-v', help=argparse.SUPPRESS, dest = 'debug', action='store_true')

    # Parser arguments for 'list' sub-parser defined below
    listParser = argparse.ArgumentParser(add_help=False)
    listParser.add_argument('--list', help=argparse.SUPPRESS, dest='modeList', action='store_true')
    listParser.add_argument('-v', help=argparse.SUPPRESS, dest = 'debug', action='store_true')

    # Sub-Parsers defined
    sp = parser.add_subparsers()
    sp_add = sp.add_parser('apply', help='Apply security tag to VM', parents=[addParser])
    sp_del = sp.add_parser('remove', help='Remove security tag from VM', parents=[delParser])
    sp_list = sp.add_parser('list', help='List security tags applied to a VM', parents=[listParser])

    # Load the parser into a variable
    args = parser.parse_args()

    # Reads command line flags and saves them to variables
    nsx_username = args.username
    nsxmanager = args.nsxmanager
    vmName = args.vm
    tagName = args.tag
    modeDebug =args.debug

    try:
        modeDelete = args.modeDelete
    except AttributeError:
        modeDelete = None

    try:
        modeAdd = args.modeAdd
    except AttributeError:
        modeAdd = None

    try:
        modeList = args.modeList
    except AttributeError:
        modeList = None

def f_pw_check():
    global nsx_password
    # Check to see if the password is hard coded
    try:
        nsxMgrPass
        nsx_password = nsxMgrPass
    except NameError:
        nsx_password = getpass.getpass(prompt='NSX Manager password:')

def f_set_output_formats():
    ''' Sets basic output formatting '''
    global outputSectionTitle
    global outputSectionTask
    outputSectionTitle = '{0:^79}'
    outputSectionTask = '{0:68} [{1:^8}]'

def f_get_vmObjectId(nsx,vmName):
    vmList = nsx.read('secGroupScopeMemberType',
        uri_parameters={'scopeId': globalScopeId,
                        'memberType': 'VirtualMachine'})

    for x in vmList['body']['list']['basicinfo']:
        if vmName.lower() == x['name'].lower():
            vmObjectId = x['objectId']
            pass
    try:
        if vmObjectId:
            return vmObjectId
    except:
        print(outputSectionTask.format(
                'Find virtual machine - %s' % (vmName),'Failed'))
        exit()

def f_get_secTagObjectId(nsx,tagName):
    sectagList = nsx.read('securityTag')

    for x in sectagList['body']['securityTags']['securityTag']:
        if x['name'] == tagName:
            tagObjectId = x['objectId']
            pass
    try:
        if tagObjectId:
            return tagObjectId
    except:
        print(outputSectionTask.format(
                'Find security tag - %s' % (tagName),'Failed'))
        exit()

def f_update_secTag(nsx,vmObjectId,tagObjectId):
    response = nsx.update('securityTagVM', 
                            uri_parameters={'tagId': tagObjectId, 
                            'vmMoid': vmObjectId})
    if response['status'] == 200:
        print(outputSectionTask.format(
                'Apply tag (%s) to VM (%s)' % (tagName,vmName),'OK'))
    else:
        print(outputSectionTask.format(
                'Apply tag (%s) to VM (%s)' % (tagName,vmName),'FAILED'))

def f_delete_secTag(nsx,vmObjectId,tagObjectId):
    response = nsx.delete('securityTagVM', 
                            uri_parameters={'tagId': tagObjectId, 
                            'vmMoid': vmObjectId})
    if response['status'] == 200:
        print(outputSectionTask.format(
                'Remove tag (%s) from VM (%s)' % (tagName,vmName),'OK'))
    else:
        print(outputSectionTask.format(
                'Remove tag (%s) from VM (%s)' % (tagName,vmName),'FAILED'))

def f_mode_list():
    response = nsx.read('secGroupLookupVM', 
                            uri_parameters={'virtualMachineId': vmObjectId})
    try:
        sgDict = response['body']['securityGroups']['securityGroups']['securitygroup']
        if type(sgDict) is list:
            for x in sgDict:
                if x['name'].startswith('internal_security_group'):
                    pass
                else:
                    print(outputSectionTask.format(
                        'Member Of: %s' % (x['name']),'NA'))
        else:
            if x['name'].startswith('internal_security_group'):
                pass
            else:
                print(outputSectionTask.format(
                        'Member Of: %s' % (sgDict['name']),'NA'))
    except TypeError:
        pass

def main():
    global nsx
    global vmObjectId

    f_load_arguments()
    f_pw_check()
    f_set_output_formats()

    nsx = NsxClient(nsxraml_file, nsxmanager, nsx_username, 
                           nsx_password, debug=modeDebug)

    vmObjectId = f_get_vmObjectId(nsx,vmName)

    if modeAdd != None:
        tagObjectId = f_get_secTagObjectId(nsx,tagName)
        f_update_secTag(nsx,vmObjectId,tagObjectId)

    if modeDelete != None:
        tagObjectId = f_get_secTagObjectId(nsx,tagName)
        f_delete_secTag(nsx,vmObjectId,tagObjectId)

    if modeList != None:
        f_mode_list()

if __name__ == '__main__':
    print
    main()
    print
exit()
