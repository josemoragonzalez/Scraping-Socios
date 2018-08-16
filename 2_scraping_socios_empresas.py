# Imports de librerías necesarias
import requests
import csv
import time
import random
import traceback
import numpy as np
from bs4 import BeautifulSoup
from itertools import islice
from itertools import cycle
from pathlib import Path
from lxml.html import fromstring

# Creamos el archivo donde se guardarán los registros, si es que no existe, como csv separado por semicolon
my_file = Path("/Users/josemora/AnacondaProjects/Socios/CSV/socios_empresas.csv")
if not my_file.is_file():
    with open('/Users/josemora/AnacondaProjects/Socios/CSV/socios_empresas.csv','w') as newFile:
        newFileWriter = csv.writer(newFile, delimiter=';')
        newFileWriter.writerow(['Rut_Base','Proveedor','Rut', 'Fecha_Consulta', 'Socio'])
# Contamos cuantos RUT hay en la base
with open('/Users/josemora/AnacondaProjects/Socios/CSV/RUT_Empresas.csv') as csvfile:
    datos = csv.reader(csvfile, delimiter=';')
    Listado = [r for r in datos]
    Listado = np.array(Listado)
    Listado = Listado[:,1:2]
    Listado = Listado.tolist()

#Creamos una lista de agentes para ir rotando
user_agent_list = [
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

# Lista de proxies, hay que comprar premium para que sea rápido
proxies = ['180.250.88.165:8080', '177.204.85.203:80']

#Creamos el ciclo de IP
proxy_pool = cycle(proxies)
    
# hacemos un ciclo para hacer append sobre el csv, por parte, para evitar caidas
q = 0
while q < (len(Listado) + 500):
    y = q + 500
    if y > len(Listado):
         y = len(Listado) + 1
            
    datafile=open('/Users/josemora/AnacondaProjects/Socios/CSV/RUT_Empresas.csv','r')
    datareader=csv.reader(datafile,delimiter=';')
    MyArray = []
    MyArray.extend(islice(datareader, q, y))

    #Generamos el request a la página por cada RUT
    for r in range(len(MyArray)):

        # Seleccionamos un agente aleatorio
        user_agent = random.choice(user_agent_list)
        
        #Seteamos los headers 
        headers = {'User-Agent': user_agent}

        # cambiamos de proxy
        proxy = next(proxy_pool)

        # Conectamos y de haber error cambiamos de proxy
        try:
            page = requests.get("http://chp221.mercadopublico.cl/ConsultarFichaFull/Certificados.aspx?rut="+MyArray[r][0], verify=False, headers=headers, proxies={"http": proxy, "https": proxy})
        
        except:
            proxy = next(proxy_pool)
            page = requests.get("http://chp221.mercadopublico.cl/ConsultarFichaFull/Certificados.aspx?rut="+MyArray[r][0], verify=False, headers=headers, proxies={"http": proxy, "https": proxy})

        soup = BeautifulSoup(page.content, 'html.parser')
        if not (soup.find(id="lblProveedor") is None):
            Proveedor = soup.find(id="lblProveedor").get_text()
            Rut = soup.find(id="lblRut").get_text()
            Fecha_Consulta = soup.find(id="lblFechaConsulta").get_text()
            Socios_dirt = soup.find_all(class_="txtlabel_sinFondo11px")
            Socios=[]
            j = 0
            for i in range(len(Socios_dirt)):
                if i >= 4:
                    x = Socios_dirt[i].get_text()
                    Socios.append(x[4:])
                    j = j + 1
            if not Socios:
                Socios.append("nulo")
        else:
            Proveedor = 'nulo'
            Rut = 'nulo'
            Fecha_Consulta = 'nulo'
            Socios = ['nulo']
        
        for k in range(len(Socios)):
            with open('/Users/josemora/AnacondaProjects/Socios/CSV/socios_emrpesas.csv','a') as newFile:
                newFileWriter = csv.writer(newFile, delimiter=';')
                newFileWriter.writerow([MyArray[r][0], Proveedor, Rut, Fecha_Consulta, Socios[k]])
            newFile.close()
    q = q + 500
