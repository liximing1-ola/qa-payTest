import requests

# Try to get the raw log for the failed job
# Job ID for 3.12 failure
job_id = None
r = requests.get('https://api.github.com/repos/liximing1-ola/qa-payTest/actions/runs/38880446170/jobs?per_page=5')
jobs = r.json()
for j in jobs.get('jobs', []):
    if j.get('conclusion') == 'failure':
        job_id = j['id']
        print(f"Found failed job: {j['name']} (ID: {job_id})")
        break

if job_id:
    # Try different log endpoints
    for url in [
        f"https://api.github.com/repos/liximing1-ola/qa-payTest/actions/jobs/{job_id}/logs",
    ]:
        r2 = requests.get(url, headers={'Accept': 'application/vnd.github.v3.raw'})
        print(f"URL: {url}, Status: {r2.status_code}")
        if r2.status_code == 200:
            lines = r2.text.split('\n')
            # Print last 200 lines to find test failures
            for line in lines[-200:]:
                print(line)
            break
        else:
            print(f"  Response: {r2.text[:200]}")
