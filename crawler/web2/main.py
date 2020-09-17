#!/usr/bin/env python
# coding: utf-8

# In[10]:


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
confini = "ken_config.ini" # config名稱（config須自行建立）
#=============================================================

#計時開始
#-------------------------------------------------------------
timeS = monitor.timing()
#=============================================================

#conf變數
#-------------------------------------------------------------
errlogfilename, logfilename, serialnumfile ,codenum , to_mail , gmail_user, gmail_password , Subject , logdb ,logtable , loguser, logpw , logip , setlogfile ,token,detailerr= monitor.conf(confini)
#=============================================================

#主程式
#-------------------------------------------------------------
def Cadtc_ED():
    chrome_options=Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    #隱藏彈出視窗
    chrome_driver_path="/root/chromedriver"
    #指定chromedriver在本機的位置
    driver = webdriver.Chrome(chrome_driver_path, chrome_options=chrome_options)
    url="https://www.cadtc.com.tw/index.html"
    try: 
        driver.implicitly_wait(30)
        driver.get(url)
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
            file.write(now+'執行第一步完錯誤為: '+str(e))
            file.write('\n')
    finally:
        return urls,driver
#===========================開始抓網址內的東西==========================================
def get_data(urls,diver): 
    final_title_list=[]
    final_date_list=[]
    final_outline_list=[]
    final_goal_list=[]
    final_peaple_list=[]
    final_future_list=[]
    for j in tqdm(range(len(urls))):
        try:
            driver.get(urls[j])
            time.sleep(5)
            try: 
                #第1種風格網址
                try:
                    #第1種風格網址title.date一樣的
                    title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[1]/td/span[@id='course-title-name']").text
                    date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                    try:
                        outline=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[2]/td/div").text
                        goal_list=[]
                        for i in range(3,7):                    
                            goal=driver.find_element_by_css_selector("#synopsis_board > tbody > tr > td > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child({}) > td".format(i)).text
                            goal_list.append(goal)
                        peaple_list=[]
                        for j in range(10,14):
                            peaple=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[{}]/td".format(j)).text
                            peaple_list.append(peaple)
                        future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[4]/td").text
                    except:
                        try:
                            time.sleep(2)
                            #第1種風格網址第二種格式
                            outline=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/div[@id='p_content']/p").text.replace('\n', ' ')               
                            goal_list=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[3]/td/table/tbody/tr[5]/td[@class='style166']/table/tbody").text.replace('\n', ' ')  
                            peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[3]/td/table/tbody/tr[5]/td[@class='style166']")[0].text.replace('\n', ' ') 
                            future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[3]/td/table/tbody/tr[3]/td[@class='style166']/span[@class='style118']").text.replace('\n', ' ')
                        except:
                            try:
                                time.sleep(2)
                                #第1種風格網址第三種格式
                                outline=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[5]/td/p").text.replace('\n', ' ')               
                                goal_list=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[8]/td/table/tbody/tr[1]/td").text.replace('\n', ' ')  
                                peaple=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[5]/td/table[3]/tbody/tr/td")[0].text
                                peaple_list=peaple[110:231].replace('\n', ' ') 
                                future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[5]/td/table[3]/tbody/tr/td/span[12]").text
                            except:
                                time.sleep(2)
                                #第1種風格網址第四種格式
                                goal=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[2]/td/p").text.replace('\n', ' ')               
                                outline=driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/div[1]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody").text.replace('\n', ' ')  
                                peaple=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline'][2]/tbody/tr[2]/td")[0].text
                                peaple_list=peaple[:60].replace('\n', ' ') 
                                future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline'][2]/tbody/tr[1]/td").text.replace('\n', ' ')
                                if len(date)<3: #防止第8網址抓錯
                                    date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr[1]/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136'][2]").text
                                    peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr[1]/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline'][2]/tbody/tr[2]/td/p[1]")[0].text.replace('\n', ' ')
                except:
                    try:
                        time.sleep(2)
                        #第1種風格網址第9種格式
                        title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/span[@id='course-title-name']").text
                        date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                        goal_list=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='content_main']/tbody/tr[4]/td/table/tbody/tr[3]/td/table[@class='style166']/tbody").text.replace('\n', ' ') 
                        outline=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/div/table[@id='about_embedded2']/tbody/tr[2]/td/div[@id='swDiv1']/table/tbody/tr/td/table/tbody/tr/td/div/table[@id='content_main_board2']").text.replace('\n', ' ')  
                        peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='content_main']/tbody/tr[5]/td/table/tbody/tr[3]/td")[0].text
                        future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='content_main']/tbody/tr[6]/td/table/tbody/tr[3]/td/span[@class='style166']").text
                    except:
                        try:
                            time.sleep(2)
                            #第1種風格網址第10種格式
                            title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[1]/td/span[@id='course-title-name']").text
                            date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                            goal_list=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[3]/td").text.replace('\n', ' ') 
                            outline=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/div/table[@id='about_embedded2']/tbody/tr[2]/td/div[@id='swDiv1']/table/tbody/tr/td/table/tbody/tr/td/div/table[@id='content_main_board2']").text.replace('\n', ' ')  
                            peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[9]/td")[0].text.replace('\n', ' ')
                            future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[4]/td").text

                        except:
                            try:
                                time.sleep(2)
                                #第1種風格網址第13種格式
                                title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[1]/td/span[@id='course-title-name']").text
                                date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                                goal_list=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[2]/td/span[2]").text.replace('\n', ' ')
                                outline=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[4]/td/div/div[@id='swDiv1']/table[@id='content_board']/tbody/tr/td/table/tbody/tr[2]/td/table[@id='content_main_board3']/tbody/tr[1]/td").text.replace('\n', ' ')  
                                peaple_list=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[3]/td/table/tbody/tr[7]/td/table/tbody/tr/td").text.replace('\n', ' ') 
                                future=[]
                                for i in range(1,3):
                                    future1=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[3]/td/table/tbody/tr[4]/td/table/tbody/tr/td[{}]".format(i)).text.replace('\n', ' ') 
                                    future.append(future1)
                            except:
                                try:
                                    time.sleep(2)
                                    #第1種風格網址第15種格式
                                    title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[1]/td/span[@class='course_title_en']").text
                                    date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/table[@id='class_date_main']/tbody/tr/td/span[2]").text
                                    goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info'][1]/tbody/tr[2]/td/ul")[0].text.replace('\n', ' ')
                                    outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info_02'][1]/tbody/tr/td")[0].text.replace('\n', ' ')  
                                    peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info'][2]/tbody/tr[2]/td[1]/ul")[0].text.replace('\n', ' ') 
                                    future=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info_02'][2]/tbody/tr[2]")[0].text.replace('\n', ' ') 

                                except:
                                    try:
                                        time.sleep(2)
                                        #第1種風格網址第16種格式
                                        title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[1]/td/span[@class='course_title_en']").text
                                        date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/table[@id='class_date_main']/tbody/tr/td/span[2]").text
                                        goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info'][1]/tbody/tr[2]/td/ul")[0].text.replace('\n', ' ')
                                        outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info_02'][1]/tbody/tr/td")[0].text.replace('\n', ' ')  
                                        peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info'][4]/tbody/tr[2]/td[1]/ul")[0].text.replace('\n', ' ') 
                                        future=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info_02'][2]/tbody")[0].text.replace('\n', ' ') 
                                    except:
                                        try:
                                            time.sleep(2)
                                            #第1種風格網址第17種格式
                                            title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[1]/tbody/tr[1]/td[1]/table[@id='content_main3']/tbody/tr[1]/td/span[@class='class_title']").text
                                            date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/table[@id='class_date_main']/tbody/tr/td/p/span[@class='style136'][2]").text
                                            goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[1]/tbody/tr[1]/td[1]/table[@id='content_main3']/tbody/tr[2]/td/table/tbody/tr[3]/td/span[@class='style161']")[0].text.replace('\n', ' ')
                                            outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[1]/tbody/tr[4]/td/span[@class='style160']")[0].text.replace('\n', ' ')  
                                            peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[1]/tbody/tr[2]/td")[0].text.replace('\n', ' ') 
                                            future=["Linux系統管理工程師"]
                                        except:
                                            try:
                                                time.sleep(2)
                                                #第1種風格網址第18種格式
                                                title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr/td/table/tbody/tr[1]/td").text
                                                date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/table[@id='class_date_main']/tbody/tr/td/div[@id='weekend']/span[1]").text
                                                goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr/td/table/tbody/tr[4]/td[2]/p")[0].text.replace('\n', ' ')
                                                outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr/td/table/tbody/tr[11]/td/p")[0].text.replace('\n', ' ')  
                                                peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr/td/table/tbody/tr[8]/td/table/tbody/tr[3]/td[2]")[0].text.replace('\n', ' ') 
                                                future=["嵌入式Linux系統程式設計工程師"]
                                            except:
                                                try:
                                                    time.sleep(2)
                                                    #第1種風格網址第19種格式
                                                    title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[1]/td/span[@class='class_title']").text
                                                    date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/table[@id='class_date_main']/tbody/tr/td/span[@class='style136']").text
                                                    goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr/td[2]/span[@class='style161']")[0].text.replace('\n', ' ')
                                                    outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[6]/td/table/tbody/tr/td[2]/table/tbody/tr")[0].text.replace('\n', ' ')  
                                                    peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[8]/td")[0].text.replace('\n', ' ') 
                                                    future=["C語言程式設計工程師"]
                                                except:
                                                    try:
                                                        time.sleep(2)
                                                        #第1種風格網址第20種格式
                                                        title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[1]/td/span[@class='class_title']").text
                                                        date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/table[@id='class_date_main']/tbody/tr/td/span[2]").text
                                                        goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info']/tbody/tr[2]/td/ul")[0].text.replace('\n', ' ')
                                                        outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi'][2]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr/td/table/tbody/tr[2]/td/div[@id='course_info']")[0].text.replace('\n', ' ')  
                                                        peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[6]/td/table[@class='course_syn_info']/tbody/tr[2]/td/ul")[0].text.replace('\n', ' ') 
                                                        future=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info_02']/tbody/tr[2]/td[1]")[0].text.replace('\n', ' ')
                                                    except:
                                                        try:
                                                            time.sleep(2)
                                                            #第1種風格網址第21種格式
                                                            title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/span[@id='course-title-name']").text
                                                            date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                                                            goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[2]/td")[0].text.replace('\n', ' ')
                                                            outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[4]/td/div/div[@id='swDiv1']/table[@id='content_board']/tbody/tr/td/table/tbody/tr/td/table[@id='content_main_board3']/tbody")[0].text.replace('\n', ' ')  
                                                            peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[3]/td/table/tbody/tr[7]/td/table/tbody/tr/td")[0].text.replace('\n', ' ') 
                                                            future=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[3]/td/table/tbody/tr[4]/td")[0].text.replace('\n', ' ')
                                                        except:
                                                            time.sleep(2)
                                                            #第1種風格網址第22種格式
                                                            title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/span[@id='course-title-name']").text
                                                            date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                                                            goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[3]/td")[0].text.replace('\n', ' ')
                                                            outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[4]/td/div/div[@id='swDiv1']/table[@id='content_board']/tbody/tr/td/div[@id='course_module_chapter']")[0].text.replace('\n', ' ')  
                                                            peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[4]/td/table/tbody/tr[6]/td/table/tbody/tr")[0].text.replace('\n', ' ') 
                                                            future=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[4]/td/table/tbody/tr[3]/td/table/tbody/tr")[0].text.replace('\n', ' ')

                final_title_list.append(title)
                final_date_list.append(date)
                final_outline_list.append(outline)
                final_goal_list.append(goal_list)
                final_peaple_list.append(peaple_list)
                final_future_list.append(future)
            except: 
                #第2種風格網址
                time.sleep(5)
                title1=driver.find_elements_by_xpath("/html/body/div[4]/div[5]/h1")[0].text
                date1=driver.find_elements_by_xpath("/html/body/div[@id='wrap']/div[@id='instant']/ol/li[2]/div[@class='instant-li-info']")[0].text.replace('\n', ' ')
                outline1=driver.find_elements_by_xpath("/html/body/div[@id='wrap']/div[@id='aiotcourse-panel']/div[@class='aiotcourse-info']")[0].text.replace('\n', ' ')
                goal1=driver.find_elements_by_xpath("/html/body/div[@id='wrap']/div[@id='about-panel']/div[@class='about']/ol/li[1]/p")[0].text.replace('\n', ' ')              
                try:
                    time.sleep(2)
                    #第2種風格網址第一種格式
                    peaple_list1=driver.find_element_by_xpath("/html/body/div[4]/div[14]/div/ol/li[2]/ul[1]").text.replace('\n', ' ')
                    future1=driver.find_element_by_xpath("/html/body/div[4]/div[14]/div/ol/li[2]/ul[2]").text
                except:
                    try:
                        time.sleep(2)
                        #第2種風格網址第二種格式
                        peaple_list1=driver.find_element_by_xpath("/html/body/div[4]/div[14]/div/ol/li[5]/div/ul").text.replace('\n', ' ')
                        future1=driver.find_element_by_xpath("/html/body/div[4]/div[15]/div/ol/li[2]/ul[2]/li").text
                    except:
                        time.sleep(2)
                        peaple_list1=driver.find_element_by_xpath("/html/body/div[4]/div[14]/div/ol/li[1]/ul").text.replace('\n', ' ')
                        future1=driver.find_element_by_xpath("/html/body/div[4]/div[14]/div/ol/li[2]").text.replace('\n', ' ')


                final_title_list.append(title1)
                final_date_list.append(date1)
                final_outline_list.append(outline1)
                final_goal_list.append(goal1)
                final_peaple_list.append(peaple_list1)
                final_future_list.append(future1)
#===============================不完整連結的=================================
        except:
            driver.get('https://www.cadtc.com.tw/'+urls[j])#把沒加前面網址URL補上
            time.sleep(5)
            try:
                #第1種風格網址第五種格式
                title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[1]/td/span[@id='course-title-name']").text
                date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                goal_list=[]
                for i in range(3,6):
                    goal=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[{}]/td".format(i)).text
                    goal_list.append(goal)
                outline=driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td/div/table/tbody/tr[2]/td/div[1]/table/tbody/tr[2]/td/table/tbody/tr/td/div/table/tbody/tr").text.replace('\n', ' ')  
                peaple_list=[]
                for j in range(7,10):
                    peaple=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[{}]/td".format(j))[0].text
                    peaple_list.append(peaple)
                future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td").text.replace('\n', ' ')
            except:
                try:
                    time.sleep(2)
                    #第1種風格網址第六種格式
                    title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[1]/td/span[@id='course-title-name']").text
                    date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                    goal_list=[]
                    for i in range(3,8):
                        goal=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[{}]/td".format(i)).text
                        goal_list.append(goal)
                    outline=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/div/table[@id='about_embedded2']/tbody/tr[2]/td/div[@id='swDiv1']/table/tbody/tr/td/table/tbody/tr/td/div/table[@id='content_main_board2']").text.replace('\n', ' ')  
                    future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[4]/td").text
                    peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[9]/td")[0].text.replace('\n', ' ') 
                    #修正第11網址抓錯
                    if len(peaple_list)<6:
                        peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[10]/td")[0].text.replace('\n', ' ') 
                        for i in range(5,9):
                            goal=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[{}]/td".format(i)).text
                            goal_list.append(goal)
                    if len(future)<6:
                        #防止第16網址抓到錯誤內容
                        future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[5]/td").text
                        goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr/td/table[@id='synopsis_board2']/tbody/tr/td/table/tbody/tr[2]/td/table[@class='_sline']/tbody/tr[2]/td/table/tbody/tr[2]/td")[0].text.replace('\n', ' ')
                except:
                    try:
                        time.sleep(2)
                        #第1種風格網址第8種格式
                        title=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@class='main-block'][1]/div[@id='intro']/span[@id='course-title-name']").text
                        date=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='sidebar']/div[@id='class-date']/div[@class='block-border']/p/span[2]").text              
                        outline=driver.find_elements_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@id='tag']/div[@class='block-border']")[0].text.replace('\n', ' ')
                        goal_list=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@class='main-block'][1]/div[@id='intro']/ul[@class='skills']").text.replace('\n', ' ')
                        peaple_list=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@class='main-block'][1]/div[@id='intro']/p[5]").text
                        future=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@class='main-block'][1]/div[@id='intro']/p[6]").text

                    except:
                        try:
                            time.sleep(2)
                            #第1種風格網址第11種格式
                            title=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@class='main-block'][1]/div[@id='intro']/span[@id='course-title-name']").text
                            date=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='sidebar']/div[@id='class-date']/div[@class='block-border']/p/span[2]").text              
                            outline=driver.find_elements_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@id='tag']/div[@class='block-border']")[0].text.replace('\n', ' ')
                            goal_list=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@class='main-block'][1]/div[@id='intro']/ul[@class='skills']").text.replace('\n', ' ')
                            peaple_list=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@class='main-block'][1]/div[@id='intro']/table[2]/tbody/tr/td/span[4]").text
                            future=driver.find_element_by_xpath("/html/body/div[@id='warper']/div[@id='content']/div[@id='content-mid']/div[@id='main']/div[@class='main-block'][1]/div[@id='intro']/table[2]/tbody/tr/td/span[5]/spsn").text

                        except:
                            try:
                                time.sleep(2)
                                #第1種風格網址第12種格式
                                title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[1]/td/span[@id='course-title-name']").text
                                date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/p/span[@class='style136']").text
                                goal_list=[]
                                for i in range(3,6):
                                    goal=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[2]/td/table[2]/tbody/tr[2]/td/table/tbody/tr[{}]/td".format(i)).text.replace('\n', ' ') 
                                    goal_list.append(goal)
                                outline=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/div/table[@id='about_embedded2']/tbody/tr[2]/td/div[@id='swDiv1']/table/tbody/tr/td/table/tbody/tr/td/div/table[@id='content_main_board2']").text.replace('\n', ' ')  
                                peaple_list=[]
                                for j in range(16,19):
                                    peaple=driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table[2]/tbody/tr[2]/td/table/tbody/tr[{}]".format(j)).text
                                    peaple_list.append(peaple)
                                future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[1]/td/table[@id='synopsisi']/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table/tbody/tr[4]/td").text
                            except:
                                try:
                                    time.sleep(2)
                                    #第1種風格網址第14種格式
                                    title=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[1]/td/span[@class='course_title_en']").text
                                    date=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[2]/table[@id='main_right']/tbody/tr[2]/td/table[@id='class_date']/tbody/tr[2]/td/table[@id='class_date_main']/tbody/tr/td/span[2]").text
                                    goal_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info'][1]/tbody/tr[2]/td/ul")[0].text.replace('\n', ' ')
                                    outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info_02'][1]/tbody/tr/td")[0].text.replace('\n', ' ')  
                                    if len(outline)<5:
                                        #防止第20個網址抓錯
                                        outline=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info_02'][1]/tbody")[0].text.replace('\n', ' ')
                                    peaple_list=driver.find_elements_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info'][3]/tbody/tr[2]/td[1]/ul")[0].text.replace('\n', ' ') 
                                    future=driver.find_element_by_xpath("/html/body/table[@id='basic']/tbody/tr[2]/td/table[@id='main']/tbody/tr/td[1]/table[@id='main_left']/tbody/tr[2]/td/table[@id='synopsisi'][1]/tbody/tr[2]/td/table[@id='synopsis_board']/tbody/tr/td/table[@id='content_main']/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table[@class='course_syn_info_02'][2]/tbody/tr[2]/td").text.replace('\n', ' ') 
                                except Exception as e:
                                    now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
                                    with open(detailerr,'a+') as file:            
                                        file.write(now+'執行第二步完錯誤為: '+str(e)+',可能有新增新格式的網址')
                                        file.write('\n')
                                        
            final_title_list.append(title)
            final_date_list.append(date)
            final_outline_list.append(outline)
            final_goal_list.append(goal_list)
            final_peaple_list.append(peaple_list)
            final_future_list.append(future)       
            
    return final_title_list,final_date_list,final_outline_list,final_goal_list,final_peaple_list,final_future_list
##===============寫成DataFrame並寫入csv檔=================================================
def data_frame(final_title_list,final_date_list,final_outline_list,final_goal_list,final_peaple_list,final_future_list):        
    try:
        today=datetime.today().strftime("%Y-%m-%d")
        data = {
                'today':today,
                'title': final_title_list, 
                'during': final_date_list,
                'audience': final_peaple_list,
                'content':final_outline_list,
                'future':final_future_list,
                'purpose':final_goal_list
                }
        df = pd.DataFrame(data)
#===============寫入CSV黨以方便觀察檔案=================================================
        df.to_csv("cadtc_ED.csv",index=True, index_label="id")
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行第三步完錯誤為: '+str(e)+',轉DataFrame有誤')
            file.write('\n')
    finally:
        return today
#===============寫入Database=================================================        
def indatabase(today):        
    try:
        #Open database connection
        engine = create_engine('mysql+pymysql://'+loguser+':'+logpw+'@'+logip+':3306/'+logdb) 
        df = pd.read_csv("cadtc_ED.csv", sep=',')
        df.to_sql('cadtc_ED', engine, index= False,if_exists = "replace")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行第四步完,資料庫新增成功')
            file.write('\n')
    except Exception as e:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行第四步完錯誤為: '+str(e)+',新增失敗')
            file.write('\n')
    finally:
        now = datetime.now().strftime("[%Y%m%d %H:%M:%S]")
        with open(detailerr,'a+') as file:            
            file.write(now+'執行第四步完,寫入結束')
            file.write('\n')
        
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
    urls,driver=Cadtc_ED()
    
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 2
    #function2
    description = '執行完第二步驟時錯誤'
    logtext = '一般log紀錄  第二步'
    final_title_list,final_date_list,final_outline_list,final_goal_list,final_peaple_list,final_future_list=get_data(urls,driver)
    
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 3
    #function3
    description = '執行完第三步驟時錯誤'
    logtext = '一般log紀錄  第三步'
    today=data_frame(final_title_list,final_date_list,final_outline_list,final_goal_list,final_peaple_list,final_future_list)
    
    monitor.filewrite(setlogfile,logtext,processnum)
    #--------------------------
    processnum = 4
    #function1
    description = '執行完第四步驟時錯誤'
    logtext = '一般log紀錄  第四步'
    indatabase(today)
    
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
    sql = "select count(*) as cou from cadtc_ED "
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







