class Basket:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

        if quantity is None:
             self.quantity = []
        else:
             self.quantity = quantity

    def add_item(self):
        #added_item = Basket(self.product, self.quantity)
        # for x in range(self.product)
        added_item = Basket(self.product,self.quantity + 1)
        print(added_item.product, added_item.quantity)
        #return added_item

    # def PrintMe(self):
    #     for x in range(self.product):
    #         print(self.product, self.quantity)




product_1 = Basket("banana", 2)

print(product_1.product, product_1.quantity)

product_1.add_item()

print(product_1.product, product_1.quantity)

#Basket.PrintMe()