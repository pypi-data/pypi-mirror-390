import socket
import time

from ssm_cli.commands.ssh_proxy.server import SshServer
from ssm_cli.instances import Instance, Instances, SessionManagerPluginError, SessionManagerPluginPortError
from ssm_cli.config import CONFIG
from ssm_cli.commands.base import BaseCommand
from ssm_cli.cli_args import ARGS

import logging
logger = logging.getLogger(__name__)


class SshProxyCommand(BaseCommand):
    HELP="SSH ProxyCommand feature"
    def add_arguments(parser):
        parser.add_argument("group", type=str, help="group to run against")

    def run():
        logger.info("running proxycommand action")


        instances = Instances()
        instance = instances.select_instance(ARGS.group, CONFIG.actions.proxycommand.selector)

        if instance is None:
            logger.error("failed to select host")
            raise RuntimeError("failed to select host")

        logger.info(f"connecting to {repr(instance)}")
        
        connections = {}
        server = SshServer(direct_tcpip_callback(instance, connections))
        server.start()

def direct_tcpip_callback(instance: Instance, connections: dict) -> callable:
    def callback(host, remote_port) -> socket.socket:
        internal_port, proc = None, None

        if (host, remote_port) in connections:
            internal_port, proc = connections[(host, remote_port)]
            if proc.poll() is not None:
                logger.debug(f"process for {host}:{remote_port} has exited, restarting")
                del connections[(host, remote_port)]
                internal_port, proc = None, None
        
        if internal_port is None:
            # Retry because of rare race condition from get_free_port
            for attempt in range(3):
                try:
                    internal_port = get_free_port()
                    proc = instance.start_port_forwarding_session_to_remote_host(host, remote_port, internal_port)
                    connections[(host, remote_port)] = (internal_port, proc)
                    break
                except SessionManagerPluginPortError as e:
                    logger.warning(f"session-manager-plugin attempt {attempt} failed due to port clash, retrying: {e}")
                    time.sleep(0.1)
                except SessionManagerPluginError as e:
                    logger.error(f"session-manager-plugin failed: {e}")
                    return None
        
        logger.debug(f"connecting to session manager plugin on 127.0.0.1:{internal_port}")
        # Even though we wait for the process to say its connected, we STILL need to wait for it
        for attempt in range(10):
            try:
                if proc.poll() is not None:
                    logger.error(f"session-manager-plugin has exited")
                    raise RuntimeError("session-manager-plugin has exited")
                sock = socket.create_connection(('127.0.0.1', internal_port))
                logger.info(f"connected to 127.0.0.1:{internal_port}")
                break
            except Exception as e:
                logger.warning(f"connection attempt {attempt} failed: {e}")
                time.sleep(0.1)
        
        return sock

    return callback


def get_free_port(bind_host="127.0.0.1"):
    """
    Ask OS for an ephemeral free port. Returns the port number, however it is not guaranteed that the port will remain free. A retry should be used.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((bind_host, 0))  # port 0 => let OS pick
    port = s.getsockname()[1]
    s.close()
    return port