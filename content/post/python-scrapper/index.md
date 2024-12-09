+++
title = "Web scrapper using Python"
description = "Scrapping FIIs using Python and Pandas"
date = "2020-11-20"
draft = false
toc = false
categories = ["python"]
tags = ["python"]
image = "panda.png"
+++

So I needed to learn how to scrape a web page using Python.
<!--more--->  My teammate suggested that I could learn a few tricks in python by scraping FIIs, which is the brazilian equivalent to american REITs. I did some research and found some good examples using a module called pandas (https://realpython.com/python-csv/) , a tool designed for data analisys and manipulation and very popular among people working with data science.
My goal was much less ambitious but i thought i might as well use what everyone else is using, since it would provide a good learning opportunity.

I based my code on Renata Magner's (https://github.com/RenataMagner/web_scraping_fii/blob/master/web_scraping-fiiv2.ipynb). I still have to implement error handling and many other improvements on the code, that's just the first version. Without further ado, that's what i came up with:

```
from bs4 import BeautifulSoup
import requests
import pandas as pd

url = 'https://www.fundsexplorer.com.br/ranking'
html = requests.get(url).content
soup = BeautifulSoup(html, 'html.parser')

# stores scraped data on a list
results = soup.find_all("td")

# counts how many entries we got. each entry has 26 'td' lines each.
fii_count=int(len(results)/26)

# initialize the variables
fii_info={}
fii_list=[]

'''
index - field
[0] - COD FUNDO
[1] - SETOR
[2] - PRECO_ATUAL
[3] - LIQUIDEZ DIARIA
[4] - DIVIDENDO
[5] - dividend_yield
[6] - dy_3m
[7] - dy_6m
[8] - dy_12m
[9]- dy_3m_media
[10] - dy_6m_media
[11] - dy_12m_media
[12] - dy_ano
[13] - variacao_preco
[14] - rentabilidade_periodo
[15] - rentabilidade_acumulada
[16] - patrimonio_liq
[17] - vpa
[18] - p_vpa
'''

# runs through collected data and extracts the desided info
for fii in range(fii_count):
    fii_info['codigo_fundo']=results[fii*26].get_text()
    fii_info['preco_atual']=results[fii*26+2].get_text()
    fii_info['setor']=results[fii*26+1].get_text()
    fii_info['p/vpa']= results[fii*26+18].get_text()
    fii_info['dividend_yield']=results[fii*26+5].get_text()
    fii_info['dividendo']=results[fii*26+4].get_text()
    fii_info['dy_12m_media']=results[fii*26+11].get_text()
    fii_list.append(fii_info)
    fii_info={}

# generates the CSV output
fii_table = pd.DataFrame(data=fii_list)
fii_table.to_csv('fii_table.csv')
```

**References:**

https://github.com/RenataMagner/web_scraping_fii/blob/master/web_scraping-fiiv2.ipynb

https://realpython.com/python-csv/

https://www.fundsexplorer.com.br/ranking