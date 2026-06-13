import re
import time
import socks
import socket
import urllib.request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

TOKEN = "8822193766:AAE37wp7qkk_SMVlknm6VufbXk5Mg7PaisY"
failed_proxies = []
used_proxies = []

def fetch_proxies_from_github():
    proxies = []
    sources = [
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
        "https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks5.txt"
    ]
    for url in sources:
        try:
            print(f"Loading {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8')
                for line in content.splitlines():
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#') and line.count(':') == 1:
                        if line not in failed_proxies and line not in used_proxies:
                            proxies.append(line)
        except:
            pass
    proxies = list(dict.fromkeys(proxies))
    print(f"Found new proxies to test: {len(proxies)}")
    return proxies

def check_proxy(ip, port):
    try:
        test_socket = socks.socksocket()
        test_socket.set_proxy(socks.SOCKS5, ip, int(port))
        test_socket.settimeout(3)
        test_socket.connect(("api.telegram.org", 443))
        test_socket.close()
        return True
    except:
        return False

def find_working_proxy():
    print("Looking for working proxy...")
    proxies = fetch_proxies_from_github()
    if not proxies:
        proxies = ["185.242.7.35:1080", "45.139.174.38:1080"]
    
    for proxy in proxies:
        ip, port = proxy.split(':')
        if proxy in used_proxies:
            continue
        print(f"Testing {ip}:{port}")
        if check_proxy(ip, port):
            print(f"FOUND WORKING PROXY: {ip}:{port}")
            used_proxies.append(proxy)
            return f"socks5://{ip}:{port}"
        else:
            print(f"Proxy {ip}:{port} failed")
            failed_proxies.append(proxy)
            continue
    
    print("No working proxy found")
    return None

async def handle_message(update, context):
    msg = update.message
    print("="*50)
    print("MESSAGE RECEIVED!")
    if msg and msg.text:
        print(f"Text: {msg.text}")
        print(f"From: {msg.from_user.username if msg.from_user else 'unknown'}")
        await msg.reply_text('Privet')
        print("Reply sent: Privet")
    else:
        print("No text in message")
    print("="*50)

def main():
    print("="*50)
    print("STARTING BOT")
    print("="*50)
    while True:
        try:
            proxy_url = find_working_proxy()
            if proxy_url:
                print(f"\n>>> USING PROXY: {proxy_url}\n")
                request = HTTPXRequest(proxy_url=proxy_url, connect_timeout=15, read_timeout=30)
            else:
                print("\n>>> NO PROXY, WORKING DIRECTLY\n")
                request = None
            
            app = Application.builder().token(TOKEN).request(request).build()
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            print("\n>>> BOT IS RUNNING. SEND IT A MESSAGE TO TEST.\n")
            app.run_polling()
            
        except Exception as e:
            print(f"\n>>> ERROR: {e}\n")
            print(">>> Restarting in 10 seconds...\n")
            time.sleep(10)
            continue

if __name__ == '__main__':
    main()