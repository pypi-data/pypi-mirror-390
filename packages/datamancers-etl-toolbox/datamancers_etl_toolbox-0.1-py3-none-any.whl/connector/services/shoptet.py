import pandas as pd
import requests as r
url = "https://www.vitco.cz/export/orders.csv?patternId=-9&partnerId=8&hash=dfdf220f1f11f7bbb01b5faf59b199939e6a75b10cb10c24143e7952c41f23cb"
data1=r.get(url)
data=pd.read_csv(url,sep=";",encoding="cp1250",header=0)

data