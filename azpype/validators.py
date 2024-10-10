import os
from urllib.parse import urlparse
from pathlib import Path
from typing import Any
import socket
from logging import Logger

# Source Desination formatting validators
def validate_azure_blob_url(url: str, logger: Logger) -> bool:
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        logger.info(f"Invalid URL: {url}")
        return False
    if parsed_url.scheme not in ["https", "http"]:
        logger.info(f"Invalid URL: {url}")
        return False
    if 'blob.core.windows.net' not in parsed_url.netloc:
        logger.info(f"Invalid URL: {url}\nURL must be a valid Azure Blob Storage URL.")
        return False
    logger.info(f"Provided URL appears to be valid: {url}")
    return True

def validate_local_path(path: str, logger: Logger) -> bool:
    if not Path(path).exists():
        logger.info(f"File or Directory does not exist locally at path: {path}")
        return False
    logger.info(f"Found File or Directory locally at path: {path}")
    return True

def is_valid_path_or_url(path:str, logger: Logger) -> bool:
    return validate_local_path(path, logger) or validate_azure_blob_url(path, logger)


# Auth validators   
def validate_azcopy_envs(vars:list, logger: Logger):
    """
    Checks for the existence of an environment variable.
    
    To run this with a service principal as intended in azpype, the following environment variables must be set:
    [AZCOPY_SPA_CLIENT_SECRET, AZCOPY_SPA_APPLICATION_ID, AZCOPY_TENANT_ID, AZCOPY_AUTO_LOGIN_TYPE]
    """
    missing_vars = []
    for var in vars:
        if var not in os.environ:
            missing_vars.append(var)

    if missing_vars:
        logger.info(f"Missing environment variables: {missing_vars}")
        return missing_vars
    else:
        return True

def validate_login_type(logger: Logger):
    if os.getenv('AZCOPY_AUTO_LOGIN_TYPE') == 'SPN':
        return True
    else:
        logger.info(f"AZCOPY_AUTO_LOGIN_TYPE environment variable must be set to 'SPN' to use azpype.")
        return False

def validate_network_available(logger: Logger, host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        logger.info("No internet connection.")
        logger.info(f"Socket error:{ex}")
        return False
        



