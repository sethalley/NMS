import psutil
import time
import subprocess
import socket
import platform



############################### DEVICE METRICS ############################
def get_cpu_metrics():
    return {
        'cpu_usage_percent': psutil.cpu_percent(interval=1),
        'cpu_cores': psutil.cpu_count(logical=True),
        'cpu_physical_cores': psutil.cpu_count(logical=False),
        'cpu_frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {'current': None, 'min': None, 'max': None}
    }

def get_memory_metrics():
    virtual_memory = psutil.virtual_memory()._asdict()
    swap_memory = psutil.swap_memory()._asdict()
    return {
        'virtual_memory': virtual_memory,
        'swap_memory': swap_memory
    }

def get_disk_metrics():
    disk_usage = psutil.disk_usage('/')._asdict()  # Root partition
    disk_io = psutil.disk_io_counters()._asdict()
    return {
        'disk_usage': disk_usage,
        'disk_io': disk_io
    }

def get_system_metrics():
    boot_time = psutil.boot_time()
    return {
        'boot_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time)),
        'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else 'Not available'
    }

def fetch_device_metrics():
    return {
        'cpu': get_cpu_metrics(),
        'memory': get_memory_metrics(),
        'disk': get_disk_metrics(),
        'system': get_system_metrics(),
        'gpu': get_gpu_metrics()
    }

####################################### INTERFACE METRICS ##############################
def fetch_interface_metrics():
    # Initialize totals metrics
    totals_metrics = {
        'total_interfaces': 0,
        'interfaces_up': 0,
        'total_errors': 0,
        'total_packets': 0,
        'total_bytes': 0
    }
    
    # Initialize a dictionary to store per-interface metrics
    interface_metrics = {}

    # Get network interface stats
    network_interfaces = psutil.net_if_addrs()
    network_stats = psutil.net_if_stats()
    network_io = psutil.net_io_counters(pernic=True)

    for interface, addrs in network_interfaces.items():
        # Increment the total interface count
        totals_metrics['total_interfaces'] += 1

        # Get IP address (use socket.AF_INET for IPv4)
        ip_address = None
        for addr in addrs:
            if addr.family == socket.AF_INET:  # IPv4
                ip_address = addr.address
                break
        
        # Get interface stats (status, speed)
        status = "Up" if network_stats[interface].isup else "Down"
        if network_stats[interface].isup:
            totals_metrics['interfaces_up'] += 1  # Count interfaces that are up
        
        speed = network_stats[interface].speed if network_stats[interface].speed else "N/A"
        
        # Get network I/O stats (bytes sent, received, etc.)
        io = network_io.get(interface, None)
        bytes_sent = io.bytes_sent if io else 0
        bytes_received = io.bytes_recv if io else 0
        packets_sent = io.packets_sent if io else 0
        packets_received = io.packets_recv if io else 0
        input_errors = io.errin if io else 0
        output_errors = io.errout if io else 0
        dropped_in = io.dropin if io else 0
        dropped_out = io.dropout if io else 0

        # Update the total errors count
        totals_metrics['total_errors'] += input_errors + output_errors

        # Update the total packets and bytes transmitted (sent + received)
        totals_metrics['total_packets'] += packets_sent + packets_received
        totals_metrics['total_bytes'] += bytes_sent + bytes_received

        # Store interface-specific metrics
        interface_metrics[interface] = {
            'ip_address': ip_address,
            'status': status,
            'speed': f"{speed} Mbps",
            'bytes_sent': f"{bytes_sent / (1024 ** 2):.2f} MB",
            'bytes_received': f"{bytes_received / (1024 ** 2):.2f} MB",
            'packets_sent': packets_sent,
            'packets_received': packets_received,
            'input_errors': input_errors,
            'output_errors': output_errors,
            'dropped_in': dropped_in,
            'dropped_out': dropped_out
        }

    # Get latency (ping time)
    try:
        ping_result = subprocess.run(["ping", "-c", "4", "8.8.8.8"], capture_output=True, text=True)
        if ping_result.returncode == 0:
            latency = ping_result.stdout.splitlines()[-1].split("/")[-3]  # Get avg ping from result
            totals_metrics['latency'] = f"{latency} ms"
        else:
            totals_metrics['latency'] = "Ping failed"
    except Exception as e:
        totals_metrics['latency'] = f"Error fetching latency: {e}"

    return totals_metrics, interface_metrics  # Return both dictionaries



################################ NETWORK INFO #####################################
import subprocess
import platform
import re

def fetch_network_info():
    system_platform = platform.system()

    if system_platform == "Darwin":  # macOS
        return fetch_network_info_mac()
    
    elif system_platform == "Windows":  # Windows
        return fetch_network_info_windows()

    elif system_platform == "Linux":  # Linux
        return fetch_network_info_linux()

    else:
        return {"error": f"Unsupported OS: {system_platform}"}

# macOS-specific function
def fetch_network_info_mac():
    try:
        ssid = subprocess.check_output(["networksetup", "-getairportnetwork", "en0"]).decode().strip().split(": ")[1]
        ip_address = subprocess.check_output(["ifconfig", "en0"]).decode()
        local_ip = [line.split(" ")[1] for line in ip_address.splitlines() if "inet " in line][0]
        encryption = subprocess.check_output(["networksetup", "-getinfo", "Wi-Fi"]).decode().strip().split("\n")[5].split(": ")[1]
        public_ip = subprocess.check_output(["curl", "ifconfig.me"]).decode().strip()
        latency = subprocess.check_output(["ping", "-c", "4", "google.com"]).decode()
        latency = [line.split("time=")[-1].split(" ms")[0] for line in latency.splitlines() if "time=" in line]
        latency = latency[-1] if latency else "N/A"
        
        # Getting DNS and Default Gateway info
        dns_output = subprocess.check_output(["scutil", "--dns"]).decode().splitlines()
        # Extracting the DNS servers (if available)
        dns_servers = [line.split(": ")[1] for line in dns_output if "nameserver" in line]
        # If there are DNS servers, use the first one; otherwise, set it to 'N/A'
        dns = dns_servers[0] if dns_servers else "N/A"
        # Getting the default gateway
        default_gateway_output = subprocess.check_output(["netstat", "-nr"]).decode().splitlines()
        default_gateway = [line.split()[1] for line in default_gateway_output if "default" in line]

        # If a default gateway is found, return the first one; otherwise, set it to 'N/A'
        default_gateway = default_gateway[0] if default_gateway else "N/A"

        # Getting MAC Address
        mac_address = subprocess.check_output(["ifconfig", "en0"]).decode()
        mac_address = [line.split(" ")[1] for line in mac_address.splitlines() if "ether " in line][0]

        # Check if IPv6 is enabled
        ipv6_address = subprocess.check_output(["ifconfig", "en0"]).decode()
        ipv6_match = re.search(r"inet6 ([a-f0-9:]+)", ipv6_address)
        ipv6_address = ipv6_match.group(1) if ipv6_match else None
        is_ipv6 = bool(ipv6_address)

        return {
            "local_ip": local_ip,
            "is_ipv6": is_ipv6,
            "ipv6_address": ipv6_address or "N/A",
            "public_ip": public_ip,
            "dns": dns,
            "default_gateway": default_gateway,
            "latency": latency,
            "mac_address": mac_address,
            "ssid": ssid,
            "channel_freq": "N/A",  # No direct method to get channel/frequency on macOS
            "encryption": encryption
        }
    except subprocess.CalledProcessError as e:
        return {"error": f"Error fetching network info: {str(e)}"}

# Windows-specific function
def fetch_network_info_windows():
    try:
        ssid = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode()
        ssid = [line.split(":")[1].strip() for line in ssid.splitlines() if "SSID" in line][0]
        ip_address = subprocess.check_output(["ipconfig"]).decode()
        local_ip = [line.split(":")[1].strip() for line in ip_address.splitlines() if "IPv4" in line][0]
        encryption = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode()
        encryption = [line.split(":")[1].strip() for line in encryption.splitlines() if "Authentication" in line][0]
        public_ip = subprocess.check_output(["curl", "ifconfig.me"]).decode().strip()
        latency = subprocess.check_output(["ping", "-n", "4", "google.com"]).decode()
        latency = [line.split("time=")[-1].split("ms")[0] for line in latency.splitlines() if "time=" in line]
        latency = latency[-1] if latency else "N/A"
        
        # Getting DNS and Default Gateway info
        dns = subprocess.check_output(["nslookup", "google.com"]).decode()
        dns = [line.split(":")[1].strip() for line in dns.splitlines() if "Address" in line and "non-authoritative" in line]
        default_gateway = subprocess.check_output(["ipconfig"]).decode()
        default_gateway = [line.split(":")[1].strip() for line in default_gateway.splitlines() if "Default Gateway" in line][0]

        # Getting MAC Address
        mac_address = subprocess.check_output(["getmac"]).decode().splitlines()
        mac_address = [line.split()[0] for line in mac_address if "Ethernet" in line][0]

        # Check if IPv6 is enabled
        ipv6_address = subprocess.check_output(["ipconfig"]).decode()
        ipv6_match = re.search(r"IPv6 Address.*: (.*)", ipv6_address)
        ipv6_address = ipv6_match.group(1) if ipv6_match else None
        is_ipv6 = bool(ipv6_address)

        return {
            "local_ip": local_ip,
            "is_ipv6": is_ipv6,
            "ipv6_address": ipv6_address or "N/A",
            "public_ip": public_ip,
            "dns": dns,
            "default_gateway": default_gateway,
            "latency": latency,
            "mac_address": mac_address,
            "ssid": ssid,
            "channel_freq": "N/A",  # No direct method to get channel/frequency on Windows
            "encryption": encryption
        }
    except subprocess.CalledProcessError as e:
        return {"error": f"Error fetching network info: {str(e)}"}

# Linux-specific function
def fetch_network_info_linux():
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
        ip_address = subprocess.check_output(["hostname", "-I"]).decode().strip()
        local_ip = ip_address
        encryption = subprocess.check_output(["iwlist", "wlan0", "encryption"]).decode().strip()
        public_ip = subprocess.check_output(["curl", "ifconfig.me"]).decode().strip()
        latency = subprocess.check_output(["ping", "-c", "4", "google.com"]).decode()
        latency = [line.split("time=")[-1].split(" ms")[0] for line in latency.splitlines() if "time=" in line]
        latency = latency[-1] if latency else "N/A"
        
        # Getting DNS and Default Gateway info
        dns = subprocess.check_output(["cat", "/etc/resolv.conf"]).decode().splitlines()
        dns = [line.split(" ")[1] for line in dns if "nameserver" in line]
        default_gateway = subprocess.check_output(["ip", "route", "show"]).decode().splitlines()
        default_gateway = [line.split()[2] for line in default_gateway if "default" in line][0]

        # Getting MAC Address
        mac_address = subprocess.check_output(["ifconfig", "wlan0"]).decode()
        mac_address = [line.split(" ")[1] for line in mac_address.splitlines() if "ether " in line][0]

        # Check if IPv6 is enabled
        ipv6_address = subprocess.check_output(["ifconfig", "wlan0"]).decode()
        ipv6_match = re.search(r"inet6 ([a-f0-9:]+)", ipv6_address)
        ipv6_address = ipv6_match.group(1) if ipv6_match else None
        is_ipv6 = bool(ipv6_address)

        return {
            "local_ip": local_ip,
            "is_ipv6": is_ipv6,
            "ipv6_address": ipv6_address or "N/A",
            "public_ip": public_ip,
            "dns": dns,
            "default_gateway": default_gateway,
            "latency": latency,
            "mac_address": mac_address,
            "ssid": ssid,
            "channel_freq": "N/A",  # No direct method to get channel/frequency on Linux
            "encryption": encryption
        }
    except subprocess.CalledProcessError as e:
        return {"error": f"Error fetching network info: {str(e)}"}
