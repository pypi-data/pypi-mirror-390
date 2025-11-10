
import time
import subprocess
from selenium import webdriver
subprocess.call("killall Google\ Chrome",shell=True)

options = webdriver.ChromeOptions()

options.add_argument("user-data-dir=/Users/vitmrnavek/chrome_driver_profile")
options.add_argument("profile-directory=Profile 4")
webdriver.Chrome().close()
driver = webdriver.Chrome(options=options)
reporting_page='https://lookerstudio.google.com/reporting/0df10c1e-b854-4902-b852-d110a3ce1f8b/page/'
for i in ["p_xxlnegkled","p_1svvbgkled","p_7uxu8fkled","p_96deffkled"]:
    driver.get(f"{reporting_page}{i}")
    #driver.find_element("body").send_keys(Keys.CONTROL + 't')
    #driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
    time.sleep(20)



print("all processes finished successfully")
