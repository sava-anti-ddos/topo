# send http request to the target forever

import random
import time
import requests
import sys

# send http request to the target
def send_http_request(target):
    try:
        response = requests.get(target, timeout=3)
        print(response)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    # check the param
    if len(sys.argv) != 3:
        print('Usage: python3 random_http_request.py <start_delay> <interval>')
        sys.exit(1)

    start_delay = sys.argv[1]
    interval = sys.argv[2]
    time.sleep(float(start_delay))
    # target list
    target = '40.40.10.10'
    # loop forever
    while True:
        # send http request to the target
        send_http_request(f'http://{target}')
        # random sleep
        time.sleep(float(interval))