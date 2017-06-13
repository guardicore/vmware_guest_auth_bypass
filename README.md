# VIX Auth bypass demo

This is a demonstration script to check if VIX users are capable of interacting with guest machines without required permissions.

For more details on the vulnerability, check out the post we wrote up in [LinkHere](TodoLink)

## Simple Demo
Example:

```vix.py -s [target_ip] -u root -p password -c notepad.exe windows_demo_server```

Command line options include:
* `-s`, `--host`: Remote host to connect to
* `-o`, `--port`: Port to use, default is 443
* `-u`, `--user`: User name to use when connecting to host
* `-p`, `--password`: Password to use when connecting to host. Can be ommitted and entered interactively
* `-c`, `--command`: Command to run on victim. Default exists for linux targets

Enter as a position argument the target vm name.

## Setup
In order to run the vulnerability, vix.dll or libvixAllProducts.so must be available in the load path.

On Windows this has been tested using vix.dll 1.13.2.


# Authors (of most of the code)
* [Itamar Tal](https://github.com/itamartal)
* [Oran Nadler](https://github.com/orannadler)