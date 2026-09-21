from remote_sccs.main import app
from remote_sccs.constants_classes import RemoteSCCSConstants


import uvicorn

def main(rc: RemoteSCCSConstants) -> None:
    uvicorn.run(app, host=rc.NETWORK_IP, port=8000)