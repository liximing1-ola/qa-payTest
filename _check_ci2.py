import requests

# Get the latest failed run
r = requests.get('https://api.github.com/repos/liximing1-ola/qa-payTest/actions/runs/38880446170/jobs?per_page=5')
jobs = r.json()
for j in jobs.get('jobs', []):
    if j.get('conclusion') == 'failure':
        print(f"=== Job: {j['name']} ===")
        # Get logs for the failed step
        for s in j.get('steps', []):
            if s.get('conclusion') == 'failure':
                print(f"\n--- Failed step: {s['name']} ---")
                log_url = s.get('log')
                if log_url:
                    # Try to get step log
                    headers = {'Accept': 'application/vnd.github.v3+json'}
                    r2 = requests.get(f"https://api.github.com/repos/liximing1-ola/qa-payTest/actions/jobs/{j['id']}/logs", headers=headers)
                    if r2.status_code == 200:
                        # Print last 100 lines
                        lines = r2.text.split('\n')
                        for line in lines[-100:]:
                            print(line)
                    else:
                        print(f"Could not get logs: {r2.status_code}")
        break
