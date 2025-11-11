# sc-napalm

This repo is for building custom [NAPALM](https://napalm.readthedocs.io/en/latest/) "getters" to pull operational data from network devices, as well as
override existing NAPALM getters with custom code if needed. At the moment only one custom getter is implemented: `get_inventory`. This getter
pulls model and serial numbers of device components: fans, psus, and optics.

What's cool about NAPALM is that if you nest your custom drivers under `custom_napalm` as is done in this project, you can install your custom drivers
in the same virtual environment as the main NAPALM package, and they will override NAPALM's core drivers. This allows us to leverage NAPALM in a pretty 
seamless way - by that I mean applications that leverage NAPALM (like Nautobot or Nornir) can be easily altered to use this code instead.

Right now, the following platforms are supported:
* eos
* iosxr (via netconf)
* junos
* nos (Drivenets)
* nxos
* srl (Nokia SR Linux)
* sros


## Using sc-napalm
The package comes with a cli script called `sc-napalm-get` that will run a particular getter against a particular device and output the results
to your terminal.

To use the script, you can install the package from pypi, ideally into a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
pip install sc-napalm
```
Now that you've done this you can run `sc-napalm-get` from your venv. Note that you must either provide your credentials
directly to the script, or set them as environment variables `SC_USERNAME` and `SC_PASSWORD`. Run it with `--help` to see all the
various options.
```
(venv) aliebowitz@sysauto:~$ export SC_USERNAME=nso
(venv) aliebowitz@sysauto:~$ export SC_PASSWORD=<redacted>
(venv) aliebowitz@sysauto:~$ sc-napalm-get --help
usage: sc-napalm-get [-h] [--ssh-cfg SSH_CFG] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL} | -L {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--logfile LOGFILE] [--sc_username SC_USERNAME]
                     [--sc_password SC_PASSWORD]
                     device {iosxr,nxos,junos,sros,srl,eos,nos} {get_config,get_facts,get_optics,get_lldp_neighbors,get_inventory}

Run a specific sc_napalm "getter" against a device.

positional arguments:
  device                device hostname or IP address
  {iosxr,nxos,junos,sros,srl,eos,nos}
                        The platform of this device
  {get_config,get_facts,get_optics,get_lldp_neighbors,get_inventory}
                        The getter command to run against this device

options:
  -h, --help            show this help message and exit
  --ssh-cfg SSH_CFG     Use SSH config file to connect
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set log level for sc_napalm only
  -L {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --LOG-LEVEL {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        set global log level
  --logfile LOGFILE     Save logging to a file (specified by name) instead of to stdout
  --sc_username SC_USERNAME
                        Specify credentials
  --sc_password SC_PASSWORD
                        Specify credentials
(venv) aliebowitz@sysauto:~$ sc-napalm-get 2001:468:1f07:ff19::1d eos get_inventory
[{'name': 'Ethernet45',
  'part_number': 'QSFP-100G-LR4',
  'serial_number': 'XYL252206819',
  'subtype': 'QSFP-100G-LR4',
  'type': 'optic'},
 {'name': 'Ethernet46',
  'part_number': 'QSFP-100G-LR4',
  'serial_number': 'XYL252206822',
  'subtype': 'QSFP-100G-LR4',
  'type': 'optic'},
 {'name': 'PSU 1',
  'part_number': 'PWR-511-AC-RED',
  'serial_number': 'EEWT2420216960',
  'subtype': None,
  'type': 'psu'},
  ...
```

## Developing sc-napalm
Currently, the getters that are exposed as options in the `get` script are defined in the [base class](https://scinet.supercomputing.org:8443/automation/sc25/sc-napalm/-/blob/main/src/custom_napalm/base.py?ref_type=heads) of the custom drivers.
Note that because most of the custom classes inherit the NAPALM getters, we could easily define all the other NAPALM getters there, but I've only included ones I think are obviously useful to us.

My hope is that instead of just printing out results we can write code that saves data in Nautobot, or some other place.
This could be done with Nornir or Nautobot jobs.

## To-dos
* `get_inventory` methods for sros
* Test/mock classes for custom getters

