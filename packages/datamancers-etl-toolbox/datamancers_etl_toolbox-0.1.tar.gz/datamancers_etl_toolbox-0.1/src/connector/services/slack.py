
import logging
logger=logging.getLogger(__name__)


from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class instance:
    def __init__(self,token):
        self.token = token
        self.client = WebClient(token=self.token)
        try:
            self.client.api_test()
        except SlackApiError as e:
            logger.error(msg="authentication failed, message:{}".format(e.response["error"]))


    def send_message(self,channel,message):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message
            )
            if response.status_code == 200:
                logger.info(msg="message sent successfuly, message:{}".format(message))
        except SlackApiError as e:
            logger.info(msg="message failed, message:{}".format(e.response["error"]))# You will get a SlackApiError if "ok" is False
            assert e.response["error"]    # str like 'invalid_auth', 'channel_not_found'


