#!/usr/bin/python3

# {{ ansible_managed }}

from subprocess import Popen as subprocess_popen
from subprocess import PIPE as subprocess_pipe
from sys import argv as sys_argv
from re import search as regex_search
from json import dumps as json_dumps
from socket import gethostname

RES_PREFIX = 'res'

LINUXHA_BIN = 'sudo /usr/sbin/crm'
COROSYNC_CMD = 'sudo /usr/sbin/corosync-cmapctl runtime.members | grep status'
QUORUM_CMD = 'sudo /usr/sbin/corosync-quorumtool -s'
ZBX_KEY = '{#LINHA_RES}'

try:
    CHECK = sys_argv[1]

    try:
        RESOURCE = sys_argv[2]

    except IndexError:
        RESOURCE = None

except IndexError:
    raise SystemExit('You must specify the following arguments: 1 => check-type')

if CHECK == 'discover':
    cmd = f'{LINUXHA_BIN} resource status'

elif CHECK in ['members', 'members_active']:
    cmd = COROSYNC_CMD

elif CHECK in ['votes', 'quorum']:
    cmd = QUORUM_CMD

else:
    cmd = f"{LINUXHA_BIN} status bynode"

with subprocess_popen([cmd], shell=True, stdout=subprocess_pipe, stderr=subprocess_pipe) as ps:
    _stdout, _stderr = ps.communicate()
    STDOUT = _stdout.decode('utf-8')
    STDERR = _stderr.decode('utf-8')


def output(msg: (str, int)):
    print(msg)
    raise SystemExit


if CHECK == 'discover':
    result = {'data': []}

    for line in STDOUT.split('\n'):
        res = regex_search(r'\s((%s).*?)(\s|\t)' % RES_PREFIX, line)
        if res is not None:
            result['data'].append({ZBX_KEY: res.group(1)})

    output(json_dumps(result))

elif CHECK == 'resource':
    # if one of the hosts is the active node for the given resource
    result = 0

    for line in STDOUT.split('\n'):
        if line.find(RESOURCE) != -1 and (line.find('Started') != -1 or line.find('Master') != -1):
            result = 1
            break

    output(result)

elif CHECK == 'resource_active':
    # if the current host is the active node for the given resource
    node_start = False
    result = 0

    for line in STDOUT.split('\n'):
        if not node_start and line.find(f'Node {gethostname()}') != -1:
            # if own node block begins
            node_start = True
            continue

        if node_start and line.find('Node ') != -1:
            # if own node block ended
            break

        if node_start:
            if line.find(RESOURCE) != -1 and (line.find('Started') != -1 or line.find('Master') != -1):
                result = 1
                break

    output(result)

elif CHECK == 'quorum':
    for line in STDOUT.split('\n'):
        if line.find('Quorate') != -1:
            output(1) if line.find('Yes') != -1 else output(0)
            break

elif CHECK == 'votes':
    votes_expected = 0
    votes_now = 0
    for line in STDOUT.split('\n'):
        if line.find('Expected votes') != -1:
            votes_expected = int(line.split(':', 1)[1].strip())

        elif line.find('Total votes') != -1:
            votes_now = int(line.split(':', 1)[1].strip())
            break

    output(1) if votes_expected == votes_now else output(0)

elif CHECK == 'members':
    # all available members
    output(STDOUT.count('runtime.members'))

elif CHECK == 'members_active':
    # currently 'online' members
    output(STDOUT.count('joined'))

else:
    output('No supported check found')
