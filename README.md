This repository contains two scripts related to the VIX authentication bypass presented in Black Hat.
* vix.py - An attack script using the vulnerability.
* role_discovery.py - A risk assessment tool for vSphere environments.

For more details on the vulnerability, check out our presentation in [BlackHat 2017](https://www.blackhat.com/us-17/briefings/schedule/index.html#escalating-insider-threats-using-vmwares-api-7300).

# vix.py

This is a demonstration script for the bypass. The script checks if a given user can run arbitrary commands on a given virtual machine.

The script relies on the existence of the VIX plugin DLLs (or SO files), which can be easily downloaded from [VMWare](https://code.vmware.com/web/sdk/60/vix). 
After downloading and installing the plugin, extract the DLL files and place them in the same path as the python file.

## Usage
Example execution

```vix.py -s 10.15.0.25 -u root -p vmware -c notepad.exe windows_server_3.vmx```

Command line flags:
* `-s`, `--host`: Remote vSphere or ESXi host
* `-u`, `--user`: User name to use when connecting to host
* `-p`, `--password`: Password to use when connecting to host, can omit and enter from stdin
* `-c`, `--command`: Command to run on victim. Default exists for linux creates a file under /tmp

As a final argument, pass in the target vm name.

## Authors (of most of the code)
* [Itamar Tal](https://github.com/itamartal)
* [Oran Nadler](https://github.com/orannadler)


# role_discovery.py

This is a risk assessment tool to check which virtual machines in a vSphere environment are vulnerable to this attack.
The tool checks for each VM if it's running on a vulnerable host or running vulnerable versions of VMWare tools.

In addition, the script reports if there are non administrator users with the appropriate privileges to execute the attack, given a vulnerable machine.


## Usage
Example usage

```role_discovery.py -c 192.168.13.37 -u administrator@vsphere.local -p Password1!```

Command line flags:
* `-c`, `--host`: Remote vSphere or ESXi host
* `-u`, `--user`: User name to use when connecting to host
* `-p`, `--password`: Password to use when connecting to host, can omit and enter from stdin
