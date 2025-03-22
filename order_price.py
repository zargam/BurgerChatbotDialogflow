item_price = {
    "hamburger": 2.40,
    "cheeseburger": 2.70,
    "MCS": 3.85,
    "fries": 1.85,
    "shake": 2.45,
    "cocoa": 1.60,
    "milk": 0.99,
    "coffee": 1.25
}

fries_opt_price = {
    "anteater style": 1.80,
    "cheese": 1.50,
    "well done": 0,
    "light well": 0
}

drink_opt_price = {
    "small": 1.50,
    "medium": 1.60,
    "large": 1.80,
    "extra large": 2.00
}

def find_price(item_object):
    price = 0
    category = item_object.get("category")
    options = item_object.get("options", [])
    name = item_object.get("name")
    amount = item_object.get("amount", 1)

    if category == "combo":
        # combo includes burger + fries + medium drink
        price = item_price.get(options[0], 0) + item_price.get("fries", 0) + drink_opt_price.get("medium", 0)

    elif category == "fries":
        price = item_price.get("fries", 0)
        for option in options:
            price += fries_opt_price.get(option, 0)

    elif category == "drink":
        # ✅ Fix: safely handle missing or empty options
        size = options[0] if options else "medium"
        price = drink_opt_price.get(size, drink_opt_price.get("medium", 0))

    else:
        price = item_price.get(name, 0)

    return price * amount

def order_price(item_objects):
    price = 0
    for item_object in item_objects:
        price += find_price(item_object)

    # Add CA TAX 0.0775
    price *= (1 + 0.0775)

    return "{:.2f}".format(price)  # Format to 2 decimal places