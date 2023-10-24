import telegram
from telegram.ext import Updater, CommandHandler
import subprocess
import multiprocessing
import os

TOKEN = os.environ['TOKEN']
 

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! ")

def run_trade_bot():
   
    python_interpreter = '/usr/local/bin/python3.11'

    script_to_run = 'ruistradingbotwtg.py'


    subprocess.run([python_interpreter, script_to_run])
    
def call_trade_bot(update, context):
    trade_bot_process = multiprocessing.Process(target=run_trade_bot)
    trade_bot_process.start()  
    
def main():
    bot = telegram.Bot(token='TOKEN')
    updater = Updater(token='TOKEN', use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    trade_handler = CommandHandler('trade', call_trade_bot)
    dispatcher.add_handler(trade_handler)
   
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
