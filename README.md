# docker-parse

一个简单的解析docker已有配置, 反推当时的docker run命令的程序... 写得很片面... 就是根据自己可能用到的命令做的..
再加上Python初学.. 只是实现了基本功能, docker-run的参数好多啊... 以后有空再慢慢改进

```bash
sudo pip install docker-parse

## export docker-run command
```bash
docker-parse [container]
docker -p|--pretty [container]
```

## export docker-compose yaml
```bash
docker-parse [container]
docker -c|--compose [container]
```

## TODO
* ~~Foreground or Detached (`-d`)~~
* Container Identification
    * ~~Name (`--name`)~~
    * PID equivalent (`--cidfile=""`)
* PID Settings (`--pid=""`)
* IPC Settings (`--ipc=""`)
* Network settings
    * ~~`--dns=[]`~~
    * `--net="bridge"`
    * `--add-host=""`
    * `--mac-address=""`
* ~~Restart policies (`--restart`)~~
* Clean up (`--rm`)
* Runtime constraints on CPU and memory
    * `-m=""`
    * `-c=0`
* Runtime privilege, Linux capabilities, and LXC configuration
    * `--cap-add`
    * `--cap-drop`
    * ~~`--privileged=false`~~
    * ~~`--device=[]`~~
    * `--lxc-conf=[]`
* Overriding Dockerfile image defaults
    * ~~CMD (Default Command or Options)~~
    * ~~`--entrypoint=""`~~
    * ~~`--expose=[]`~~
    * `-P=false`
    * ~~`-p=[]`~~
    * `--link=""`
    * ~~ENV (environment variables) (`-e`)~~
    * ~~`-h`~~
    * ~~`-v=[]`~~
    * `--volumes-from=""`
    * ~~`-u=""`~~
    * ~~`-w=""`~~
