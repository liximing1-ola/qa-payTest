import requests

r = requests.get('https://api.github.com/repos/liximing1-ola/qa-payTest/actions/runs?per_page=3')
data = r.json()
for w in data.get('workflow_runs', []):
    print(f"Run ID: {w['id']}, Status: {w['status']}, Conclusion: {w['conclusion']}, Created: {w['created_at']}, Head: {w['head_sha'][:7]}")
    r2 = requests.get(f"https://api.github.com/repos/liximing1-ola/qa-payTest/actions/runs/{w['id']}/jobs?per_page=5")
    jobs = r2.json()
    for j in jobs.get('jobs', []):
        print(f"  Job: {j['name']}, Conclusion: {j['conclusion']}")
        for s in j.get('steps', []):
            marker = " <--" if s.get('conclusion') == 'failure' else ""
            print(f"    Step {s['number']}: {s['name']} - {s['conclusion']}{marker}")
