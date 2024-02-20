import net
import os
from net import ReflectionAttackNet
from mininet.cli import CLI
from log import get_logger

logger = get_logger(__name__)

# current directory
current_dir = os.getcwd()
net.CONF_PREFIX = os.path.join(current_dir, 'conf')
logger.info(f"net.CONF_PREFIX = " + net.CONF_PREFIX)

# run at the project root path
if __name__ == '__main__':
    net = ReflectionAttackNet()
    net.start()
    net.cmd('h6', 'sudo python3 -m http.server 80 &')
    net.cmd('h4', 'sudo python3 -m http.server 80 &')
    CLI(net)
    net.stop()