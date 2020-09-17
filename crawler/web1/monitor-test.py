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
#log變數
#-------------------------------------------------------------
monitor = monitor() #引入監控程式
daytime = monitor.daytime() #時間
absFilePath = os.path.abspath('') #路徑（切換成.py使用__file__）
path, filename = os.path.split(absFilePath) #路徑
confini = "config.ini" # config名稱（config須自行建立）
#=============================================================

#計時開始
#-------------------------------------------------------------
timeS = monitor.timing()
#=============================================================

#conf變數
#-------------------------------------------------------------
errlogfilename, logfilename, serialnumfile ,setlogfile,detail_err ,codenum , to_mail , gmail_user, gmail_password , Subject , logdb ,logtable , loguser, logpw , logip  ,token,DB= monitor.conf(confini)
#=============================================================

#主程式
#-------------------------------------------------------------
def UCOM_ED():
    #/Users/chih-liangyang/Downloads/chromedriver
    chrome_options=Options()
    chrome_options.add_argument('--headless')
    #隱藏彈出視窗
    chrome_driver_path="/Users/chih-liangyang/Downloads/chromedriver"
    #指定chromedriver在本機的位置
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=chrome_options)
    url="https://www.uuu.com.tw/Course"
    try: 
#        driver.implicitly_wait(20)
        driver.get(url)
        driver.implicitly_wait(20)#給予等待時間渲染網頁
        html = driver.page_source
        soup=bs(html,"lxml")
        return soup,driver
 #===============報各種可能錯誤==================================================    
    except TypeError:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+'執行完第ㄧ步驟的錯誤為: TypeError')
#           print('TypeError')
    except AttributeError:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+'執行完第ㄧ步驟的錯誤為: AttributeError')
#        print('AttributeError')
    except ZeroDivisionError:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+'執行完第ㄧ步驟的錯誤為: ZeroDivisionError')
#        print('ZeroDivisionError')
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+'執行完第ㄧ步驟的錯誤為: '+e)
#        print(e) #報錯誤    
#====================================================================
#function
#URL的function
def find_url(soup):
    raw_data=soup.find_all("div","panel-body")#抓所有的區塊
    urls=[]
    for i in raw_data:
        a=1
        try:
            urls.append("https://www.uuu.com.tw"+i.find('a').get('href'))#找個別的網址放入list
        except:
            now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
            with open(detail_err,'a') as file:            
                file.write(now+'"執行完第二步驟時: "+ a + "個有缺網址"')
#            print("第"+a+"個有缺網址")
            continue
        a+=1
    return urls
#data的function
def get_data(urls,driver):
    try:
        h1_list=[]
        time_list=[]
        price_list=[]
        goal_list=[]
        peaple_list=[]
        outline_list=[]
        date_list=[]
        for j in tqdm(range(len(urls))):
            res = requests.get(urls[j])
            soup1 = bs(res.text,'lxml')
            driver.get(urls[j])
            driver.implicitly_wait(20)
            h1=soup1.select("#CourseHeader > h1")
            time.sleep(2)
            h1_list.append(h1[0].text)
            time=soup1.select("#CourseHeader > ul > li:nth-child(1)")
            time.sleep(2)
            time_list.append(time[0].text)
            price=soup1.select("#CourseHeader > ul > li:nth-child(2)")
            time.sleep(2)
            price_list.append(price[0].text)
            goal=soup1.select("#CourseDocument > div.DocumentBOX.Objective > div")
            time.sleep(2)
            goal_list.append(goal[0].text.replace('\n', ' '))
            peaple=soup1.select("#CourseDocument > div.DocumentBOX.Target")
            time.sleep(2)
            peaple_list.append(peaple[0].text.replace('\n', ' '))
            outline=soup1.select("#CourseDocument > div.DocumentBOX.Outline > div ")
            time.sleep(2)
            outline_list.append(outline[0].text.replace('\n', ' '))
            date=driver.find_elements_by_xpath("//tr[@class='body ClassInfoContent']/td[@class='Date']")
            time.sleep(2)
            date_text=[]
            for i in date:
                date_text.append(i.text)
            date_list.append(date_text)
        return h1_list,time_list,price_list,goal_list,peaple_list,outline_list,date_list
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+'執行完第三步驟的錯誤為: '+e)
#dataFrame的function
def data_Frame(h1_list,time_list,price_list,goal_list,peaple_list,outline_list,date_list):
    try:
        today=datetime.today().strftime("%Y%m%d")
        data = {
                    'Today':today,
                    'Title': h1_list, 
                    'Price': price_list,
                    'During': date_list,
                    'Audience': peaple_list,
                    'Content':outline_list,
                    'Hours':time_list,
                    'Purpose':goal_list        
                }
        df = pd.DataFrame(data)
        #===============寫入CSV檔以方便觀察檔案=========
        df.to_csv(today+"_UCOM_ED.csv")
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+'執行完第四步驟的錯誤為: '+e)
#寫入Database的function
def indatabase():
    try:
        #Open database connection
        engine = create_engine(DB) 
        df = pd.read_csv(today+"_UCOM_ED.csv", sep=',')
        df.to_sql(today+'_UCOM_ED', engine, index= False)
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+'執行完第五步驟時: 新增成功')
#        print("新增成功")
    except create_engine.Error as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+"'執行完第五步驟的錯誤為: '+str(e)+',連結資料庫失敗'")
#         print(str(e))
#         print("連結資料庫失敗")
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+"'執行完第五步驟的錯誤為: '+str(e)+',新增失敗'")
#         print(str(e))
#         print("新增失敗")
    finally:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detail_err,'a') as file:            
            file.write(now+'第五步驟寫入結束')
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
    soup,driver=UCOM_ED()
    description = '執行完第一步驟時錯誤'
    logtext = '一般log紀錄  第一步'
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 2
    #function2
    urls=find_url(soup)
    description = '執行完第二步驟時錯誤'
    logtext = '一般log紀錄  第二步'
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 3
    #function3
    h1_list,time_list,price_list,goal_list,peaple_list,outline_list,date_list=get_data(urls,driver)
    description = '執行完第三步驟時錯誤'
    logtext = '一般log紀錄  第三步'
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 4
    #function4
    data_Frame(h1_list,time_list,price_list,goal_list,peaple_list,outline_list,date_list)
    description = '執行完第四步驟時錯誤'
    logtext = '一般log紀錄  第四步'
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 5
    #function5
    indatabase()
    description = '執行完第五步驟時錯誤'
    logtext = '一般log紀錄  第五步'
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
finally: 
    driver.quit()
#=============================================================

# 比對  應放入資料庫筆數 / 已入資料庫筆數
# note:此處因為沒有真實資料先使用log資料，上線後請改成爬蟲或清洗資料
#------------------------------------------------------------- 
try:
    #請放入此次執行應進SQL行數（改成df行數）
    sSQL = len(urls)
    #請select出此次執行已進入SQL行數(改成已輸入的DATA數量)
    sql = "select count(*) as cou from "+today+"_UCOM_ED "
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





# In[ ]:





# In[ ]:





# In[ ]:




