import sys
import csv

def check_p95(jtl_file, sla_ms):
    elapsed_times = []
    with open(jtl_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('success', '').strip().lower() == 'true':
                try:
                    elapsed_times.append(int(row['elapsed']))
                except (ValueError, KeyError):
                    continue

    if not elapsed_times:
        print('ERROR: No successful samples found in JTL')
        sys.exit(1)

    elapsed_times.sort()
    p95   = elapsed_times[int(len(elapsed_times) * 0.95)]
    total = len(elapsed_times)

    print(f'Total samples : {total}')
    print(f'P95           : {p95}ms')
    print(f'SLA           : {sla_ms}ms')
    print(f'Result        : {"PASS" if p95 <= sla_ms else "FAIL"}')

    if p95 > sla_ms:
        print(f'GATE FAILED — P95 {p95}ms exceeds SLA {sla_ms}ms')
        sys.exit(1)

    print('GATE PASSED')
    sys.exit(0)

if __name__ == '__main__':
    check_p95(sys.argv[1], int(sys.argv[2]))
