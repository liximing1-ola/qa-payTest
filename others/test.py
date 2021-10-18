import requests

def test():
    url = 'http://192.168.11.46/test?uid=105002093&rid=200000563'
    res = requests.get(url)
    print(res)