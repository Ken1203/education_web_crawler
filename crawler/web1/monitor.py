#!/usr/bin/env python
# coding: utf-8

import time
import socket
import os
import random
import sys
import traceback
import pymysql
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
import configparser
from datetime import datetime
import requests
#使用說明：
# 請自行定義相關參數
# 程式全程以try execpt 建立，必須跑完完整程式碼

# 事前準備 建立SQL Table
# CREATE TABLE `yourdb`.`table` ( `daytime` datetime NOT NULL,  `timeSP` float NOT NULL,  `ip` text NOT NULL,  `filename` text NOT NULL,  `state` text NOT NULL,  `sSQL` int(11) NOT NULL,  `aSQL` int(11) NOT NULL,  `missSQL` int(11) NOT NULL,  `serialnum` text NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
# ex:CREATE TABLE `logTest`.`logtest2` ( `daytime` datetime NOT NULL,  `timeSP` float NOT NULL,  `ip` text NOT NULL,  `filename` text NOT NULL,  `state` text NOT NULL,  `sSQL` int(11) NOT NULL,  `aSQL` int(11) NOT NULL,  `missSQL` int(11) NOT NULL,  `serialnum` text NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

# 1 程式中需自行定義參數
# state = "success" or "fail+result" (fail要加進度與原因並以空白分隔) 
# (state需自行在程式中建立檢核點 ex : "70% 入庫前清洗發生錯誤")
# sSQL = 242 sql 輸入行數
# sql = "請輸入此次已入行數語法" 帶出一個int
# logfilename = 'logfile 絕對路徑' 請給定名稱跟路徑以用來創立
# errlogfilename = 'errlogfile 絕對路徑' 請給定名稱跟路徑以用來創立
# serialnumfile = '流水號紀錄檔絕對路徑' 請給定名稱跟路徑以用來創立
# codenum = 程式代碼 int 0~99 每隻程式不重複

# 2 在主程式區段編寫程式
# 依照流程區分 process1 process2 process3......

# 3 程式說明 ：
# def timing(): 計時的時間最後會相減
# def daytime():目前日期與時間
# def ip():取得當前ip如有多張網卡要另外做確認並註記
# def filename():取得當前檔案名稱
# state 請自行建立狀態代碼 str ex: 成功：success 失敗：fail,原因（原因用空白分隔
# sSQL = should be imported to SQL (int) 到SQL資料庫query
# aSQL = alreadly imported to SQL (int) 到SQL資料庫query
# def serialnum(): 
    # serialnumfile : file location 流水號紀錄位置
    # codenum : 固定機器編號 machine code
    # errnum : 增量值
    # 1 create file # create file and column names
    # 2 read csv file to df
    # 3 add new machine
    # if input new machine number
    # given all values 0 
    # and return serial number
    # 4 update old number
    # if input old machine number
    # donum +1
    # newerrnum + errnum
    # and return serial number
# def add60(num): add 0 to 6 digits
# def add30(num): add 0 to 3 digits
# def toFile(logfilename , daytime, timeS, timeE ,ip ,filename ,state ,sSQL ,aSQL ,serialnum):
# 將所有資料輸出到file
# def toErrFile(errlogfilename , daytime,filename,e, serialnum):
# 將錯誤訊息統一輸出到另外一個errlogfilename
# def pymysqlcon(ip, user, pw, db ,sql): 將toFile的訊息轉到sql

class monitor:
    def __init__(self,):
        pass
    def timing(self):
        timenow = time.time()
        return timenow
    def daytime(self):
        daytime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
        return daytime
    def ip(self):
        hostname = socket.gethostname()
        ipAddr = socket.gethostbyname(hostname)   
        return ipAddr
    def filename(self):
        absFilePath = os.path.abspath(__file__)
        path, filename = os.path.split(absFilePath)
        return filename

    def serialnum(self,serialnumfile,codenum,errnum):
        codenum = int(codenum)
        if os.path.isfile(serialnumfile) != True:
            with open(serialnumfile,'a') as file:
                file.write('donum,errnum,codenum\n')
        with open(serialnumfile,'r') as file:
            csvfile = file.read()
        df = pd.read_csv(serialnumfile)
        if codenum not in list(df["codenum"]):
            donum = 1
            df = df.append({'donum':donum,'errnum':errnum,'codenum':codenum}, ignore_index=True)
            df.to_csv(serialnumfile, index=False)
            donumS = self.add60(int(donum))
            errnumS = self.add60(int(errnum))
            codenumS = self.add20(int(codenum))
            serialnum = donumS + errnumS + codenumS
            return serialnum
        elif codenum in list(df["codenum"]):
            oldrow = df[df['codenum']==codenum]
            df = df.drop([df[df['codenum']==codenum].index[0]])
            newdonum = list(oldrow['donum'])[0] + 1
            newerrnum = list(oldrow['errnum'])[0] + errnum
            df = df.append({'donum':newdonum,'errnum':newerrnum,'codenum':codenum}, ignore_index=True)
            df.to_csv(serialnumfile, index=False)
            donumS = self.add60(newdonum)
            errnumS = self.add60(newerrnum)
            codenumS = self.add20(codenum)
            serialnum = donumS + errnumS + codenumS
            return serialnum
            
    def add60(self,num):
        if num < 10:
            numS = '0' + '0' + '0' + '0' + '0' + str(num)
        elif num < 100:
            numS = '0' + '0' + '0' + '0' + str(num)
        elif num < 1000:
            numS = '0' + '0' + '0' + str(num)
        elif num < 10000:
            numS = '0' + '0' + str(num)
        elif num < 100000:
            numS = '0' + str(num)
        else:
            numS = str(num)
        return numS
    def add20(self, num):
        if num < 10:
            numS = '0' + str(num)
        else :
            numS = str(num)
        return numS
    def toFile(self,logfilename , daytime, timeS, timeE ,filename ,state ,sSQL ,aSQL ):
        if os.path.isfile(logfilename) != True:
            with open(logfilename,'a') as file:
                timeSP = timeE - timeS
                missSQL = sSQL - aSQL
                file.write('%s,%s,%s,%s,%s,%s,%s\n'%("daytime", "timeSP"  ,"filename" ,"state" ,"sSQL" ,"aSQL" ,"missSQL"))

        with open(logfilename,'a') as file:
            timeSP = timeE - timeS
            missSQL = sSQL - aSQL
            file.write('%s,%.2f,%s,%s,%s,%s,%s\n'%(daytime, timeSP ,filename ,state ,sSQL ,aSQL ,missSQL))
    def toErrFile(self,errlogfilename , daytime, filename, e ,processnum,description):
        print(e)
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        err = "File \"{}\" line {} in {} : [{}] {}".format(filename, lineNum, funcName, error_class, detail)
        if os.path.isfile(errlogfilename) != True:
            with open(errlogfilename,'a') as file:
                file.write('%s,%s,%s,%s,%s\n'%("daytime","filename", "processnum","err" , "description" ))

        with open(errlogfilename,'a') as file:
            file.write('%s,%s,%s,%s,%s\n'%(daytime, filename, processnum, err ,description))
    def pymysqlcon(self,ip, user, pw, db ,sql):
        db = pymysql.connect(ip, user, pw, db)
        cursor = db.cursor(pymysql.cursors.DictCursor)#拿到dict
        cursor.execute(sql)
        db.commit()#commit是把查詢語句提交到資料庫內
        accounts = cursor.fetchall()
        db.close()
        return db, cursor ,accounts
    def mail(self,gmail_user,gmail_password,Subject,content,to_mail):
        msg = MIMEText(content)
        msg['Subject'] = Subject
        msg['From'] = gmail_user
        msg['To'] = to_mail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
    def conf(self,confini):
        config_path = str(Path(__file__).parent.absolute()) + "/../../conf/"+confini
        # 從設定檔讀取Database相關參數
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8-sig")

        # # 絕對路徑
        errlogfilename = config.get('section1', 'errlogfilename')
        logfilename = config.get('section1', 'logfilename')
        serialnumfile = config.get('section1', 'serialnumfile')
        setlogfile = config.get('section1', 'setlogfile')
        
        codenum = config.get('section2', 'codenum')
        to_mail = config.get('section3', 'to_mail')
        gmail_user = config.get('section3', 'gmail_user')
        gmail_password = config.get('section3', 'gmail_password')
        Subject = config.get('section3', 'Subject')
        logdb = config.get('section4', 'logdb')
        logtable = config.get('section4', 'logtable')
        loguser = config.get('section4', 'loguser')
        logpw = config.get('section4', 'logpw')
        logip = config.get('section4', 'logip')
        token = config.get('section5', 'token')
        detailerr = config.get('section1', 'detailerr')


        return errlogfilename, logfilename, serialnumfile ,codenum , to_mail , gmail_user, gmail_password , Subject, logdb ,logtable , loguser, logpw , logip ,setlogfile,token, detailerr

    def logSQL(self ,logtable, daytime,timeSP,filename,state,sSQL,aSQL ,missSQL , logdb):
        sql = "INSERT INTO `{}` VALUES ('{}', {:.2f}, '{}', '{}', {}, {}, {});".format(logtable, daytime,timeSP,filename,state,sSQL,aSQL ,missSQL)
        sqlcreate = '''CREATE TABLE IF NOT EXISTS `{}`.`{}` (  
            `daytime` datetime NOT NULL,  
            `timeSP` float NOT NULL,
            `filename` text NOT NULL,  `state` text NOT NULL,  
            `sSQL` int(11) NOT NULL,  `aSQL` int(11) NOT NULL,  
            `missSQL` int(11) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''.format(logdb,logtable)
        return sql , sqlcreate
    def filewrite(self ,setlogfile,logtext,processnum):
        now = datetime.now()
        nowtime = now.strftime("[%Y%m%d %H:%M:%S]")
        with open(setlogfile,'a+') as file:
            oneline = str(nowtime) + ' process number '+str(processnum)+' : ' + str(logtext)
            file.write(oneline)
            file.write('\n')

    def filewriteS(self,setlogfile):
        with open(setlogfile,'a') as file:
            oneline = '---'
            file.write(oneline)
            file.write('\n')
    def lineNotifyMessage(self,token, msg):
        headers = {
          "Authorization": "Bearer " + token, 
          "Content-Type" : "application/x-www-form-urlencoded"
        }
        payload = {'message': msg}
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        return r.status_code