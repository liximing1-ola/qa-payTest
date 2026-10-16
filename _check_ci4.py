import requests

r = requests.get('https://api.github.com/repos/liximing1-ola/qa-payTest/actions/runs?per_page=5')
data = r.json()
for w in data.get('workflow_runs', []):
    print(f"ID: {w['id']}, Status: {w['status']}, Conclusion: {w['conclusion']}, Created: {w['created_at']}, Head: {w['head_sha'][:7]}")
