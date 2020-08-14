import telebot
import config
import pb
import datetime
import pytz
import json
import traceback



P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):  
    bot.send_message(  
        message.chat.id,  
        'Привет!  Я могу показать вам курсы валют.\n' +  
        'Чтобы узнать курсы обмена нажмите /exchange.\n' +  
        'Чтобы получить помощь, нажмите /help.'  
  )
  
@bot.message_handler(commands=['help'])
def help_command(message):  
    keyboard = telebot.types.InlineKeyboardMarkup()  
    keyboard.add(  
        telebot.types.InlineKeyboardButton(  
            'Сообщение Админу', url='telegram.me/moneynotsleep_admin'  
  )  
    )  
    bot.send_message(  
        message.chat.id,  
        '1) Чтобы получить список доступных валют, нажмите /exchange.\n' +  
        '2) Нажмите на интересующую вас валюту.\n' +  
        '3) Вы получите сообщение, содержащее информацию об источнике и целевых валютах, ' +  
        'цены покупки и цены продажи.\n' +  
        '4) Нажмите «Обновить», чтобы получить актуальную информацию о запросе. ' +  
        'Бот также покажет разницу между предыдущим и текущим обменным курсом.\n' +  
        '5) Бот поддерживает встроенный режим.  Введите @haiko_bot в любом чате и первые буквы валюты.',  
        reply_markup=keyboard  
    )


@bot.message_handler(commands=['exchange'])  
def exchange_command(message):  
    keyboard = telebot.types.InlineKeyboardMarkup()  
    keyboard.row(  
        telebot.types.InlineKeyboardButton('USD', callback_data='get-USD'),
        telebot.types.InlineKeyboardButton('BTC', callback_data='get-BTC')
    )  
    keyboard.row(  
        telebot.types.InlineKeyboardButton('EUR', callback_data='get-EUR'),  
        telebot.types.InlineKeyboardButton('RUR', callback_data='get-RUR')  
    )  
  
    bot.send_message(  
        message.chat.id,   
        'Нажмите на валюту для выбора:',  
        reply_markup=keyboard  
    )
    
@bot.callback_query_handler(func=lambda call: True)  
def iq_callback(query):  
    data = query.data  
    if data.startswith('get-'):  
        get_ex_callback(query)  
    else:  
        try:  
            if json.loads(data)['t'] == 'u':  
                edit_message_callback(query)  
        except ValueError:  
            pass

def get_ex_callback(query):  
    bot.answer_callback_query(query.id)  
    send_exchange_result(query.message, query.data[4:])

def send_exchange_result(message, ex_code):  
    bot.send_chat_action(message.chat.id, 'typing')  
    ex = nby.get_exchange(ex_code)  
    bot.send_message(  
        message.chat.id, serialize_ex(ex),  
        reply_markup=get_update_keyboard(ex),  
	parse_mode='HTML'  
    )
    
def get_update_keyboard(ex):  
    keyboard = telebot.types.InlineKeyboardMarkup()  
    keyboard.row(  
        telebot.types.InlineKeyboardButton(  
            'Update',  
	    callback_data=json.dumps({  
                't': 'u',  
		'e': {  
                    'b': ex['buy'],  
		    's': ex['sale'],  
		    'c': ex['ccy']  
                }  
            }).replace(' ', '')  
        ),  
	telebot.types.InlineKeyboardButton('Share', switch_inline_query=ex['ccy'])  
    )  
    return keyboard
    
def serialize_ex(ex_json, diff=None):  
    result = '<b>' + ex_json['base_ccy'] + ' -> ' + ex_json['ccy'] + ':</b>\n\n' + \  
             'Buy: ' + ex_json['buy']  
    if diff:  
        result += ' ' + serialize_exchange_diff(diff['buy_diff']) + '\n' + \  
                  'Sell: ' + ex_json['sale'] + \  
                  ' ' + serialize_exchange_diff(diff['sale_diff']) + '\n'  
    else:  
        result += '\nSell: ' + ex_json['sale'] + '\n'  
    return result



def serialize_exchange_diff(diff):  
    result = ''  
    if diff > 0:  
        result = '(' + str(diff) + ' <img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="↗️" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/72x72/2197.png">" src="https://s.w.org/images/core/emoji/72x72/2197.png">)'  
    elif diff < 0:  
        result = '(' + str(diff)[1:] + ' <img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="↘️" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/72x72/2198.png">" src="https://s.w.org/images/core/emoji/72x72/2198.png">)'  
    return result

def edit_message_callback(query):  
    data = json.loads(query.data)['e']  
    exchange_now = nby.get_exchange(data['c'])  
    text = serialize_ex(  
        exchange_now,  
	get_exchange_diff(  
            get_ex_from_iq_data(data),  
	    exchange_now  
        )  
    ) + '\n' + get_edited_signature()  
    if query.message:  
        bot.edit_message_text(  
            text,  
	    query.message.chat.id,  
	    query.message.message_id,  
	    reply_markup=get_update_keyboard(exchange_now),  
	    parse_mode='HTML'  
	)  
    elif query.inline_message_id:  
        bot.edit_message_text(  
            text,  
	    inline_message_id=query.inline_message_id,  
	    reply_markup=get_update_keyboard(exchange_now),  
	    parse_mode='HTML'  
	)

def get_ex_from_iq_data(exc_json):  
    return {  
        'buy': exc_json['b'],  
	'sale': exc_json['s']  
    }
    
def get_exchange_diff(last, now):  
    return {  
        'sale_diff': float("%.6f" % (float(now['sale']) - float(last['sale']))),  
	'buy_diff': float("%.6f" % (float(now['buy']) - float(last['buy'])))  
    }
    
def get_edited_signature():  
    return '<i>Updated ' + \
           str(datetime.datetime.now(P_TIMEZONE).strftime('%H:%M:%S')) + \
           ' (' + TIMEZONE_COMMON_NAME + ')</i>'
           
bot.polling(none_stop=True)