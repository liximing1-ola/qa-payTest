import requests, json

r = requests.get('https://api.github.com/repos/liximing1-ola/qa-payTest/actions/runs?per_page=3')
data = r.json()
for w in data.get('workflow_runs', []):
    print(f"ID: {w['id']}, Status: {w['status']}, Conclusion: {w['conclusion']}, Created: {w['created_at']}")
    # Get jobs for this run
    r2 = requests.get(f"https://api.github.com/repos/liximing1-ola/qa-payTest/actions/runs/{w['id']}/jobs?per_page=5")
    jobs = r2.json()
    for j in jobs.get('jobs', []):
        print(f"  Job: {j['name']}, Status: {j['status']}, Conclusion: {j['conclusion']}")
        # Get steps
        for s in j.get('steps', []):
            if s.get('conclusion') == 'failure':
                print(f"    FAILED STEP: {s['name']} (status={s['status']})")
