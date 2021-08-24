import datetime
from tempgen.libs.num2t4ru import decimal2text

def ru_date_month_as_string_year():
    month_names = ['', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    now = datetime.datetime.today()
    return ' '.join([str(x) for x in [now.day, month_names[now.month], now.year]]) + 'г.'

def ru_monetary_ending_append(value, *args):
    temp = str(value).split('.')
    integral, fractional = temp if len(temp) > 1 else temp + ['']
    truncated = float('.'.join([integral, fractional[:1]]))
    monetary_ending = decimal2text(truncated, int_units=((u'рубль', u'рубля', u'рублей'), 'm')).split(' ')[-2]
    return '%s %s' % (value, monetary_ending)

class Transforms():
    def __init__(self):
        self.name_transform_map = {
            'append': lambda value, postfix, *args: str(value) + postfix,
            'inverted_date': lambda *args: datetime.datetime.today().strftime('%Y%m%d')[2:],
            'ru_date_month_as_string_year': lambda *args: ru_date_month_as_string_year(),
            'ru_monetary_string_replace': lambda value, *args: "{:,.2f}".format(float(value)).replace(",", " ").replace('.', ','),
            'ru_monetary_as_string': lambda value, *args: decimal2text(float(value),
                int_units=((u'рубль', u'рубля', u'рублей'), 'm'),
                exp_units=((u'копейка', u'копейки', u'копеек'), 'f')
            ).capitalize(),
            'ru_monetary_ending_append': ru_monetary_ending_append,
        }
