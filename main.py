import net
# 修改为conf文件夹的绝对路径
net.CONF_PREFIX = '/home/mininet/codebase/sav-d/conf'

from net import ReflectionAttackNet
from mininet.cli import CLI

# 在项目根目录运行
if __name__ == '__main__':
    net = ReflectionAttackNet()
    net.start()
    net.cmd('h6', 'sudo python3 -m http.server 80 &')
    net.cmd('h4', 'sudo python3 -m http.server 80 &')
    # net.cmd('r6', 'sudo python sniff.py &')
    CLI(net)
    net.stop()