import MySQLdb
import requests
from bs4 import BeautifulSoup
import urllib.request
import re
import urllib3
import os
import time
import sys
import time
import datetime
import pandas as pd
import csv
from pandas.core.frame import DataFrame
from sqlalchemy.types import NVARCHAR
from sqlalchemy import inspect
from sqlalchemy import create_engine,Table,Column,Integer,String,MetaData,ForeignKey

# 使用环境变量获得数据库。兼容开发模式可docker模式。
MYSQL_HOST = os.environ.get('MYSQL_HOST') if (os.environ.get('MYSQL_HOST') != None) else "mariadb"
MYSQL_USER = os.environ.get('MYSQL_USER') if (os.environ.get('MYSQL_USER') != None) else "root"
MYSQL_PWD = os.environ.get('MYSQL_PWD') if (os.environ.get('MYSQL_PWD') != None) else "mariadb"
MYSQL_DB = os.environ.get('MYSQL_DB') if (os.environ.get('MYSQL_DB') != None) else "stocks_info"

print("MYSQL_HOST :", MYSQL_HOST, ",MYSQL_USER :", MYSQL_USER, ",MYSQL_DB :", MYSQL_DB)
MYSQL_CONN_URL = "mysql+mysqldb://" + MYSQL_USER + ":" + MYSQL_PWD + "@" + MYSQL_HOST + ":3306/" + MYSQL_DB + "?charset=utf8"
print("MYSQL_CONN_URL :", MYSQL_CONN_URL)

# 创建新数据库。
def create_new_database():
    with MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PWD, "mysql", charset="utf8") as db:
        try:
            create_sql = " CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8 COLLATE utf8_general_ci " % MYSQL_DB
            print(create_sql)
            db.autocommit(on=True)
            db.cursor().execute(create_sql)
        except Exception as e:
            print("error CREATE DATABASE :", e)

def engine_to_db(to_db):
    MYSQL_CONN_URL_NEW = "mysql+mysqldb://" + MYSQL_USER + ":" + MYSQL_PWD + "@" + MYSQL_HOST + ":3306/" + to_db + "?charset=utf8"
    engine = create_engine(
        MYSQL_CONN_URL_NEW,
        encoding='utf8', convert_unicode=True)
    return engine           
            
def insert_db(to_db, data, table_name, write_index, primary_keys):
    # 定义engine
    engine_mysql = engine_to_db(to_db)
    # 使用 http://docs.sqlalchemy.org/en/latest/core/reflection.html
    # 使用检查检查数据库表是否有主键。
    insp = inspect(engine_mysql)
    col_name_list = data.columns.tolist()
    # 如果有索引，把索引增加到varchar上面。
    if write_index:
        # 插入到第一个位置：
        col_name_list.insert(0, data.index.name)
    print(col_name_list)
    data.to_sql(name=table_name, con=engine_mysql, schema=to_db, if_exists='append',
                dtype={col_name: NVARCHAR(length=255) for col_name in col_name_list}, index=write_index)
    # 判断是否存在主键
    if insp.get_primary_keys(table_name) == []:
        with engine_mysql.connect() as con:
            # 执行数据库插入数据。
            try:
                con.execute('ALTER TABLE `%s` ADD PRIMARY KEY (%s);' % (table_name, primary_keys))
            except  Exception as e:
                print("################## ADD PRIMARY KEY ERROR :", e)
                
##################################################################################################################

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
        if not os.path.exists('stocks_info'):
            os.makedirs('stocks_info')
        response = http.request('GET', allInfo)
        with open('stocks_info/'+ stockNO + '.csv', 'wb') as f:
            f.write(response.data)
        response.release_conn()
        
        tmp_lst = [] 
        with open('stocks_info/'+ stockNO + '.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                tmp_lst.append(row)
        df = pd.DataFrame(tmp_lst[1:], columns=tmp_lst[0])
        print(df)
        insert_db(MYSQL_DB, df, stockNO, True, "`code`")

    except:
        raise
        
# 多线程异步获取所有股票信息
def getAllStockInfo(stockList):
    count = 0
    for stockNO in stockList:
        try:
            getStockInfo(stockNO)
            count = count + 1
            print("\rCrawl is successful, current progress: {:.2f}%".format(count*100/len(stockList)),end="")            
        except:
            count = count + 1
            print("\rCrawl failed, current progress: {:.2f}%".format(count*100/len(stockList)),end="")
            continue                      

# main函数入口
if __name__ == '__main__':

    # 检查，如果执行 select 1 失败，说明数据库不存在，然后创建一个新的数据库。
    try:
        with MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PWD, MYSQL_DB,
                             charset="utf8") as db:
            db.autocommit(on=True)
            db.cursor().execute(" select 1 ")
    except Exception as e:
        print("check  MYSQL_DB error and create new one :", e)
        # 检查数据库失败，
        create_new_database()

    stockList=[]
    start = time.perf_counter()
    getStockList(stockList)
    getAllStockInfo(stockList)
    time_cost = time.perf_counter() - start
    print("Crawl is successful, time-consuming：{:.2f}s".format(time_cost))
    

