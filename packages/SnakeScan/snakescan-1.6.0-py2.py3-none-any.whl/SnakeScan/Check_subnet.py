import ipaddress
import subprocess
import platform
from threading import Thread
import socket
from termcolor import colored

global threads
threads = []


def Check_network(host):
    def check_host(host):
        try:
            if platform.system().lower() == "windows":
                command = ["ping", "-n", "1", str(host)]
            else:
                command = ["ping", "-c", "1", str(host)]
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                print(f"{ip}-->{colored('|√|','green')}")
                return True
            else:
                print(f"{ip}-->{colored('|X|','red')}")
                return False
        except Exception as e:
            print(f"Check error {ip}: {e}")
            return False

    try:
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
        network_str = network
        network = ipaddress.ip_network(network_str)
        print(f"Checking the IP addresses in the subset {network_str}...")
        for ip in network.hosts():
            t = Thread(target=check_host, kwargs={"host": host})
            t.start()
            threads.append(t)
            for t in threads:
                t.join()
    except ValueError as e:
        print(f"Error creating network object {e}")
