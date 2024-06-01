import re
# def extract_product_info(string):
#     product_name, condition, price = "", "", ""
#     match = re.search(r'^(.*?)\s*,\s*(.*?)(?:\s+\$(\d+))?$', string)
#     if match:
#         product_name = match.group(1)
#         condition = match.group(2)
#         if match.group(3):
#             price = int(match.group(3))
#         else:
#             price = 10000
#         return product_name, condition, price
#     else:
#         return product_name, condition, price

def extract_product_details(string):
    product_name, condition, price ="", "", ""
    match = re.search(r'^(.*?)\s*,\s*(.*?)\s+\$(\d+)$', string)
    if match:
        product_name = match.group(1)
        condition = match.group(2)
        price = int(match.group(3))
        return product_name, condition, price
    else:
        return product_name, condition, price

input_string1 = "Laptop, Used $500"
input_string2 = "Desk, New"

product_name1, condition1, price1 = extract_product_details(input_string1)
product_name2, condition2, price2 = extract_product_details(input_string2)

print(f"Product 1: {product_name1}, {condition1}, ${price1}")
print(f"Product 2: {product_name2}, {condition2}, ${price2}")

