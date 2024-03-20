import requests
import random
import threading
import time
from datetime import datetime
import queue
import re

request_counts = 0
try:
    with open('result.txt', 'r', encoding="utf-8") as f:
        sbd_got = f.read().split('\n')
except:
    sbd_got = []
for i in range(len(sbd_got)):
    sbd_got[i] = sbd_got[i].split(': ')[0]
print(sbd_got)
try:
    with open('uncorrect.txt', 'r', encoding="utf-8") as f:
        sbd_wrong = f.read().split('\n')
except:
    sbd_wrong = []
    
proxies = []
def generate_data():
    maMon = ['04']  # Simplified for testing
    sbd = [str(i).zfill(3) for i in range(1, 700)]
    dob = [f'{str(i).zfill(2)}{str(j).zfill(2)}2006' for i in range(1, 32) for j in range(1, 13)]
    data = [f'{i}_{j}-{k}' for i in maMon for j in sbd for k in dob]
    return data

def get_proxy():
    global proxies
    proxy_info = requests.get('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=all&timeout=15000&proxy_format=protocolipport&format=json').json()
    for proxy in proxy_info['proxies']:
        proxy = proxy['proxy']
        proxies.append(proxy)

    proxy_info = requests.get('https://free-proxy-list.net/').text
    regex = re.compile(r'(\d+\.\d+\.\d+\.\d+):(\d+)')
    # Add http:// to the beginning of each proxy
    proxies += [f'http://{match[0]}:{match[1]}' for match in regex.findall(proxy_info)]

    proxy_info = requests.get('https://www.us-proxy.org/').text
    regex = re.compile(r'(\d+\.\d+\.\d+\.\d+):(\d+)')
    # Add http:// to the beginning of each proxy
    proxies += [f'http://{match[0]}:{match[1]}' for match in regex.findall(proxy_info)]

    proxy_info = requests.get('https://www.socks-proxy.net/').text
    regex = re.compile(r'(\d+\.\d+\.\d+\.\d+):(\d+)')
    # Add socks5:// to the beginning of each proxy
    proxies += [f'socks5://{match[0]}:{match[1]}' for match in regex.findall(proxy_info)]

    proxy_info = requests.get('https://www.juproxy.com/free_api').text
    # Add http:// to the beginning of each proxy
    proxies += [f'http://{proxy}' for proxy in proxy_info.split('\n')]
    '''
    # Current date
    date = datetime.now().strftime('%Y-%m-%d')
    proxy_info = requests.get(f'https://checkerproxy.net/api/archive/{date}').json()
    for proxy in proxy_info:
        if proxy['ip'] != "172.18.0.1": # Remove the default proxy
            if proxy['type'] == 1:
                proxy = proxy['addr']
                # Add http:// to the beginning of each proxy
                proxies.append(f'http://{proxy}')
            elif proxy['type'] == 2:
                proxy = proxy['addr']
                # Add https:// to the beginning of each proxy
                proxies.append(f'https://{proxy}')
            elif proxy['type'] == 4:
                proxy = proxy['addr']
                # Add socks5:// to the beginning of each proxy
                proxies.append(f'socks5://{proxy}')'''
    # Remove duplicates
    proxies = list(set(proxies))
    # Remove empty strings
    proxies = list(filter(None, proxies))
    '''
    # Check if the proxy is working
    for proxy in proxies:
        try:
            http_proxy = f"{proxy}"
            https_proxy = f"{proxy}"
            res = requests.get('https://api.ipify.org', proxies={'https': https_proxy, 'http': http_proxy}, timeout=15)
        except requests.exceptions.RequestException as e:
            # Remove the proxy if it's not working
            try:proxies.remove(proxy)
            except:pass
            continue
    '''
def get_data(item):
    global proxies
    global request_counts
    global sbd_got
    #for item in data:
    link = 'https://meta.hcm.edu.vn/examResult/65f381cf565cbdcf4e283663/result/' + str(item)
    if item.split('-')[0] not in str(sbd_got) and item not in sbd_wrong:
        try:
            while True:
                if item.split('-')[0] not in str(sbd_got) and item not in sbd_wrong:
                    try:
                        proxy = random.choice(proxies)
                        http_proxy = f"{proxy}"
                        https_proxy = f"{proxy}"
                        res = requests.get(link, proxies={'https': https_proxy, 'http': http_proxy}, timeout=15)
                        if res.status_code != 429 and '"sbd":' not in res.text:
                            #print(res.text)
                            print(f'{item}: Uncorrect')
                            request_counts += 1
                            with open('uncorrect.txt', 'a') as f:
                                f.write(f'{item}\n')
                            break
                        else:
                            print('Error: Rate limited')
                            proxy = random.choice(proxies)
                        if '"sbd":' in res.text:
                            with open('result.txt', 'a', encoding='utf-8') as f:
                                f.write(f'{item}: {res.text}\n')
                            print(f'{item}: {res.text}')
                            sbd_got.append(item)
                            request_counts += 1
                            break
                    except requests.exceptions.RequestException as e:
                        # Remove the proxy if it's not working
                        try:proxies.remove(proxy)
                        except:pass
                        continue
                else:
                    # print(f'{item}: Already got')
                    break
        except IndexError:
            print("No more proxies available.")
    else:
        #print(f'{item}: Already got')
        pass

def calculate_cpm():
    global request_counts
    global proxies
    print(f'{datetime.now().strftime("%H:%M:%S")}: 0 requests per minute')
    while True:
        time.sleep(60)
        # Devide by total time then multiply by 60 to get requests per minute
        cpm = request_counts / ((datetime.now() - start_time).seconds / 60)
        try:
            print(f'{datetime.now().strftime("%H:%M:%S")}: {cpm} requests per minute - {request_counts} requests in total')
        except ZeroDivisionError:
            print(f'{datetime.now().strftime("%H:%M:%S")}: 0 requests per minute')
        print(f'Got {len(proxies)} working proxies')
        if len(threading.enumerate()) <= 3:  # If there are only 3 threads running, it means the main function has finished
            return None

def get_proxies():
    global proxies
    get_proxy()
    print(f'Got {len(proxies)} proxies')
    global start_time
    start_time = datetime.now()
    time.sleep(15)  # Wait for the main function to start
    while True:
        if len(proxies) < 500:
            get_proxy()
        if len(threading.enumerate()) <= 3:  # If there are only 3 threads running, it means the main function has finished
            return None


def worker(data_queue):
    while not data_queue.empty():
        try:
            # Get the next item from the queue.
            item = data_queue.get_nowait()
        except queue.Empty:
            break  # The queue is empty.

        # Process the item.
        get_data(item)

        # Signal that the task is done.
        data_queue.task_done()


def main():
    while True:
        if len(proxies) > 100:
            data = generate_data()  # Your function to generate data.
            data_queue = queue.Queue()

            # Fill the queue with your data items.
            for item in data:
                data_queue.put(item)

            # Create and start 200 threads.
            threads = []
            for _ in range(200):
                t = threading.Thread(target=worker, args=(data_queue,))
                t.start()
                threads.append(t)

            # Wait for all items in the queue to be processed.
            data_queue.join()

            # Wait for all threads to complete (optional, since join ensures all tasks are done).
            for t in threads:
                t.join()
            break
threading.Thread(target=calculate_cpm).start()
threading.Thread(target=get_proxies).start()

if __name__ == "__main__":
    main()
    if len(threading.enumerate()) <= 3: # If there are only 3 threads running, it means the main function has finished
        print('Done')
        exit()

