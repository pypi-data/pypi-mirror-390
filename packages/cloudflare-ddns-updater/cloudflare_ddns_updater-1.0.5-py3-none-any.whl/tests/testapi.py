import argparse
import json
import shutil
import sys
import requests
import logging
from getpass import getpass
from crontab import CronTab
from cloudflare_ddns_updater.constants import *
import cloudflare_ddns_updater.ip_updater


api_token = "Y1a7bhfkodq-cuRYqLUCSB61-HCn8HM8bkRHzA9N"
zone_id = "8ca4a07424856f5168a42d6703124802"
zone_name = "robgst.it"
robgst_id = "c9a058d4ccd1737a86f7497a10080e33"

url = "https://api.cloudflare.com/client/v4/zones"
headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

# Get dns record id
try:
    dns_records = f"{url}/{zone_id}/dns_records"
    response = requests.request("GET", dns_records, headers=headers)
    d = response.json()["result"]
    print(d)
    dns_record_id = "none"
    print(f"The current records for your domain {zone_name} are:")
    for i in range(len(d)):
        if d[i]["type"] == "A":
            print(f'  {d[i]["name"]}')
    print("You may choose one of the existing records or create a new one.")

    # Choose record
    correct_record = False
    while correct_record is False:
        dns_input = input(f"Insert record you want to manage [default: dns.{zone_name}]: ")
        if dns_input == "":
            # create a default record
            dns_record = f"dns.{zone_name}"
            correct_record = True
        else:
            # Check for spaces
            dns_record = dns_input.replace(" ", "")
            # Check if domain is correct and change if necessary.
            if dns_record.endswith(zone_name) is False:
                dns_record = f"{dns_record.split('.', 1)[0]}.{zone_name}"
            # ask if correct
            confirm_good = input(f"{dns_record} will be managed. Confirm? [Y/n] ").lower()

            if confirm_good == "y" or confirm_good == "":
                correct_record = True
    # User chooses an existing record
    for i in range(len(d)):
        if d[i]["name"] == dns_record and d[i]["type"] == "A":
            dns_record_id = d[i]["id"]
            print(dns_record_id)
    # User chooses a new record
    if dns_record_id == "none":
        print("dns record id is none")
    print(f"{dns_record} will be kept updated")
except Exception as e:
    print(f"Something went wrong: {e}")
    sys.exit()
