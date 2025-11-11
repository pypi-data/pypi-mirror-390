import requests

class Payamak:
    BASE_URL = "https://api.sms-webservice.com/api/V3/Send"
    
    #sandbox
    # BASE_URL = "https://api.sms-webservice.com/api/V3SandBox/Send/"

    def __init__(self, api_key:str, sender:int=50004075014432):
        self.api_key = api_key
        self.sender = sender

    def send_sms(self, text, *recipients)->dict:
        recipients_str = ",".join(recipients)
        url = f"{self.BASE_URL}?ApiKey={self.api_key}&Text={text}&Sender={self.sender}&Recipients={recipients_str}"

        try:
            response = requests.get(url)
            response.raise_for_status() 

            res = str(response.text).replace('true','True').replace('false','False').replace('null','None')
            
            return res

        except requests.exceptions.RequestException as err:
            print(f"❌ Error sending SMS: {err}")
            return None

                                                