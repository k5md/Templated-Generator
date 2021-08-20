import datetime
from tempgen.libs.num2t4ru import decimal2text

def ru_dmy():
    month_names = ['', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    now = datetime.datetime.today()
    return ' '.join([str(x) for x in [now.day, month_names[now.month], now.year]]) + 'г.'

name_transform_map = {
    'num2text': lambda x: decimal2text(x,
        int_units=((u'рубль', u'рубля', u'рублей'), 'm'),
        exp_units=((u'копейка', u'копейки', u'копеек'), 'f')
    ).capitalize(),
    'inverted_date': lambda x: datetime.datetime.today().strftime('%Y%m%d')[2:],
    'ru_dmy': lambda x: ru_dmy()
}