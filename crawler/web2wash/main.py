#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
#資料庫讀取function
def cadtc_ED_wash():
    try:
        sql="select * from cadtc_ED "
        engine = create_engine('mysql+pymysql://'+loguser+':'+logpw+'@'+logip+':3306/'+logdb)
#        engine = create_engine('mysql+pymysql://ken:3989889@localhost:3306/test') 
        df=pd.read_sql(sql,engine)
        time_list = get_time()
 #===============報各種可能錯誤==================================================        
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第ㄧ步驟的錯誤為: '+str(e))
            file.write('\n')
#        print(e) #報錯誤    
    finally:
        return engine , df ,time_list
#====================================================================
#function
#data清洗的function
def data_wash(df,time_list):
    try:
        tech_list=[]    
        others_list=[]
        for i in df['title']:
            if "Java" in i :
                tech_list.append("Java")
                others_list.append(False)
            elif "C語言" in i :
                tech_list.append("C++")
                others_list.append(False)
            elif "Spark" in i :
                tech_list.append("Database")
                others_list.append(False)
            elif "Python" in i :
                tech_list.append("Python")
                others_list.append(False)
            elif "Linux" in i :
                tech_list.append("Linux")
                others_list.append(False)
            else:
                tech_list.append(np.nan)
                others_list.append(True)
        weekday_list=[]
        weekends_list=[]
        for i in range(len(time_list)):
            if "一" in time_list[i] or "二" in time_list[i] or "三" in time_list[i] or "四" in time_list[i] or "五" in time_list[i] or "平" in time_list[i]:
                weekday_list.append(True)
                if "週六" in time_list[i] or "週日" in time_list[i]:
                     weekends_list.append(True)
                else:
                    weekends_list.append(False)
            elif "週六" in time_list[i] or "週日" in time_list[i]:
                weekday_list.append(False)
                weekends_list.append(True)
            else:
                weekday_list.append(False)
                weekends_list.append(False)
        time_split_list=[time_list[j].split("班")[1].split(")")[0].split("至") for j in range(len(time_list))]
        start_time_list=[]
        end_time_list=[]
        for w in range(len(time_split_list)):
            start_time_list.append(datetime.strptime(time_split_list[w][0].replace('\u3000', '').replace(' ', ''),'%p%I:%M').strftime('%H:%M'))
            end_time_list.append(datetime.strptime(time_split_list[w][1].replace('至', ''),'%p%I:%M').strftime('%H:%M'))
    except:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第二步驟的錯誤為: '+str(e))
            file.write('\n')
    finally:
        return tech_list,others_list, weekday_list,weekends_list,start_time_list,end_time_list
#dataFrame的function
def data_Frame(df,tech_list,others_list,weekday_list,weekends_list,start_time_list,end_time_list):
    try:
        today=datetime.today().strftime("%Y-%m-%d")
        data_wash=[]
        for k in range(len(tech_list)):
            a={}
            a['today']=today
            a['web']='中華行動數位科技'
            a['title']=df['title'][k]
            a['price']=np.nan
            a['hours']=np.nan            
            a['tech']=tech_list[k]            
            a['bz']=np.nan
            a['lan']=np.nan
            a['others']=others_list[k]
            a['start_time']=start_time_list[k]
            a['end_time']=end_time_list[k]
            a['type']='offline'
            a['all_city']='taipei'
            a['taipei_dist']='中正區'
            a['address']= '台北市開封街1段2號9樓'
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
        df_wash.to_sql('cadtc_ED_wash',engine, index= False,if_exists = "replace",dtype=dtype1)
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
    url="https://www.cadtc.com.tw/index.html"
    driver.get(url)
    driver.implicitly_wait(30)
    try:
        html = driver.page_source
        soup=bs(html,"lxml")
    #================================抓取所有課程網址=======================================
        raw_data=soup.select("#section03")
        urls=[]
        for i in raw_data:
            a=i.find_all('a')
        for j in a:
            urls.append(j.get('href'))
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'爬取網址出錯誤為: '+str(e))
            file.write('\n')
    time_list=[]
    try:
        for j in tqdm(range(len(urls))):
            try:
                driver.get(urls[j])
                try:            
                    driver.implicitly_wait(5)
                    time=driver.find_elements_by_xpath("/html/body/div[@id='wrap']/div[@id='co2-panel']/div[@class='co2']/ol/li[4]")[0].text.replace('開課時間\n', '')
                except:
                    try:
                        driver.implicitly_wait(5)
                        time=driver.find_elements_by_xpath("/html/body/div[@id='wrap']/div[@id='instant']/ol/li[3]/div[@class='instant-li-info']")[0].text.replace('開課時間\n', '')
                    except:
                        try:
                            driver.implicitly_wait(5)
                            time=driver.find_elements_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/p")[0].text[:55].replace('\n', '').replace('開課時間', '')
                        except:
                            driver.implicitly_wait(5)
                            time=driver.find_elements_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td")[0].text[:75].replace('\n', '').replace('開課時間', '')
                time_list.append(time)
            except:
                driver.get('https://www.cadtc.com.tw/'+urls[j])#把沒加前面網址URL補上
                try:
                    try:
                        driver.implicitly_wait(5)
                        time=driver.find_elements_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/p")[0].text[:57].replace('\n', '').replace('開課時間', '')        
                    except:
                        driver.implicitly_wait(5)
                        time=driver.find_elements_by_xpath("/html/body/div[2]/div/div[3]/div[3]/div[1]/div/p")[0].text[:57].replace('\n', '').replace('開課時間', '')                        
                except:
                    try:
                        driver.implicitly_wait(5)
                        time=driver.find_elements_by_xpath("/html/body/div[2]/div/div[3]/div[2]/div[1]/div/p")[0].text[:57].replace('\n', '').replace('開課時間', '')        
                    except:            
                        driver.implicitly_wait(5)
                        time=driver.find_elements_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td")[0].text[:57].replace('\n', '').replace('開課時間', '')

                time_list.append(time)
    except:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'爬取時間出錯誤可能有新格式,錯誤為: '+str(e))
            file.write('\n')
    finally:
        return time_list
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
    engine, df,time_list = cadtc_ED_wash()
    description = '執行完第一步驟時錯誤'
    logtext = '一般log紀錄  第一步'     
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 2
    #function2
    tech_list,others_list,weekday_list,weekends_list,start_time_list,end_time_list = data_wash(df,time_list)
    description = '執行完第二步驟時錯誤'
    logtext = '一般log紀錄  第二步'   
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 3
    #function3
    df_wash = data_Frame(df,tech_list,others_list,weekday_list,weekends_list,start_time_list,end_time_list)
    description = '執行完第三步驟時錯誤'
    logtext = '一般log紀錄  第三步' 
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 4
    #function4
    indatabase(df_wash,engine)
    description = '執行完第四步驟時錯誤'
    logtext = '一般log紀錄  第四步'   
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
    sSQL = len(tech_list)
    #請select出此次執行已進入SQL行數(改成已輸入的DATA數量)
    sql = "select count(*) as cou from cadtc_ED_wash "
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

