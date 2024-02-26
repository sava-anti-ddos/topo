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
    # start http server at h1-h5
    for i in [1, 2, 3, 4, 5]:
        net.cmd('h{}'.format(i), 'python3 -m http.server 80 &')
    # start http client at h1-h5
    for i in [1, 2, 3, 4, 5]:
        host_ip = net.get('h{}'.format(i)).IP()
        net.cmd('h{}'.format(i), 'python3 random_http_request.py {} &'.format(host_ip))
    CLI(net)
    net.stop()