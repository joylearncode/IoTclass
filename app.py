from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import RPi.GPIO as GPIO
import adafruit_dht
import time
import board

# Initialize Flask app
app = Flask(__name__)

# Line bot API setup
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
USER_ID = 'USER_ID_TO_NOTIFY'

# GPIO setup
GPIO.setmode(GPIO.BCM)
DHT_SENSOR = Adafruit_DHT.DHT22
TEMP_PIN = 4
FLAME_PIN = 21
GAS_PIN = 14
GPIO.setup(FLAME_PIN, GPIO.IN)
GPIO.setup(GAS_PIN, GPIO.IN)

# Function to read temperature
def read_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, TEMP_PIN)
    return temperature

# Function to check fire
def detect_flame():
    return GPIO.input(FLAME_PIN) == GPIO.LOW

# Function to check gas
def detect_gas():
    return GPIO.input(GAS_PIN) == GPIO.LOW

# Alert function
def send_alert(message):
    line_bot_api.push_message(USER_ID, TextSendMessage(text=message))

# Background monitoring
def monitor_sensors():
    while True:
        try:
            temp = read_temperature()
            flame = detect_flame()
            gas = detect_gas()

            if temp and temp > 45:
                send_alert(f"Warning: High temperature detected! Current temperature: {temp:.1f}°C")
            if flame:
                send_alert("Warning: Flame detected in the kitchen!")
            if gas:
                send_alert("Warning: Gas leak detected in the kitchen!")

            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")

# Line bot webhook
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "temp":  # "\u6eab\u5ea6" is "\u6eab\u5ea6" in Unicode (Temperature)
        temp = read_temperature()
        if temp:
            reply = f"Current temperature: {temp:.1f}°C"
        else:
            reply = "Unable to read temperature."
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    try:
        # Run sensor monitoring in a separate thread
        from threading import Thread
        monitor_thread = Thread(target=monitor_sensors)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Run Flask app
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        GPIO.cleanup()