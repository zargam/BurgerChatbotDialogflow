from words_to_number import words_to_numbers  # Assuming you have words_to_numbers.py
from item_option import item_map, burger_ingredients, option_map  # Assuming item_options.py

def match_set(input_string, input_set):
    """Finds elements from a set that are present in a string."""
    matches = []
    for element in input_set:
        if input_string.find(element) != -1:
            matches.append(element)
    return matches

def match_options(input_string, category):
    """Finds options from a category's option set that are present in a string."""
    option_set = option_map.get(category, set())  # Use get with default empty set
    matches = []
    if category == "other":
        return matches

    for element in option_set:
        if input_string.find(element) != -1:
            matches.append(element)
            if category in ["combo", "shake", "drink"]:
                break
    return matches

def parse_item(input_string):
    """Parses an item from a string."""
    input_string = input_string.replace("?", "")  # Remove "?"
    input_string = words_to_numbers(input_string)  # Convert words to numbers

    item_object = {}
    items = match_set(input_string, item_map.keys())  # Find matching items
    if items:
        item_object["name"] = items[0]
        item_object["category"] = item_map.get(item_object["name"])
        item_object["options"] = match_options(input_string, item_object["category"])  # Find matching options

        if item_object["category"] == "burger":
            ingredients = match_set(input_string, burger_ingredients)
            if ingredients:
                item_object["options"].append("with")
                item_object["options"].extend(ingredients)

        if input_string.startswith("7-up"):  # Check if string starts with "7-up"
            item_object["amount"] = 1
        else:
            try:
                item_object["amount"] = int(input_string.split()[0]) # Try to convert the first word to int
            except (ValueError, IndexError):
                item_object["amount"] = 1 # If the first word is not a number, set amount to 1
    else:
        item_object = {"name":None, "category":None, "options":[], "amount": 1} #if no items are found set default values.
    return item_object