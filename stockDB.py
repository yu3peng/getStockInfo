import MySQLdb
import requests
from bs4 import BeautifulSoup
import urllib.request
import re
import urllib3
import os
import time
from sqlalchemy import create_engine,Table,Column,Integer,String,MetaData,ForeignKey

# 创建新数据库。
def create_new_database():
    with MySQLdb.connect(mariadb, root, mariadb, "mysql", charset="utf8") as db:
        try:
            create_sql = " CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8 COLLATE utf8_general_ci " % all_stock_info
            print(create_sql)
            db.autocommit(on=True)
            db.cursor().execute(create_sql)
        except Exception as e:
            print("error CREATE DATABASE :", e)

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
                stockList.append(stockNO)
        except:
            continue

# 获取股票信息
def getStockInfo(stockNO):   
    try:
        # TCLOSE收盘价 ;HIGH最高价;LOW最低价;TOPEN开盘价;LCLOSE前收盘价;CHG涨跌额;PCHG涨跌幅;TURNOVER换手率;VOTURNOVER成交量;VATURNOVER成交金额;TCAP总市值;MCAP流通市值
        allInfo = 'http://quotes.money.163.com/service/chddata.html?code=' + stockNO + '&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
        http = urllib3.PoolManager()
        if not os.path.exists(stockNO):
            os.makedirs('stocks/'+stockNO)
        response = http.request('GET', allInfo)
        with open('stocks/'+ stockNO + '/allInfo.csv', 'wb') as f:
            f.write(response.data)
        response.release_conn()
    except:
        raise
        
# 多线程异步获取所有股票信息
def getAllStockInfo(stockList):
    count = 0
    for stockNO in stockList:
        try:
            getStockInfo(stockNO)
            count = count + 1
            print("\r爬取成功，当前进度: {:.2f}%".format(count*100/len(stockList)),end="")            
        except:
            count = count + 1
            print("\r爬取失败，当前进度: {:.2f}%".format(count*100/len(stockList)),end="")
            continue                      

# main函数入口
if __name__ == '__main__':

    # 检查，如果执行 select 1 失败，说明数据库不存在，然后创建一个新的数据库。
    try:
        with MySQLdb.connect(mariadb, root, mariadb, all_stock_info,
                             charset="utf8") as db:
            db.autocommit(on=True)
            db.cursor().execute(" select 1 ")
    except Exception as e:
        print("check  MYSQL_DB error and create new one :", e)
        # 检查数据库失败，
        create_new_database()

    engine=create_engine("mysql+mysqldb://root:mariadb@mariadb:3306/all_stock_info?charset=utf8",  encoding='utf8', convert_unicode=True)
    metadata=MetaData(engine)










user=Table('user',metadata,
            Column('id',Integer,primary_key=True),
            Column('name',String(20)),
            Column('fullname',String(40)),
            )
address_table = Table('address', metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', None, ForeignKey('user.id')),
            Column('email', String(128), nullable=False)
            )

metadata.create_all()
