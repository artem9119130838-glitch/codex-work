import socket

domain = "xn--80aaagi1aieb9a7amg.xn--p1ai" # доставкакитай.рф

try:
    ip = socket.gethostbyname(domain)
    print(f"Resolved IP for {domain}: {ip}")
    if ip == "185.26.122.79":
        print("Success: DNS already updated to Hostland IP from our perspective!")
    elif ip == "185.215.4.43":
        print("Still pointing to Tilda IP.")
    else:
        print("Pointing to another IP:", ip)
except Exception as e:
    print("Failed to resolve domain:", e)
