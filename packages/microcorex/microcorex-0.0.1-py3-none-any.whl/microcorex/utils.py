"""
Utility Module

Provides utility functions for IP retrieval, address resolution, etc.
"""

import socket



def get_local_ip() -> str:
    """
    Get local IP address with fallback to 127.0.0.1

    Returns:
        str: Local IP address
    """
    try:
        # Try connecting to external address to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            return ip
    except (OSError, socket.error):
        try:
            # Fallback: Get hostname IP
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            # If 127.0.0.1 is obtained, try other methods
            if ip.startswith("127."):
                # Get all network interface IPs
                for interface in [socket.gethostbyname_ex(host)[2]
                                  for host in socket.gethostbyname_ex(socket.gethostname())[2]]:
                    for addr in interface:
                        if not addr.startswith("127.") and not addr.startswith("169.254."):
                            return addr
                return "127.0.0.1"
            return ip
        except (OSError, socket.error):
            return "127.0.0.1"


def is_valid_port(port: int) -> bool:
    """
    Check if port number is valid

    Args:
        port: Port number

    Returns:
        bool: Whether valid
    """
    return 1 <= port <= 65535


def is_valid_ip(ip: str) -> bool:
    """
    Check if IP address is valid

    Args:
        ip: IP address

    Returns:
        bool: Whether valid
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def resolve_address(address: str) -> tuple[str, int]:
    """
    Parse address string into IP and port

    Args:
        address: Address string in format "ip:port"

    Returns:
        tuple[str, int]: (ip, port)
    """
    if ":" not in address:
        raise ValueError(f"Invalid address format: {address}, expected format: ip:port")

    ip, port_str = address.rsplit(":", 1)

    try:
        port = int(port_str)
    except ValueError:
        raise ValueError(f"Invalid port number: {port_str}")

    if not is_valid_ip(ip):
        raise ValueError(f"Invalid IP address: {ip}")

    if not is_valid_port(port):
        raise ValueError(f"Port number out of range: {port}")

    return ip, port
