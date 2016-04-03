#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
docker-parse is a useful command to get
docker-run commands or docker-compose configurations from running containers
'''

from __future__ import absolute_import
from __future__ import print_function

import sys
import pipes
import getopt

import yaml
from docker import Client

__version__ = '0.5.2'

def output_compose(info, image_info):
    '''output as docker-compose format'''

    container = info['Name'][1:]

    conf = info['Config']
    hconf = info['HostConfig']

    compose = {}
    compose['container_name'] = str(container)
    compose['image'] = str(conf['Image'])

    # Volumes
    if 'Binds' in hconf and isinstance(hconf['Binds'], list):
        options = []
        for volume in hconf['Binds']:
            options.append(str(volume))
        if len(options) > 0:
            compose['volumes'] = options

    if 'PortBindings' in hconf and isinstance(hconf['PortBindings'], dict):
        options = []
        for binding, hosts in hconf['PortBindings'].items():
            for host in hosts:
                portbinding = ''
                if 'HostIp' in host and host['HostIp']:
                    portbinding += host['HostIp'] + ':'
                if 'HostPort' in host and host['HostPort']:
                    portbinding += host['HostPort'] + ':'
                portbinding += binding
                options.append(str(portbinding))
        if len(options) > 0:
            compose['ports'] = options

    # Devices
    if 'Devices' in hconf and isinstance(hconf['Devices'], list):
        options = []
        for device in hconf['Devices']:
            options.append(str(device))
        if len(options) > 0:
            compose['devices'] = options

    # RestartPolicy
    if 'RestartPolicy' in hconf and hconf['RestartPolicy']['Name']:
        policy = hconf['RestartPolicy']['Name']
        if hconf['RestartPolicy']['MaximumRetryCount'] > 0:
            policy += ':' + str(hconf['RestartPolicy']['MaximumRetryCount'])
        compose['restart'] = str(policy)

    # Privileged
    if hconf['Privileged']:
        compose['privileged'] = True

    # Env
    if isinstance(conf['Env'], list) and len(conf['Env']) > 0:
        options = []
        for env in conf['Env']:
            if env not in image_info['Config']['Env']:
                options.append(str(env))
        if len(options) > 0:
            compose['environment'] = options

    # DNS
    if 'Dns' in hconf and isinstance(hconf['Dns'], list):
        options = []
        for dns in hconf['Dns']:
            options.append(str(dns))
        if len(options) > 0:
            compose['dns'] = options

    # ExposedPorts
    if 'ExposedPorts' in conf and isinstance(conf['ExposedPorts'], dict):
        options = []
        for port, _ in conf['ExposedPorts'].items():
            if ('ExposedPorts' not in image_info['Config'] or
                    port not in image_info['Config']['ExposedPorts']):
                options.append(str(port))
        if len(options) > 0:
            compose['expose'] = options

    # User
    if conf['User'] and image_info['Config']['User'] != conf['User']:
        compose['user'] = str(conf['User'])

    # WorkingDir
    if image_info['Config']['WorkingDir'] != conf['WorkingDir']:
        compose['working_dir'] = str(conf['WorkingDir'])

    # EntryPoint
    if conf['Entrypoint'] != image_info['Config']['Entrypoint']:
        if isinstance(conf['Entrypoint'], list):
            entry = []
            for entry_item in conf['Entrypoint']:
                entry.append(str(entry_item))
            if len(entry) > 0:
                compose['entrypoint'] = entry
        elif isinstance(conf['Entrypoint'], str):
            compose['entrypoint'] = str(conf['Entrypoint'])

    name = str(info['Name'][1:])
    print(yaml.dump({name:compose}, encoding='utf-8', default_flow_style=False))

def output_command(info, image_info, pretty=False):
    '''output as docker-run command format'''

    sep = pretty and ' \\\n    ' or ' '

    short_options = ''
    options = []

    container = info['Name'][1:]
    conf = info['Config']
    hconf = info['HostConfig']

    options.append("--name={name}".format(name=container))

    if not conf['AttachStdout']:
        short_options += 'd'

    if conf['OpenStdin']:
        short_options += 'i'

    if conf['Tty']:
        short_options += 't'

    if len(short_options) > 0:
        options.append('-' + short_options)

    options.append("-h {hostname}".format(hostname=conf['Hostname']))

    # Volumes
    if 'Binds' in hconf and isinstance(hconf['Binds'], list):
        for volume in hconf['Binds']:
            options.append("-v {volume}".format(volume=volume))

    # PortBindings
    if 'PortBindings' in hconf and isinstance(hconf['PortBindings'], dict):
        for port, hosts in hconf['PortBindings'].items():
            for host in hosts:
                portbinding = ''
                if 'HostIp' in host and host['HostIp']:
                    portbinding += host['HostIp'] + ':'
                if 'HostPort' in host and host['HostPort']:
                    portbinding += host['HostPort'] + ':'
                portbinding += port
                options.append("-p {portbinding}".format(portbinding=portbinding))

    # Devices
    if 'Devices' in hconf and isinstance(hconf['Devices'], list):
        for device in hconf['Devices']:
            options.append("--device={device}".format(device=device))

    # RestartPolicy
    if 'RestartPolicy' in hconf and hconf['RestartPolicy']['Name']:
        policy = hconf['RestartPolicy']['Name']
        if hconf['RestartPolicy']['MaximumRetryCount'] > 0:
            policy += ':' + str(hconf['RestartPolicy']['MaximumRetryCount'])
        options.append("--restart={policy}".format(policy=policy))

    # Privileged
    if hconf['Privileged']:
        options.append('--privileged')

    # DNS
    if 'Dns' in hconf and isinstance(hconf['Dns'], list):
        for dns in hconf['Dns']:
            options.append("-dns={dns}".format(dns=dns))

    # ExposedPorts
    if 'ExposedPorts' in conf and isinstance(conf['ExposedPorts'], dict):
        for port, _ in conf['ExposedPorts'].items():
            if ('ExposedPorts' not in image_info['Config'] or
                    port not in image_info['Config']['ExposedPorts']):
                options.append("--expose={port}".format(port=port))

    # Env
    if isinstance(conf['Env'], list):
        for env in conf['Env']:
            if env not in image_info['Config']['Env']:
                options.append("-e {env}".format(env=pipes.quote(env)))

    # EntryPoint
    if conf['Entrypoint'] != image_info['Config']['Entrypoint']:
        entry = []
        if isinstance(conf['Entrypoint'], list):
            for entry_item in conf['Entrypoint']:
                entry.append(pipes.quote(entry_item))
        elif isinstance(conf['Entrypoint'], str):
            entry.append(pipes.quote(conf['Entrypoint']))
        if len(entry) > 0:
            options.append("--entrypoint={entry}".format(entry=pipes.quote(' '.join(entry))))

    # WorkingDir
    if image_info['Config']['WorkingDir'] != conf['WorkingDir']:
        options.append("-w {dir}".format(dir=pipes.quote(conf['WorkingDir'])))

    # User
    if conf['User'] and image_info['Config']['User'] != conf['User']:
        options.append("-u {user}".format(user=pipes.quote(conf['User'])))

    # Cmd
    cmd = []
    if conf['Cmd'] != image_info['Config']['Cmd']:
        if isinstance(conf['Cmd'], list):
            for cmd_item in conf['Cmd']:
                cmd.append(pipes.quote(cmd_item))
        elif isinstance(conf['Cmd'], str):
            cmd.append(pipes.quote(conf['Cmd']))

    print('# docker-run command for {container}'.format(container=container))
    cmd_str = 'docker run{sep}{options}{sep}{image}'.format(
        options=sep.join(options), sep=sep, image=conf['Image'])

    if len(cmd) > 0:
        cmd_str += ' '.join(cmd)

    print(cmd_str)
    print()


def main():
    '''main entry'''

    cli = Client()

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "pcv", ["pretty", "compose"])
    except getopt.GetoptError as _:
        print("Usage: docker-parse [--pretty|-p|--compose|-c] [containers]")
        sys.exit(2)

    if len(args) == 0:
        containers = map(lambda c: c['Names'][0][1:], cli.containers())
    else:
        containers = args

    as_compose = False
    pretty = False
    for opt, _ in opts:
        if opt == '-v':
            print(__version__)
            sys.exit()
        elif opt == '-p' or opt == '--pretty':
            pretty = True
            break
        elif opt == '-c' or opt == '--compose':
            as_compose = True
            break

    for container in containers:

        info = cli.inspect_container(container)

        # diff with image info to reduce information
        image_info = cli.inspect_image(info['Config']['Image'])

        if as_compose:
            output_compose(info, image_info)
        else:
            output_command(info, image_info, pretty)

if __name__ == "__main__":
    main()

