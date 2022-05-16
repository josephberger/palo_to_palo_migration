import argparse
import sys
import json

def main():

    args = get_inputs()

    if args.f:
        file1 = args.f
    else:
        print("argument for first file (-f) required")
        sys.exit(1)

    if args.s:
        file2 = args.s
    else:
        print("argument for second file (-s) required")
        sys.exit(1)

    try:
        with open(file1,"r") as file:
            sys_check1 = json.loads(file.read())

        with open(file2, "r") as file:
            sys_check2 = json.loads(file.read())
    except Exception as e:
        print(f"error encountered opening the files: {e}")

    line= []

    hostname1 = sys_check1['hostname']
    hostname2 = sys_check2['hostname']

    #Total Routes
    if sys_check1['all_routes']["All-Routes"]['total'] != sys_check2['all_routes']["All-Routes"]['total']:
        sc1 = int(sys_check1['all_routes']["All-Routes"]['total'])
        sc2 = int(sys_check2['all_routes']["All-Routes"]['total'])
        total_missing = abs(sc1-sc2)
        line.append("ALL-ROUTES DIFFERENT")
        line.append("==================")
        line.append(f"{hostname1}: {sc1}")
        line.append(f"{hostname2}: {sc2}")
        line.append(f"Difference by {total_missing}")
        line.append("")

    #Active Routes
    if sys_check1['all_routes']["All-Routes"]['active'] != sys_check2['all_routes']["All-Routes"]['active']:
        sc1 = int(sys_check1['all_routes']["All-Routes"]['active'])
        sc2 = int(sys_check2['all_routes']["All-Routes"]['active'])
        total_missing = abs(sc1-sc2)
        line.append("ACTIVE-ROUTES DIFFERENT")
        line.append("==================")
        line.append(f"{hostname1}: {sc1}")
        line.append(f"{hostname2}: {sc2}")
        line.append(f"Difference by {total_missing}")
        line.append("")

    #Static Routes
    if sys_check1['all_routes']["Static-Routes"]['total'] != sys_check2['all_routes']["Static-Routes"]['total']:
        sc1 = int(sys_check1['all_routes']["Static-Routes"]['total'])
        sc2 = int(sys_check2['all_routes']["Static-Routes"]['total'])
        total_missing = abs(sc1-sc2)
        line.append("STATIC-ROUTES DIFFERENT")
        line.append("==================")
        line.append(f"{hostname1}: {sc1}")
        line.append(f"{hostname2}: {sc2}")
        line.append(f"Difference by {total_missing}")
        line.append("")

    #Connected Routes
    if sys_check1['all_routes']["Connect-Routes"]['total'] != sys_check2['all_routes']["Connect-Routes"]['total']:
        sc1 = int(sys_check1['all_routes']["Connect-Routes"]['total'])
        sc2 = int(sys_check2['all_routes']["Connect-Routes"]['total'])
        total_missing = abs(sc1-sc2)
        line.append("CONNECT-ROUTES DIFFERENT")
        line.append("==================")
        line.append(f"{hostname1}: {sc1}")
        line.append(f"{hostname2}: {sc2}")
        line.append(f"Difference by {total_missing}")
        line.append("")

    skip_vrs = set()

    "Virtual Routers"
    for vr in sys_check1['virtual_routers']:
        if vr in sys_check2['virtual_routers']:
            if 'bgp' in sys_check1['virtual_routers'][vr]:
                for peer in sys_check1['virtual_routers'][vr]['bgp']['peers']:
                    if peer in sys_check2['virtual_routers'][vr]['bgp']['peers']:
                        status1 = sys_check1['virtual_routers'][vr]['bgp']['peers'][peer]['status']
                        status2 = sys_check2['virtual_routers'][vr]['bgp']['peers'][peer]['status']
                        if status1 != status2:
                            line.append(f"VR {vr} PEER {peer} DIFFERENT")
                            line.append(f"{hostname1}: {status1}")
                            line.append(f"{hostname2}: {status2}")
                            line.append("")

        else:
            line.append(f"VIRTUAL ROUTER {vr} MISSING FROM {hostname2}!  Skipping...")
            skip_vrs.add(vr)

    print("\n".join(line))


    with open(f"{hostname1}_{hostname2}_diff.txt", "w") as file:
        file.write("\n".join(line))

    print(f"Output can be found in {hostname1}_{hostname2}_diff.txt")

def get_inputs():
    """
    Argparser
    """
    parser = argparse.ArgumentParser(
        description="system check json diff",
        epilog="Example usgae:\n python3 diff.py -f {hostname1}.json -s file2.json",
    )

    parser.add_argument(
        "-f",
        "--first-file",
        help="first json file to diff",
        action="store",
        dest="f",
    )

    parser.add_argument(
        "-s",
        "--second-file",
        help="second json file to diff",
        action="store",
        dest="s",
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()