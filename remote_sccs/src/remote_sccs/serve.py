import socket
import uvicorn

from remote_sccs.constants_classes import RemoteSCCSConstants
from remote_sccs.main import app


def print_SCCS_server_startup(rc: RemoteSCCSConstants):
    # Establish a temporary socket connection to detect the local network IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((rc.PUBLIC_IP_ADDRESS, rc.PORT_80))
    ip_address = sock.getsockname()[rc.FIRST_ITEM_INDEX]
    sock.close()
    
    print(rc.SCCS_SERVER_IP_MESSAGE.format(ip_address=ip_address))
    print(rc.STARTING_UVICORN_SERVER_MESSAGE)

def main(rc: RemoteSCCSConstants) -> None:
    print_SCCS_server_startup(rc)
    
    uvicorn.run(app, host=rc.NETWORK_IP, port=rc.PORT_8000)
