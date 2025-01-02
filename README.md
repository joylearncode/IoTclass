# [物聯網與大數據] 期末專題 廚房火災偵測器
![PXL_20241228_021016582](https://github.com/user-attachments/assets/b152b173-a8fc-4259-ad6f-bd74d993b67e)

## :beginner: Design Info 研究動機

:small_blue_diamond:Design Name: 廚房火災偵測器

:small_blue_diamond:Why:

近年來，台灣老年人口比例逐漸攀升，獨居長者和隔代教養的家庭也日益增多。由於生理機能退化或記憶力衰退等因素，老年人在居家生活中面臨許多安全風險，其中廚房火災更是不容忽視的潛在危險。

本研究計畫旨在運用物聯網科技，結合簡易的硬體設備和軟體程式，開發一套 基於樹莓派的廚房火災偵測系統，以期降低居家火災發生的風險，提升居家安全。

:small_blue_diamond:計畫緣起：

家中長輩習慣使用傳統瓦斯爐烹飪，但偶爾會因記憶力衰退或注意力不集中而忘記關火，造成安全隱患。
由於工作或其他因素，子女無法與長輩同住，無法即時提供協助或照護。
考量家中電路配置和電費成本等因素，更換 IH 爐等設備的可行性較低。
長輩保有自行烹飪的習慣和意願，且不偏好仰賴外送餐點。
基於上述背景，本研究希冀透過科技的力量，為長輩打造更安全的居家環境，同時兼顧其生活習慣和自主性。
## :wrench: Components

| **Item** 	| **Discription** 	| 
|----------	|----------	|
| Raspberry Pi 4 |          	|
| Breadboard|          	| 
| Wires|          	| 
| Flame sensor| 偵測火焰
| DHT-22| 偵測溫度
| MQ-2| 偵測瓦斯氣體

## :house: 應用場景示意圖
<img width="778" alt="截圖 2024-12-30 下午3 22 08" src="https://github.com/user-attachments/assets/0c911ed8-7d21-4063-8f99-17b2c5fc44c3" />

## ⭐ Assemble Your Circuit
![demo1_bb](https://github.com/user-attachments/assets/07b075fd-bf08-439e-a18a-ce4fe1e062dd)


## :blush: Code
***請見app.py***

## 💁‍♀️ 製作過程
▶️ Step 1<br>
設計溫濕度偵測器、火焰sensor、瓦斯氣體senor，使樹莓派可以同時作動三種功能，
並串接data線至樹莓派GPIO上。
<br>
</br>
▶️ Step 2<br>
至Line Developers (https://developers.line.biz/zh-hant/) 開通LineBot功能，
並取得User ID, Channel secret, Channel access token (long-lived)
這三個資訊稍後會串接至python中。<br>
遇到花比較久時間研究的問題是webhook URL，後來用ngrok解決，順利串接API成功。
<br>
</br>
▶️ Step 3</br>
開始寫code。
這裡開始遇到比較多的困難，
🐛1 首先因為一開始使裝的樹莓派版本中內建的Python版本偏舊，導致LineBot API無法串接，
所以先重新燒錄樹莓派作業系統。
</br>
<img width="580" alt="截圖 2025-01-02 中午12 08 56" src="https://github.com/user-attachments/assets/16a678b7-9e97-40a5-a6d0-6e32b5843090" />
</br>
🐛2 但新安裝好的系統在Thonny中執行LineBot還是有問題，安裝套件後無法在Thonny中被執行，所以我改在虛擬環境中跑程式。</br>
安裝虛擬環境 https://docs.python.org/zh-tw/3/tutorial/venv.html</br>
安裝好後再開始安裝所需套件，之後則可由終端機進入虛擬環境中，並將欲執行的程式碼存在與venv一樣的地方。</br>
</br>
進入虛擬環境：</br>
`pi@raspberrypi:cd myproject`<br/>
`pi@raspberrypi:~/myproject$ source venv/bin/activate`
<br>
</br>
直到這裡才算是將運行Python的環境建置完成。
<br>
</br>
正式開始設計程式：<br>
🟢 DTH22 需安裝額外套件 adafruit_dht <br>
🟢 GPIO PIN腳設定：<br>
DHT_PIN = 4  # 溫度感測器 <br>
FIRE_PIN = 21  # 火焰感測器 <br>
GAS_PIN = 14  # 瓦斯氣體感測器 <br>
🟢 LineBot API串接：
```
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 初始化 Flask 應用程式
app = Flask(__name__)

# 填入您的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = '你的 Channel Access Token'
LINE_CHANNEL_SECRET = '你的 Channel Secret'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 HTTP 標頭中的 X-Line-Signature
    signature = request.headers['X-Line-Signature']
    # 獲取 POST 請求的 body
    body = request.get_data(as_text=True)

    try:
        # 驗證請求並處理事件
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 獲取使用者傳送的訊息
    user_message = event.message.text
    # 回覆訊息
    reply_message = f"您說的是：{user_message}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

🟢 設定警示條件並回傳Linebot發出警示：

```
if temp and temp > 45:
  send_alert(f"Warning: High temperature detected! Current temperature: {temp:.1f}°C")
if flame:
  send_alert("Warning: Flame detected in the kitchen!")
if gas:
  send_alert("Warning: Gas leak detected in the kitchen!")
```
🟢 反覆測試微調程式碼 <br>
🟢 Linebot訊息傳送通知如下：<br>
![image](https://github.com/user-attachments/assets/c3fa7207-f2c2-4934-87bc-b2bf1b6836c1)
<br>
</br>
## 🔴 檢討：<br>
1. 火焰sensor的工作基礎是火焰在燃燒過程中釋放的光輻射，範圍涵蓋了紫外線(UV)、可見光(VIS) 和紅外線(IR)。<br>
所以只要敏感度稍微調高一點，只要偵測到可見光也會發出alert。如果可以改用紅外線偵測鏡頭，可以更準確地監控環境（但缺點是價格太高）。<br>
2. 瓦斯sensor到最後都沒有成功發出alert，不確定是不是環境中的瓦斯濃度不夠高的關係，但也的確網路上的樹莓派project中，尚未看過有人拿gas sensor實測。<br>
但有找到可以讓裝置回傳氣體濃度的影片。<br>
所以我認為demo的時候如果可以加一個回傳空氣中氣體濃度的code，而非偵測到一定濃度的氣體才發出alert會更好（因為也不確定這個裝置的敏感度數值是如何設定，但又需要確認裝置是否有效時，另外設定偵測氣體濃度數值會更好）。<br>
![截圖 2025-01-02 中午12 49 03](https://github.com/user-attachments/assets/22d8981a-04bb-4df1-b5e9-141c3ba3825d)
