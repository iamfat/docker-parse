#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import subprocess
import sys
import pipes
import getopt


def main():
    if len(sys.argv) < 2:
        print("Please specific container name!")
        sys.exit()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "p", ["pretty"])
    except getopt.GetoptError as e:
        print("Usage: docker-parse [--pretty|-p] <container>")
        sys.exit(2)

    if len(args) > 0:
        container = args[0]
    else:
        print("Please specific container name!")
        sys.exit()

    sep = ' '
    for o, a in opts:
        if o == "-p" or o == "--pretty":
            sep = ' \\\n    '

    try:
        cmd = ["docker", "inspect"]
        cmd.extend([container])
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        sys.exit()

    infos = json.loads(output)
    for info in infos:

        short_options = ''
        options = []

        conf = info['Config']
        hconf = info['HostConfig']

        options.append("--name {name}".format(name=info['Name'][1:]))

        if not conf['AttachStdout']:
            short_options += 'd'

        if conf['OpenStdin']:
            short_options += 'i'

        if conf['Tty']:
            short_options += 't'

        if (len(short_options) > 0):
            options.append('-' + short_options)

        options.append("-h {hostname}".format(hostname=conf['Hostname']))

        if 'Binds' in hconf and isinstance(hconf['Binds'], list):
            for v in hconf['Binds']:
                options.append("-v {binds}".format(binds=v))

        if 'PortBindings' in hconf and isinstance(hconf['PortBindings'], dict):
            for k, v in hconf['PortBindings'].items():
                for hv in v:
                    portbinding = ''
                    if 'HostIp' in hv and hv['HostIp']:
                        portbinding += hv['HostIp'] + ':'
                    if 'HostPort' in hv and hv['HostPort']:
                        portbinding += hv['HostPort'] + ':'
                    portbinding += k
                    options.append("-p {portbinding}".format(portbinding=portbinding))

        if 'RestartPolicy' in hconf and hconf['RestartPolicy']['Name']:
            policy = hconf['RestartPolicy']['Name']
            if hconf['RestartPolicy']['MaximumRetryCount'] > 0:
                policy += ':' + str(hconf['RestartPolicy']['MaximumRetryCount'])
            options.append("--restart={policy}".format(policy=policy))

        for v in conf['Env']:
            options.append("-e={env}".format(env=pipes.quote(v)))

        cmd = []
        for v in conf['Cmd']:
            cmd.append(pipes.quote(v))

        print('docker run {options} {image} {cmd}'.format(
            options=sep.join(options), image=conf['Image'], cmd=sep + ' '.join(cmd)))

if __name__ == "__main__":
    main()
