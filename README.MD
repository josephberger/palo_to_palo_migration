# Palo to Palo Migration System Checks

Simple script to pull information about virtual routers, routes, IPSEC tunnels and BGP Peers (put together specifically to system check a Palo Alto Networks NGFW against another for a 1:1 migration).  Please do not report problems, this will never be updated.

First run system_check.py on the old firewall PRIOR to shutdown/interface turn down to get a current state.  After the migration has completed, run system_check.py against the new firewall.  The output in the CLI output file is easy to read but if a lot of VRs and BGP peers exist; use the diff for a quick look.  Please note that this will not FIX anything it is a simple script to get the technician/engineer going in the right direction.

## Installation

Create and activate the python virtual environment (mac/linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

```bash
(venv)python3 system_check.py
NGFW Hostname: somehostname.acme.com
Username: Username
Password: *********

**EXAMPLE OUTPUT***

CLI output can be found in hostname_cli_output_1969-01-01_01-01.txt
JSON output can be found in hostname_json_output_1969-01-01_01-01.json
```
This will provide two files:

hostname_cli_output_date_time.txt - this is the same output that is provided by the program.

hostname_json_output_date_time.json - this is similar data but in json format (used for diff)

```bash
(venv)python3 diff.py -f file_from_first_firewall.json -s file_from_second_firewall.json

**EXAMPLE OUTPUT***

CONNECT-ROUTES DIFFERENT
==================
Hostname1: 243
Hostname2: 241
Difference by 2

VR INTERNET-EDGE PEER eth2.456 DIFFERENT
Hostname1: Established
Hostname2: Connect

Output can be found in hostname1_hostname2_diff.txt
```

This will provide differences for all routes, static routes, connect routes, bgp routes and a difference in BGP peer status.  Note that it only provides output from differences and nothing will be provided for things that are the same.


