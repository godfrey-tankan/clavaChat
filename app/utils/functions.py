import  re
def extract_house_details(string):
    pattern = r'^(.*?)\sin\s(.*?)(?:\s*\$([\d,]+))?$'
    match = re.search(pattern, string)
    house_info, location, budget = "", "", 0
    
    if match:
        house_info = match.group(1)
        location_parts = match.group(2).split(" ")
        location = " ".join(location_parts[:2])
        # location = match.group(2)
        try:
            budget = int(match.group(3).replace(',', '')) if match.group(3) else 100000
        except (IndexError, ValueError):
            budget = 0
    return house_info, location, budget

x = extract_house_details("3 bedroom house in Lekki near police station or else $300")
print(x)