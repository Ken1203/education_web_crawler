#!/usr/bin/env python
# coding: utf-8

# In[7]:


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
import sqlalchemy
import pymysql
import numpy as np
#from sqlalchemy import exc
#log變數
#-------------------------------------------------------------
monitor = monitor() #引入監控程式
daytime = monitor.daytime() #時間
absFilePath = os.path.abspath('') #路徑（切換成.py使用__file__）
path, filename = os.path.split(absFilePath) #路徑
confini = "wash_ken_config.ini" # config名稱（config須自行建立）
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
def UCOM_ED_wash():
    try:
        sql="select * from UCOM_ED "
        engine = create_engine('mysql+pymysql://'+loguser+':'+logpw+'@'+logip+':3306/'+logdb)
#        engine = create_engine('mysql+pymysql://ken:3989889@localhost:3306/test') 
        df=pd.read_sql(sql,engine)
        time_list =get_time()
 #===============報各種可能錯誤==================================================        
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第ㄧ步驟的錯誤為: '+str(e))
            file.write('\n')
#        print(e) #報錯誤    
    finally:
        return engine,df,time_list
#====================================================================
#function
#data清洗的function
def data_wash(df,time_list):
    try:
        price_list=[]
        for i in df['price']:
            a=i.replace('費用：NT$ ', '').replace(',', '')
            price_list.append(a)
#         price_list=[i.replace('費用：NT$ ', '').replace(',', '') for i in df['price']]
        hours_list=[]
        for j in df['hours']:
            b=j.replace('時數：', '').replace('小時', '')
            hours_list.append(b)
#         hours_list=[j.replace('時數：', '').replace('小時', '') for j in df['hours']]
        tech_list=[]    
        others_list=[]
        for i in df['title']:
            if "資訊安全" in i  or "Network" in i or "網路系統"in i  or "CCNA"in i  or "資安" in i :
                tech_list.append("Network")
                others_list.append(False)
            elif "PHP" in i  or "JavaScript" in i  or "網頁" in i :
                tech_list.append("WebDesign")
                others_list.append(False)
            elif "Hadoop" in i  or "SQL" in i  or "MySQL" in i :
                tech_list.append("Database")
                others_list.append(False)
            elif "Python" in i :
                tech_list.append("Python")
                others_list.append(False)
            elif "RHCE" in i :
                tech_list.append("Linux")
                others_list.append(False)
            else:
                tech_list.append(np.nan)
                others_list.append(True)
        start_time_list=[]
        end_time_list=[]
        for j in time_list:
            try:
                a= j.replace('~', '')
                start_time=a[:5]
                start_time_list.append(start_time)
                end_time=a[5:]
                end_time_list.append(end_time)
            except:
                a=j
                start_time_list.append(np.nan)
                end_time_list.append(np.nan)
        weekday_list=[]
        weekends_list=[]
        for n in range(len(df['during'])): 
            try:
                if "六" in df['during'][n].split(",")[0] or "日" in df['during'][n].split(",")[0]:
                    weekends_list.append(True)
                    if "一" in df['during'][n].split(",")[0] or "二" in df['during'][n].split(",")[0] or "三" in df['during'][n].split(",")[0] or "四" in df['during'][n].split(",")[0] or "五" in df['during'][n].split(",")[0]:
                        weekday_list.append(True)
                    else:
                        weekday_list.append(False)
                elif "一" in df['during'][n].split(",")[0] or "二" in df['during'][n].split(",")[0] or "三" in df['during'][n].split(",")[0] or "四" in df['during'][n].split(",")[0] or "五" in df['during'][n].split(",")[0]:
                    weekends_list.append(False)
                    weekday_list.append(True)
                else:
                    weekday_list.append(False)
                    weekends_list.append(False)
            except Exception as e:
                now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
                with open(detailerr,'a+') as file:            
                    file.write(now+'執行完第二步驟的錯誤為: '+str(e))
                    file.write('\n')
#                 print(str(e))
    except:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第二步驟的錯誤為: '+str(e))
            file.write('\n')
    finally:
        return price_list,hours_list,tech_list,others_list,start_time_list,end_time_list,weekday_list,weekends_list
#dataFrame的function
def data_Frame(df,price_list,hours_list,tech_list,others_list,start_time_list,end_time_list,weekday_list,weekends_list):
    try:
        today=datetime.today().strftime("%Y-%m-%d")
        data_wash=[]
        address_list=['10491台北市松山區復興北路99號','300新竹市東區光復路二段295號','403台中市西區台灣大道二段309號','806高雄市前鎮區中山二路2號']
        all_city_list=['taipei','hsinchu','taichung','kaohsiung']
        for e in range(len(address_list)):
            for k in range(len(price_list)):
                a={}
                a['today']=today
                a['web']='恆逸教育訓練中心'
                a['title']=df['title'][k]
                a['price']=price_list[k]
                a['hours']=hours_list[k] 
                a['tech']=tech_list[k]            
                a['bz']=np.nan
                a['lan']=np.nan
                a['others']=others_list[k]
                a['start_time']=start_time_list[k]
                a['end_time']=end_time_list[k]
                a['type']='offline'
                a['all_city']=all_city_list[e]
                if e<1:
                    a['taipei_dist']='松山區'
                else:
                    a['taipei_dist']=np.nan
                a['address']= address_list[e]
                a['weekday']=weekday_list[k]
                a['weekends']=weekends_list[k]
                data_wash.append(a)
        df_wash = pd.DataFrame(data_wash)
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第三步驟的錯誤為: '+str(e))
            file.write('\n')
    finally:
        return df_wash
#寫入Database的function
def indatabase(df_wash,engine):
    try:
        dtype1={
            'price':sqlalchemy.types.INTEGER(),
            'hours':sqlalchemy.types.Float(precision=1),
            'bz':sqlalchemy.types.Text(),
            'lan':sqlalchemy.types.Text(),
            'others':sqlalchemy.types.Boolean,
            'weekday':sqlalchemy.types.Boolean,
            'weekends':sqlalchemy.types.Boolean
        }
        df_wash.to_sql('UCOM_ED_wash',engine, index= False,if_exists = "replace",dtype=dtype1)
        #dtype後面塞想指定column的型態 
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第四步驟時: 新增成功')
            file.write('\n')
#        print("新增成功")
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第四步驟的錯誤為: '+str(e)+',新增失敗')
            file.write('\n')
        print(str(e))
#        print("新增失敗")
    finally:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'第四步驟:寫入結束')
            file.write('\n')
#        print("結束寫入")
# get_time的function
def get_time():
    chrome_options=Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    #隱藏彈出視窗
 #   chrome_driver_path="/Users/chih-liangyang/Downloads/chromedriver"
    chrome_driver_path="/root/chromedriver"
    #指定chromedriver在本機的位置
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=chrome_options)
    url="https://www.uuu.com.tw/Course"
    try: 
        driver.get(url)
        driver.implicitly_wait(20)#給予等待時間渲染網頁
        html = driver.page_source
        soup=bs(html,"lxml")
        raw_data=soup.find_all("div","panel-body")#抓所有的區塊
        urls=[]
        for i in raw_data:
            a=1
            try:
                urls.append("https://www.uuu.com.tw"+i.find('a').get('href'))#找個別的網址放入list
            except:
                now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
                with opn(detailerr,'a') as file:            
                    file.write(now+"抓取所有網址時: 第"+ a + "個有缺網址")
                    file.write('\n')
                #print("第"+a+"個有缺網址")
                continue
            a+=1
        time_list=[]
        try:
            for j in range(len(urls)):
                driver.get(urls[j])
                driver.implicitly_wait(10)
                try:
                    time=driver.find_elements_by_xpath("/html/body/article/section[2]/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[4]")
                    time_list.append(time[0].text)
                except:
                    time_list.append(np.nan)
        except Exception as e:
            now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
            with opn(detailerr,'a') as file:            
                    file.write(now+"執行抓取時間有錯誤: "+ str(e))
                    file.write('\n')
                    #print(str(e))
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with opn(detailerr,'a') as file:            
                file.write(now+"執行整個抓取程式有錯誤: "+ str(e))
                file.write('\n')
        #print(str(e)) #報錯誤 
    finally:
        return time_list
        #print(time_list)
        driver.quit()
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
    engine,df,time_list = UCOM_ED_wash()     
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 2
    #function2
    description = '執行完第二步驟時錯誤'
    logtext = '一般log紀錄  第二步'
    price_list,hours_list,tech_list,others_list,start_time_list,end_time_list,weekday_list,weekends_list = data_wash(df,time_list)   
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 3
    #function3
    description = '執行完第三步驟時錯誤'
    logtext = '一般log紀錄  第三步' 
    df_wash = data_Frame(df,price_list,hours_list,tech_list,others_list,start_time_list,end_time_list,weekday_list,weekends_list)
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 4
    #function4
    description = '執行完第四步驟時錯誤'
    logtext = '一般log紀錄  第四步' 
    indatabase(df_wash,engine)  
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
    sSQL = len(df_wash)
    #請select出此次執行已進入SQL行數(改成已輸入的DATA數量)
    sql = "select count(*) as cou from UCOM_ED_wash "
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




