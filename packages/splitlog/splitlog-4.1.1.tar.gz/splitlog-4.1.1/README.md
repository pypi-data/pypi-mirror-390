splitlog
========
 
Hadoop Yarn application logs aggregate all container logs of a Yarn application into a single file. This makes it very
difficult to use Unix command line tools to analyze these logs: Grep will search over all containers and context
provided for hits often does not include Yarn container name or host name. `splitlog` splits a combined logfile for all
containers of an application into a file system hierarchy suitable for further analysis:

```
out
└── hadoopnode
    ├── container_1671326373437_0001_01_000001
    │   ├── directory.info
    │   ├── launch_container.sh
    │   ├── prelaunch.err
    │   ├── prelaunch.out
    │   ├── stderr
    │   ├── stdout
    │   └── syslog
    ├── container_1671326373437_0001_01_000002
    │   ├── directory.info
    │   ├── launch_container.sh
    │   ├── prelaunch.err
    │   ├── prelaunch.out
    │   ├── stderr
    │   ├── stdout
    │   └── syslog
    └── container_1671326373437_0001_01_000003
        ├── directory.info
        ├── launch_container.sh
        ├── prelaunch.err
        ├── prelaunch.out
        ├── stderr
        ├── stdout
        └── syslog

4 directories, 21 files
```
 
Installation
------------
Python 3.11+ must be available. Installation via [pipx](https://pypi.org/project/pipx/):

```shell script
pipx install splitlog
```
 
How to use
----------

Read logs from standard input:
```shell script
yarn logs -applicationId application_1582815261257_232080 | splitlog
```

Read logs from file `application_1582815261257_232080.log`:
```shell script
splitlog -i application_1582815261257_232080.log
```
