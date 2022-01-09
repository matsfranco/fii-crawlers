import re
import numpy as np
import sys, unittest, time, datetime
import urllib.request, urllib.error, urllib.parse
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import NoSuchElementException  
from selenium.common.exceptions import TimeoutException       

class Fii :

    def __init__(self) :
        self.detalhes = []
        self.historicos = []
        self.mediaDividendYield = 0.0
        self.medianaDividendYield = 0.0
        self.desvioPadraoDividendYield = 0.0
        self.coeficienteVariacaoDividendYield = 0.0
    
    def adicionarDado(self, detalhe) :
        self.detalhes.append(detalhe) 

    def adicionarDadoHistorico(self, historico) :
        self.historicos.append(historico)

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

class HistoricoDados :
    
    def __init__(self) :
        self.nome = ''
        self.tipo = ''
        self.dataReferencia = []
        self.valor = []
        self.tamanhoAmostra = 0
        self.media = 0
        self.mediana = 0
        self.desvioPadrao = 0
        self.coeficienteVariacao = 0
        self.dataReferenciaMaisRecente = 'N/A'

    def definirNomeDado(self, nome) :
        self.nome = nome

    def coletarDatasReferencia(self, dataReferencia) :
        self.dataReferencia = dataReferencia
        return 0

    def coletarValores(self, valor) :
        self.valor = valor
        return 0
    
    def printHistoricoDados(self) :
        i = 0
        print('dataReferencia\tvalor')
        for i in range(len(self.dataReferencia)) :
            print(str(self.dataReferencia[i])+'\t'+str(self.valor[i]).replace('.',','))

    def calcularParametrosAnalise(self,periodo) : 
        self.tamanhoAmostra = len(self.dataReferencia)
        if periodo > self.tamanhoAmostra : 
            periodo = self.tamanhoAmostra
        datasReferenciaNoPeriodo = self.dataReferencia[self.tamanhoAmostra-periodo:self.tamanhoAmostra]
        #print(datasReferenciaNoPeriodo)
        valoresNoPeriodo = self.valor[self.tamanhoAmostra-periodo:self.tamanhoAmostra]
        #print(valoresNoPeriodo)
        self.calcularMedia(valoresNoPeriodo)
        self.calcularMediana(valoresNoPeriodo)
        self.calcularDesvioPadrao(valoresNoPeriodo)
       # self.calcularCoeficienteVariacao()
        self.dataRefereciaMaisRecente()

    def calcularMedia(self,amostra) :
        self.media ='{0:.5f}'.format(np.mean(amostra)/100.0).replace('.',',')

    def calcularMediana(self,amostra) :
        self.mediana ='{0:.5f}'.format(np.median(amostra)/100.0).replace('.',',')

    def calcularDesvioPadrao(self,amostra) :
        self.desvioPadrao = '{0:.5f}'.format(np.std(amostra)/100.0).replace('.',',')   

    def calcularCoeficienteVariacao(self) :
        self.coeficienteVariacao = self.desvioPadrao/self.media

    def dataRefereciaMaisRecente(self) :
        if(self.tamanhoAmostra > 0 ) : 
            self.dataReferenciaMaisRecente = self.dataReferencia[self.tamanhoAmostra-1]
            print(self.dataReferenciaMaisRecente)

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
        self.historicos = []
        self.criarModeloDados()

    def adicionarHistorico(self, nome, metodo, path):
        self.historicos.append(Dado(nome,metodo, path,''))

    def listarFiis(self) :
        self.driver.get(self.urlBase)
        tabelaFiis = self.driver.find_elements(self.tabelaMetodo,self.tabelaPathBase)
        print('>> Plataforma: Listando Fundos Imobiliários disponíveis em '+self.urlBase+'...')
        for item in tabelaFiis:
            url = item.find_element(By.TAG_NAME,'a')
            if(url.get_attribute('href') == 'https://www.fundsexplorer.com.br/funds/mtof11') : print('mtof11')
            else : self.urls.append(url.get_attribute('href'))
        self.quantidadeFundos = len(self.urls)
        print('>> Plataforma: Foram encontrados '+str(self.quantidadeFundos)+' Fundos Imobiliários') 

    def criarModeloDados(self) :
        # Dados Gerais
        self.dados.append(Dado('ticker',By.XPATH,'//*[@id="head"]/div/div/div/div[2]/h1',''))
        self.dados.append(Dado('nome',By.XPATH,'//*[@id="basic-infos"]/div/div/div[2]/div/div[1]/ul/li[1]/div[2]/span[2]',''))
        self.dados.append(Dado('segmento',By.XPATH,'//*[@id="basic-infos"]/div/div/div[2]/div/div[2]/ul/li[4]/div[2]/span[2]',''))
        self.dados.append(Dado('tipoGestao',By.XPATH,'//*[@id="basic-infos"]/div/div/div[2]/div/div[1]/ul/li[3]/div[2]/span[2]',''))
        self.dados.append(Dado('cotacao',By.XPATH,'//*[@id="stock-price"]/span[1]',''))
        self.dados.append(Dado('patrimonioLiquido',By.XPATH,'//*[@id="main-indicators-carousel"]/div/div/div[4]/span[2]',''))
        self.dados.append(Dado('vpPorCota',By.XPATH,'//*[@id="main-indicators-carousel"]/div/div/div[5]/span[2]',''))
        self.dados.append(Dado('ultimoRendimento',By.XPATH,'//*//*[@id="main-indicators-carousel"]/div/div/div[6]/span[2]',''))
        self.dados.append(Dado('p_vp',By.XPATH,'//*[@id="main-indicators-carousel"]/div/div/div[7]/span[2]',''))
        # Dados Específicos
        self.dados.append(Dado('negociacoesDiarias',By.XPATH,'//*[@id="main-indicators-carousel"]/div/div/div[1]/span[2]',''))
        self.dados.append(Dado('ultimoDividendYield',By.XPATH,'//*[@id="main-indicators-carousel"]/div/div/div[3]/span[2]',''))          

    def criarFii(self) :
        return Fii()

    def incluirFii(self, fii) :
        self.fiis.append(fii)
        print('>> Plataforma: novo FII incluido com sucesso')

class Crawler:

    def __init__(self, plataforma) :
        self.plataforma = plataforma
        self.driver = plataforma.driver
        self.duracaoMedia = 0.03
        self.wait = WebDriverWait(self.driver, 10)

    def incluirUrl(self, url) :
        self.urls.append(url)

    def acessarDetalhes(self) :
        print('>> Crawler: Iniciando coleta de dados. Estimativa de duração: {0:.2f} mins'.format(self.duracaoMedia*self.plataforma.quantidadeFundos))  
        i = 0
        for url in self.plataforma.urls :
            i+=1
            print(str(i)+' de '+str(self.plataforma.quantidadeFundos)+'. Tempo restante estimado: '+str((self.plataforma.quantidadeFundos-i)*self.duracaoMedia)+' mins.')
            self.driver.get(url)
            time.sleep(0.3)
            self.coletarDados()        

    def coletarDados(self) :
        dados = self.plataforma.dados
        historicos = self.plataforma.historicos
        fii = self.plataforma.criarFii()
        # Coleta dados Gerais
        for dado in dados :
            #print(dado.nome)
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
        # Coleta Históricos
        for historico in historicos :
            try:
                conteudo = self.wait.until(EC.presence_of_element_located((historico.metodo,historico.path)))
                conteudoHtml = conteudo.get_attribute('innerHTML')
                processadorDados = ProcessadorScript(conteudoHtml)
                historicoDados = HistoricoDados()
                historicoDados.coletarDatasReferencia(processadorDados.obterDatasReferencia())
                historicoDados.definirNomeDado(processadorDados.obterNomeDados())
                historicoDados.coletarValores(processadorDados.obterValores())
                #historicoDados.printHistoricoDados()
                historicoDados.calcularParametrosAnalise(13)
                fii.adicionarDadoHistorico(historicoDados)
            except NoSuchElementException :
                continue
            except TimeoutException :
                continue
            continue
        self.plataforma.incluirFii(fii)
        self.adicionarLinha(fii)
    
    def abrirArquivoSaída(self) :
        dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        self.outputFile = open(self.plataforma.nome+'_'+dt+'.txt', 'a+',encoding='utf-8')
        # Gerar cabeçalho
        for dado in self.plataforma.dados :
            self.outputFile.write(str(dado.nome)+'\t')
        for historico in self.plataforma.historicos :
            self.outputFile.write(str(historico.nome)+'_media'+'\t')
            self.outputFile.write(str(historico.nome)+'_mediana'+'\t')
            self.outputFile.write(str(historico.nome)+'_desvioPadrao'+'\t')
            self.outputFile.write(str(historico.nome)+'_coefVariacao'+'\t')
            self.outputFile.write(str(historico.nome)+'_tamAmostra'+'\t')
            self.outputFile.write(str(historico.nome)+'_dataRefMaisRecente')
        self.outputFile.write('\n')
        # Gerar linhas

    def adicionarLinha(self, fii) :
        for detalhe in fii.detalhes :
            self.outputFile.write(str(detalhe.valor)+'\t')
        for historico in fii.historicos :
            self.outputFile.write(str(historico.media)+'\t')
            self.outputFile.write(str(historico.mediana)+'\t')
            self.outputFile.write(str(historico.desvioPadrao)+'\t')
            self.outputFile.write(str(historico.coeficienteVariacao)+'\t')
            self.outputFile.write(str(historico.tamanhoAmostra)+'\t')
            self.outputFile.write(str(historico.dataReferenciaMaisRecente))
        self.outputFile.write('\n')

    def fecharArquivoSaida(self) :
        self.outputFile.close()

def main() :

    driver=webdriver.Chrome()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)  

    fundsExplorer = Plataforma(driver,'FundsExplorer','https://www.fundsexplorer.com.br/funds',By.XPATH,'//*[@id="fiis-list-container"]/div')    
    fundsExplorer.adicionarHistorico('dividendYieldL52W',By.XPATH,'//*[@id="yields-chart-wrapper"]/script')
    fundsExplorer.listarFiis()

    crawler = Crawler(fundsExplorer)
    crawler.abrirArquivoSaída()
    crawler.acessarDetalhes()
    crawler.fecharArquivoSaida()    

main()





