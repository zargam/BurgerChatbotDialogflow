# item_options.py

item_map = {
    "combo": "combo",
    "hamburger": "burger",
    "cheeseburger": "burger",
    "MCS": "burger",
    "burger": "burger",
    "fries": "fries",
    "shake": "shake",
    "milk": "other",
    "coffee": "other",
    "cocoa": "other",
    "water": "other",
    "drink": "drink",
    "coke": "drink",
    "root beer": "drink",
    "dr pepper": "drink",
    "7-up": "drink",
    "lemonade": "drink",
    "iced tea": "drink"
}

combo_options = {
    "hamburger",
    "cheeseburger",
    "MCS"
}

burger_options = {
    "medium rare",
    "well done",
    "cut in half",
    "anteater style"
}

burger_ingredients = {
    "more tomato", "no tomato",
    "more cheese", "no cheese",
    "more onion", "no onion",
    "more veggie", "no veggie",
    "more lettuce", "no lettuce",
    "more pickle", "no pickle",
    "more salt", "no salt",
    "more meat", "no meat",
    "extra toasted buns", "lightly toasted buns", "untoasted buns",
    "cold cheese", "grilled cheese",
    "mustard", "ketchup"
}

fries_options = {
    "anteater style",
    "cheese",
    "well done",
    "light well"
}

shake_options = {
    "chocolate",
    "strawberry",
    "vanilla"
}

drink_options = {
    "small",
    "medium",
    "extra large",
    "large"
}

other_options = set()

option_map = {
    "combo": combo_options,
    "burger": burger_options,
    "fries": fries_options,
    "shake": shake_options,
    "drink": drink_options,
    "other": other_options
}

burger_options_type_map = {
    "with": "with",
    "more tomato": "tomato",
    "no tomato": "tomato",
    "no cheese": "cheese",
    "more cheese": "cheese",
    "cold cheese": "cheese",
    "grilled cheese": "cheese",
    "more onion": "onion",
    "no onion": "onion",
    "more veggie": "veggie",
    "no veggie": "veggie",
    "more lettuce": "lettuce",
    "no lettuce": "lettuce",
    "more pickle": "pickle",
    "no pickle": "pickle",
    "more salt": "salt",
    "no salt": "salt",
    "more meat": "meat",
    "no meat": "meat",
    "extra toasted buns": "buns",
    "lightly toasted buns": "buns",
    "untoasted buns": "buns",
    "mustard": "mustard",
    "ketchup": "ketchup",
    "medium rare": "cook",
    "well done": "cook",
    "cut in half": "cut",
    "anteater style": "style"
}

fries_options_type_map = {
    "anteater style": "style",
    "cheese": "style",
    "well done": "cook",
    "light well": "cook"
}

drink_options_type_map = {
    "small": "size",
    "medium": "size",
    "large": "size",
    "extra large": "size"
}

shake_options_type_map = {
    "chocolate": "chocolate",
    "strawberry": "strawberry",
    "vanilla": "vanilla"
}

options_type_map = {
    'burger': burger_options_type_map,
    'fries': fries_options_type_map,
    'drink': drink_options_type_map,
    'shake': shake_options_type_map
}