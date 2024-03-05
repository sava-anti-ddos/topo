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
    # start http server at h5
    for i in [5]:
        net.cmd('h{}'.format(i), 'sudo python3 -u -m http.server 80 > log/httpd.log 2>&1 &')
    # start http client at h1-h5
    for i in [1, 2, 3, 4]:
        start_delay = i
        net.cmd('h{}'.format(i), 'sudo python3 random_http_request.py {} &'.format(i))
    CLI(net)
    net.stop()