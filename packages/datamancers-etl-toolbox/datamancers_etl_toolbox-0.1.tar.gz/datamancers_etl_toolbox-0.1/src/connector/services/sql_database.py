from sqlalchemy import create_engine
import pandas as pd
import logging
import datamonk.utils.functions as utls


class instance():
    def __init__(self,sqlSystem,username,password,host,port,database):
        self.engine = create_engine(sqlSystem + '://'+username+':'+password + '@'+host+':'+port+'/'+database)
        self.engine.connect()
        logging.info("connected to database:" + host +  "-" + database)
        logging.info("")
    def query_table(self,tableName,columns="*",output="pandas",**kwargs):
        logging.info("QUERY generation for table: "+tableName)
        logging.info("")
        query = 'SELECT ' + columns + ' FROM "' + tableName + '"'
        if "table_config" in kwargs:
            for key in ["where","incremental"]:
                if key in list(kwargs["table_config"].keys()):
                    kwargs[key]=kwargs["table_config"][key]
        if "where" in kwargs:
            query = query + " WHERE " +  kwargs["where"]
        if "incremental" in kwargs and kwargs["output_table"].exists == True:
                lastValue = kwargs["output_table"].get_lastValue(column=kwargs["incremental"]["column"])
                if lastValue == "NaT":
                    lastValue="2019-01-01"
                operator = " AND " if "where" in kwargs else " WHERE "

                query = query + operator + kwargs["incremental"]["column"] + " > '" + lastValue + "'"
        logging.info(query)

        if output == "pandas":
            results_output = pd.read_sql_query(query, con=self.engine)
        elif output == "dict":
            results= self.engine.execute(query).fetchall()
            results_output = [utls.dictionary.formatting(dict(row),"gcp_type_conversion",**kwargs) for row in results]

        logging.info("")
        logging.info ("QUERY table: "+tableName +"  sucessful")

        return results_output

    def query_string(self,query_string,output="pandas"):
        if output == "pandas":
            results_output = pd.read_sql_query(query_string, con=self.engine)
        elif output == "dict":
            results= self.engine.execute(query_string).fetchall()
            results_output = [utls.dictionary.formatting(dict(row),"gcp_type_conversion",**kwargs) for row in results]
        return results_output
    def get_schema(self):
        result=self.engine.execute("SELECT * FROM INFORMATION_SCHEMA.COLUMNS").fetchall()
        return result