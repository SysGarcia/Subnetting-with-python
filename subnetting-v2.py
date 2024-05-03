import sys
import ctypes
import ipaddress

def enable_windows_ansi_support():
    if sys.platform.startswith('win32'):
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

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

def find_minimum_mask(ip_list):
    # Convertir las direcciones IP en objetos IP y obtener sus partes binarias
    binary_ips = [ipaddress.ip_network(ip, strict=False).network_address.packed for ip in ip_list]
    min_mask = 32  # Máxima longitud de máscara, comienza asumiendo que todas las direcciones son únicas

    # Comparar cada par de direcciones para encontrar el prefijo común más largo
    for i in range(len(binary_ips)):
        for j in range(i + 1, len(binary_ips)):
            # Convertir bytes a cadenas binarias
            bin_i = ''.join(f'{byte:08b}' for byte in binary_ips[i])
            bin_j = ''.join(f'{byte:08b}' for byte in binary_ips[j])
            # Calcular el prefijo común
            common_prefix_length = 0
            for b1, b2 in zip(bin_i, bin_j):
                if b1 == b2:
                    common_prefix_length += 1
                else:
                    break
            # Actualizar la mínima máscara si el prefijo común es menor
            if common_prefix_length < min_mask:
                min_mask = common_prefix_length

    return min_mask

def summarize_routes(ip_list):
    # Primero encontrar la máscara mínima necesaria para agrupar todas las direcciones
    min_mask = find_minimum_mask(ip_list)
    # Construir una nueva red usando la máscara mínima encontrada
    base_ip = ipaddress.ip_network(ip_list[0], strict=False)
    new_network = ipaddress.ip_network(f'{base_ip.network_address}/{min_mask}', strict=False)
    return new_network

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
    enable_windows_ansi_support()
    prompt = (colored((73, 171, 156), "Selecciona ") + colored((236, 237, 235), "[1] ") +
              colored((73, 171, 156), "para calcular la dirección de red, dispositivos y dirección de difusión dado una IP y una máscara. Selecciona ") +
              colored((236, 237, 235), "[2] ") +
              colored((73, 171, 156), "para calcular la máscara dado el número de dispositivos ") + 
              colored((236, 237, 235), "[3] ") +
              colored((73, 171, 156), "para dar una tupla de IPs y resumirlas: ")) 

    while True:
        choice = input(prompt)

        if choice == "1":
            ip_address = input(colored((255, 255, 0), "Ingresa la dirección IP: "))
            subnet_mask = input(colored((255, 255, 0), "Ingresa la máscara de subred (por ejemplo, 255.255.255.0 o /24): "))

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
            number_of_devices = int(input(colored((255, 255, 0), "Ingresa el número de dispositivos: ")))
            subnet_mask = calculate_subnet_mask_from_hosts(number_of_devices)
            print(colored((60, 179, 113), f"Your subnet mask is: /{subnet_mask}"))

        elif choice == "3":
            # Ejemplo con colores
            text = (
                colored((255, 215, 0), "-Ejemplo-\n") +
                colored((135, 206, 250), "ENTRADA: ") + colored((255, 255, 255), "192.168.0.1, 192.168.0.2, 192.168.0.3\n") +
                colored((50, 205, 50), "SALIDA: ") + colored((255, 255, 255), "192.168.0.0/24\n") +
                colored((255, 69, 0), "EL FORMATO ES: ") + colored((255, 255, 255), "XXX.XXX.XXX.XXX, YYY.YYY.YYY.YYY\n") +
                colored((255, 255, 255), "Introduce las direcciones IP separadas por comas y presiona ENTER.\n")
            )

            print(text)
            ip_addresses_input = input(colored((255, 165, 0), "Dame una lista de IPs y las resumiré automáticamente: "))

            # Eliminar espacios y separar las IPs introducidas por comas
            ip_addresses = ip_addresses_input.replace(" ", "").split(',')

            # Uso de la función summarize_routes para encontrar la red mínima que agrupe todas las IPs
            try:
                summarized_network = summarize_routes(ip_addresses)
                print(colored((154, 205, 50), f"La red resumida mínima es: {summarized_network}"))
            except ValueError as e:
                print(colored((220, 20, 60), f"Error: {str(e)}"))
                
        elif choice.lower() in ["e", "exit"]:
            print(colored((220, 20, 60), "Program terminated..."))
            break
        
        else:
            print(colored((255, 0, 0), f'\nInvalid input, try something other than "{choice}"\n'))

if __name__ == "__main__":
    main()