#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import subprocess
import sys
import pipes


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

        if isinstance(hconf["Binds"], list) and len(hconf["Binds"]) > 0:
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
            restart_str = ' --restart=' + hconf['RestartPolicy']['Name']
            if hconf['RestartPolicy']['MaximumRetryCount'] > 0:
                misc += restart_str + ':' + str(hconf['RestartPolicy']['MaximumRetryCount'])
            else:
                misc += restart_str

        for v in conf['Env']:
            misc += ' -e {}'.format(pipes.quote(v))

        cmd = ''
        for v in conf['Cmd']:
            cmd += ' {}'.format(pipes.quote(v))

        print('docker run --name {name} -d{misc} {image}{cmd}'.format(
            name=name, misc=misc,
            image=conf['Image'], cmd=cmd))

if __name__ == "__main__":
    main()
