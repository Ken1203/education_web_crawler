#!/usr/bin/env python
# coding: utf-8

# In[5]:


#!/usr/bin/env python
# coding: utf-8
from monitor import monitor
import sys
import traceback
import os
from selenium import webdriver
import time
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.options import Options
import requests
from tqdm import tqdm
import pandas as pd
from datetime import datetime 
from sqlalchemy import create_engine
#from sqlalchemy import exc
#log變數
#-------------------------------------------------------------
monitor = monitor() #引入監控程式
daytime = monitor.daytime() #時間
absFilePath = os.path.abspath('') #路徑（切換成.py使用__file__）
path, filename = os.path.split(absFilePath) #路徑
confini = "ken_config.ini" # config名稱（config須自行建立）
#=============================================================

#計時開始
#-------------------------------------------------------------
timeS = monitor.timing()
#=============================================================

#conf變數
#-------------------------------------------------------------
errlogfilename, logfilename, serialnumfile  ,codenum , to_mail , gmail_user, gmail_password , Subject , logdb ,logtable , loguser, logpw , logip ,setlogfile , token, detailerr= monitor.conf(confini)
#=============================================================

#主程式
#-------------------------------------------------------------
def school1111():
    page =764
    return page
#====================================================================
#function
#time的function
def dtime():
    return datetime.today().strftime('%Y-%m-%d')
#data的function
def get_data(page):
    all_class = []
    try:
        for i in tqdm(range(1, int(page) + 1)):
            res = requests.get('http://www.1111edu.com.tw/advancedStudies_courseList.php?nowpage={}&cate2=0&adSearchAddress=&adSearchTime=&adSearchCdate=&keyword=&page_sort_col=&page_sort_order=#news-wrapper'.format(i))
            soup = bs(res.text,'lxml')
            title = soup.select('#mainContent > div > div.civtableS01 > table > tbody > tr > td:nth-child(1) > a')
            school = soup.select('#mainContent > div > div.civtableS01 > table > tbody > tr > td:nth-child(2) > a')
            location = soup.select('#mainContent > div > div.civtableS01 > table > tbody > tr > td:nth-child(3) > strong')
            price = soup.select('#mainContent > div > div.civtableS01 > table > tbody > tr > td:nth-child(4)')
            date = soup.select('#mainContent > div > div.civtableS01 > table > tbody > tr > td:nth-child(5) > strong')
            href = soup.select('#mainContent > div > div.civtableS01 > table > tbody > tr > td:nth-child(1) > a')
            data = zip(title, school, location, price, date ,href)
            for title, school, location, price, date ,href in data:
                dic = {}
                dic['web'] = '1111進修網'
                dic['today'] = dtime()
                dic['title'] = title.text
                dic['school'] = school.text
                dic['location'] = location.text
                dic['price'] = price.text
                dic['date'] = date.text
                dic['href'] = 'http://www.1111edu.com.tw/' + href.get('href')
                all_class.append(dic)
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第二步驟的錯誤為: '+str(e))
            file.write('\n')
    finally:
        return all_class

#dataFrame&寫入Databas的function
def indatabase(all_class):
    try:
        df = pd.DataFrame(all_class)
        #Open database connection
        engine = create_engine('mysql+pymysql://'+loguser+':'+logpw+'@'+logip+':3306/'+logdb)
        df.to_sql('school1111', engine, index= False, if_exists='replace') 
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第三步驟時: 新增成功')
            file.write('\n')
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第三步驟的錯誤為: '+str(e)+',新增失敗')
            file.write('\n')
#         print(str(e))
#         print("新增失敗")
    finally:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'第三步驟寫入結束')
            file.write('\n')
#        print("結束寫入")
        return df

#=============================================================
#先設定錯誤備註為空值
description = ''

#主要執行區
#-------------------------------------------------------------
try:
    #logfile分隔線
    #--------------------------
    monitor.filewriteS(setlogfile)
    #--------------------------
    processnum = 1
    #function1
    
    description = '執行完第一步驟時錯誤'
    logtext = '一般log紀錄  第一步'
    page=school1111()
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 2
    #function2
    
    description = '執行完第二步驟時錯誤'
    logtext = '一般log紀錄  第二步'
    all_class=get_data(page)
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 3
    #function3
   
    description = '執行完第三步驟時錯誤'
    logtext = '一般log紀錄  第三步'
    df=indatabase(all_class)
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    #.........
    state = "success"
    errnum = 0
except Exception as e:  
    state = "fail"
    errnum = 1
    #文件寫入點1 寫入錯誤
    monitor.toErrFile(errlogfilename , daytime, filename, e ,processnum,description)
#=============================================================

# 比對  應放入資料庫筆數 / 已入資料庫筆數
# note:此處因為沒有真實資料先使用log資料，上線後請改成爬蟲或清洗資料
#------------------------------------------------------------- 
try:
    #請放入此次執行應進SQL行數（改成df行數）
    sSQL = len(df)
    #請select出此次執行已進入SQL行數(改成已輸入的DATA數量)
    sql = "select count(*) as cou from school1111 "
    #SQL query 請更改 ip account password databases query
    db, cursor ,accounts = monitor.pymysqlcon(logip, loguser, logpw, logdb ,sql)
    aSQL = accounts[0]['cou']
except:
    sSQL = 0
    aSQL = 99
#=============================================================  

#執行次數紀錄
#-------------------------------------------------------------   
monitor.serialnum(serialnumfile,codenum,errnum) 
#=============================================================  

#花費時間
#-------------------------------------------------------------   
timeE = monitor.timing() 
timeSP = timeE -timeS
#=============================================================   

#文件寫入點2 寫入log檔
#-------------------------------------------------------------   
monitor.toFile(logfilename , daytime, timeS, timeE ,filename ,state ,sSQL ,aSQL )
#=============================================================   

# log to SQL
#-------------------------------------------------------------

missSQL = sSQL - aSQL  #漏掉資料量
try:
    #建立 SQL 語法 insert & createtable
    sql , sqlcreate = monitor.logSQL(logtable, daytime,timeSP,filename,state,sSQL,aSQL ,missSQL ,logdb)
    #log to SQL 
    #  1.create table
    monitor.pymysqlcon(logip, loguser, logpw, logdb ,sqlcreate)
    #  2.insert log
    monitor.pymysqlcon(logip, loguser, logpw, logdb ,sql)
    logerrnum =0
except:
    logerrnum = 1
#=============================================================  

# line Send error message
#-------------------------------------------------------------   
if errnum == 1:        
    # 修改為你要傳送的訊息內容
    message = str(errlogfilename) +"\n"+ str(daytime) +"\n"+ str(filename) +"\n"+ str(processnum) +"\n"+ str(description)
    # 修改為你的權杖內容
    monitor.lineNotifyMessage(token, message)
    
if logerrnum == 1:        
    # 修改為你要傳送的訊息內容
    message = str(errlogfilename) +"\n"+ str(daytime) +"\n"+ str(filename) +"\n"+ 'log to SQL error'
    # 修改為你的權杖內容
    monitor.lineNotifyMessage(token, message)
#=============================================================  

# 一、自定義log 建議
# --- START crawing at 2020-05-13 11:42:20.386133 ---
# ---
# Finished crawing [ spark ] at 2020-05-13 11:44:05.156622
# [Success] Check Point 1 : CorpNo. 71 = JobNo. 71
# [Success] Check Point 2 : CorpNo. and JobNo. (71/71) = TotalJobs 71 and NO Exceptions
# [Success] Check Point 3 : CorpNo. or JobNo. (71/71) = InsertedJobs 71 
# ---

# 二、line傳送錯誤訊息
# 去 https://notify-bot.line.me/zh_TW/ 個人頁面設定 tocken


# In[ ]:




