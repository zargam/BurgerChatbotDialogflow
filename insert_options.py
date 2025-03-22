from item_option import (
    burger_options,
    burger_ingredients,
    fries_options,
    shake_options,
    drink_options,
    options_type_map
)


def setOption(item, option, remove=False):
    if remove and option in item["options"]:
        item["options"].remove(option)
    elif not remove and option not in item["options"]:
        item["options"].append(option)


def insert_options_to_item(item, new_options_map):
    category = item.get("category")
    old_options = item.get("options", [])
    new_options = new_options_map.get(category, [])
    category_options_type_map = options_type_map.get(category, {})

    if category in ["drink", "shake", "other"]:
        item["options"] = new_options
        return item

    no_cheese = "no cheese" in new_options

    if not old_options:
        item["options"] = new_options
        return item

    for option in new_options:
        if option in old_options:
            continue

        for old_option in old_options[:]:
            if old_option == "with":
                continue
            option_type = category_options_type_map.get(option)
            old_option_type = category_options_type_map.get(old_option)

            if option_type != "cheese":
                if option_type == old_option_type:
                    setOption(item, old_option, remove=True)
            elif no_cheese:
                if old_option_type == "cheese":
                    setOption(item, old_option, remove=True)
            elif option == "grilled cheese" and old_option == "cold cheese":
                setOption(item, old_option, remove=True)
            elif option == "cold cheese" and old_option == "grilled cheese":
                setOption(item, old_option, remove=True)
            else:
                setOption(item, "no cheese", remove=True)
                setOption(item, option)

        setOption(item, option)

    if no_cheese:
        setOption(item, "no cheese")

    return item


def get_category_option(new_options, item=None):
    unique_options = list(dict.fromkeys(new_options))
    category_option = {}

    for option in unique_options:
        item_type = get_option_type(option)

        if item and item.get("category") == "fries" and option in ["well done", "anteater style"]:
            item_type = "fries"

        category_option.setdefault(item_type, []).append(option)

    return category_option


def get_option_type(option):
    if option in burger_ingredients or option in burger_options or option == "with":
        return "burger"
    elif option in fries_options:
        return "fries"
    elif option in shake_options:
        return "shake"
    elif option in drink_options:
        return "drink"
    else:
        return "other"


def is_options_conflict(new_options_map):
    for category, new_options in new_options_map.items():
        available_options_type_map = options_type_map.get(category, {})

        if category == "drink" and len(new_options) > 1:
            print("Size options for drinks have conflict!")
            return True

        if category == "shake":
            print("No conflicts in new options for shakes. Proceed.")
            continue

        buns_index = cook_index = style_index = -1

        for option in new_options:
            option_type = available_options_type_map.get(option, "")
            has_no_category = f"no {option_type}" in new_options
            has_category = option != f"no {option_type}"

            if has_no_category and has_category:
                print("No/Add options conflict!")
                return True

            if "cold cheese" in new_options and "grilled cheese" in new_options:
                print("Cold/grilled cheese options conflict!")
                return False

            if option_type == "buns":
                if buns_index != -1:
                    print("Buns options conflict!")
                    return True
                buns_index = new_options.index(option)

            if option_type == "cook":
                if cook_index != -1:
                    print("Cook options conflict!")
                    return True
                cook_index = new_options.index(option)

            if option_type == "style":
                if style_index != -1:
                    print("Style options conflict!")
                    return True
                style_index = new_options.index(option)

    return False
