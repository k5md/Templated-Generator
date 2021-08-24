import datetime
from tempgen.libs.num2t4ru import decimal2text

def ru_date_month_as_string_year():
    month_names = ['', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    now = datetime.datetime.today()
    return ' '.join([str(x) for x in [now.day, month_names[now.month], now.year]]) + 'г.'

class Transforms():
    def __init__(self):
        self.name_transform_map = {
            'append': lambda value, postfix, *args: str(value) + postfix,
            'inverted_date': lambda *args: datetime.datetime.today().strftime('%Y%m%d')[2:],
            'ru_date_month_as_string_year': lambda *args: ru_date_month_as_string_year(),
            'ru_monetary_string_replace': lambda value, *args: "{:,.2f}".format(float(value)).replace(",", " ").replace('.', ','),
            'ru_monetary_as_string': lambda value, *args: decimal2text(value,
                int_units=((u'рубль', u'рубля', u'рублей'), 'm'),
                exp_units=((u'копейка', u'копейки', u'копеек'), 'f')
            ).capitalize(),
        }
