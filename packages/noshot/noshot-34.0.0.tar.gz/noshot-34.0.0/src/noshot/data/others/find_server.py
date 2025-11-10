from urllib.request import urlopen
import socket

for i in range(1, 256):
    url = f"http://192.168.1.{i}:8080/whoami"
    try:
        urlopen(url, timeout=0.01)
        print(url)
    except socket.timeout:
        print(url)
    except:
        pass