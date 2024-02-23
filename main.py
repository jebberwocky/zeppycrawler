from lxml import html
import requests
import configparser
from email.message import EmailMessage
import pathlib
from pathlib import Path
import smtplib, ssl
import csv
import sqlite3
from datetime import datetime

now = datetime.now()
path: Path = pathlib.Path(__file__).parent.resolve()
config = configparser.ConfigParser()
#print(str(path)+'/default.ini')
config.read(str(path)+'/default.ini')
stage = config['env']['stage']
debug = config['env']['debug']
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = config['email']['sender'] # Enter your address
receiver_email = config['email']['to']  # Enter receiver address
password = config['email']['apppwd'] 
output = []
new_events = []
rows = []


def requestURL(url):
    return  requests.get(url)

def parse(url, xpath, hall):
    with sqlite3.connect(str(path)+"/events.db") as connection:
        cursor = connection.cursor()
        _rows = cursor.execute("SELECT name FROM events").fetchall()
        for _r in _rows:
            rows.append(_r[0])
        pageResp = requestURL(url)
        tree = html.fromstring(pageResp.text)
        elements = tree.cssselect(xpath) 
        #print(elements)
        for element in elements:
            y = element.cssselect('p.sch-content-date__year')[0].text
            m = element.cssselect('p.sch-content-date__month')[0].text
            w = element.cssselect('p.sch-content-date__week')[0].text
            if len(element.cssselect('h2.sch-content-text__performer'))>0:
                #output.append(''+y+' '+m+' '+w)
                #output.append(''+element.cssselect('h2.sch-content-text__performer')[0].text)
                performer = element.cssselect('h2.sch-content-text__performer')[0].text
                output.append([y,m,w,performer])
                if performer not in rows:
                    new_events.append([y,m,w,performer,hall])
                    cursor.execute("INSERT INTO events VALUES (?)", (performer,))
    connection.commit()                
                #output.append('\t'+element.cssselect('h3.sch-content-text__ttl')[0].text)
                
def new_events_str():
    if len(new_events) >0:
        return "new events\n"+'\n'.join(' '.join(x) for x in new_events)+"\n"
    else:
        return "\n"

def zeppy(fm,tm,v):
    for hall in v:
        output.append(['\n',hall])
        print(hall)
        for i in range(fm, tm):
            if i >= datetime.now().month:
                print(i)
                #output.append(str(i))
                parse("https://www.zepp.co.jp/hall/"+hall+"/schedule/?_y=2024&_m="+str(i),
                    'a.sch-content', hall)
            
    print('\n'.join(' '.join(x) for x in output))
    with open('output.txt', 'w') as f:
        f.write(new_events_str()+"\n"+'\n'.join(' '.join(x) for x in output))
    #mail
    msg = EmailMessage()
    msg.set_content(new_events_str()+'\n'.join(' '.join(x) for x in output))
    msg['Subject'] = "Zeppy"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    #only sending email in production
    if stage == 'production' and  config['email']['email'] :
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(msg, from_addr=sender_email, to_addrs=receiver_email.split(","))
    #csv
    if config['csv']['csv']:
        with open(config['csv']['directory']+'/test.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(output)
            f.close()

    print(new_events_str())

def eplus():
    eplus_out = []
    for i in range(1, 2):
        print(str(i))
        url = "https://ib.eplus.jp/index.php?dispatch=tour_group.ajax_get_tour_group&area_ids%5B0%5D=1&area_ids%5B1%5D=2&area_ids%5B2%5D=3&area_ids%5B3%5D=4&category_ids%5B0%5D=1&category_ids%5B1%5D=2&category_ids%5B2%5D=4&page="+str(i)+"&result_ids=top_product_list&is_ajax=0&render_type=html"
        payload = {}
        headers = {
        'authority': 'ib.eplus.jp',
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': 'KOJIN_SHIKIBETSU=240217190144S33176; _gcl_au=1.1.2107173230.1708164108; __lt__cid=2ebd7c4b-d08c-477a-873c-30ac820d8a4b; _yjsu_yjad=1708164109.26b1780b-8349-4ebf-8baa-76b319e55838; _tt_enable_cookie=1; _ttp=VcvJgJNRQOuFC8hqMoGvw6L-bFb; usertrack_asp3=1697102508947.462230884; _fbp=fb.1.1708164111139.815085140; _ga_SQ2W44L884=GS1.1.1708164108.1.0.1708164116.52.0.0; sid_customer_7ebb3=32b38917755abc9e1763a1fd9392dfe3-1-C; _ga=GA1.3.722244723.1708164108; _gid=GA1.3.1531724436.1708502290; _gid=GA1.2.1531724436.1708502290; gdpr_settings=%7B%22allow%22%3A%22I_ACCEPT%22%7D; _ga=GA1.2.722244723.1708164108; _ga_E8TF4GDJFW=GS1.1.1708502289.1.1.1708502922.0.0.0; sid_customer_7ebb3=32b38917755abc9e1763a1fd9392dfe3-1-C',
        'referer': 'https://ib.eplus.jp/index.php?dispatch=index.index&area_ids%5B%5D=1&area_ids%5B%5D=2&category_ids%5B%5D=1&category_ids%5B%5D=2&category_ids%5B%5D=4&area_ids%5B%5D=3&area_ids%5B%5D=4',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        #print(response.text)
        tree = html.fromstring(response.text)
        elements = tree.cssselect("div.caption") 
        for element in elements:
            eplus_out.append({'t':element.cssselect('h5')[0].text,
                              'd':element.cssselect('div.description')[0].text})
    context = '\n\n'.join(map(lambda x: x['t']+"\n"+x['d'],eplus_out ))
     #mail
    msg = EmailMessage()
    msg.set_content(context)
    msg['Subject'] = "eplus"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    #only sending email in production
    if stage == 'production' and  config['email']['email'] :
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(msg, from_addr=sender_email, to_addrs=receiver_email.split(","))




if __name__ == '__main__':
    print(now.strftime("%m/%d/%Y, %H:%M:%S"))
    output.append([now.strftime("%m/%d/%Y, %H:%M:%S")])
    zeppy(1,13,['divercity','sapporo','haneda','shinjuku','yokohama','nagoya','osakabayside','fukuoka'])
    #zeppy(1,13,['divercity','sapporo'])
    eplus()