#!/usr/bin/env python
# coding: utf-8

# ## MODULES AND FUNCTIONS



import pandas_read_xml as pdx
import pandas as pd
import requests





## PARSE XML FUNCTION
import xml.etree.ElementTree as et

def parse_XML(xml_file, df_cols): 
    """Parse the input XML file and store the result in a pandas 
    DataFrame with the given columns. 
    
    The first element of df_cols is supposed to be the identifier 
    variable, which is an attribute of each node element in the 
    XML data; other features will be parsed from the text content 
    of each sub-element. 
    """
    
    xtree = et.fromstring(xml_file)
    
    rows = []
    
    for node in xtree: 
        res = []
        for el in df_cols: 
            if node is not None and node.find(el) is not None:
                res.append(node.find(el).text)
            else: 
                res.append(None)
        rows.append({df_cols[i]: res[i] 
                     for i, _ in enumerate(df_cols)})
    
    out_df = pd.DataFrame(rows, columns=df_cols)
        
    return out_df





### NESTED NODES PARSING

feed_nestedNodes_df=pdx.read_xml(path_or_xml=feed_URL
                 ,root_key_list=['SHOP','SHOPITEM']
                )

feed_param=feed_nestedNodes_df.loc[:,["PARAM"]]

# in case for separated columns for delivery nested part - commented out
#feed_delivery=pdx.auto_flatten(feed_nestedNodes_df.loc[:,["DELIVERY"]])
#feed_delivery.columns=feed_delivery.columns.str.replace(r'DELIVERY\|', '')

feed_delivery=feed_nestedNodes_df.loc[:,["DELIVERY"]]


### UNNESTED NODES PARSING AND ENCODING HANDLING

unNested_columns=feed_nestedNodes_df.columns
unNested_columns=[i for i in feed_nestedNodes_df.columns if i not in ["DELIVERY","PARAM"]]


response=requests.get(feed_URL)
response.encoding=response.apparent_encoding


feedUnNested_df=parse_XML(response.text,
                          df_cols=unNested_columns
                         )


# ### FINAL OUTPUT AND SAVING

##JOIN ALL PARTS OF FEED
feed_output=pd.concat([feedUnNested_df,feed_delivery,feed_param],axis=1)
#feed_output["HEUREKA_CPC"]=feed_output["HEUREKA_CPC"].str.replace(",",".")
feed_output["date"]=today
## SAVE TO OUTPUT DESTINATION

feed_output.to_csv(output_path ,index=False)


