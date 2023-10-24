import websocket
import json
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
import requests
import time
from binance.error import ClientError
from binance.um_futures import UMFutures
import ccxt
import telegram
from telegram.ext import Updater, CommandHandler


TOKEN = ${{secrets.TOKEN}}
chatid =${{secrets.CHATID}}

class TextColor:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


key = ${{secrets.KEY}}
secret = ${{secrets.SECRET}}

exchange = ccxt.binance({
    'apiKey': key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    }
})
def send_message_using_token(message_text):
    bot = telegram.Bot(token=TOKEN)
    bot.send_message(chat_id=chatid, text=message_text)
    
um_futures_client = UMFutures(key=key, secret=secret)
account_balance =  um_futures_client.balance()
target_asset = "USDT"
target_asset_balance = next((item for item in account_balance if item['asset'] == target_asset), None)
if target_asset_balance:
    cross_wallet_balance = target_asset_balance.get('crossWalletBalance', None)
    if cross_wallet_balance is not None:
        print('')
        print(f"{TextColor.YELLOW}Cross Wallet Balance ({target_asset}){TextColor.RESET}: 64.750000")
        print('')
        message_text = f"Cross Wallet Balance {target_asset}: {cross_wallet_balance}"+'\n\n'
        send_message_using_token(message_text)
    else:
        print(f"No 'crossWalletBalance' available for {target_asset}: {cross_wallet_balance}")
        
else:
    print(f"No balance available for {target_asset}")
    

SOCKET = 'wss://fstream.binance.com/ws/btcusdt@trade'
INTERVAL = 300
total_volume = 0.0
ticker_endpoint = "https://fapi.binance.com/fapi/v1/ticker/24hr"
params = {
    'symbol': 'btcusdt',
}
average_price = 0.0
prices = [] 
next_average_time = time.time() + INTERVAL
in_position = False 
number_of_positions = 0
volume_list = []
price_list = []
iteration_no=int(0)

allowed_precision = 2
rounded_quantity = round(float(cross_wallet_balance), allowed_precision)


       
def get_current_btc_price():
    try:
        response_btc = requests.get(ticker_endpoint, params)
        ticker_data_btc = response_btc.json()
        price_btc = float(ticker_data_btc['lastPrice'])
        return price_btc
    except Exception as e:
        print(f"Error fetching BTC price: {e}")
        return 0.0
def get_24h_volume():
    try:
        response = requests.get(ticker_endpoint, params)
        ticker_data = response.json()
        volume_btc = float(ticker_data['volume'])
        return volume_btc
    except Exception as e:
        print(f"Error fetching 24h volume: {e}")
        return 0.0
def calculate_average_price(prices):
    if prices:
        return sum(prices) / len(prices)
    return 0.0


def on_message(ws, message):
    global message_text,average_price, prices, next_average_time, previous_volume, previous_price, in_position, number_of_positions, total_volume_usdt,current_price_btc, volume_list, price_list, in_position,iteration_no
    
    
    try:
        current_price_btc = get_current_btc_price()
        volume_btc = get_24h_volume()
        total_volume_usdt = round((current_price_btc * volume_btc),2)
        volume_list.append(total_volume_usdt)
        price_list.append(current_price_btc)
        
           
        if len(volume_list) > 1:
            previous_volume = round(volume_list[-2],2)
            previous_price = round(price_list[-2],2)
        else:
            previous_volume=0.0
            previous_price=0.0
            
        iteration_no=iteration_no+1
       
        
        current_time = time.time()
        if current_time >= next_average_time:
            if prices:
                avg_price = calculate_average_price(prices)
                print(f"Average BTC PRICE: {avg_price:.2f}")
                prices.clear()
                next_average_time = current_time + INTERVAL
        print('\n')
        
        print(TextColor.BLUE+f"Iteration no. {iteration_no}"+TextColor.RESET)
        print('')
        print(f"{TextColor.GREEN}Previous Volume: {TextColor.RESET} {previous_volume}")
        print(f"{TextColor.GREEN}Current Volume:   {TextColor.RESET}{total_volume_usdt}")
        print('')
        print(f"{TextColor.GREEN}Previous Price:   {TextColor.RESET}{previous_price}")
        print(f"{TextColor.GREEN}Curent Price:     {TextColor.RESET}{current_price_btc}")
        
        message_text = f"Iteration no. {iteration_no}"+'\n\n'
        message_text += f"Prev Volume:  {previous_volume}\n"
        message_text += f"Curr Volume:  {total_volume_usdt}\n\n"
        message_text += f"Prev Price:      {previous_price}\n"
        message_text += f"Curr Price:      {current_price_btc}"
        if iteration_no == 1:
            send_message_using_token(message_text)
    
        
        if len(volume_list)>1:
            volume_increase=(((total_volume_usdt-previous_volume)/previous_volume)*100)
        else:
            volume_increase=0.0
        if len(volume_list)>1:
            if previous_volume * 1.01 <= total_volume_usdt:
                print('valid')
                if not in_position:
                    if current_price_btc > previous_price:
                        print('long long')
                        symbol = 'BTC/USDT'
                        type = 'market'  
                        side = 'buy'  
                        amount = 0.0025 
                        params = {
                            'positionSide': 'LONG'
                            }
                        long_order = exchange.create_order(symbol, type, side, amount, params=params)
                        print(long_order)
                        
                        if long_order:
                            in_position = True
                            print(in_position)
                            number_of_positions += 1
                            print(number_of_positions)
                            
                if in_position:
                    if current_price_btc>=35000.00:
                        in_position = False
                print('di pa abot')
                    
                if number_of_positions < 2:
                    if current_price_btc < previous_price:
                        print('short')
                        symbol = 'BTC/USDT'
                        type = 'market'  
                        side = 'sell'  
                        amount = 0.0025 
                        params = {
                            'positionSide': 'SHORT'}
                        short_order = exchange.create_order(symbol, type, side, amount, params=params)
                        print(short_order)
                        if short_order:
                            number_of_positions += 1
                    print('not valid')
            else:
                print('')
                print(f"{TextColor.MAGENTA}Volume increased:{TextColor.RESET} {round(volume_increase,2)}%")
                print('\n')
                print(TextColor.RED+"A trade wasn't executed"+TextColor.RESET)
                message_text += f"\n\nVolume Up:     {round(volume_increase,2)}%"
                message_text += "\n\nA trade wasn't executed"
                send_message_using_token(message_text)
                
    
        
    except Exception as e:
        print(f"Error: {e}")
    
    INTERVAL=10
    print('\n') 
    
    while INTERVAL > 0:
        minutes, seconds = divmod(INTERVAL, 60)
        print(TextColor.BLACK+f"Next iteration in {minutes:02d}:{seconds:02d}", end='\r'+TextColor.RESET)
        time.sleep(1) 
        INTERVAL -= 1
    print('=====================================')
    
              
            
def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")

def on_open(ws):
    print(TextColor.BLACK+"WebSocket Opened"+TextColor.RESET)
    message_text = "\n\nWebSocket Opened"
    send_message_using_token(message_text)
    payload = {
        "method": "SUBSCRIBE",
        "params": [
            f"btcusdt@trade"
        ],
        "id": 1
    }
    ws.send(json.dumps(payload))

if __name__ == "__main__":
    while True:
        ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.run_forever()
        time.sleep(INTERVAL)
        
        
       
        #if new volume na 5 minutes interval +1% > last volume man chcek ff conditions
        #if current btc price>= average price or btc< provided price, create long future in_position=true/false
        #if current btc price< average price or  btc> provided price, create short
        #if in_position=true, number of positions=1 define take profit, if 2 positions no take profit

        
