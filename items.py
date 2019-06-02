'''
Created on 01-Jun-2019

@author: rohit
'''


class Category:
    def __init__(self, name, discount=0):
        self.name = name
        self.discount = discount


class subCategory():
    def __init__(self, category, name, discount=0):
        self.name = name
        self.discount = discount
        self.category = category


class Item():
    def __init__(self,
                 sub_category,
                 name,
                 price,
                 unit,
                 discount_percent=0,
                 discount_tuple=(0, 0)):
        self.name = name
        self.price = price
        self.unit = unit
        self.discount = discount_percent if discount_percent else discount_tuple
        self.sub_category = sub_category

    def unit_convertor(self, unit):
        conversion = 1
        if unit == 'Grams' and self.unit == 'Kilograms':
            conversion = 1.0 / 1000
        elif unit == 'Mililiters' and self.unit == 'Liters':
            conversion = 1.0 / 1000
        elif unit == 'Number' and self.unit == 'Dozon':
            conversion = 1.0 / 12
        return conversion

    def get_purchase_money(self, quantity, unit):
        quantity *= self.unit_convertor(unit)
        max_price = quantity * self.price
        if isinstance(self.discount, tuple):
            '''
                quantity >= n*tuple[0] + n*tuple[1]
                quantity/(tuple[0]+tuple[1]) >= n
            '''
            quantity = (quantity / (self.discount[0] + self.discount[1])
                        ) * self.discount[0] + quantity % (self.discount[0] +
                                                           self.discount[1])
        else:
            quantity -= quantity * max(
                self.discount, self.sub_category.discount,
                self.sub_category.category.discount) / 100.0

        return quantity * self.price, max_price


class Items():
    def __init__(self):
        self.items = {}

    def add_item(self,
                 sub_category,
                 name,
                 price,
                 unit,
                 discount_percent=0,
                 discount_tuple=(0, 0)):
        item = Item(sub_category, name, price, unit, discount_percent,
                    discount_tuple)
        self.items[item.name] = item

    def get_item(self, name):
        return self.items[name] if name in self.items else None

    def get_purchase_money_of_an_item(self, name, quantity, unit):
        item = self.get_item(name)
        return item.get_purchase_money(quantity, unit) if item else 0


def add_initial_items():
    items = Items()

    cat1 = Category('Produce', discount=10)
    sc1 = subCategory(cat1, 'Fruits', 18)
    sc2 = subCategory(cat1, 'Veg', 5)
    items.add_item(sc1, 'Apple', 50, "Kilograms", discount_tuple=(3, 1))
    items.add_item(sc1, 'Orange', 80, "Kilograms", discount_percent=20)
    items.add_item(sc2, 'Potato', 30, "Kilograms", discount_tuple=(5, 2))
    items.add_item(sc2, 'Tomato', 70, "Kilograms", discount_percent=10)

    cat2 = Category('Dairy', discount=15)
    sc1 = subCategory(cat2, 'Milk', 20)
    sc2 = subCategory(cat2, 'Cheese', 20)
    items.add_item(sc1, 'Cow Milk', 50, "Liters", discount_tuple=(3, 1))
    items.add_item(sc1, 'Soy Milk', 40, "Liters", discount_percent=10)
    items.add_item(sc2, 'Cheddar', 50, "Liters", discount_tuple=(2, 1))
    items.add_item(sc2, 'Gouda', 80, "Liters", discount_percent=10)
    return items
