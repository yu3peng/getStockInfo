import requests
from bs4 import BeautifulSoup
import urllib.request
import re
import urllib3
import os
import time
import re  

def getHTMLText(url, code="utf-8"):  #获取HTML文本
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ""

# 获取股票代码列表
def getStockList(list, list_url):          #获取股票代码列表
    html = getHTMLText(list_url, "GB2312")
    soup = BeautifulSoup(html, 'html.parser') 
    a = soup.find_all('a')      #得到一个列表
    for i in a:
        try:
            href = i.attrs['href']       #股票代码都存放在href标签中
            prenandno = re.findall(r"[S][HZ]\d{6}", href)[0]
            stockno = '0' + prenandno[2,7]
            list.append(stockno)
        except:
            continue
                  
def main():
    stock_list_url = 'https://hq.gucheng.com/gpdmylb.html'
    stock_list=[]
    getStockList(stock_list, stock_list_url)    
    for stock_no in stock_list:

        zycwzb = 'http://quotes.money.163.com/service/zycwzb_'+ stock_no +'.html?type=report'
        ylnl = 'http://quotes.money.163.com/service/zycwzb_'+ stock_no +'.html?type=report&part=ylnl'
        chnl = 'http://quotes.money.163.com/service/zycwzb_'+ stock_no +'.html?type=report&part=chnl'
        cznl = 'http://quotes.money.163.com/service/zycwzb_'+ stock_no +'.html?type=report&part=cznl'
        yynl = 'http://quotes.money.163.com/service/zycwzb_'+ stock_no +'.html?type=report&part=yynl'
        cwbbzy = 'http://quotes.money.163.com/service/cwbbzy_'+ stock_no +'.html'
        zcfzb = 'http://quotes.money.163.com/service/zcfzb_'+ stock_no +'.html'
        lrb = 'http://quotes.money.163.com/service/lrb_'+ stock_no +'.html'
        xjllb = 'http://quotes.money.163.com/service/xjllb_'+ stock_no +'.html'

        http = urllib3.PoolManager()

        if not os.path.exists(stock_no):
            os.makedirs('stocks/'+stock_no)

        response = http.request('GET', zycwzb)
        with open('stocks/'+ stock_no + '/zycwzb.csv', 'wb') as f:
            f.write(response.data)

        response = http.request('GET', ylnl)
        with open('stocks/'+ stock_no + '/ylnl.csv', 'wb') as f:
            f.write(response.data)

        response = http.request('GET', chnl)
        with open('stocks/'+ stock_no + '/chnl.csv', 'wb') as f:
            f.write(response.data)

        response = http.request('GET', cznl)
        with open('stocks/'+ stock_no + '/cznl.csv', 'wb') as f:
            f.write(response.data)

        response = http.request('GET', yynl)
        with open('stocks/'+ stock_no + '/yynl.csv', 'wb') as f:
            f.write(response.data)

        response = http.request('GET', cwbbzy)
        with open('stocks/'+ stock_no + '/cwbbzy.csv', 'wb') as f:
            f.write(response.data)

        response = http.request('GET', zcfzb)
        with open('stocks/'+ stock_no + '/zcfzb.csv', 'wb') as f:
            f.write(response.data)

        response = http.request('GET', lrb)
        with open('stocks/'+ stock_no + '/lrb.csv', 'wb') as f:
            f.write(response.data)

        response = http.request('GET', xjllb)
        with open('stocks/'+ stock_no + '/xjllb.csv', 'wb') as f:
            f.write(response.data)

        response.release_conn()
        print('完成'+stock_no)
        time.sleep(3)

main()        
