import requests
from bs4 import BeautifulSoup
import pandas as pd




df = pd.DataFrame()
for i in range(1000):
    offset = i*100
    url = f'http://bridge.no/layout/set/print/bridgemodule/medlemmer_json?node_url_alias=Organisasjon%2FNasjonal-MP-oversikt&offset={offset}&sortMethod=hcp&sortType=0'
    
    
    resp = requests.get(url)
    
    
    soup = BeautifulSoup(resp.json()['html'],'lxml')
    tmpdf = pd.read_html(str(soup.find_all('table')[1]),header=0,index_col=0,decimal=',',thousands='.')[0]
    if tmpdf.size < 1:
        break
    df = pd.concat([df,tmpdf])
    
dfu = df[~df.index.duplicated(keep='last')]

#for i,v in dfu.Navn.iteritems():
#    if 'Kristiansen' in v:
#        print(i,v)