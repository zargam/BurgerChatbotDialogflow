def print_option(option):
    countable_ingredients = {"more onion", "more veggie", "more pickle"}
    if option in countable_ingredients:
        return option + "s"
    return option

def print_options(options, start, end):
    length = end - start
    result = ''
    if length == 1:
        result += print_option(options[start])
    elif length == 2:
        result += print_option(options[start]) + ' and ' + print_option(options[end - 1])
    else:  # more than 2 items
        for i in range(start, end - 1):
            result += print_option(options[i]) + ', '
        result += 'and ' + print_option(options[end - 1])
    return result

def print_item_object(item_object):
    """Formats a single item object into a human-readable description."""
    if not isinstance(item_object, dict) or "name" not in item_object:
        return "Invalid item format"

    amount = int(item_object.get("amount", 1))
    name = item_object["name"]
    options = item_object.get("options", [])

    if name == "fries":
        amount_str = f"{amount} order{'s' if amount > 1 else ''} of {name}"
    else:
        item_name = f"{name}{'s' if amount > 1 else ''}"
        amount_str = f"{amount} {item_name}"

    if not options:
        return amount_str

    option_str = ", ".join(options)
    return f"{option_str} {name}{'s' if amount > 1 else ''}"


def print_items(item_objects, conjunction="and", separator=", "):
    print(item_objects);
    """Formats a list of item objects into a string with customizable conjunction and separator."""
    if not item_objects:
        return "No items"

    descriptions = [print_item_object(item) for item in item_objects]

    if len(descriptions) == 1:
        return descriptions[0]
    elif len(descriptions) == 2:
        return f" {conjunction} ".join(descriptions)
    else:
        return separator.join(descriptions[:-1]) + f"{separator}{conjunction} " + descriptions[-1]
