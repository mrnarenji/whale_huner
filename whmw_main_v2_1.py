#install on server: python-venv-pip-selenium-webdriver_manager-bs4-telethon-pytz-datetime & google chrome
#settings: duration, interval, sleep, telegram channels, headless 
#no longer supported


#-1001838385325 whmw_test
#-1001628157906 main whale hunters channel
#-1001686786349 whale hunter market watch

# replace API Key & Telegram Bot Token


#V2:
#- Symbols Rank Checker Added
#- every selenium driver launch saves only tokens of the according duration and results are not cumulative

    #V2_1:
    #Update telegram messaging
    #binance page updated



#توی این پروژه از وب درایور سلنیوم استفاده می‌کنیم تا صفحه‌ای که یکجا لود نمیشه رو بتونیم لود کنیم
from selenium import webdriver
#از کروم استفاده میکنیم برای لود کردن صفحه
from webdriver_manager.chrome import ChromeDriverManager
#این کتابخونه بهمون اجازه میده که بتونیم عناصری که میخایم رو توی صفحه تشخیص بدیم و روشون کلیک کنیم
from selenium.webdriver.common.by import By
# #این کتابخونه بهمون اجازه میده صفحه رو ببریم اونجایی که دلمون میخاد و یه کارایی توش انجام بدیم
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

#from telethon import TelegramClient, sync
import time
from datetime import datetime, time as dt_time

import pytz
import traceback

import itertools

import requests
import json

#-------------------------------------------------------------
#-------------------------------------------------------------
#Functions
#-------------------------------------------------------------
#-------------------------------------------------------------

def sel_launch(url):
    
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument('--no-sandbox')
    #  اگر درایور مناسب برای کروم نصب نباشه باید درایور مناسب رو نصب کنه
    try:
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        #driver=webdriver.Chrome(options=chrome_options)
    except:
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    driver.get(url)

    return driver



def binance_initiator():
    #-------------------------------------------------------------
    #binance initiate
    #-------------------------------------------------------------
    binance_url='https://www.binance.com/en/markets/trading_data'
    binance_page=sel_launch(binance_url)
    time.sleep(5)
    #    برای اولین بار یه باکس کوکی نشون میده که باید از دستش خلاص بشیم
    button=binance_page.find_element(By.XPATH, '//button[@id="onetrust-reject-all-handler"]')
    if button.is_displayed():
        button.click()
    #button = binance_page.find_element(By.ID,"market_sector_overview")
    #button.click()
    print("binance launched successfully")

    return binance_page


def kucoin_initiator():
    #-------------------------------------------------------------
    #kucoin initiate
    #-------------------------------------------------------------
    kucoin_url='https://www.kucoin.com/markets?spm=kcWeb.B1homepage.Header3.1'
    kucoin_page=sel_launch(kucoin_url)
    print("kucoin launched successfully")
    
    return kucoin_page


def kucoin_scraper(target_dict, kucoin_page, btn, sleeptime):
    btn.click()
    time.sleep(sleeptime)
    soup=BeautifulSoup(kucoin_page.page_source, 'html.parser')
    div=soup.find_all('h2', attrs={'class':'lrtcss-1w9xz0o'})
    for item in div[:10]:
        if str(item.text) not in target_dict:
            target_dict[str(item.text)]=1
        else:
            target_dict[str(item.text)]+=1
    

def binance_scraper(binance_page, binance_gainers, binance_loosers):
    soup=BeautifulSoup(binance_page.page_source, 'html.parser')
    div=soup.select(".css-lzsise", limit=20)

    for j in range(0,10):
        g=div[j].findChild("div", class_="css-y361ow").text
        l=div[j+10].findChild("div", class_="css-y361ow").text

        if str(g) not in binance_gainers:
            binance_gainers[str(g)]=1
        else:
            binance_gainers[str(g)]+=1

        if str(l) not in binance_loosers:
            binance_loosers[str(l)]=1
        else:
            binance_loosers[str(l)]+=1       


def get_ranks(symbols):
    symbols_string = ','.join(symbols)
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbols_string}&CMC_PRO_API_KEY=here"
    headers = { "Accepts": "application/json"}
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    return data

def print_crypto_info(crypto_dict):
    symbols = list(crypto_dict.keys())
    data = get_ranks(symbols)
    ranks = []
    for symbol, value in crypto_dict.items():
        try:
            rank = data['data'][symbol]['cmc_rank']
            ranks.append(rank)
        except KeyError:
            ranks.append(None)
    return ranks


def rank_checker(targetdict,itemcount):
    new_dict = dict(itertools.islice(targetdict.items(), itemcount))
    ranks=print_crypto_info(new_dict)
    return ranks

def message_creator(exchange,kucoin_gainers,kucoin_loosers,binance_gainers,binance_loosers,itemcount):
    
    if exchange=='kucoin':
        ranks_kucoin_gainers = rank_checker(kucoin_gainers, itemcount)
        ranks_kucoin_loosers = rank_checker(kucoin_loosers, itemcount)
    else:
        ranks_binance_gainers = rank_checker(binance_gainers, itemcount)
        ranks_binance_loosers = rank_checker(binance_loosers, itemcount)

    message=f"{exchange.capitalize()}:\n----------\n\U0001F7E2 Top Gainers:\n"

    g_counter=1
    l_counter=1

    for (key, value),item in zip(kucoin_gainers.items(),ranks_kucoin_gainers) if exchange=='kucoin' else zip(binance_gainers.items(),ranks_binance_gainers):
        message=message+f"{key} ({value}) > {item}\n"
        if g_counter==itemcount:
            break
        g_counter+=1

    message=message+'\n\U0001F534 Top Loosers:\n'

    for (key, value),item in zip(kucoin_loosers.items(),ranks_kucoin_loosers) if exchange=='kucoin' else zip(binance_loosers.items(),ranks_binance_loosers):
        message=message+f"{key} ({value}) > {item}\n"
        if l_counter==itemcount:
            break
        l_counter+=1

    return message


def dict_combiner(dict1,dict2):
    output = dict1.copy()
    for key, value in dict2.items():
        output[key] = output.get(key, 0) + value
    
    return output

def send_to_telegram(chatid,message):

    apiToken = ''
    chatID = chatid
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
    except Exception as e:
        print(e)

#-------------------------------------------------------------
#-------------------------------------------------------------
# Main Program
#-------------------------------------------------------------
#-------------------------------------------------------------


code_executed = False
while True:

    mainloop_start_time=datetime.now(pytz.timezone('Asia/Tehran'))
    mainloop_start_str="Start: "+mainloop_start_time.strftime("%d/%m/%Y %H:%M:%S")

    daily_kucoin_gainers={}
    daily_kucoin_loosers={}
    daily_binance_gainers={}
    daily_binance_loosers={}

    interval=60*5 #5m=60*5
    duration=60*60*4 #4h=60*60*4
    sleep=2

    count=int(duration/interval)

    start_time_period = dt_time(8, 00) # 8am=8,00
    end_time_period = dt_time(8, 30) # 8:30am=8,30

    flag=False
    while not flag:
        
        kucoin_gainers={}
        kucoin_loosers={}
        binance_gainers={}
        binance_loosers={}
        
        try:
            print(f"\nScraping initiated successfully - time: "+datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M:%S"))

            innerloop_start_time=datetime.now(pytz.timezone('Asia/Tehran'))
            innerloop_start_str="Start: "+innerloop_start_time.strftime("%d/%m/%Y %H:%M:%S")

            binance_page=binance_initiator()

            kucoin_page=kucoin_initiator()
            time.sleep(10)
            btn = kucoin_page.find_element(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "lrtcss-1kj8yx6", " " )) and (((count(preceding-sibling::*) + 1) = 3) and parent::*)]//span')

            for i in range(0,count):

                current_time = datetime.now(pytz.timezone('Asia/Tehran')).time()
                if start_time_period <= current_time <= end_time_period and not code_executed:
                    code_executed = True
                    flag = True
                    break
                elif current_time > end_time_period:
                    code_executed = False

                print(f"\nInterval {i+1}/{count} Started - time: "+datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M:%S"))

                #-------------------------------------------------------------
                #kucoin loop
                #-------------------------------------------------------------
                kucoin_scraper(kucoin_loosers, kucoin_page, btn, sleep)
                kucoin_scraper(kucoin_gainers, kucoin_page, btn, sleep)
                btn.click()
                
                print(f"Kucoin Scraping Finished & Binance Scraping Started - time: "+datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M:%S"))

                #-------------------------------------------------------------
                #binance loop
                #-------------------------------------------------------------
                binance_scraper(binance_page, binance_gainers, binance_loosers)

                print(f"Interval {i+1}/{count} Finished  - time: "+datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M:%S"))
                print('Code Executed:', code_executed, ' -flag:', flag, ' -time', current_time)

                if i!=count-1:
                    time.sleep(interval)
                

            kucoin_page.close()
            binance_page.close()
        except Exception:
            current_time = datetime.now(pytz.timezone('Asia/Tehran')).time()
            error=traceback.format_exc()
            send_to_telegram('-1001838385325', "Error:\n"+str(current_time)+"\n\n"+error)
            time.sleep(600)
            pass

        sorted_kucoin_loosers=dict(sorted(kucoin_loosers.items(), key=lambda item: item[1], reverse=True))
        sorted_kucoin_gainers=dict(sorted(kucoin_gainers.items(), key=lambda item: item[1], reverse=True))
        sorted_binance_gainers=dict(sorted(binance_gainers.items(), key=lambda item: item[1], reverse=True))
        sorted_binance_loosers=dict(sorted(binance_loosers.items(), key=lambda item: item[1], reverse=True))

        listofsorted=[sorted_kucoin_gainers,sorted_kucoin_loosers,sorted_binance_gainers,sorted_binance_loosers]

        kucoin_gainers=listofsorted[0]
        kucoin_loosers=listofsorted[1]
        binance_gainers=listofsorted[2]
        binance_loosers=listofsorted[3]

        daily_binance_gainers=dict_combiner(daily_binance_gainers,binance_gainers)
        daily_binance_loosers=dict_combiner(daily_binance_loosers, binance_loosers)
        daily_kucoin_gainers=dict_combiner(daily_kucoin_gainers, kucoin_gainers)
        daily_kucoin_loosers=dict_combiner(daily_kucoin_loosers, kucoin_loosers)

        innerloop_finish_time=datetime.now(pytz.timezone('Asia/Tehran'))
        innerloop_finish_str="Finish: "+innerloop_finish_time.strftime("%d/%m/%Y %H:%M:%S")

        innerloop_duration_delta=innerloop_finish_time-innerloop_start_time
        innerloop_duration_str="Duration: "+str(innerloop_duration_delta).split('.')[0]

        send_to_telegram('-1001686786349', innerloop_start_str+"\n"+innerloop_finish_str+"\n"+innerloop_duration_str+"\n\n"+message_creator('kucoin',kucoin_gainers,kucoin_loosers,binance_gainers,binance_loosers,20))
        send_to_telegram('-1001686786349', innerloop_start_str+"\n"+innerloop_finish_str+"\n"+innerloop_duration_str+"\n\n"+message_creator('binance',kucoin_gainers,kucoin_loosers,binance_gainers,binance_loosers,20))

        if flag:
            break
    


    sorted_daily_kucoin_loosers=dict(sorted(daily_kucoin_loosers.items(), key=lambda item: item[1], reverse=True))
    sorted_daily_kucoin_gainers=dict(sorted(daily_kucoin_gainers.items(), key=lambda item: item[1], reverse=True))
    sorted_daily_binance_gainers=dict(sorted(daily_binance_gainers.items(), key=lambda item: item[1], reverse=True))
    sorted_daily_binance_loosers=dict(sorted(daily_binance_loosers.items(), key=lambda item: item[1], reverse=True))

    listofsorted=[sorted_daily_kucoin_gainers,sorted_daily_kucoin_loosers,sorted_daily_binance_gainers,sorted_daily_binance_loosers]

    daily_kucoin_gainers=listofsorted[0]
    daily_kucoin_loosers=listofsorted[1]
    daily_binance_gainers=listofsorted[2]
    daily_binance_loosers=listofsorted[3]


    mainloop_finish_time=datetime.now(pytz.timezone('Asia/Tehran'))
    mainloop_finish_str="Finish: "+mainloop_finish_time.strftime("%d/%m/%Y %H:%M:%S")

    mainloop_duration_delta=mainloop_finish_time-mainloop_start_time
    mainloop_duration_str="Duration: "+str(mainloop_duration_delta).split('.')[0]

    send_to_telegram('-1001628157906', mainloop_start_str+"\n"+mainloop_finish_str+"\n"+mainloop_duration_str+"\n\n"+message_creator('kucoin',daily_kucoin_gainers,daily_kucoin_loosers,daily_binance_gainers,daily_binance_loosers,20))
    send_to_telegram('-1001628157906', mainloop_start_str+"\n"+mainloop_finish_str+"\n"+mainloop_duration_str+"\n\n"+message_creator('binance',daily_kucoin_gainers,daily_kucoin_loosers,daily_binance_gainers,daily_binance_loosers,20))

    time.sleep(5)
