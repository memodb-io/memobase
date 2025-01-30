import os
from typing import Set
from ipaddress import ip_address, ip_network
from ..models.utils import CODE, Promise
from ..env import LOG

ALLOWED_ADMIN_IPS: Set[str] = {
    ip.strip() for ip in os.getenv("ALLOWED_MEMOBASE_ADMIN_IPS", "127.0.0.1").split(",")
}
ALLOWED_ADMIN_NETWORKS: Set[str] = {
    network.strip()
    for network in os.getenv("ALLOWED_MEMOBASE_ADMIN_NETWORKS", "localhost").split(",")
    if network.strip()
}


def is_root_ip_allowed(client_ip: str) -> Promise[bool]:
    """Check if an IP is allowed to access admin endpoints"""
    LOG.info(f"{client_ip} is accessing /admin endpoints")
    if client_ip in ALLOWED_ADMIN_IPS:
        return Promise.resolve(True)
    try:
        addr = ip_address(client_ip)
        return Promise.resolve(
            any(addr in ip_network(network) for network in ALLOWED_ADMIN_NETWORKS)
        )
    except ValueError:
        return Promise.reject(CODE.BAD_REQUEST, "Invalid IP address")
