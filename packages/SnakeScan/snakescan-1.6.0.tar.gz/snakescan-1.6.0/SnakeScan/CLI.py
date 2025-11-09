import sys
import argparse
import socket
import ipaddress
from concurrent.futures import ProcessPoolExecutor
from termcolor import colored
from threading import Thread
from tqdm import tqdm
from SnakeScan.Check_subnet import Check_network
from SnakeScan.PoolExecutor import PoolProcessExecutor


def main():
    pass


if __name__ == "__main__":
    main()
OpenPorts = []
threads = []
portsopen = 0
portsclosed = 0
Bool = True
boolsd = True
boolean = 0
ports = {
    20: "FTP-DATA",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    43: "WHOIS",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    69: "TFTP",
    80: "http",
    110: "POP3",
    115: "SFTP",
    123: "NTP",
    139: "NetBios",
    143: "IMAP",
    161: "SNMP",
    179: "BGP",
    443: "HTTPS",
    445: "MICROSOFT-DS",
    465: "SSL/TLS",
    514: "SYSLOG",
    515: "PRINTER",
    554: "RTSP",
    587: "TLS/STARTTLS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS",
    1194: "OpenVPN",
    1433: "SQL Server",
    1723: "PPTP",
    2222: "SSH",
    3128: "HTTP",
    3268: "LDAP",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "Tomcat",
    10000: "Webmin",
}
version = "1.6.0"


def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((host, port))
        except (OSError, socket.timeout):
            return False
        else:
            return True


def is_port_open_threads(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((host, port))
        except (OSError, socket.timeout):
            try:
                print(f"Closed{colored('|X|','red')}-->{ports.get(port)}|{port}|")
            except:
                print(f"Closed{colored('|X|','red')}-->|{port}|")
        else:
            print(f"Open{colored('|√|','green')}-->{ports.get(port)}|{port}|")


def SnakeArgs():
    parser = argparse.ArgumentParser(
        description="Snake - It's a command line module SnakeScan. Use him for more fast starting"
    )
    parser.add_argument("host", nargs="?", default="None")
    parser.add_argument("-sp", "--speed", action="store_true", help="speed scan")
    parser.add_argument("-v", "--version", action="store_true", help="version")
    parser.add_argument("-i", "--info", action="store_true", help="ip info")
    parser.add_argument("-p", "--ports", help="ports")
    parser.add_argument("-s", "--single", help="single scan")
    parser.add_argument("-t", "--thread", action="store_true", help="fast scan")
    parser.add_argument("-ch", "--check", action="store_true", help="scan subnet")
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        help="view you public ip - need internet",
    )
    args = parser.parse_args()
    return args


port_user = SnakeArgs().ports
host = SnakeArgs().host
if host.startswith("http://"):
            host = host.strip()
            host = host.split("http:")
            host = host[1].strip("//")
            host = host.split("/")
            host = host[0]
            for i in range(len(host)):
                if host[i] == "/":
                    host = host[0:i]
if host.startswith("https://"):
            host = host.strip()
            host = host.split("https:")
            host = host[1].strip("//")
            host = host.split("/")
            host = host[0]
            for i in range(len(host)):
                if host[i] == "/":
                    host = host[0:i]
if host == "None":
    host = "localhost"
if SnakeArgs().ports:
    try:
        length = int(port_user)
    except:
        port_user = "100"
        print(f"{colored('[!]','red')}Port:invalid value")
        for i in range(0, len(port_user)):
            if port_user[i] == " ":
                port_user = 100
        port_user = int(port_user)
        length = port_user
    length = int(length) + 1
    for port in tqdm(range(1, length)):
        if is_port_open(host, port):
            for name in ports:
                if port == name:
                    OpenPorts = [port]
                    portsopen += 1
        else:
            portsclosed += 1
        if port_user != "":
            if int(port_user) == port:
                if port_user == "":
                    pass
                elif int(port_user) == port:
                    if is_port_open(host, port):
                        Bool = True
                        boolean += 1
            else:
                Bool = False
    if boolean == 1:
        pass
    for i in OpenPorts:
        print(f"Open{colored('|√|','green')}-->{ports[i]}|{i}|")
    print(f"{host}".center(60, "-"))
    print(f"Closed{colored('|X|','red')}:{portsclosed}")
    portsclosed = 0
    print(f"Open{colored('|√|','green')}:{portsopen}")
    portsopen = 0
    print("-" * 60)
if SnakeArgs().check:
    Check_network(host)
if SnakeArgs().single:
    port_user = SnakeArgs().single.split(",")

    port_list = port_user
    port_user = []
    for i in range(len(port_list)):
        try:
            port_user.append(int(port_list[i]))
        except:
            print(f"{port_list[i]}-->Invalid value")

    for port in range(len(port_user)):
        if is_port_open(host, port_user[port]):
            print(
                f"Open{colored('|√|','green')}{host}-->{ports[port_user[port]]}|{port_user[port]}|"
            )
        else:
            try:
                print(
                    f"Closed{colored('|X|','red')}{host}-->{ports[port_user[port]]}|{port_user[port]}|"
                )
            except:
                print(f"Closed{colored('|X|','red')}{host}-->|{port_user[port]}|")
if SnakeArgs().local:
    local = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        local = s.getsockname()[0]
    except Exception as e:
        local = f"127.0.0.1:{e}"
    finally:
        s.close()
        print(local)
if SnakeArgs().info:
    if host == "None":
        host = "localhost"
    host = host.strip("-i").strip()
    print("".center(60, "-"))
    try:
        host = socket.gethostbyname(host)
    except Exception as e:
        print(e)
        print("".center(60, "^"))
        print("".center(60, "-"))

    hosting = ""
    hosting = host.split(".")
    hosting[len(hosting) - 1] = "0"
    network = ""
    for i in range(len(hosting) - 1):
        network += hosting[i] + "."
    network += "0"
    network += "/24"
    hosting = network
    try:
        ip_obj = ipaddress.ip_address(host)
    except Exception as e:
        print(e)
        sys.exit()
    print(f"Type IP: {type(ip_obj)}")
    print(f"Version IP: {ip_obj.version}")
    network_obj = ipaddress.ip_network(network)
    print(f"Network: {network_obj}")
    print(f"Subnet mask: {network_obj.netmask}")
    try:
        hostname = socket.gethostbyaddr(host)
        print(f"Host:{hostname[0]}")
    except:
        hostname = "Undefined"
        print(f"Host:{hostname}")
    try:
        print(f"IP:{socket.gethostbyname(host)}")
    except Exception as e:
        print(f"IP:{e}")

    finally:
        print("".center(60, "-"))
if SnakeArgs().thread:
    print(f"Thread".center(60, "-"))

    for port in ports.keys():
        t = Thread(
            target=is_port_open_threads,
            kwargs={"host": host, "port": port},
        )
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
if SnakeArgs().version:
    print(f"Build_{version}")
if SnakeArgs().speed:
    print(f"ProcessPoolExecutor".center(60, "-"))
    PoolProcessExecutor(host)
