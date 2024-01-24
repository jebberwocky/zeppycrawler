from lxml import html
import requests
import configparser
from email.message import EmailMessage
import pathlib
from pathlib import Path
import smtplib, ssl
import csv


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


def requestURL(url):
    return  requests.get(url)

def parse(url, xpath):
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
            output.append([y,m,w,element.cssselect('h2.sch-content-text__performer')[0].text])
            #output.append('\t'+element.cssselect('h3.sch-content-text__ttl')[0].text)

def zeppy(fm,tm,v):
    for hall in v:
        output.append([hall])
        print(hall)
        for i in range(fm, tm):
            print(i)
            #output.append(str(i))
            parse("https://www.zepp.co.jp/hall/"+hall+"/schedule/?_y=2024&_m="+str(i),
                'a.sch-content')
    print('\n'.join(' '.join(x) for x in output))
    with open('output.txt', 'w') as f:
        f.write('\n'.join(' '.join(x) for x in output))
    msg = EmailMessage()
    msg.set_content('\n'.join(' '.join(x) for x in output))
    msg['Subject'] = "Zeppy"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    #only sending email in production
    if stage == 'production' and  config['email']['email'] :
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(msg, from_addr=sender_email, to_addrs=receiver_email.split(","))
    #
    if config['csv']['csv']:
        with open(config['csv']['directory']+'/test.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(output)
            f.close()


if __name__ == '__main__':
    #zeppy(1,13,['divercity','sapporo','haneda','shinjuku','yokohama','nagoya','osakabayside','fukuoka'])
    zeppy(1,13,['divercity','sapporo'])