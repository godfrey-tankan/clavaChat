import re

def extract_product_details(string):
    product_name, condition, price = "", "", ""
    match = re.search(r'^(.*?)\s*,\s*(.*?)(?:\s+\$(\d+))?$', string)
    if match:
        product_name = match.group(1)
        condition = match.group(2)
        if match.group(3):
            price = int(match.group(3))
        else:
            price = 20000
        return product_name, condition, price
    else:
        print("Invalid input")
        return product_name, condition, price

x=extract_product_details("s22 ultra, boxed $20")
print(x)
