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
#資料庫讀取function
def school1111_wash():
    try:
        sql="select * from school1111 "
        engine = create_engine('mysql+pymysql://'+loguser+':'+logpw+'@'+logip+':3306/'+logdb)
#        engine = create_engine('mysql+pymysql://ken:3989889@localhost:3306/test') 
        df=pd.read_sql(sql,engine)
 #===============報各種可能錯誤==================================================        
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第ㄧ步驟的錯誤為: '+str(e))
            file.write('\n')
#        print(e) #報錯誤    
    finally:
        return engine , df
#====================================================================
#function
#data清洗的function
def data_wash(df):
    try:
    #================洗出價格====================
        price_list=[]
        try:            
            for i in range(len(df['price'])):
                if "線上" in df['price'][i] or "電洽" in df['price'][i] or "補助訓練" in df['price'][i]:
                    price_list.append(np.nan)
                elif "免費" in df['price'][i]:
                    price_list.append(0)
                else:
                    price_list.append(df['price'][i])
        except:
            now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
            with open(detailerr,'a+') as file:            
                file.write(now+'執行完第二步驟的清洗price發生錯誤,錯誤為: '+str(e))
                file.write('\n')
    #===================洗出type,城市,地區================
        type_list=[]
        all_city=[]
        taipei_dist=[]
        try:
            for j in range(len(df['location'])):
                if "線上" in df['location'][j]:
                    type_list.append("online")
                    all_city.append(np.nan)
                    taipei_dist.append(np.nan)
                elif "市" in df['location'][j] or "縣" in df['location'][j]:
                    type_list.append("offline")
                    if "北" in df['location'][j][:3] :
                        all_city.append('taipei')
                        taipei_dist.append(df['location'][j][3:])
                    else:
                        taipei_dist.append(np.nan)
                        if "基隆" in df['location'][j][:3]:
                            all_city.append("keelung")
                        elif "宜蘭" in df['location'][j][:3]:
                            all_city.append("yilan")
                        elif "桃園" in df['location'][j][:3]:
                            all_city.append("taoyuan ")
                        elif "新竹" in df['location'][j][:3]:
                            all_city.append("hsinchu")
                        elif "苗栗" in df['location'][j][:3]:
                            all_city.append("miaoli")
                        elif "台中" in df['location'][j][:3]:
                            all_city.append("taichung")
                        elif "彰化" in df['location'][j][:3]:
                            all_city.append("changhua")    
                        elif "南投" in df['location'][j][:3]:
                            all_city.append("nantou")
                        elif "雲林" in df['location'][j][:3]:
                            all_city.append("yunlin")
                        elif "嘉義" in df['location'][j][:3]:
                            all_city.append("chiayi")
                        elif "台南" in df['location'][j][:3]:
                            all_city.append("tainan")
                        elif "高雄" in df['location'][j][:3]:
                            all_city.append("kaohsiung")
                        elif "屏東" in df['location'][j][:3]:
                            all_city.append("pingtung")
                        elif "台東" in df['location'][j][:3]:
                            all_city.append("taitung")
                        elif "花蓮" in df['location'][j][:3]:
                            all_city.append("hualien")
                        elif "澎湖" in df['location'][j][:3]:
                            all_city.append("penghu")
                        elif "金門" in df['location'][j][:3]:
                            all_city.append("kinmen")
                        elif "連江" in df['location'][j][:3]:
                            all_city.append("lienchiang")                    
                        else:
                            all_city.append(np.nan)
                else:
                    type_list.append(np.nan)
                    all_city.append(np.nan)
                    taipei_dist.append(np.nan)
        except:
            now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
            with open(detailerr,'a+') as file:            
                file.write(now+'執行完第二步驟的清洗location發生錯誤,錯誤為: '+str(e))
                file.write('\n')
    #===================洗出課程類別=========================
        tech_list=[] 
        bz_list=[]
        lan_list=[]
        others_list=[]
        try:
            for i in df['title']:
                if "Java" in i or "MIS程試" in i:
                    tech_list.append("Java")
                    bz_list.append(np.nan)
                    lan_list.append(np.nan)
                    others_list.append(False)
                elif 'C++' in i or 'C＋＋' in i or 'C語言' in i:
                    tech_list.append("C++")
                    bz_list.append(np.nan)
                    lan_list.append(np.nan)
                    others_list.append(False)    
                elif "Python" in i or '爬蟲' in i or 'Keras' in i or 'Django' in i or 'Flask' in i or 'python' in i or '機器學習' in i:
                    tech_list.append("Python")
                    bz_list.append(np.nan)
                    lan_list.append(np.nan)
                    others_list.append(False)    
                elif 'Network' in i or "CCNA" in i or "CCNP" in i or "雲端" in i or "資訊安全" in i or "網路系統" in i or "網路管理" in i or "歐洲雲" in i or "TCP" in i or "RHCE" in i or "Cisco" in i:
                    tech_list.append("Network")
                    bz_list.append(np.nan)
                    lan_list.append(np.nan)
                    others_list.append(False)
                elif "Linux" in i or "RHCA" in i or "RHCSA" in i :
                    tech_list.append("Linux")
                    bz_list.append(np.nan)
                    lan_list.append(np.nan)
                    others_list.append(False)
                elif 'C#' in i:
                    tech_list.append("C#")
                    bz_list.append(np.nan)
                    lan_list.append(np.nan)
                    others_list.append(False)
                elif '前端' in i or 'PHP' in i or 'HTML' in i or 'CSS' in i or 'javaScript' in i or 'jQuery' in i or 'RWD' in i or '網站設計' in i or '網頁' in i or '網站後端' in i or 'ASP.NET' in i or 'Dreamweaver' in i:
                    tech_list.append("WebDesign")
                    bz_list.append(np.nan)
                    lan_list.append(np.nan)
                    others_list.append(False)
                elif 'Database' in i or '資料庫' in i or 'SQL' in i or 'DB' in i:
                    tech_list.append("Database")
                    bz_list.append(np.nan)
                    lan_list.append(np.nan)
                    others_list.append(False)
                else:
                    tech_list.append(np.nan)
                    if '行銷' in i or "銷售" in i :
                        bz_list.append('MKT')
                        lan_list.append(np.nan)
                        others_list.append(False)
                    elif '商管' in i or "經營管理" in i or "管理" in i or "營運" in i:
                        bz_list.append('MGMT')
                        lan_list.append(np.nan)
                        others_list.append(False)
                    elif '證照' in i or '檢定' in i or '考照' in i or '證書' in i:
                        bz_list.append('LIS')
                        lan_list.append(np.nan)
                        others_list.append(False)
                    elif "財務" in i or "預算" in i or "會計" in i or "財報" in i or "記帳" in i or "稅務" in i:
                        bz_list.append('FIN')
                        lan_list.append(np.nan)
                        others_list.append(False)
                    else:
                        bz_list.append(np.nan)
                        if "英文" in i or "多益" in i or "美語" in i or "英語" in i or "雅思" in i or "托福" in i:
                            lan_list.append('ENG')
                            others_list.append(False)
                        elif "韓語" in i or "韓文" in i:
                            lan_list.append('KO')
                            others_list.append(False)
                        elif "日語" in i or "日檢" in i or "日文" in i:
                            lan_list.append('JA')
                            others_list.append(False)
                        elif "越南語" in i:
                            lan_list.append('VN')
                            others_list.append(False)
                        elif "西語" in i:
                            lan_list.append('ES')
                            others_list.append(False)
                        elif "華語" in i or "國語" in i or "廣東話" in i:
                            lan_list.append('ZH')
                            others_list.append(False)
                        elif "泰語" in i:
                            lan_list.append('TH')
                            others_list.append(False)
                        elif "法語" in i:
                            lan_list.append('FR')
                            others_list.append(False)
                        elif "德語" in i:
                            lan_list.append('DE')
                            others_list.append(False)
                        elif "義大利語" in i:
                            lan_list.append('IT')
                            others_list.append(False)
                        else:
                            lan_list.append(np.nan)
                            others_list.append(True)
        except:
            now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
            with open(detailerr,'a+') as file:            
                file.write(now+'執行完第二步驟的清洗課程分類發生錯誤,錯誤為: '+str(e))
                file.write('\n')
    except:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行完第二步驟的錯誤為: '+str(e))
            file.write('\n')
    finally:
        return price_list,type_list,all_city,taipei_dist,tech_list,bz_list,lan_list,others_list
#dataFrame的function
def data_Frame(df,price_list,type_list,all_city,taipei_dist,tech_list,bz_list,lan_list,others_list):
    try:
        today=datetime.today().strftime("%Y-%m-%d")
        data_wash=[]
        for k in range(len(price_list)):
            a={}
            a['today']=today
            a['web']=df['web'][k]
            a['title']=df['title'][k]
            a['price']=price_list[k]
            a['hours']=np.nan            
            a['tech']=tech_list[k]            
            a['bz']=bz_list[k]
            a['lan']=lan_list[k]
            a['others']=others_list[k]
            a['start_time']=np.nan 
            a['end_time']=np.nan 
            a['type']=type_list[k]
            a['all_city']=all_city[k]
            a['taipei_dist']=taipei_dist[k]
            a['address']= np.nan 
            a['weekday']=np.nan
            a['weekends']=np.nan
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
            'start_time':sqlalchemy.types.Text(),
            'end_time':sqlalchemy.types.Text(),
            'address':sqlalchemy.types.Text(),
            'others':sqlalchemy.types.Boolean,
            'weekday':sqlalchemy.types.Boolean,
            'weekends':sqlalchemy.types.Boolean
        }
        df_wash.to_sql('school1111_wash',engine, index= False,if_exists = "replace",dtype=dtype1)
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
    engine ,df = school1111_wash()
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 2
    #function2    
    description = '執行完第二步驟時錯誤'
    logtext = '一般log紀錄  第二步'
    price_list,type_list,all_city,taipei_dist,tech_list,bz_list,lan_list,others_list = data_wash(df)
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 3
    #function3
    description = '執行完第三步驟時錯誤'
    logtext = '一般log紀錄  第三步'
    df_wash = data_Frame(df,price_list,type_list,all_city,taipei_dist,tech_list,bz_list,lan_list,others_list)
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
    sql = "select count(*) as cou from school1111_wash "
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

