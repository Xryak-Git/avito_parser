import re
#print(''.join(filter(lambda x: x.isdigit(), '53 jnsdfs 000')))

# s = '3dfjnaskl ker32 ,. d32vl,  '
# pattern = r'\d,\d'
# ans = re.findall(pattern, s)
# print(ans[-1])

def _get_price():
    price = 0
    try:
        price = 'Цена не указана'
        price = int(price)
    except Exception as ex:
        print(ex)
    return price

print(_get_price())