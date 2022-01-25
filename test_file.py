my_dict = {}
my_dict_2 = {}
prod_collection = form_to_dict(request.forms)
print(prod_collection)

product_id_list = prod_collection.keys()
print(product_id_list)

for k in product_id_list:
    prod_name = getFromDB("products", "product_name", "product_id", k)
    my_dict[prod_name + "_name"] = getFromDB("products", "product_name", "product_id", k)
    my_dict[prod_name + "_price"] = str(getFromDB("products", "price", "product_id", k))
    my_dict[prod_name + "_qty"] = prod_collection[k]

print(my_dict)
basket_list = list(my_dict.values())

for k in product_id_list:
    prod_name = getFromDB("products", "product_name", "product_id", k)
    my_dict_2[prod_name + "_name"] = getFromDB("products", "product_name", "product_id", k)
    my_dict_2[prod_name + "_price"] = getFromDB("products", "price", "product_id", k)
    my_dict_2[prod_name + "_qty"] = prod_collection[k]

print(my_dict_2)
basket_2 = list(my_dict_2.values())
price_values = basket_2[1::3]
print(type(price_values))


summ_qty = basket_list[2::3]
print(type(summ_qty))

strings_qty = [str(integer) for integer in summ_qty]
a_string = "".join(strings_qty)
an_integer = int(a_string)
print(an_integer)

# we obtain iterated quantity of products
quantity = [int(a) for a in str(an_integer)]
print(quantity)

# # we want to obtain iterated price of products

products_sum = [x * y for x, y in zip(price_values, quantity)]
print(products_sum)

total_sum = sum(products_sum)