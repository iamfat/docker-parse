#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import yaml
import subprocess
import sys
import pipes
import getopt
from pprint import pprint

def docker_inspect(container, image=False):
    try:
        cmd = ["docker", "inspect"]
        if image:
            cmd.extend(["--type=image"])
        cmd.extend([container])
        output = subprocess.check_output(cmd, universal_newlines=True)
        infos = json.loads(output, encoding='utf-8')
        return infos[0]
    except subprocess.CalledProcessError as e:
        sys.exit()

def output_compose(info, image_info):
    container = info['Name'][1:]
    conf = info['Config']
    hconf = info['HostConfig']

    compose = {}
    compose['container_name'] = str(container)
    compose['image'] = str(conf['Image'])

    # Volumes
    if 'Binds' in hconf and isinstance(hconf['Binds'], list):
        options = []
        for v in hconf['Binds']:
            options.append(str(v))
        if len(options) > 0: compose['volumes'] = options

    if 'PortBindings' in hconf and isinstance(hconf['PortBindings'], dict):
        options = []
        for k, v in hconf['PortBindings'].items():
            for hv in v:
                portbinding = ''
                if 'HostIp' in hv and hv['HostIp']:
                    portbinding += hv['HostIp'] + ':'
                if 'HostPort' in hv and hv['HostPort']:
                    portbinding += hv['HostPort'] + ':'
                portbinding += k
                options.append(str(portbinding))
        if len(options) > 0: compose['ports'] = options

    # RestartPolicy
    if 'RestartPolicy' in hconf and hconf['RestartPolicy']['Name']:
        policy = hconf['RestartPolicy']['Name']
        if hconf['RestartPolicy']['MaximumRetryCount'] > 0:
            policy += ':' + str(hconf['RestartPolicy']['MaximumRetryCount'])
        compose['restart'] = str(policy)

    # Privileged
    if hconf['Privileged']:
        compose['privileged'] = true

    # Env
    if type(conf['Env']) is list and len(conf['Env']) > 0:
        options = []
        for v in conf['Env']:
            if v not in image_info['Config']['Env']:
                options.append(str(v))
        if len(options) > 0:compose['env'] = options

    # DNS
    if 'Dns' in hconf and isinstance(hconf['Dns'], list):
        options = []
        for dns in hconf['Dns']:
            compose['dns'].append(str(dns))
        if len(options) > 0:compose['dns'] = options
    # ExposedPorts
    if 'ExposedPorts' in conf and isinstance(conf['ExposedPorts'], dict):
        for port,foo in conf['ExposedPorts'].items():
            if port not in image_info['Config']['ExposedPorts']:
                options.append("--expose={port}".format(port=port))

    name = str(info['Name'][1:])
    print(yaml.dump({ name : compose }, encoding='utf-8', default_flow_style=False))

def output_command(info, image_info, pretty=False):

    sep = pretty and ' \\\n    ' or ' '

    short_options = ''
    options = []

    container = info['Name'][1:]
    conf = info['Config']
    hconf = info['HostConfig']

    options.append("--name {name}".format(name=container))

    if not conf['AttachStdout']:
        short_options += 'd'

    if conf['OpenStdin']:
        short_options += 'i'

    if conf['Tty']:
        short_options += 't'

    if (len(short_options) > 0):
        options.append('-' + short_options)

    options.append("-h {hostname}".format(hostname=conf['Hostname']))

    # Volumes
    if 'Binds' in hconf and isinstance(hconf['Binds'], list):
        for v in hconf['Binds']:
            options.append("-v {binds}".format(binds=v))

    # PortBindings
    if 'PortBindings' in hconf and isinstance(hconf['PortBindings'], dict):
        for k, v in hconf['PortBindings'].items():
            for hv in v:
                portbinding = ''
                if 'HostIp' in hv and hv['HostIp']:
                    portbinding += hv['HostIp'] + ':'
                if 'HostPort' in hv and hv['HostPort']:
                    portbinding += hv['HostPort'] + ':'
                portbinding += k
                options.append("-p={portbinding}".format(portbinding=portbinding))

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
        for port,foo in conf['ExposedPorts'].items():
            if port not in image_info['Config']['ExposedPorts']:
                options.append("--expose={port}".format(port=port))

    # Env
    if type(conf['Env']) is list :
        for v in conf['Env']:
            if v not in image_info['Config']['Env']:
                options.append("-e={env}".format(env=pipes.quote(v)))

    # EntryPoint
    entry = []
    if type(conf['Entrypoint']) is list :
        for v in conf['Entrypoint']:
            if v not in image_info['Config']['Entrypoint']:
                entry.append(pipes.quote(v))
    elif type(conf['Entrypoint']) is str :
        if conf['Entrypoint'] != image_info['Config']['Entrypoint']:
            entry.append(pipes.quote(conf['Entrypoint']))

    if (len(entry) > 0):
        options.append("--entrypoint={entry}".format(entry=' '.join(entry)))

    # WorkingDir
    if image_info['Config']['WorkingDir'] != conf['WorkingDir']:
        options.append("-w={dir}".format(dir=pipes.quote(conf['WorkingDir'])))

    # Cmd
    cmd = []
    if conf['Cmd'] != image_info['Config']['Cmd']:
        if type(conf['Cmd']) is list :
            for v in conf['Cmd']:
                cmd.append(pipes.quote(v))
        elif type(conf['Cmd']) is str:
            cmd.append(pipes.quote(conf['Cmd']))

    print('# docker-run command for {container}'.format(container=container))
    cmd_str = 'docker run{sep}{options}{sep}{image}'.format(
        options=sep.join(options), sep=sep, image=conf['Image'])
    
    if (len(cmd) > 0):
        cmd_str += ' '.join(cmd)
        
    print(cmd_str)
    print()


def main():

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "pc", ["pretty", "compose"])
    except getopt.GetoptError as e:
        print("Usage: docker-parse [--pretty|-p|--compose|-c] <container>")
        sys.exit(2)

    if len(args) == 0:
        # enumerate all containers via `docker ps`
        try:
            containers = subprocess.check_output("docker ps -q", shell=True).splitlines()
            def readable_name(container):
                try:
                    return subprocess.check_output(
                                "docker inspect -f {{.Name}} %s" % container,
                                shell=True).lstrip('/').rstrip('\n')
                except subprocess.CalledProcessError as e:
                    return container
            containers = map(readable_name, containers)
        except subprocess.CalledProcessError as e:
            print ("%r" % str(e))
            sys.exit()
    else:
        containers = args

    as_compose = False
    pretty = False
    for o, a in opts:
        if o == '-p' or o == '--pretty':
            pretty = True
            break
        elif o == '-c' or o == '--compose':
            as_compose = True
            break

    for container in containers:

        info = docker_inspect(container)

        # diff with image info to reduce information
        image_info = docker_inspect(info['Config']['Image'])

        if as_compose:
            output_compose(info, image_info)
        else:
            output_command(info, image_info, pretty)

if __name__ == "__main__":
    main()
