# each host send http requests to the other hosts, and wait a random time before sending the next request

import random
import time
import requests
import sys

# send http request to the target
def send_http_request(target):
    try:
        response = requests.get(target)
        print(response)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    # check the param
    if len(sys.argv) != 2:
        print('Usage: python3 random_http_request.py <self_ip>')
        sys.exit(1)

    # self ip
    self_ip = sys.argv[1]
    # target list
    targets = ['40.40.10.10',]
    # loop forever
    while True:
        # random pick a target except self
        target = random.choice(targets)
        if target != self_ip:
            # send http request to the target
            send_http_request(f'http://{target}')
            # random sleep
            time.sleep(random.randint(1, 1))