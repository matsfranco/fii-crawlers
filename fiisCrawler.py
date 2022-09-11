# scrape-youtube-channel-videos-url.py
#_*_coding: utf-8_*_
import pandas as pd 
import re
import numpy as np
import sys, unittest, time, datetime
import urllib.request, urllib.error, urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import NoSuchElementException        

class Fii :

    def __init__(self, ticker, name, fundType, manager, lastDividendYield, lastEarning, equity, equityPerShare, registrationDate, managementType, shareQuantity) :
        self.ticker = ticker 
        self.name = name
        self.manager = manager
        self.lastDividendYield = lastDividendYield
        self.lastEarning = lastEarning
        self.equity = equity
        self.equityPerShare = equityPerShare
        self.registrationDate = registrationDate
        self.managementType = managementType
        self.shareQuantity = shareQuantity
        self.fundType = fundType
        self.earningHistory = []
        self.dyStandardDeviation = -1.0
        self.dyMean = -1.0
        self.median = -1.0
        self.dyMedian = 0
        self.sampleSize = 0
        #print(self.printData())

    def printData(self):
        return(self.ticker+'\t'+self.name+'\t'+self.fundType+'\t'+self.manager+'\t'+str(self.lastDividendYield).replace('.',',')+'\t'+self.lastEarning+'\t'+self.equity+'\t'+self.equityPerShare+'\t'+self.registrationDate+'\t'+self.managementType+'\t'+self.shareQuantity+'\t'+str(self.dyStandardDeviation)+'\t'+str(self.dyMean)+'\t'+str(self.dyMedian)+'\t'+str(self.sampleSize)+'\n')

    def calculateMeanMedianAndStandardDeviation(self):
        dividendYields = []
        if(self.earningHistory) :
            for item in self.earningHistory :
                dividendYields.append(item.dividendYield) 
            self.dyStandardDeviation = '{0:.5f}'.format(np.std(dividendYields)/100).replace('.',',') 
            self.dyMean = '{0:.5f}'.format(np.mean(dividendYields)/100).replace('.',',')
            self.dyMedian = '{0:.5f}'.format(np.mean(dividendYields)/100).replace('.',',')
            #print(str(self.dyStandardDeviation))
            #print(str(self.dyMean))
            #print(str(self.dyMedian))


    def addEarningHistoryEntry(self, earningHistoryItem) :
        self.sampleSize += 1 
        self.earningHistory.append(earningHistoryItem)

    def getEarningHistory(self):
        earnings_datatable = driver.find_elements(By.XPATH,'//*[@id="last-revenues--table"]/tbody/tr')
        wait = WebDriverWait(driver, 10)
        i = 0
        try:
            for item in earnings_datatable:
                i+=1
                date = item.find_element(By.XPATH,'//*[@id="last-revenues--table"]/tbody/tr['+str(i)+']/td[1]').text
                paymentDate = item.find_element(By.XPATH,'//*[@id="last-revenues--table"]/tbody/tr['+str(i)+']/td[2]').text
                baseQuote = item.find_element(By.XPATH,'//*[@id="last-revenues--table"]/tbody/tr['+str(i)+']/td[3]').text
                raw_dividendYield =  item.find_element(By.XPATH,'//*[@id="last-revenues--table"]/tbody/tr['+str(i)+']/td[4]').text
                dividendYield = float(re.sub(',','.',re.sub('%','',raw_dividendYield)))
                earning = item.find_element(By.XPATH,'//*[@id="last-revenues--table"]/tbody/tr['+str(i)+']/td[5]').text
                self.addEarningHistoryEntry(EarningHistory(date,paymentDate,baseQuote,dividendYield,earning))
        except NoSuchElementException:
            return False
        return True

class EarningHistory:

    def __init__(self, date, paymentDate, baseQuote, dividendYield, earning):
        self.date = date
        self.paymentDate = paymentDate
        self.baseQuote = baseQuote
        self.dividendYield = dividendYield
        self.earning = earning

    def printEntry(self) :
        print('date: '+self.date)
        print('paymentDate: '+self.paymentDate)
        print('baseQuote: '+self.baseQuote)
        print('dividendYield: '+str(self.dividendYield))
        print('earning: '+str(self.earning))

#url = sys.argv[1]
url = 'https://fiis.com.br/lista-de-fundos-imobiliarios/'
#driver=webdriver.Firefox()
driver=webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(1)
dt=datetime.datetime.now().strftime("%Y%m%d%H%M")
height = driver.execute_script("return document.documentElement.scrollHeight")
lastheight = 0
wait = WebDriverWait(driver, 10)

# listagem de vídeos
html_list = driver.find_elements(By.XPATH,'//*[@id="items-wrapper"]/div/a')
print(html_list)
urls = []
time.sleep(1)
print('Listando Fundos Imobiliários disponíveis em '+url+'...')
for item in html_list:
    #url = item.find_element(By.TAG_NAME,'a')
    urls.append(item.get_attribute('href'))
numberOfFunds = len(urls)
print('Foram encontrados '+str(numberOfFunds)+' FIIs')
print('Iniciando coleta de dados. Estimativa de duração: '+str(0.03*numberOfFunds)+' mins')
i = 0

fiis = []
outputFile = open('fiis'+'-'+dt+'.txt', 'a+',encoding='utf-8')
outputFile.write('ticker\tname\tfundType\tmanager\tlastDividendYield\tlastEarning\tequity\tequityPerShare\tregistrationDate\tmanagementType\tshareQuantity\tstandardDeviation\tmean\tmedian\tsampleSize\n')
for url in urls :
    i+=1
    if(i>0) :
        print(str(i)+' de '+str(numberOfFunds)+'. Tempo restante estimado: '+str((numberOfFunds-i)*0.03)+' mins.')
        print(url)
        driver.get(url)
        time.sleep(0.3)
        ticker = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="fund-ticker"]'))).text
        name = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="fund-name"]'))).text
        fundType = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--basic"]/div[1]/div[2]/span[2]'))).text
        manager = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--admin"]/div[1]/div[2]/span[2]'))).text
        lastDividendYield = float(wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--indexes"]/td[1]/h3[1]'))).text.replace('%','').replace(',','.'))/100
        lastEarning = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--indexes"]/td[2]/h3[1]'))).text
        equity = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--indexes"]/td[3]/h3[1]'))).text
        equityPerShare = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--indexes"]/td[4]/h3[1]'))).text
        registrationDate = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--basic"]/div[1]/div[4]/span[2]'))).text
        managementType = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--basic"]/div[1]/div[3]/span[2]'))).text
        shareQuantity = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="informations--basic"]/div[2]/div[1]/span[2]'))).text
        newFii = Fii(ticker, name, fundType, manager, lastDividendYield, lastEarning, equity, equityPerShare,registrationDate,managementType, shareQuantity)
        newFii.getEarningHistory()
        newFii.calculateMeanMedianAndStandardDeviation()
    
        fiis.append(newFii)
        outputFile.write(newFii.printData())

outputFile.close()
