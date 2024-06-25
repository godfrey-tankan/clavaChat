import re

def extract_product_details(string):
    product_name, condition, price = "", "", ""
    if 'new' in string:
        condition = 'new'
    elif 'used' in string:
        condition = 'used'
    elif 'boxed' in string:
        condition = 'boxed'
    else:
        condition = 'pre-owned' 

    product_name = string.split(condition)[0].strip()

    price_match = re.findall(r'\$\d+', string)
    if price_match:
        price = float(price_match[0][1:]) 
    else:
        price = 20000 
    return product_name, condition, price

x,y,z = extract_product_details("iPhone 12 13 pro max boxed 1000")
print(x,y,z)  # ('iPhone 12', 'new', 1000.0)