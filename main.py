import asyncio
import csv,time
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

SUCCESS = Fore.GREEN
ERROR = Fore.RED
INFO = Fore.CYAN
HIGHLIGHT = Fore.MAGENTA
MUTED = Fore.LIGHTBLACK_EX
RESET = Style.RESET_ALL
ORANGE = "\033[38;5;208m"
BRIGHT_GREEN = "\033[38;5;82m"
SOFT_GREEN = "\033[38;5;120m"
REAL_ORANGE = "\033[38;2;255;140;0m"
stats_data = []

def print_banner():
    banner = f"""
{REAL_ORANGE}
███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗██╗      ██████╗     ██████╗ ██████╗  ██████╗ ███████╗
████╗ ████║██╔═══██╗██╔══██╗██║   ██║██║     ██╔═══██╗    ██╔══██╗██╔══██╗██╔═══██╗██╔════╝
██╔████╔██║██║   ██║██║  ██║██║   ██║██║     ██║   ██║    ██║  ██║██║  ██║██║   ██║███████╗
██║╚██╔╝██║██║   ██║██║  ██║██║   ██║██║     ██║   ██║    ██║  ██║██║  ██║██║   ██║╚════██║
██║ ╚═╝ ██║╚██████╔╝██████╔╝╚██████╔╝███████╗╚██████╔╝    ██████╔╝██████╔╝╚██████╔╝███████║
╚═╝     ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝ ╚═════╝     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

{Style.DIM}{Fore.WHITE}by Qudratillo Salohiddinov{Style.RESET_ALL}
"""
    print(banner)
    time.sleep(2)

print_banner()
# Async request
async def send_request(request_id, target_ip, target_port):
    send_time = asyncio.get_event_loop().time()
    status_code = "0"
    status_msg = "failed"
    error_detail = "None"
    latency = 0
    sent_len = 0

    try:
        reader, writer = await asyncio.open_connection(target_ip, target_port)
        request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nConnection: close\r\n\r\n"
        encoded_request = request.encode()
        sent_len = len(encoded_request)

        start = asyncio.get_event_loop().time()
        writer.write(encoded_request)
        await writer.drain()
        data = await reader.read(1024)
        latency = asyncio.get_event_loop().time() - start

        if data:
            status_msg = "success"
            try:
                status_code = data.decode().split()[1]
            except IndexError:
                status_code = "unknown"

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        latency = asyncio.get_event_loop().time() - send_time
        error_detail = type(e).__name__

    # Print live log
    if status_msg == "success":
        print(f"{SUCCESS}[OK]{RESET} {HIGHLIGHT}#{request_id}{RESET} {MUTED}{latency:.4f}s{RESET} STATUS={status_code} {Fore.LIGHTCYAN_EX}{target_ip}:{target_port}{Fore.RESET}")
    else:
        print(f"{ERROR}[XATO]{RESET} {HIGHLIGHT}#{request_id}{RESET} {MUTED}{latency:.4f}s{RESET} {ERROR}{error_detail}{RESET}")

    stats_data.append({
        "request_id": request_id,
        "timestamp": datetime.now().strftime("%H:%M:%S.%f"),
        "latency_sec": round(latency, 4),
        "bytes_sent": sent_len,
        "http_status": status_code,
        "outcome": status_msg,
        "error_type": error_detail
    })

# Save CSV
def save_to_csv(filename):
    if not stats_data:
        print(ERROR + "Ma'lumot topilmadi!")
        return
    keys = stats_data[0].keys()
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(stats_data)
    print(f"{SUCCESS}SAQLANDI:{RESET} {HIGHLIGHT}{filename}{RESET}")

# Main async runner
async def main(target_ip, target_port, num_requests):
    tasks = [send_request(i, target_ip, target_port) for i in range(num_requests)]
    await asyncio.gather(*tasks)

import argparse
parser = argparse.ArgumentParser(description="Async Network Tester")
parser.add_argument("--ip", required=True)
parser.add_argument("--port", type=int, default=80)
parser.add_argument("--requests", type=int, default=100)
parser.add_argument("--output", default="result.csv")
args, unknown = parser.parse_known_args()
asyncio.run(main(args.ip, args.port, args.requests))
save_to_csv(args.output)