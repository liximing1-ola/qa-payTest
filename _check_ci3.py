import requests, os

token = os.environ.get('GITHUB_TOKEN', '')
headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'} if token else {'Accept': 'application/vnd.github.v3+json'}

# Get job details for the failed run
r = requests.get('https://api.github.com/repos/liximing1-ola/qa-payTest/actions/runs/38880446170/jobs?per_page=5', headers=headers)
jobs = r.json()
for j in jobs.get('jobs', []):
    print(f"Job: {j['name']}, Conclusion: {j['conclusion']}")
    for s in j.get('steps', []):
        print(f"  Step: {s['number']} {s['name']} - {s['conclusion']}")
    if j.get('conclusion') == 'failure':
        # Try to get logs
        r2 = requests.get(f"https://api.github.com/repos/liximing1-ola/qa-payTest/actions/jobs/{j['id']}/logs", headers=headers)
        print(f"  Log status: {r2.status_code}")
        if r2.status_code == 200:
            lines = r2.text.split('\n')
            # Find test failure lines
            for i, line in enumerate(lines):
                if 'FAILED' in line or 'ERROR' in line or 'assert' in line.lower() or 'ModuleNotFoundError' in line:
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    for l in lines[start:end]:
                        print(f"    {l}")
                    print("    ---")
