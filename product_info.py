from order_price import order_price  # Assuming order_price.py exists
from parse_item import parse_item  # Assuming parse_item.py exists

product_map = {
    "eat": "We have hamburger, cheeseburger, MCS burger, fries, and shake with different ingredient options. Which one do you want?",
    "drink": "We have coke, root beer, 7-up, lemonade, dr pepper, iced tea, milk, cocoa, and coffee. What would you like to have?"
}

ingredient_map = {
    "hamburger": "A hamburger includes toasted buns, 1 beef patty, onions, lettuce, tomato, pickles, and spread.",
    "cheeseburger": "A cheeseburger includes toasted buns, 1 cheese slice, 1 beef patty, onions, lettuce, tomato, pickles, and spread.",
    "MCS": "A MCS burger includes toasted buns, 2 cheese slices, 2 beef patties, onions, lettuce, tomato, pickles, and spread.",
    "fries": "Fries is made of fresh potatoes.",
    "combo": "A combo consists of a burger, an order of fries and 1 medium drink.",
    "hamburger combo": " A combo consists of a hamburger, an order of fries and 1 medium drink.",
    "cheeseburger combo": "A cheeseburger combo consists of a hamburger, an order of fries and 1 medium drink.",
    "MCS combo": "A MCS burger combo consists of a MCS burger, an order of fries and 1 medium drink.",
    "shake": "A shake is made of real ice cream."
}

option_map = {
    "burger": "We have hamburger, cheeseburger and MCS burger.",
    "hamburger": "You can customized your hamburger with options such as no/more onion/lettuce/tomato/pickle...  We provide lots of options for you. Please check our menu.",
    "cheeseburger": "You can customized your cheeseburger with options such as no/more onion/lettuce/tomato/pickle...  We provide lots of options for you. Please check our menu.",
    "MCS burger": "You can customized your MCS burger with options such as no/more onion/lettuce/tomato/pickle...  We provide lots of options for you. Please check our menu.",
    "shake": "You can choose chocolate, vanilla or strawberry flavor for your shake.",
    "fries": "You can have your fries cooked well done/light well, add cheese, or make it anteater style.",
    "coke": "For coke we provide 4 sizes: small, medium, large and extra large.",
    "7-up": "For 7-up we provide 4 sizes: small, medium, large and extra large.",
    "lemonade": "For lemonade we provide 4 sizes: small, medium, large and extra large.",
    "dr pepper": "For dr pepper we provide 4 sizes: small, medium, large and extra large.",
    "iced tea": "For iced tea we provide 4 sizes: small, medium, large and extra large.",
    "root beer": "For root beer we provide 4 sizes: small, medium, large and extra large.",
    "drink": "For drinks we provide 4 sizes: small, medium, large and extra large; milk, coca, and coffee are one-size."
}

have_map = {
    "combo": "We have hamburger combo, cheeseburger combo, and MCS burger combo.",
    "burger": "We have hamburger, cheeseburger, and MCS burger.",
    "shake": "We have 3 flavors for you to choose: chocolate, strawberry, and vanilla.",
    "drink": "We have coke, root beer, 7-up, lemonade, dr pepper, iced tea, milk, cocoa, and coffee. What would you like to have?",
    "hamburger": "Yes, we do.",
    "cheeseburger": "Yes, we do.",
    "MCS burger": "Yes, we do.",
    "fries": "Yes, we do.",
    "coke": "Yes, we do.",
    "7-up": "Yes, we do.",
    "lemonade": "Yes, we do.",
    "dr pepper": "Yes, we do.",
    "iced tea": "Yes, we do.",
    "root beer": "Yes, we do.",
    "milk": "Yes, we do.",
    "cocoa": "Yes, we do.",
    "coffe": "Yes, we do.",
    "shake": "Yes, we do.",
    "chocolate shake": "Yes, we do.",
    "vanilla shake": "Yes, we do.",
    "strawberry shake": "Yes, we do."
}

def query_info(query_type, item):
    
    """Retrieves information based on query type and item."""
    if query_type in ["eat", "drink"]:
        return product_map.get(query_type)

    if item.endswith("s") and item != "fries":
        item = item[:-1]

    if query_type == "ingredient":
        return ingredient_map.get(item)
    elif query_type == "price":
        obj = parse_item(item)
        return f"It's {order_price([obj])} dollars after tax."
    elif query_type == "option":
        return option_map.get(item)
    elif query_type == "have":
        return have_map.get(item, "Sorry, we don't have that.")
    else:
        return None