import socket
import ipaddress

class NetworkUtils:
    @staticmethod
    def is_valid_ip(address: str) -> bool:
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    @staticmethod
    def resolve_domain(domain: str) -> list:
        ips = []
        try:
            for info in socket.getaddrinfo(domain, None):
                ip = info[4][0]
                if ip not in ips:
                    ips.append(ip)
        except Exception:
            pass
        return ips

    @staticmethod
    def is_port_open(ip: str, port: int, timeout: float = 1.0) -> bool:
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return True
        except Exception:
            return False
