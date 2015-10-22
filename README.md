# NSX-Tag-a-VM
A script to apply and remove a security tag from a VM


##Prerequisites
NSX RAML
https://github.com/vmware/nsxraml

NSXRAMLCLIENT
https://github.com/vmware/nsxramlclient


##Usage
```
python tagvm.py -h
```
Output:
```
usage: tagvm.py [-h] --nsxmgr nsxmanager [--user [username]] --vm VM
                       Name [--tag [tag]]
                       {apply,remove,list} ...

Apply or remove a tag from a VM

positional arguments:
  {apply,remove,list}
    apply              Apply security tag to VM
    remove             Remove security tag from VM
    list               List security tags applied to a VM

optional arguments:
  -h, --help           show this help message and exit
  --nsxmgr nsxmanager  NSX Manager hostname, FQDN or IP address
  --user [username]    OPTIONAL - NSX Manager username (default: admin)
  --vm VM Name         Virtual Machine Name
  --tag [tag]          OPTIONAL - Security Tag Name
```

##Examples
Apply the security tag "ST-Essential Services" to the VM ubuntu-004
```
python tagvm.py --nsxmgr 10.10.128.123 --vm ubuntu-004 --tag "ST-Essential Services" apply

Apply tag (ST-Essential Services) to VM (ubuntu-004)                 [   OK   ]

```
Remove the security tag "ST-Essential Services" to the VM ubuntu-004
```
python tagvm.py --nsxmgr 10.10.128.123 --vm ubuntu-004 --tag "ST-Essential Services" remove

Remove tag (ST-Essential Services) from VM (ubuntu-004)              [   OK   ]
```
List all the security groups VM ubuntu-004 is a member of.
```
python tagvm.py --nsxmgr 10.10.128.123 --vm ubuntu-004 list

Member Of: SG-C.NTP                                                  [   NA   ]
Member Of: SG-C.DNS Internal                                         [   NA   ]
Member Of: SG-SECDOM.None                                            [   NA   ]
Member Of: SG-CLASS.None                                             [   NA   ]
```



