import pan.xapi
import xmltodict
from getpass import getpass
import json
from datetime import datetime

class NGFirewall:

    def __init__(self,hostname,username,password):

        self.hostname = hostname
        self.xapi = pan.xapi.PanXapi(hostname=hostname, api_username=username, api_password=password)
        self.check_time = datetime.now()

        #ipsec info
        self.ipsec_name = set()
        self.down_ipsec = set()
        self.up_ipsec = set()

        #virtual-router info
        self.all_routes = {}
        self.virtual_routers = {}

        #run commands
        self.parse_ipsec()
        self.parse_routes()

    def parse_ipsec(self):

        self.xapi.op(cmd="<show><vpn><flow></flow></vpn></show>")
        xml = self.xapi.xml_result()
        tun = xmltodict.parse("<root>" + xml + "</root>")

        proxy_tunnel = {}

        #sort out the non-proxy tunnels
        for entry in tun['root']['IPSec']['entry']:

            if ':' not in entry['name']:
                self.ipsec_name.add(entry['name'])
                if entry['state'] == 'active':
                    self.up_ipsec.add(entry['name'])
                else:
                    self.down_ipsec.add(entry['name'])
            else:
                real_name = entry['name'].split(':')[0]
                self.ipsec_name.add(real_name)

                if real_name not in proxy_tunnel:
                    proxy_tunnel[real_name] = []

                proxy_tunnel[real_name].append(entry['state'])

        for pt in proxy_tunnel:
            if 'active' in proxy_tunnel[pt]:
                self.up_ipsec.add(pt)
            else:
                self.down_ipsec.add(pt)

    def parse_routes(self):

        self.xapi.op(cmd="<show><routing><summary></summary></routing></show>")
        output = xmltodict.parse("<root>" + self.xapi.xml_result() + "</root>")

        for o in output['root']['entry']:
            if 'All-Routes' in o:
                self.all_routes = o
            else:
                self.virtual_routers[o['@name']] = {}
                if 'bgp' in o:
                    self.virtual_routers[o['@name']]['bgp'] = o['bgp']
                    self.virtual_routers[o['@name']]['bgp']['peers'] = {}

        self.xapi.op(cmd="<show><routing><protocol><bgp><peer></peer></bgp></protocol></routing></show>")
        output = xmltodict.parse("<root>" + self.xapi.xml_result() + "</root>")

        for o in output['root']['entry']:
            peer_name = o['@peer']
            vr = o['@vr']
            self.virtual_routers[vr]['bgp']['peers'][peer_name] = {}
            self.virtual_routers[vr]['bgp']['peers'][peer_name]['status'] = o['status']
            try:
                prefix = o['prefix-counter']['entry']
                del prefix['@afi-safi']
                self.virtual_routers[vr]['bgp']['peers'][peer_name]['prefix_stats'] = prefix
            except:
                pass

    def print_json_output(self):

        json_output = {}
        json_output['hostname'] = self.hostname
        json_output['ipsec_names'] = list(self.ipsec_name)
        json_output['up_ipsec'] = list(self.up_ipsec)
        json_output['down_ipsec'] = list(self.down_ipsec)
        json_output['all_routes'] = self.all_routes
        json_output['virtual_routers'] = self.virtual_routers

        with open(f"{self.hostname}_output.json","w") as file:
            file.write(json.dumps(json_output))

    def json_output(self):

        json_output = {}
        json_output['hostname'] = self.hostname
        json_output['ipsec_names'] = list(self.ipsec_name)
        json_output['up_ipsec'] = list(self.up_ipsec)
        json_output['down_ipsec'] = list(self.down_ipsec)
        json_output['all_routes'] = self.all_routes
        json_output['virtual_routers'] = self.virtual_routers

        return json_output
def main():

    hostname = input("NGFW Hostname:")
    username = input("Username:")
    password = getpass("Password:")
    
    line = []
    
    firewall = NGFirewall(hostname=hostname,username=username,password=password)
    check_time = firewall.check_time.strftime("%Y-%m-%d %H:%M")
    line.append(f"{firewall.hostname} - SYSTEM CHECKS @{check_time}")
    #IPSEC information
    line.append("==================")
    line.append("IPSEC TUNNEL SUMMARY")
    line.append(f"Total Tunnels: {len(firewall.ipsec_name)}")
    line.append(f"Tunnels Up: {len(firewall.up_ipsec)}")
    line.append(f"Tunnels Down: {len(firewall.down_ipsec)}")
    line.append("")
    line.append("==================")

    #Total Routes information
    line.append("ROUTES SUMMARY SUMMARY")
    line.append(f"Total Routes: {firewall.all_routes['All-Routes']['total']}")
    line.append(f"Active Routes: {firewall.all_routes['All-Routes']['active']}")
    line.append("")
    line.append(f"Static Routes: {firewall.all_routes['Static-Routes']['total']}")
    line.append(f"Connect Routes: {firewall.all_routes['Connect-Routes']['total']}")
    line.append(f"BGP Routes: {firewall.all_routes['BGP-Routes']['total']}")
    line.append("")
    line.append("==================")

    #virtual router information
    line.append("VIRTUAL ROUTERS\n")
    for vr in firewall.virtual_routers:
        line.append(f"VIRTUAL ROUTER: {vr}")
        line.append("    ==================")
        if 'bgp' in firewall.virtual_routers[vr]:
            line.append(f"    BGP")
            line.append(f"    PEERS:")
            for peer in firewall.virtual_routers[vr]['bgp']['peers']:
                status = firewall.virtual_routers[vr]['bgp']['peers'][peer]['status']
                line.append(f"        {peer} -- {status}")
                if 'prefix_stats' in firewall.virtual_routers[vr]['bgp']['peers'][peer]:
                    line.append(f"        PREFIX STATUS")
                    for ps in firewall.virtual_routers[vr]['bgp']['peers'][peer]['prefix_stats']:
                        stat = firewall.virtual_routers[vr]['bgp']['peers'][peer]['prefix_stats'][ps]
                        line.append(f"            {ps}: {stat}")
        line.append("\n")

    print("\n".join(line))

    file_time = firewall.check_time.strftime("%Y-%m-%d_%H-%M")

    with open(f"{firewall.hostname}_cli_output_{file_time}.txt","w") as file:
        file.write("\n".join(line))

    print(f"CLI output can be found in {firewall.hostname}_cli_output_{file_time}.txt")

    with open(f"{firewall.hostname}_json_output_{file_time}.json","w") as file:
        file.write(json.dumps(firewall.json_output()))

    print(f"JSON output can be found in {firewall.hostname}_json_output_{file_time}.json")

if __name__ == '__main__':
    main()