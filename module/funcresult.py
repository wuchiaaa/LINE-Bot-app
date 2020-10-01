import jieba
import requests
import twder    # 新台幣匯率擷取
from django.conf import settings
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

jieba.set_dictionary('module/dictionary/dict.txt.big.txt')
jieba.load_userdict('module/dictionary/user_dict_test.txt')
with open('module/dictionary/stop_dict_test.txt', 'r', encoding='utf-8-sig') as file:
    stops = file.read().split('\n')
with open('module/dictionary/sitename_dict_test.txt', 'r', encoding='utf-8-sig') as file:
    sitenames = file.read().split('\n')


currencies = {'美金': 'USD', '美元': 'USD', '港幣': 'HKD', '英鎊': 'GBP', '澳幣': 'AUD', '加拿大幣': 'CAD', \
              '加幣': 'CAD', '新加坡幣': 'SGD', '新幣': 'SGD', '瑞士法郎': 'CHF', '瑞郎': 'CHF', '日圓': 'JPY', \
              '日幣': 'JPY', '南非幣': 'ZAR', '瑞典幣': 'SEK', '紐元': 'NZD', '紐幣': 'NZD', '泰幣': 'THB', \
              '泰銖': 'THB', '菲國比索': 'PHP', '菲律賓幣': 'PHP', '印尼幣': 'IDR', '歐元': 'EUR', '韓元': 'KRW', \
              '韓幣': 'KRW', '越南盾': 'VND', '越南幣': 'VND', '馬來幣': 'MYR', '人民幣': 'CNY'}

keys = currencies.keys()
tlist = ['現金買入', '現金賣出', '即期買入', '即期賣出']

dictCounty = {"臺北市": "臺北市", "新北市": "新北市", "桃園市": "桃園市", "臺中市": "臺中市", "臺南市": "臺南市", \
              "高雄市": "高雄市", "新竹縣": "新竹縣", "苗栗縣": "苗栗縣", "彰化縣": "彰化縣", "南投縣": "南投縣", \
              "雲林縣": "雲林縣", "嘉義縣": "嘉義縣", "屏東縣": "屏東縣", "宜蘭縣": "宜蘭縣", "花蓮縣": "花蓮縣", \
              "臺東縣": "臺東縣", "澎湖縣": "澎湖縣", "金門縣": "金門縣", "連江縣": "連江縣", "基隆市": "基隆市", \
              "新竹市": "新竹市", "嘉義市": "嘉義市", "臺北": "臺北市", "新北": "新北市", "桃園": "桃園市", \
              "臺中": "臺中市", "臺南": "臺南市", "高雄": "高雄市", "新竹": "新竹縣", "苗栗": "苗栗縣", \
              "彰化": "彰化縣", "南投": "南投縣", "雲林": "雲林縣", "嘉義": "嘉義縣", "屏東": "屏東縣", \
              "宜蘭": "宜蘭縣", "花蓮": "花蓮縣", "臺東": "臺東縣", "澎湖": "澎湖縣", "金門": "金門縣", "連江": "連江縣"}


def MakeCountyAQI(county):
    url = "http://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-000259?filters=County eq '" + \
        county + "'&sort=County&offset=0&limit=1000"

    data = requests.get(url)
    AQImsg = ''
    
    if data.status_code == 500:
        print("無AQI資料")
    else:
        AQIData = data.json()["result"]["records"]
        for row in AQIData:
            AQImsg = AQImsg + row['SiteName'] + '  ' + row['AQI'] + '  ' + row['Status'] + "\n"
            
        return AQImsg    


def MakeSiteNameAQI(sitename):
    url = "http://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-000259?filters=SiteName eq '" + \
        sitename + "'&sort=SiteName&offset=0&limit=1000"

    data = requests.get(url)
    AQImsg = ""
    
    if data.status_code == 500:
        return "無 AQI 資料"
    else:
        AQIData = data.json()["result"]["records"][0]
        AQImsg += "AQI = " + AQIData["AQI"] + "\n"
        AQImsg += "PM2.5 = " + AQIData["PM2.5"] + " μg/m3\n"
        AQImsg += "PM10 = " + AQIData["PM10"] + " μg/m3\n"
        AQImsg += "空品：" + AQIData["Status"]
        return AQImsg    
        
def getRate(currency):
    
     show = currency + '匯率：\n'
     if currency in keys:
         for i in range(4):
             exchange = float(twder.now(currencies[currency])[i+1])
             show = show + tlist[i] + '：' + str(exchange) + '\n'
         return show
     else:
        return '無此貨幣資料！'     
    

def search(event, searchword):
    
    str1 = searchword
    str1 = str1.replace('台', '臺')

    str2 = jieba.cut(str1, cut_all=False)
    
    words = []
    
    for word in str2:
        if word not in stops:
            words.append(word)
    currency = None


    result = ''
    for word in words:
        # 先判斷rate, 後判斷aqi
        if word in currencies:
            currency = word
            result = getRate(currency)
            break
        
        else:               
            set1 = set(sitenames)
            set2 = set(words)
            sitename = set1.intersection(set2)
            sitename = list(sitename)
            
            if len(sitename) > 0:
                result = sitename[0] + ':\n' + MakeSiteNameAQI(sitename[0])
                break
            else:
                for word in words:
                    print('%', word)
                    if word in dictCounty:
                        result = MakeCountyAQI(dictCounty[word])
                        break 
                    
    try:
        message = TextSendMessage(  
            text = result
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        result = '不好意思，目前沒有完全符合您提問的答案，建議您換個方式描述或是一次詢問單一問題，或許我就能回答您喔，謝謝!!!'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=result))
                        
    
    
