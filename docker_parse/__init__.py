#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import subprocess, sys

def main():
    if len(sys.argv) < 2:
        print("Please specific container name!")
        sys.exit()
    
    try:
        cmd = ["docker", "inspect"]
        cmd.extend(sys.argv[1:])
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        sys.exit()
    
    infos = json.loads(output)
    for info in infos:
        name = info['Name'][1:]
        conf = info['Config']
        hconf = info['HostConfig']

        misc = ''

        if len(hconf["Binds"]) > 0:
            misc = ' -v ' + ' -v '.join(hconf['Binds'])

        if len(hconf["PortBindings"]) > 0:
            for k, v in hconf['PortBindings'].items():
                for hv in v:
                    misc += ' -p '
                    if 'HostIp' in hv:
                        misc += hv['HostIp'] + ':'
                    if 'HostPort' in hv: 
                        misc += hv['HostPort'] + ':'
                    misc += k

        if hconf['RestartPolicy']['Name']:
            if hconf['RestartPolicy']['MaximumRetryCount'] > 0:
                misc += ' --restart=' + hconf['RestartPolicy']['Name'] + ':' + str(hconf['RestartPolicy']['MaximumRetryCount'])
            else:
                misc += ' --restart=' + hconf['RestartPolicy']['Name']

        print('docker run --name {name} -d{misc} {image}'.format(
            name = name, misc = misc, image = conf['Image']))

if __name__ == "__main__":
    main()