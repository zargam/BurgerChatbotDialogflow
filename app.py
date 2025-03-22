from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict, Any
from parse_item import parse_item
from print_items import print_items
from product_info import query_info
from insert_options import get_category_option, is_options_conflict, insert_options_to_item
from order_price import order_price
from words_to_number import words_to_numbers
from word_dictionary import word_map
import requests
import random
import datetime
import json

app = FastAPI()

OMS_URL = "https://liyutongordermanagementsystem.herokuapp.com/getOrder/"
ITEM_LIMIT = 50
ORDER_LIMIT = 10
COMBO_COMPS = set(["burger", "fries", "drink"])

class DialogflowRequest(BaseModel):
    responseId: str
    queryResult: Dict[str, Any]
    originalDetectIntentRequest: Dict[str, Any]
    session: str

@app.post('/')
async def dialogflow_firebase_fulfillment(request: DialogflowRequest):
    intent_name = request.queryResult.get("intent", {}).get("displayName")
    parameters = request.queryResult.get("parameters", {})
    output_contexts = request.queryResult.get("outputContexts", [])
    session = request.session

    def get_welcome_str():
        greet = ["Hi! ", "Hello! "]
        my_name = ["I'm Mastix. ", "My name is Mastix. "]
        ask = ["What can I get for you today?", "What do you want to eat?"]
        response = greet[random.randint(0, len(greet) - 1)] + my_name[random.randint(0, len(my_name) - 1)] + ask[random.randint(0, len(ask) - 1)]
        return response

    def welcome(output_contexts,session):
        return get_welcome_str()

    def fallback(output_contexts,session):
        return "Sorry, could you say that again?"

    def place_order(output_contexts, parameters, session):
        items = parameters.get('allProduct')
        print(parameters);
        item_objects = []
        SF = init_slot_filling()

        replace_item_params = get_context_params(session, 'replaceitem', output_contexts)
        is_replacing_item = replace_item_params.get('replaceitem') if replace_item_params else False
        for item in items:
            obj = parse_item(item)
            if obj['category'] == "drink" and not obj['options']:
                obj['options'].append("medium")
          
            if not detect_slots(SF, obj):
                item_objects.append(obj)
        all_items = get_old_items(session, output_contexts)
        clarify_items = False
        items_to_clarify = []
        length = len(all_items)
        if length > 0:
            for item_object in item_objects:
                if item_object['name'] != "combo" and item_object['name'] == all_items[length - 1]['name'] and not arrays_equal(item_object['options'], all_items[length - 1]['options']):
                    clarify_items = True
                    items_to_clarify.append(item_object)
                else:
                    if is_replacing_item:
                        item_object['amount'] = all_items[length - 1]['amount']
                        all_items[length - 1] = item_object
                        delete_context(session, 'replaceitem', output_contexts)
                    else:
                        all_items.append(item_object)
        else:
            all_items.extend(item_objects)
        new_items = reset_order_context(session, all_items, output_contexts)
        set_delivery_method(session, parameters.get('deliveryMethod'), output_contexts)

        if clarify_items:
            clarify_params = {'clarifyitems': items_to_clarify}
            set_context(session, 'clarifyitems', 5, clarify_params, output_contexts)
            return f"Would you like to modify your {items_to_clarify[0]['name']} or add {items_to_clarify[0]['amount']} more {items_to_clarify[0]['name']} {'s' if items_to_clarify[0]['name'] != 'fries' and items_to_clarify[0]['amount'] > 1 else ''}?"

        fill_slots_message = fill_slots(SF, output_contexts, session)
        if fill_slots_message:
                return fill_slots_message

        if check_empty_order(new_items, output_contexts, session):
            return "Your order is empty."
        return confirm_all_items(new_items)
      

    def add_item(output_contexts, parameters, session):
       
        obj = create_item_object(parameters.get('allItem'), parameters.get('itemAmount'), 1)
        if obj['category'] == "drink" and not obj['options']:
           obj['options'].append("medium")  # medium by default

        SF = init_slot_filling()
        all_items = get_old_items(session, output_contexts)
        length = len(all_items)
        if length > 0 and all_items[length - 1]['name'] == obj['name'] and is_included_in(obj['options'], all_items[length - 1]['options']):
            all_items[length - 1]['amount'] += obj['amount']
        elif not detect_slots(SF, obj):
            all_items.append(obj)
        new_items = reset_order_context(session, all_items, output_contexts)
        set_delivery_method(session, parameters.get('deliveryMethod'), output_contexts)

        if fill_slots(SF, output_contexts, session):
            return fill_slots(SF, output_contexts, session)

        if check_empty_order(new_items, output_contexts, session):
            return "Your order is empty."

        return confirm_all_items(new_items)

    def clarify_burger(output_contexts, parameters, session):
        burger = parameters.get('comboOption')
        clarify_context = next((context for context in output_contexts if "clarifyburger" in context.get("name", "")), None)

        if clarify_context is None or clarify_context.get('parameters') is None or clarify_context['parameters'].get('clarifyburger') is None or not clarify_context['parameters']['clarifyburger']:
            obj = parse_item(burger)
            delete_context(session, 'clarifyburger', output_contexts)
        else:
            burger_to_clarify = clarify_context['parameters'].get('clarifyburger')
            print(print_items(burger_to_clarify))
            obj = burger_to_clarify[-1]
            if len(burger_to_clarify) == 1:
                delete_context(session, 'clarifyburger', output_contexts)
            else:
                burger_to_clarify.pop()
                burger_params = {'clarifyburger': burger_to_clarify}
                set_context(session, 'clarifyburger', 5, burger_params, output_contexts)
            if obj['name'] == "burger":
                obj['name'] = burger
            if obj['name'] == "combo":
                obj['options'].append(burger)

        all_items = get_old_items(session, output_contexts)

        replace_item_params = get_context_params(session, 'replaceitem', output_contexts)
        is_replacing_item = replace_item_params.get('replaceitem') if replace_item_params else False

        if is_replacing_item:
            obj['amount'] = all_items[-1]['amount']
            all_items[-1] = obj
            delete_context(session, 'replaceitem', output_contexts)
        else:
            all_items.append(obj)

        new_items = reset_order_context(session, all_items, output_contexts)

        if check_empty_order(new_items, output_contexts, session):
            return "Your order is empty."

        return confirm_all_items(new_items)

    def clarify_shake(output_contexts, parameters, session):
        shake_option = parameters.get('shakeOption')
        clarify_context = next((context for context in output_contexts if "clarifyshake" in context.get("name", "")), None)

        if clarify_context is None or clarify_context.get('parameters') is None or clarify_context['parameters'].get('clarifyshake') is None or not clarify_context['parameters']['clarifyshake']:
            obj = parse_item(f"{shake_option} shake")
            delete_context(session, 'clarifyshake', output_contexts)
        else:
            shake_to_clarify = clarify_context['parameters'].get('clarifyshake')
            print(print_items(shake_to_clarify))
            obj = shake_to_clarify[-1]
            if len(shake_to_clarify) == 1:
                delete_context(session, 'clarifyshake', output_contexts)
            else:
                shake_to_clarify.pop()
                shake_params = {'clarifyshake': shake_to_clarify}
                set_context(session, 'clarifyshake', 5, shake_params, output_contexts)
            obj['options'].append(shake_option)

        all_items = get_old_items(session, output_contexts)

        replace_item_params = get_context_params(session, 'replaceitem', output_contexts)
        is_replacing_item = replace_item_params.get('replaceitem') if replace_item_params else False

        if is_replacing_item:
            obj['amount'] = all_items[-1]['amount']
            all_items[-1] = obj
            delete_context(session, 'replaceitem', output_contexts)
        else:
            all_items.append(obj)

        new_items = reset_order_context(session, all_items, output_contexts)

        if check_empty_order(new_items, output_contexts, session):
            return "Your order is empty."

        return confirm_all_items(new_items)

    def modify_item(output_contexts, parameters, session):
        new_options = parameters.get('allOption')
        all_items = get_old_items(session, output_contexts)

        if check_empty_order(all_items, output_contexts, session):
            return "Your order is empty."

        length = len(all_items)
        i = length - 1
        while i >= 0:
            modified_items = modify_the_item(all_items[i], new_options)
            if modified_items:
                all_items.pop(i)
                all_items.extend(modified_items)
                break
            i -= 1
        if i < 0:
            return "Sorry, that would not work. Could you say that again?"

        new_items = reset_order_context(session, all_items, output_contexts)

        if check_empty_order(new_items, output_contexts, session):
            return "Your order is empty."

        return confirm_all_items(new_items)

    
    def modify_amount(output_contexts, parameters, session):
        amount = str_to_int(parameters.get('itemAmount'))
        all_items = get_old_items(session, output_contexts)

        if check_empty_order(all_items, output_contexts, session):
            return "Your order is empty."

        length = len(all_items)
        if amount > 0:
            all_items[length - 1]['amount'] = amount
        else:
            return "Sorry, that would not work. Could you say that again?"

        new_items = reset_order_context(session, all_items, output_contexts)

        if check_empty_order(new_items, output_contexts, session):
            return "Your order is empty."

        return confirm_all_items(new_items)

    def remove_item(output_contexts, parameters, session):
        old_items = get_old_items(session, output_contexts)
        if check_empty_order(old_items, output_contexts, session):
            return "Your order is empty."

        obj = create_item_object(parameters.get('allItem'), parameters.get('itemAmount'), 999)

        temp_items = []
        for item in old_items:
            temp_items.append(item)
            if item['category'] == "combo":
                if item['options'][0] == obj['name'] or obj['name'] in ["burger", "drink"] or (obj['name'] == "fries" and not obj['options']):
                    temp_items.pop()
                    combo_map = break_combo(item)
                    for category in COMBO_COMPS:
                        temp_items.append(combo_map[category])
        all_items = merge_order(temp_items)

        new_items = []
        removed = False
        for item in all_items:
            reserved = False
            if obj['name'] in ["burger", "drink"]:
                if item['category'] != obj['name']:
                    reserved = True
            elif item['name'] != obj['name']:
                reserved = True
            elif is_included_in(obj['options'], item['options']):
                if item['amount'] - obj['amount'] > 0:
                    item['amount'] -= obj['amount']
                    reserved = True
            else:
                reserved = True

            if reserved:
                new_items.append(item)
            else:
                removed = True
        new_items = reset_order_context(session, new_items, output_contexts)

        if not removed:
            return "Sorry, that would not work. Could you say that again?"

        if check_empty_order(new_items, output_contexts, session):
            return "Your order is empty."

        return confirm_all_items(new_items)

    def replace_item(output_contexts, parameters, session):
    #Order context
        all_items = get_old_items(session, output_contexts)
        if check_empty_order(all_items, output_contexts, session):
            return "Your order is empty."

        length = len(all_items)
        last_item = all_items[length - 1]

        # Dialogflow
        all_product = parameters.get('allProduct')
        all_option = parameters.get('allOption')

        SF = init_slot_filling()

        if all_product:
            amount = last_item['amount']
            obj = parse_item(all_product)
            if detect_slots(SF, obj):
                replace_item_params = {'replaceitem': True}
                set_context(session, 'replaceitem', 5, replace_item_params, output_contexts)
                if fill_slots(SF, output_contexts, session):
                    return fill_slots(SF, output_contexts, session)
            else:
                all_items[length - 1] = obj
                all_items[length - 1]['amount'] = amount
                new_items = reset_order_context(session, all_items, output_contexts)
                if check_empty_order(new_items, output_contexts, session):
                    return "Your order is empty."
                return confirm_all_items(new_items)
        elif all_option:  # either one of these is defined
            category_options = get_category_option([all_option], last_item)
            if is_options_conflict(category_options):
                return 'Seems your customized options have conflicts. Could you say that again?'
            all_items[length - 1] = insert_options_to_item(last_item, category_options)
            all_items[length - 1] = sort_options(all_items[length - 1])

            new_items = reset_order_context(session, all_items, output_contexts)
            if check_empty_order(new_items, output_contexts, session):
                return "Your order is empty."
            return confirm_all_items(new_items)
        else:
            return 'I\'m sorry, could you say that again?'

    def finalize_order(output_contexts, parameters, session):
        all_items = get_old_items(session, output_contexts)
        if check_empty_order(all_items, output_contexts, session):
            return "Your order is empty."

        delivery_params = get_context_params(session, 'delivery', output_contexts)
        
        if delivery_params is None:
            return "Is it for here or to go?"
        else:  # delivery method has been set before
            if 'delivery' in delivery_params:
                delivery_method = delivery_params['delivery']
                return 'So your order will be ' + print_items(all_items) + ', ' + delivery_method + ' right?'
            else:
                return "Delivery method not found. Could you please specify it again?" #Handle the case where delivery key is missing.
        
    def finalize_order_choose_delivery(output_contexts, parameters, session):
        all_items = get_old_items(session, output_contexts)
        if check_empty_order(all_items, output_contexts, session):
            return "Your order is empty."
        
        delivery_method = parameters.get('deliveryMethod')
        set_delivery_method(session, delivery_method, output_contexts)
        response = 'So your order will be ' + print_items(all_items) + ', ' + delivery_method + ", right?"
        return response


    def finalize_order_confirm_order(output_contexts, parameters, session):
        all_items = get_old_items(session, output_contexts)
        print(all_items)
        if check_empty_order(all_items, output_contexts, session):
            return "Your order is empty."

        all_items = process_order(all_items)
        delivery_params = get_context_params(session, 'delivery', output_contexts)
        delivery = delivery_params['delivery'] if delivery_params else None

        # Send order information to server
        order_json = {
            "intent": "OrderFood",
            "delivery method": delivery,
            "items": all_items,
            "time": get_locale_time_string()
        }

        #request_url = OMS_URL + json.dumps(order_json)

        try:
            #response = send_to_server(request_url)
            #json_response = response.json()
            delete_context(session, 'order', output_contexts)
            delete_context(session, 'delivery', output_contexts)
            delete_context(session, 'placeorder', output_contexts)
            return f"The total will be $10.5. Your order number is #8866. Have a good one."

        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
            return "Oops! Something went wrong while placing your order. Could you try again? My apologies."

        except json.JSONDecodeError:
            print("Error decoding JSON response.")
            return "Oops! Something went wrong while placing your order. Could you try again? My apologies."

        except KeyError as e:
            print(f"Missing key in JSON response: {e}")
            return "Oops! Something went wrong while placing your order. Could you try again? My apologies."

    def choose_delivery(output_contexts, parameters, session):
        delivery = parameters.get('deliveryMethod')
        set_delivery_method(session, delivery, output_contexts)
        response = f"{get_confirm_str()} {capitalize_string(delivery)}. {get_default_follow_up_str()}"
        return response

    def place_order_add(output_contexts, parameters, session):
        clarify_context = next((context for context in output_contexts if "clarifyitems" in context.get("name", "")), None)
        if clarify_context and clarify_context.get('parameters') and clarify_context['parameters'].get('clarifyitems'):
            items_to_clarify = clarify_context['parameters'].get('clarifyitems')
            print(print_items(items_to_clarify))
            delete_context(session, 'clarifyitems', output_contexts)
            all_items = get_old_items(session, output_contexts)
            all_items.extend(items_to_clarify)
            new_items = reset_order_context(session, all_items, output_contexts)
            if check_empty_order(new_items, output_contexts, session):
                return "Your order is empty."
            return confirm_all_items(new_items)
        else:
            return "Sorry, I couldn't understand. Could you please repeat that?"

    def place_order_modify(output_contexts, parameters, session):
        clarify_context = next((context for context in output_contexts if "clarifyitems" in context.get("name", "")), None)
        if clarify_context and clarify_context.get('parameters') and clarify_context['parameters'].get('clarifyitems'):
            items_to_clarify = clarify_context['parameters'].get('clarifyitems')
            print(print_items(items_to_clarify))
            delete_context(session, 'clarifyitems', output_contexts)
            all_items = get_old_items(session, output_contexts)
            length = len(all_items)
            if length < 1:
                all_items.extend(items_to_clarify)
            else:
                i = length - 1
                while i >= 0:
                    if all_items[i]['name'] == items_to_clarify[0]['name']:
                        break
                    i -= 1
                if i >= 0:
                    new_options = items_to_clarify[0]['options']
                    item = all_items[i]
                    category_options = get_category_option(new_options, item)
                    if is_options_conflict(category_options):
                        return "Uh... I'm sorry?"
                    all_items[i] = insert_options_to_item(item, category_options)
                else:
                    all_items.extend(items_to_clarify)
            new_items = reset_order_context(session, all_items, output_contexts)
            if check_empty_order(new_items, output_contexts, session):
                return "Your order is empty."
            return confirm_all_items(new_items)
        else:
            return "Sorry, I couldn't understand. Could you please repeat that?"
    
    def capitalize_string(str):
        return str.capitalize()
    
    def query_menu(output_contexts, session):
        card_data = {
            "fulfillmentMessages": [
                {
                    "payload": {
                        "richContent": [
                            [
                                {
                                    "type": "image",
                                    "rawUrl": "https://marketplace.canva.com/EAFx4P97zOY/1/0/1131w/canva-dark-blue-and-yellow-modern-burger-menu-K6nIdbR9doo.jpg",
                                    "accessibilityText": "Burger Menu"
                                },
                                {
                                    "type": "info",
                                    "title": "Burger – Menu",
                                    "subtitle": "4:00 – 7:00 pm\n156 New Street Delhi, India",
                                    "actionLink": "https://goo.gl/oaYHG8"
                                }
                            ]
                        ]
                    }
                }
            ],
            "outputContexts": output_contexts
        }
        return json.dumps(card_data)


    def query_word(parameters, output_contexts,session):
       
        response = None
        if parameters.get('vocabulary'):
            response = word_map.get(parameters['vocabulary'])
        if parameters.get('any'):
            response = word_map.get(parameters['any'])

        if response:
            return response
        else:
            if parameters.get('any'):
                return f"Sorry, I never heard {parameters['any']} before. Anything else I can help?"
            else:
                return "Sorry, I couldn't find the word. Anything else I can help?"

    def query_product(output_contexts, parameters, session):

        item = parameters.get('allItem')
        
        product_attr = parameters.get('productAttribute')
      
        customer_need = parameters.get('customerNeed')
       
        if customer_need:
            response = query_info(customer_need)
        else:
            response = query_info(product_attr, item)

        return response

    def query_recommendation(output_contexts,session):
        text_response = "We have the best burger in Delhi. Would you like to try it? Or you can check our menu here:"
        card_response = json.loads(query_menu(output_contexts,session))
        card_response["fulfillmentMessages"].insert(0, {"text": {"text": [text_response]}})
        return json.dumps(card_response)
    
    def init_slot_filling():
        return {
            "clarifyBurger": False,
            "clarifyShake": False,
            "burgerToClarify": [],
            "shakeToClarify": []
        }

    def get_context_params(session, context_name, output_contexts): #output_contexts added here.
        context_name = f"{session}/contexts/{context_name}"
        for context in output_contexts:
            if context.get("name") == context_name:
                return context.get('parameters', {})
        return {}

    def detect_slots(SF, obj):
        name = obj['name']

        if name == "burger" or (name == "combo" and not obj['options']):
            SF['clarifyBurger'] = True
            SF['burgerToClarify'].append(obj)
            return True

        elif name == "shake" and not obj['options']:
            SF['clarifyShake'] = True
            SF['shakeToClarify'].append(obj)
            return True

        elif name == "water":
            # You may want to return an early response here via webhook response, not agent.add
            print("If you need water, just ask our friendly staff for a plastic cup. It's FREE. Thanks!")
            return True

        return False

    def get_old_items(session, output_contexts):
        context_name = f"{session}/contexts/order"
        for context in output_contexts:
            if context.get("name") == context_name:
                return context.get('parameters', {}).get('order', []) or []
        return []

    def delete_context(session, name, output_contexts):
        context_name = f"{session}/contexts/{name}"
        output_contexts[:] = [context for context in output_contexts if context.get("name") != context_name]

    def reset_order_context(session, all_items, output_contexts):
        new_items = merge_order(all_items)
        parameters = {'order': new_items}
        set_context(session, 'order', 999, parameters, output_contexts)
        return new_items
    def set_context(session, name, lifespan, parameters, output_contexts):
        context_name = f"{session}/contexts/{name}"
        found = False
        for context in output_contexts:
            if context.get("name") == context_name:
                context["lifespanCount"] = lifespan
                context["parameters"] = parameters
                found = True
                break
            if not found:
              output_contexts.append({
                "name": context_name,
                "lifespanCount": lifespan,
                "parameters": parameters
            })
              
    def merge_order(order):
        result = []
        for order_item in order:
            has_pushed = False
            for result_item in result:
                if order_item['name'] == result_item['name'] and arrays_equal(order_item['options'], result_item['options']):
                    result_item['amount'] += order_item['amount']
                    has_pushed = True
                    break
            if not has_pushed:
                result.append(order_item)

        if len(result) > ORDER_LIMIT:
            result = result[-ORDER_LIMIT:]

        for result_item in result:
            if result_item['amount'] > ITEM_LIMIT:
                result_item['amount'] = ITEM_LIMIT

        return result
    
    def arrays_equal(a1, a2):
        return len(a1) == len(a2) and set(a1) == set(a2) 

    def set_delivery_method(session, delivery_method, output_contexts):
            delivery_params = {'delivery': delivery_method}
            set_context(session, 'delivery', 999, delivery_params, output_contexts)

    def fill_slots(SF, output_contexts, session):
        if SF['clarifyBurger']:
            burger_params = {'clarifyburger': SF['burgerToClarify']}
            set_context(session, 'clarifyburger', 5, burger_params, output_contexts)
            return "Which burger would you like? Hamburger, cheeseburger, or MCS?"
        if SF['clarifyShake']:
            shake_params = {'clarifyshake': SF['shakeToClarify']}
            set_context(session, 'clarifyshake', 5, shake_params, output_contexts)
            return "What kind of flavor do you want for your shake? We have chocolate, strawberry, and vanilla. All of them are delicious!"
        return ""
    
    def confirm_all_items(all_items):
        #print(all_items);
        response = get_confirm_str() + print_items(all_items) + '. ' + get_follow_up_str(all_items)
        print(response);
        return response

    def get_confirm_str():
        confirm = ['Sure. ', 'No problem. ', 'Gotcha. ', 'Okay. ', 'Of course. ', 'Awesome. ']
        return confirm[get_random_int(len(confirm))]
    
    def check_empty_order(all_items, output_contexts, session):
        if not all_items:
            set_context(session, 'unhappy', 5, {}, output_contexts)  # parameters can be empty dict
            return "There is no item in your order. What can I get for you today?"
        return "" # return empty string when order is not empty.
    
    def get_random_int(size):
        return random.randint(0, size - 1)
    
    def get_follow_up_str(all_items):
        is_order_drink = any(item['category'] != "burger" and item['category'] != "fries" for item in all_items)
        return 'Anything to drink?' if not is_order_drink else get_default_follow_up_str()

    def get_default_follow_up_str():
        follow_up = ['What else?', 'Anything else?']
        return follow_up[get_random_int(len(follow_up))]
    
    def modify_the_item(item, new_options):
        modified_items = []
        if item['category'] == "combo":
            combo_map = break_combo(item)
            combo_modified = False
            for category in COMBO_COMPS:
                obj = combo_map.get(category)
                category_options = get_category_option(new_options, obj)
                if is_options_conflict(category_options):
                    return modified_items
                if category in category_options:
                    obj['options'] = category_options[category]
                    obj = sort_options(obj)
                    print(obj)
                    combo_map[category] = obj
                    combo_modified = True
            if combo_modified:
                for category in COMBO_COMPS:
                    modified_items.append(combo_map[category])
        else:
            category_options = get_category_option(new_options, item)
            if is_options_conflict(category_options):
                return modified_items
            if item['category'] in category_options:
                item = insert_options_to_item(item, category_options)
                item = sort_options(item)
                print(item)
                modified_items.append(item)
        return modified_items
    
    def break_combo(combo):
        combo_map = {}
        if combo['category'] != "combo":
            combo_map[combo['category']] = combo
            return combo_map

        for category in COMBO_COMPS:
            obj = {
                'name': category if category != "burger" else combo['options'][0],
                'category': category,
                'options': [] if category != "drink" else ["medium"],
                'amount': combo['amount']
            }
            combo_map[category] = obj

        return combo_map
    
    def sort_options(obj):
        if obj['category'] != "burger":
            return obj
        str = obj['name'] + ' ' + ' '.join(obj['options'])
        new_obj = parse_item(str)
        obj['options'] = new_obj['options']
        return obj
    
    def str_to_int(str):
        return int(words_to_numbers(str))
     
    def create_item_object(allItem, itemAmount, defaultAmt):
        obj = parse_item(allItem)  # amount must be 1, but the correct amount is amount
        amount = defaultAmt if itemAmount == '' else str_to_int(itemAmount)
        obj['amount'] = amount
        return obj
    
    def process_order(order):
        for item in order:
            if 'with' in item['options']:
                item['options'].remove('with')
        return order

    def is_included_in(a1, a2):
        return set(a1).issubset(set(a2))
    
    def get_locale_time_string():
        date = datetime.datetime.utcnow() + datetime.timedelta(hours=5.5)  # IST
        return date.strftime('%Y-%m-%d %H:%M:%S')
    
    intent_map = {
        'Default Welcome Intent': welcome,
        'Default Fallback Intent': fallback,
        'Place Order': place_order,
        'Add Item': add_item,
        'Clarify Burger': clarify_burger,
        'Clarify Shake': clarify_shake,
        'Modify Item': modify_item,
        'Modify Amount': modify_amount,
        'Remove Item': remove_item,
        'Replace Item': replace_item,
        'Finalize Order': finalize_order,
        'Finalize Order - Choose Delivery': finalize_order_choose_delivery,
        'Finalize Order - Choose Delivery - Yes': finalize_order_confirm_order,
        'Finalize Order - Confirm Order': finalize_order_confirm_order,
        'Choose Delivery': choose_delivery,
        'Place Order - Add': place_order_add,
        'Place Order - Modify': place_order_modify,
        'Query Menu': query_menu,
        'Query Word': query_word,
        'Query Product': query_product,
        'Query Recommendation': query_recommendation
    }

    if intent_name in intent_map:
        if intent_name in [
            "Place Order", "Clarify Burger", "Clarify Shake", "Modify Item", "Remove Item",
            "Add Item", "Finalize Order", "Finalize Order - Choose Delivery", 
            "Finalize Order - Choose Delivery - Yes", "Query Product", "Choose Delivery", 
            "Place Order - Add", "Place Order - Modify", "Replace Item", 
            "Finalize Order - Confirm Order", "Query Word"
        ]:
            response_text = intent_map[intent_name](output_contexts, parameters, session)
        else:
            response_text = intent_map[intent_name](output_contexts, session)

        try:
            response_json = json.loads(response_text)
            return {
                "fulfillmentMessages": response_json.get("fulfillmentMessages", []),
                "outputContexts": output_contexts
            }
        except json.JSONDecodeError:
            return {
                "fulfillmentText": response_text,
                "outputContexts": output_contexts
            }
    else:
        return {
            "fulfillmentText": "Intent not handled",
            "outputContexts": output_contexts
        }
