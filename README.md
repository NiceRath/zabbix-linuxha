# Zabbix LinuxHA Monitoring

Tested on Debian.

## Install

* Copy the script `linuxha.py` to the target system (*executable by the zabbix user*)
* Copy the userparameter to the target system
* Add the `sudoers` privileges via `visudo -f /etc/sudoers.d/zabbix_linuxha`
* Restart the Zabbix Agent service
* Import the Template on your Zabbix Server

----

## Testing

On the target system:

```bash
root@SRV1:~$ su zabbix --login --shell /bin/bash

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/linuxha.py discover
> {"data": [{"{#LINHA_RES}": "resIP"}, {"{#LINHA_RES}": "resService"}]}

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/linuxha.py members
> 2

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/linuxha.py members_active
> 2

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/linuxha.py votes
> 1

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/linuxha.py quorum
> 1

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/linuxha.py resource resIP
> 1

zabbix@SRV1:~$ python3 /usr/local/bin/zabbix/linuxha.py resource_active resIP
> 1
```

----

## Usage

The script expects all resources to have a name that starts with a prefix. By default `res`. You can change it in the script.

----

## Items

* Count of Members in the Cluster
* Count of active Members
* Got all expected quorum votes
* Has quorum
* Resource Discovery
  * Resource is active on any node
  * Resource is active on the current node

### Triggers

* Not all Members online (*avg*)
* No quorum (*high*)
* Missing quorum votes (*avg*)
* Resource Discovery
  * Resource offline (inactive on all nodes) (*disaster*)
