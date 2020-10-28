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
def getStockList(lst, stockURL):          #获取股票代码列表
    html = getHTMLText(stockURL, "GB2312")
    soup = BeautifulSoup(html, 'html.parser')
    lst_raw = []
    a = soup.find_all('a')      #得到一个列表
    for i in a:
        try:
            href = i.attrs['href']       #股票代码都存放在href标签中
            lst_raw.append("0" + re.findall(r"[S][HZ]\d{6}", href)[0][2:8])
        except:
            continue
            
    lst = list(set(lst_raw))            
            
def main():
    stock_list_url = 'https://hq.gucheng.com/gpdmylb.html'
    stock_nos=[]
    getStockList(stock_nos, stock_list_url)
    for stock_no in stock_nos:
        code = 'http://quotes.money.163.com/service/chddata.html?code=' + stock_no + '&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
        http = urllib3.PoolManager()
        if not os.path.exists(stock_no):
            os.makedirs('stocks/'+stock_no)

        response = http.request('GET',code)
        with open('stocks/'+ stock_no + '/code.csv', 'wb') as f:
            f.write(response.data)
        response.release_conn()
        print('完成'+stock_no)


main()
