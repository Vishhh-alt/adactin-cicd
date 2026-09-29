import sys, csv, os, glob

def get_p95(jtl_file):
    times = []
    with open(jtl_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('success', '').lower().strip() == 'true':
                try: times.append(int(row['elapsed']))
                except: continue
    times.sort()
    return times[int(len(times) * 0.95)] if times else 0

def check_trend(results_dir, current_jtl, drift_threshold_pct):
    all_jtls   = sorted(glob.glob(f'{results_dir}/adactin_*.jtl'))
    historical = [f for f in all_jtls if f != current_jtl]

    if len(historical) < 5:
        print(f'Only {len(historical)} historical builds — need 5. Skipping trend check.')
        sys.exit(0)

    recent       = historical[-5:]
    baseline_p95 = sum(get_p95(f) for f in recent) / len(recent)
    current_p95  = get_p95(current_jtl)
    drift_pct    = ((current_p95 - baseline_p95) / baseline_p95) * 100 if baseline_p95 > 0 else 0

    print(f'Baseline P95 (5-avg) : {baseline_p95:.0f}ms')
    print(f'Current P95          : {current_p95}ms')
    print(f'Drift                : {drift_pct:.1f}%')
    print(f'Drift threshold      : {drift_threshold_pct}%')

    if drift_pct > drift_threshold_pct:
        print(f'TREND GATE FAILED — {drift_pct:.1f}% drift exceeds {drift_threshold_pct}% threshold')
        sys.exit(1)

    print('TREND GATE PASSED')
    sys.exit(0)

if __name__ == '__main__':
    check_trend(sys.argv[1], sys.argv[2], float(sys.argv[3]))
