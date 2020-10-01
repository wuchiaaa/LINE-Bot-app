from django.conf import settings

from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction

import requests

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

def helpAQI(event):  
    try:
        message = TextSendMessage(  
            text = '''空氣品質查詢\n輸入例如：\n「高雄空氣品質如何?」\n「小港PM2.5?」\n「高雄前鎮空氣品質」'''
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
        
def helpRATE(event):  
    try:
        message = TextSendMessage(  
            text = '''匯率查詢\n輸入例如：\n「美元匯率如何?」\n「英鎊一元兌換台幣多少錢?」\n「日幣匯率」'''
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
     