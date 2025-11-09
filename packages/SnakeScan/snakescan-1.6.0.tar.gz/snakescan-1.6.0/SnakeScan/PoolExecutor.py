import socket
from termcolor import colored
from concurrent.futures import ProcessPoolExecutor

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


def PoolProcessExecutor(host):
    with ProcessPoolExecutor(max_workers=None) as executor:
        try:
            for port in ports.keys():
                future = executor.submit(is_port_open_threads, host, port)

        except Exception as e:
            print(e)
