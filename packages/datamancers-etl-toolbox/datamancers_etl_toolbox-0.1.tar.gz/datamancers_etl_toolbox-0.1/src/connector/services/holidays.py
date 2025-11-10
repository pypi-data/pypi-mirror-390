import files.flow_blueprints.scripts.extract.holidays as holidays
import datetime

years = [i for i in range(2000,2050)]
test=holidays.country_holidays("CZ",years=years)
import pandas as pd
dict_test=pd.DataFrame.from_dict(test,orient="index").reset_index().rename(columns={"index":"date",0:"holiday"})
dict_test.to_csv("holidays.csv",index=False)