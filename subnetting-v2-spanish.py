import sys
import ctypes

def enable_windows_ansi_support():
    if sys.platform.startswith('win32'):
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
enable_windows_ansi_support()

def coloreado(r, g, b, texto):
    return f"\033[38;2;{r};{g};{b}m{texto}\033[0m"

def calcular_direcciones_red_y_broadcast(ip, mascara):
    octetos_ip = ip.split(".")
    octetos_mascara = mascara.split(".") if '.' in mascara else cidr_a_octetos(mascara)

    bin_ip = ''.join(f'{int(octeto):08b}' for octeto in octetos_ip)
    bin_mascara = ''.join(f'{int(octeto):08b}' for octeto in octetos_mascara)

    bin_red = bin_ip[:bin_mascara.count('1')] + '0' * (32 - bin_mascara.count('1'))
    bin_broadcast = bin_ip[:bin_mascara.count('1')] + '1' * (32 - bin_mascara.count('1'))

    red = formato_ip_desde_binario(bin_red)
    broadcast = formato_ip_desde_binario(bin_broadcast)

    return red, broadcast

def cidr_a_octetos(cidr):
    longitud_mascara = int(cidr[1:])
    mascara_binaria = '1' * longitud_mascara + '0' * (32 - longitud_mascara)
    return [str(int(mascara_binaria[i:i+8], 2)) for i in range(0, 32, 8)]

def formato_ip_desde_binario(cadena_binaria):
    return '.'.join(str(int(cadena_binaria[i:i+8], 2)) for i in range(0, 32, 8))

def clasificar_ip(mascara):
    unos = mascara.count('1')
    if unos <= 8:
        return coloreado(133, 209, 56, "--> Clase A (Redes grandes)")
    elif unos <= 16:
        return coloreado(133, 209, 56, "--> Clase B (Redes medianas)")
    elif unos <= 24:
        return coloreado(133, 209, 56, "--> Clase C (Redes pequeñas)")
    else:
        return coloreado(133, 209, 56, "--> Multidifusión (224.0.0.0 – 239.255.255.255) o Investigación (240.0.0.0 – 255.255.255.255)")

def calcular_mascara_subred_desde_hosts(numero_de_hosts):
    direcciones_requeridas = numero_de_hosts + 2
    longitud_mascara = 32

    while 2 ** (32 - longitud_mascara) < direcciones_requeridas:
        longitud_mascara -= 1
    return longitud_mascara

def main():
    indicacion = (coloreado(73, 171, 156, "\nSeleccione ") + coloreado(236, 237, 235, "[1] ") +
                  coloreado(73, 171, 156, "para calcular la dirección de red, dispositivos y dirección de broadcast dada una IP y una Máscara. Seleccione ") +
                  coloreado(236, 237, 235, "[2] ") +
                  coloreado(73, 171, 156, "para calcular la máscara dada la cantidad de dispositivos: "))

    while True:
        eleccion = input(indicacion)

        if eleccion == "1":
            direccion_ip = input(coloreado(255, 255, 0, "Ingrese la dirección IP: "))
            mascara_subred = input(coloreado(255, 255, 0, "Ingrese la máscara de subred (p. ej., 255.255.255.0 o /24): "))

            red, broadcast = calcular_direcciones_red_y_broadcast(direccion_ip, mascara_subred)
            bin_mascara = ''.join(f'{int(octeto):08b}' for octeto in (mascara_subred.split('.') if '.' in mascara_subred else cidr_a_octetos(mascara_subred)))

            numero_de_redes = 2 ** bin_mascara.count("1")
            numero_de_hosts = (2 ** (32 - bin_mascara.count("1"))) - 2

            info_clase = clasificar_ip(bin_mascara)

            print(coloreado(255, 165, 0, f"\nDirección de Red: {red}"))
            print(coloreado(255, 69, 0, f"Dirección de Broadcast: {broadcast}"))
            print(coloreado(154, 205, 50, f"Número de Hosts: {numero_de_hosts}"))
            print(coloreado(100, 149, 237, f"Número de Subredes: {numero_de_redes}\n"))
            print(info_clase)

        elif eleccion == "2":
            cantidad_dispositivos = int(input(coloreado(255, 255, 0, "Ingrese el número de dispositivos: ")))
            mascara_subred = calcular_mascara_subred_desde_hosts(cantidad_dispositivos)
            print(coloreado(60, 179, 113, f"Su máscara de subred es: /{mascara_subred}"))

        elif eleccion.lower() in ["e", "salir"]:
            print(coloreado(220, 20, 60, "Programa terminado..."))
            break

        else:
            print(coloreado(255, 0, 0, f'\nEntrada inválida, intente algo distinto a "{eleccion}"\n'))

if __name__ == "__main__":
    main()
