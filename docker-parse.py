#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import subprocess, sys

if len(sys.argv) < 2:
    print "Please specific container name!"
    sys.exit()
    
try:
    cmd = ["docker", "inspect"]
    cmd.extend(sys.argv[1:])
    output = subprocess.check_output(cmd)
except subprocess.CalledProcessError, e:
    sys.exit()
    
infos = json.loads(output)
for info in infos:
    name = info['Name'][1:]
    conf = info['Config']
    hconf = info['HostConfig']
    volumes = ''; ports = ''

    if len(hconf["Binds"]) > 0:
        volumes = ' -v ' + ' -v '.join(hconf['Binds'])
    if len(hconf["PortBindings"]) > 0:
        for k, v in hconf['PortBindings'].iteritems():
            for hv in v:
                ports += ' -p ' + k
                if 'HostIp' in hv:
                    ports += ':' + hv['HostIp']
                if 'HostPort' in hv: 
                    ports += ':' + hv['HostPort']
    print 'docker run --name {name} -d {volumes} {ports} {image}'.format(
        name = name, volumes = volumes, ports = ports, image = conf['Image'])


