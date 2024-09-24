
import subprocess
import argparse
import re
import random
import logging
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

# Fancy ASCII art

ascii_art = """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⢼⡛⠛⢛⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷⠀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣿⣀⣿⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠞⠉⠁⠀⠈⠉⠻⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⣿⣆⣸⠃⠀⠀⠀⠀⠀⠀⠀⠘⣧⢠⢽⡇⠀⠀⠀⠀⠀
⠀⣤⣦⣄⣀⣀⣷⡙⢿⠀⠸⣦⡄⠀⢠⣴⠞⠀⣿⢋⣾⣁⣀⣠⡤⣤⡀
⢀⡷⠀⠉⠉⠉⠉⠙⢄⡉⠒⠤⠄⠶⠤⠤⠖⠊⡠⠊⠉⠉⠉⠉⠀⢾⡇
⠀⠳⠶⠛⠉⠉⠉⠉⠉⢻⡒⡤⡤⣤⢤⠤⣖⡿⠉⠉⠉⠉⠉⠙⠷⠾⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠈⡟⠒⠃⠸⠘⠒⢻⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⠛⠲⣶⠒⢲⠶⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⢀⡿⠀⢸⡄⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⣅⣤⣨⡿⠀⠀⠀⠀⠀⠀
       MAC Changer!! ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""


# Generate a random MAC address
def generate_random_mac():
    mac = [0x00, 0x16, 0x3e,  # OUI part
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))

# Validate the MAC address format to prevent injection
def validate_mac(mac):
    if re.match(r"([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})", mac):
        return True
    else:
        return False

# Validate the network interface name (whitelisted characters only)
def validate_interface(interface):
    if re.match(r"^[a-zA-Z0-9_-]+$", interface):
        return True
    else:
        return False

# Get the arguments from the user
def get_arguments():
    parser = argparse.ArgumentParser(description=Fore.CYAN + 'Advanced MAC Address Changer')
    parser.add_argument("-i", "--interface", dest="interface", required=True, help="Interface to change its MAC address")
    parser.add_argument("-m", "--mac", dest="new_mac", help="New MAC address (Optional: leave blank for random MAC)")
    parser.add_argument("--reset", action="store_true", help="Reset MAC address to original")

    args = parser.parse_args()

    # Validate inputs
    if not validate_interface(args.interface):
        parser.error(Fore.RED + "[-] Invalid interface name. Avoid special characters.")

    if args.new_mac and not validate_mac(args.new_mac):
        parser.error(Fore.RED + "[-] Invalid MAC address format.")

    return args

# Change the MAC address securely
def change_mac(interface, new_mac):
    print(Fore.GREEN + f"[+] Changing MAC address for {interface} to {new_mac}")
    try:
        subprocess.run(["ifconfig", interface, "down"])
        subprocess.run(["ifconfig", interface, "hw", "ether", new_mac])
        subprocess.run(["ifconfig", interface, "up"])
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[-] Error changing MAC address: {e}")
        return False
    return True

# Get the current MAC address securely
def get_current_mac(interface):
    try:
        ifconfig_result = subprocess.check_output(["ifconfig", interface]).decode('utf-8')
        mac_address_search_result = re.search(r"([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})", ifconfig_result)
        if mac_address_search_result:
            return mac_address_search_result.group(0)
        else:
            print(Fore.RED + "[-] Could not read MAC address.")
            return None
    except subprocess.CalledProcessError:
        print(Fore.RED + "[-] Could not execute ifconfig. Make sure the interface is valid.")
        return None

# Reset the MAC address to its original (using current MAC as reference)
def reset_mac(interface):
    print(Fore.YELLOW + f"[~] Resetting MAC address for {interface} to original.")
    original_mac = get_current_mac(interface)  # Store current MAC
    if change_mac(interface, original_mac):
        print(Fore.GREEN + f"[+] MAC address reset to original: {original_mac}")
    else:
        print(Fore.RED + "[-] Failed to reset MAC address.")

# Main logic
if __name__ == "__main__":
    print(Fore.MAGENTA + ascii_art)

    options = get_arguments()

    if options.reset:
        reset_mac(options.interface)
    else:
        if options.new_mac:
            new_mac = options.new_mac
        else:
            new_mac = generate_random_mac()
            print(Fore.CYAN + f"[+] Generated random MAC address: {new_mac}")

        current_mac = get_current_mac(options.interface)
        if current_mac:
            print(Fore.CYAN + f"Current MAC = {current_mac}")
            if change_mac(options.interface, new_mac):
                updated_mac = get_current_mac(options.interface)
                if updated_mac == new_mac:
                    print(Fore.GREEN + f"[+] MAC address was successfully changed to {updated_mac}")
                else:
                    print(Fore.RED + "[-] MAC address did not get changed.")
            else:
                print(Fore.RED + "[-] Failed to change MAC address.")
        else:
            print(Fore.RED + "[-] Unable to fetch current MAC address.")
