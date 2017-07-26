# VIX Auth bypass demo

This is a demonstration script for the VIX authentication bypass. The script checks if a given user can run arbitrary commands on a given virtual machine.

For more details on the vulnerability, check out our presentation in [BlackHat 2017](https://www.blackhat.com/us-17/briefings/schedule/index.html#escalating-insider-threats-using-vmwares-api-7300).

## Usage
Example execution

```vix.py -s 10.15.0.25 -u root -p vmware -c notepad.exe windows_server_3.vmx```

Command line flags:
* `-s`, `--host`: Remote vSphere or ESXi host
* `-u`, `--user`: User name to use when connecting to host
* `-p`, `--password`: Password to use when connecting to host, can omit and enter from stdin
* `-c`, `--command`: Command to run on victim. Default exists for linux creates a file under /tmp

As a final argument, pass in the target vm name.


# Authors (of most of the code)
* [Itamar Tal](https://github.com/itamartal)
* [Oran Nadler](https://github.com/orannadler)
