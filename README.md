# VIX Auth bypass demo

This is a demonstration script to check if VIX users are capable of interacting with guest machines without required permissions.

For more details on the vulnerability, check out the post we wrote up in [LinkHere](TodoLink)

## Simple Demo
Example:

```vix.py -s 10.15.0.25 -u root -p vmware -c notepad.exe windows_server_3.vmx```

Command line options include:
* `-s`, `--host`: Remote host to connect to
* `-o`, `--port`: Port to use, default is 443
* `-u`, `--user`: User name to use when connecting to host
* `-p`, `--password`: Password to use when connecting to host. Can be ommitted and entered interactively
* `-c`, `--command`: Command to run on victim. Default exists for linux targets

Enter as a position argument the target vm name.





# Authors (of most of the code)
* [Itamar Tal](https://github.com/itamartal)
* [Oran Nadler](https://github.com/orannadler)