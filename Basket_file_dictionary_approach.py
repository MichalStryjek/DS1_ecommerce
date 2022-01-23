from typing import Dict

Products: dict[str, int] = {
    'Pen': 0,
    'Apple': 0,
    'Apple pen': 0,
    'Pineapple': 0,
    'Pineapple pen': 0,
    'Pen Pineapple Apple Pen':0
}

def add_item(key):
    if key in Products.keys():
        Products[key] = Products[key] + 1

def rev_item(key):
    if key in Products.keys():
        if Products[key] == 0:
            print(Products[key])
        else:
            Products[key] = Products[key] - 1


#add_item('Pen')


Products["Pen"]=2
print(Products)
