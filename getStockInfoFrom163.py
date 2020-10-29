import requests
from bs4 import BeautifulSoup
import urllib.request
import re
import urllib3
import os
import time
import multiprocessing
from multiprocessing import Pool

# 获取HTML文本
def getHTMLText(url, code="utf-8"):  
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ""

# 获取股票代码列表
def getStockList(stockList):
    html = getHTMLText('https://hq.gucheng.com/gpdmylb.html', "GB2312")
    soup = BeautifulSoup(html, 'html.parser')
    # 得到一个列表
    a = soup.find_all('a')
    for i in a:
        try:
            # 股票代码都存放在href标签中
            href = i.attrs['href']
            # re.findall(r"[S][HZ]\d{6}", href)[0]，从gucheng网获取到的股票代码为SH000001格式，需要转换为163上需要的格式0000001
            stockNO = "0" + re.findall(r"[S][HZ]\d{6}", href)[0][2:8]
            if stockNO not in stockList:
                stockList.append("0" + re.findall(r"[S][HZ]\d{6}", href)[0][2:8])
        except:
            continue

# 获取股票信息
def getStockInfo(stockNO)：            
    # TCLOSE收盘价 ;HIGH最高价;LOW最低价;TOPEN开盘价;LCLOSE前收盘价;CHG涨跌额;PCHG涨跌幅;TURNOVER换手率;VOTURNOVER成交量;VATURNOVER成交金额;TCAP总市值;MCAP流通市值
    code = 'http://quotes.money.163.com/service/chddata.html?code=' + stockNO + '&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
    http = urllib3.PoolManager()
    if not os.path.exists(stockNO):
        os.makedirs('stocks/'+stockNO)
    response = http.request('GET',code)
    with open('stocks/'+ stockNO + '/info.csv', 'wb') as f:
        f.write(response.data)
    response.release_conn()         
           
# 获取所有股票信息
def getAllStockInfo(stockList)：
    p = Pool(multiprocessing.cpu_count())
    count = 0
    for stockNO in stockList:
        try:
            p.apply_async(getStockInfo, args=(stockNO))
            count = count + 1
            print("\r爬取成功，当前进度: {:.2f}%".format(count*100/len(lst)),end="")
        except:
            count = count + 1
            print("\r爬取失败，当前进度: {:.2f}%".format(count*100/len(lst)),end="")
            continue
    p.close()
    p.join()                        
            
def main():
    stockList=[]
    start = time.perf_counter()
    getStockList(stockList)
    getAllStockInfo(stockList)
    time_cost = time.perf_counter() - start
    print("爬取成功，共用时：" time_cost)
main()
