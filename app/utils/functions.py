# import re

# def test(message):
#     if "[" in message:
#         seller_mobile = message.split(']')[1].strip()
#         print("seller_mobile:", seller_mobile.split()[-1])
#         print("seller_name:", seller_mobile.split()[-2])
#         if "boxed" in message.lower():
#             condition = "boxed"
#         else:
#             condition = "pre-owned"
#         products_list = message.split("]")[0].strip() + "]"
#         gadget_list =eval(products_list) 
#         for gadget in gadget_list:
#             print("gadget:", gadget)
#             # product_info = gadget.split('$')
#             product_name = product_info[0].strip()
#             price = float(product_info[1].strip())
#             print(".........prod name:", product_name, "price: $", price)

#         return "gadgets added successfully."
#     else:
#         print("no gadgets found")

# message = "['Samsung A04e 32/3 $95 ','Samsung A04e 64/3 $110 ','Samsung A14 64/4   $145 ','Samsung A15 128/4 $140 ','Samsung A15 256/6 $225 ','Samsung A24 64/4   $180 ','Samsung A24 128/4 $200 ','Samsung A34 128/6 $240 ','Samsung A53 128/6 $310 ','Samsung A54 128/8 $320 ','Samsung A54 256/8 $350 ','Samsung M04 64/4   $100 ','Samsung M13 64/4   $125 ','Samsung M13 128/6 $165 ','Samsung M14 128/6 5G $150 ','Samsung M34 128/6 5G $190 ','Samsung M54 5G 128/8 $390 ','Samsung F13 64/4    $120 ','Samsung F13 128/4 $150 ','Samsung F54 256/8 $300','Tab A7 Lite $160','Tab A9 64gb $180'] boxed  wakanda_phones  0780477080"

# test(message)