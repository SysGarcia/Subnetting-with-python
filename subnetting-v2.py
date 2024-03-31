import sys
import ctypes

def enable_windows_ansi_support():
    if sys.platform.startswith('win32'):
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
enable_windows_ansi_support()

def colored(color, text):
    """
    Use it to color the terminal, recognizes between hexadecimal and RGB
    """
    if isinstance(color, tuple) and len(color) == 3:
        r, g, b = color
    elif isinstance(color, str) and len(color) == 6:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
    else:
        raise ValueError("Invalid color format")

    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def calculate_network_and_broadcast_addresses(ip, mask):
    ip_octets = ip.split(".")
    mask_octets = mask.split(".") if '.' in mask else cidr_to_octets(mask)

    bin_ip = ''.join(f'{int(octet):08b}' for octet in ip_octets)
    bin_mask = ''.join(f'{int(octet):08b}' for octet in mask_octets)

    network_bin = bin_ip[:bin_mask.count('1')] + '0' * (32 - bin_mask.count('1'))
    broadcast_bin = bin_ip[:bin_mask.count('1')] + '1' * (32 - bin_mask.count('1'))

    network = format_ip_from_binary(network_bin)
    broadcast = format_ip_from_binary(broadcast_bin)

    return network, broadcast

def cidr_to_octets(cidr):
    mask_length = int(cidr[1:])  # Extract the numerical part from CIDR notation
    binary_mask = '1' * mask_length + '0' * (32 - mask_length)
    return [str(int(binary_mask[i:i+8], 2)) for i in range(0, 32, 8)]

def format_ip_from_binary(binary_str):
    return '.'.join(str(int(binary_str[i:i+8], 2)) for i in range(0, 32, 8))

def classify_ip(mask):
    ones = mask.count('1')
    if ones <= 8:
        return colored((133, 209, 56), "--> Class A (Large networks)")
    elif ones <= 16:
        return colored((133, 209, 56), "--> Class B (Medium networks)")
    elif ones <= 24:
        return colored((133, 209, 56), "--> Class C (Small networks)")
    else:
        return colored((133, 209, 56), "--> Multicast (224.0.0.0 – 239.255.255.255) or Research (240.0.0.0 – 255.255.255.255)")

def calculate_subnet_mask_from_hosts(number_of_hosts):
    required_addresses = number_of_hosts + 2  # Net and broadcast
    mask_length = 32

    while 2 ** (32 - mask_length) < required_addresses:
        mask_length -= 1
    return mask_length

def main():
    prompt = (colored((73, 171, 156), "Select ") + colored((236, 237, 235), "[1] ") +
              colored((73, 171, 156), "for calculating network address, devices, and broadcast address given an IP and a Mask. Select ") +
              colored((236, 237, 235), "[2] ") +
              colored((73, 171, 156), "to calculate the mask given the number of devices: "))

    while True:
        choice = input(prompt)

        if choice == "1":
            ip_address = input(colored((255, 255, 0), "Enter IP address: "))
            subnet_mask = input(colored((255, 255, 0), "Enter subnet mask (e.g., 255.255.255.0 or /24): "))

            network, broadcast = calculate_network_and_broadcast_addresses(ip_address, subnet_mask)
            mask_bin = ''.join(f'{int(octet):08b}' for octet in (subnet_mask.split('.') if '.' in subnet_mask else cidr_to_octets(subnet_mask)))

            number_of_networks = 2 ** mask_bin.count("1")
            number_of_hosts = (2 ** (32 - mask_bin.count("1"))) - 2

            class_info = classify_ip(mask_bin)

            print(colored((255, 165, 0), f"\nNetwork address: {network}"))
            print(colored((255, 69, 0), f"Broadcast address: {broadcast}"))
            print(colored((154, 205, 50), f"Number of hosts: {number_of_hosts}"))
            print(colored((100, 149, 237), f"Number of subnetworks: {number_of_networks}\n"))
            print(class_info)

        elif choice == "2":
            number_of_devices = int(input(colored((255, 255, 0), "Enter the number of devices: ")))
            subnet_mask = calculate_subnet_mask_from_hosts(number_of_devices)
            print(colored((60, 179, 113), f"Your subnet mask is: /{subnet_mask}"))

        elif choice.lower() in ["e", "exit"]:
            print(colored((220, 20, 60), "Program terminated..."))
            break

        else:
            print(colored((255, 0, 0), f'\nInvalid input, try something other than "{choice}"\n'))

if __name__ == "__main__":
    main()
