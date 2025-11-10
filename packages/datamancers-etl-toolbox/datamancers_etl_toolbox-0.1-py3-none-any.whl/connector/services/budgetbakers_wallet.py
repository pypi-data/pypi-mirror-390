import requests as r

class WalletSession:
    def __init__(self,username,password):
        self.base_url_api = "https://api.budgetbakers.com"
        self.base_url = "https://web.budgetbakers.com"
        self._session = r.session()
        self._session.headers.update({"Content-Type": 'application/x-www-form-urlencoded'})
        cookie = self._session.post(self.base_url_api + "/auth/authenticate/userpass",
                           data={"username": username, "password": password}).headers["set-cookie"]
        self._session.headers.update({"Cookie": cookie})

    def get_records(self):
        res = self._session.get(self.base_url_api + "/recordList")
        return res
instance = WalletSession(username="vit.mrnavek@gmail.com",password="fgh!tcy0cpf4WTV4qnf")

records=instance.get_records()
print(records.json())