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

    def __init__(self) :
        self.detalhes = []
        self.historicoRendimentos = []
    
    def adicionarDado(self, detalhe) :
        self.detalhes.append(detalhe) 

    def listarDetalhes(self) :
        for detalhe in self.detalhes :
            print(detalhe.nome+': '+detalhe.valor)

class FiiDetalhe :
    
    def __init__(self, nome, valor) :
        self.nome = nome
        self.valor = valor

class Dado :
    
    def __init__(self, nome, metodo, path, atributo) :
        self.nome = nome
        self.metodo = metodo
        self.path = path
        self.atributo = atributo

class ProcessadorScript(object) :
    def __init__(self,script) :
        self.script = str(script)
        self.segmentarDados()
        self.nomeDado = ''
 
    def segmentarDados(self) :
        inicioSegmentoDados = self.script.index('data: {')+6
        fimSegmentoDados = self.script.index('options: {')-2
        self.__dict__ = json.loads(self.script[inicioSegmentoDados:fimSegmentoDados])
    
    def obterDatasReferencia(self) :
        return self.labels

    def obterValores(self) :
        return self.data

    def obterNomeDados(self) :
        valores = str(self.datasets[0]).replace('\'','\"')
        self.__dict__ = json.loads(valores)
        return self.label

class Plataforma :

    def __init__(self, driver, nome, urlBase, tabelaMetodo, tabelaPathBase) :
        self.driver = driver
        self.nome = nome
        self.urlBase = urlBase
        self.tabelaMetodo = tabelaMetodo
        self.tabelaPathBase = tabelaPathBase
        self.urls = []
        self.dados = []
        self.fiis = []
        self.criarModeloDados()

    def listarFiis(self) :
        self.driver.get(self.urlBase)
        tabelaFiis = self.driver.find_elements(self.tabelaMetodo,self.tabelaPathBase)
        print('>> Plataforma: Listando Fundos Imobiliários disponíveis em '+self.urlBase+'...')
        for item in tabelaFiis:
            url = item.find_element(By.TAG_NAME,'a')
            self.urls.append(url.get_attribute('href'))
        self.quantidadeFundos = len(self.urls)
        print('>> Plataforma: Foram encontrados '+str(self.quantidadeFundos)+' Fundos Imobiliários') 

    def criarModeloDados(self) :
        # Dados Gerais
        self.dados.append(Dado('ticker',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[1]/td[2]/span',''))
        self.dados.append(Dado('nome',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[2]/td[2]/span',''))
        self.dados.append(Dado('segmento',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[4]/td[2]/span/a',''))
        self.dados.append(Dado('tipoGestao',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[5]/td[2]/span',''))
        self.dados.append(Dado('cotacao',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[1]/td[4]/span',''))
        self.dados.append(Dado('dataCotacao',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[2]/td[4]/span',''))
        self.dados.append(Dado('min52W',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[3]/td[4]/span',''))
        self.dados.append(Dado('max52W',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[4]/td[4]/span',''))
        self.dados.append(Dado('volumeMedioDiarioL2M',By.XPATH,'/html/body/div[1]/div[2]/table[1]/tbody/tr[5]/td[4]/span',''))
        self.dados.append(Dado('valorMercado',By.XPATH,'/html/body/div[1]/div[2]/table[2]/tbody/tr[1]/td[2]/span',''))
        self.dados.append(Dado('numeroCotas',By.XPATH,'/html/body/div[1]/div[2]/table[2]/tbody/tr[1]/td[4]/span',''))
        self.dados.append(Dado('dataUltimoRelatorio',By.XPATH,'/html/body/div[1]/div[2]/table[2]/tbody/tr[2]/td[2]/span',''))
        self.dados.append(Dado('urlHistorico',By.XPATH,'//*[@id="menu"]/li[3]/ul/li[4]/a','href'))
        # Indicadores
        self.dados.append(Dado('ffoYield',By.XPATH,'/html/body/div[1]/div[2]/table[3]/tbody/tr[2]/td[4]/span',''))
        self.dados.append(Dado('dividendYield',By.XPATH,'/html/body/div[1]/div[2]/table[3]/tbody/tr[3]/td[4]/span',''))
        self.dados.append(Dado('p_vp',By.XPATH,'/html/body/div[1]/div[2]/table[3]/tbody/tr[4]/td[4]/span',''))
        self.dados.append(Dado('ffoPorCota',By.XPATH,'/html/body/div[1]/div[2]/table[3]/tbody/tr[2]/td[6]/span',''))
        self.dados.append(Dado('dyPorCota',By.XPATH,'/html/body/div[1]/div[2]/table[3]/tbody/tr[3]/td[6]/span',''))
        self.dados.append(Dado('vpPorCota',By.XPATH,'/html/body/div[1]/div[2]/table[3]/tbody/tr[4]/td[6]/span',''))
        # Patrimonio
        self.dados.append(Dado('ativos',By.XPATH,'/html/body/div[1]/div[2]/table[3]/tbody/tr[12]/td[4]/span',''))
        self.dados.append(Dado('patrimonioLiquido',By.XPATH,'/html/body/div[1]/div[2]/table[3]/tbody/tr[12]/td[6]/span',''))
        # Imóveis
        self.dados.append(Dado('qtdImoveis',By.XPATH,'/html/body/div[1]/div[2]/table[5]/tbody/tr[2]/td[2]/span',''))
        self.dados.append(Dado('qtdUnidades',By.XPATH,'/html/body/div[1]/div[2]/table[5]/tbody/tr[3]/td[2]/span',''))
        self.dados.append(Dado('imoveisPorPatrimonioLiquido',By.XPATH,'/html/body/div[1]/div[2]/table[5]/tbody/tr[4]/td[2]/span',''))
        self.dados.append(Dado('area',By.XPATH,'/html/body/div[1]/div[2]/table[5]/tbody/tr[2]/td[4]/span',''))
        self.dados.append(Dado('aluguelPorM2',By.XPATH,'/html/body/div[1]/div[2]/table[5]/tbody/tr[3]/td[4]/span',''))
        self.dados.append(Dado('precoPorM2',By.XPATH,'/html/body/div[1]/div[2]/table[5]/tbody/tr[4]/td[4]/span',''))
        self.dados.append(Dado('capRate',By.XPATH,'/html/body/div[1]/div[2]/table[5]/tbody/tr[2]/td[6]/span',''))
        self.dados.append(Dado('vacanciaMedia',By.XPATH,'/html/body/div[1]/div[2]/table[5]/tbody/tr[3]/td[6]/span',''))

    def criarFii(self) :
        return Fii()

    def incluirFii(self, fii) :
        self.fiis.append(fii)
        print('>> Plataforma: novo FII incluido com sucesso')

    def processarHistorico(self, fii) :
        for detalhe in fii.detalhes :
            if(detalhe.nome == 'urlHistorico') : 
                urlHistorico = detalhe.valor
                break
            else :
                continue
        self.driver.get(urlHistorico)
        tabelaHistorico = self.driver.find_elements(self.historicoMetodo,self.historicoPathBase)
        i = 0
        for itemHistorico in tabelaHistorico:
            i += 1
            self.urls.append(url.get_attribute('href'))
        self.quantidadeFundos = len(self.urls)

class Crawler:

    def __init__(self, plataforma) :
        self.plataforma = plataforma
        self.driver = plataforma.driver
        self.duracaoMedia = 0.03
        self.wait = WebDriverWait(self.driver, 10)

    def incluirUrl(self, url) :
        self.urls.append(url)

    def acessarDetalhes(self) :
        print('>> Crawler: Iniciando coleta de dados. Estimativa de duração: '+str(self.duracaoMedia*self.plataforma.quantidadeFundos)+' mins')  
        i = 0
        for url in self.plataforma.urls :
            i+=1
            print(str(i)+' de '+str(self.plataforma.quantidadeFundos)+'. Tempo restante estimado: '+str((self.plataforma.quantidadeFundos-i)*self.duracaoMedia)+' mins.')
            self.driver.get(url)
            time.sleep(0.3)
            self.coletarDados()        

    def coletarDados(self) :
        dados = self.plataforma.dados
        fii = self.plataforma.criarFii()
        for dado in dados :
            try: 
                if not dado.atributo : 
                    detalhe = FiiDetalhe(dado.nome,self.wait.until(EC.presence_of_element_located((dado.metodo,dado.path))).text)
                    fii.detalhes.append(detalhe)
                else :
                    tag = self.wait.until(EC.presence_of_element_located((dado.metodo,dado.path)))
                    detalhe = FiiDetalhe(dado.nome,tag.get_attribute(dado.atributo))
                    fii.detalhes.append(detalhe)
            except NoSuchElementException:
                continue
            continue
        self.plataforma.incluirFii(fii)
        #self.plataforma.processarHistorico(fii)
        #fii.listarDetalhes()
        self.adicionarLinha(fii)
    
    def abrirArquivoSaída(self) :
        dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        self.outputFile = open(self.plataforma.nome+'_'+dt+'.txt', 'a+',encoding='utf-8')
        # Gerar cabeçalho
        for dado in self.plataforma.dados :
            self.outputFile.write(str(dado.nome)+'\t')
        self.outputFile.write('\n')
        # Gerar linhas

    def adicionarLinha(self, fii) :
        for detalhe in fii.detalhes :
            self.outputFile.write(str(detalhe.valor)+'\t')
        self.outputFile.write('\n')

    def fecharArquivoSaida(self) :
        self.outputFile.close()

def main() :

    driver=webdriver.Chrome()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)  

    fundamentus = Plataforma(driver,'Fundamentus','https://fundamentus.com.br/fii_resultado.php',By.XPATH,'//*[@id="tabelaResultado"]/tbody/tr')    
    fundamentus.listarFiis()

    crawler = Crawler(fundamentus)
    crawler.abrirArquivoSaída()
    crawler.acessarDetalhes()
    crawler.fecharArquivoSaida()    



main()