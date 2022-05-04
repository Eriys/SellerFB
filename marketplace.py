import requests
import json
from localuseragent import ua
import random


def general_informations(data, seller_informations, seller_items):
    """ Scrap the seller informations and the item selled inforamtions if exists."""
    seller_informations.append({
        "nbr_total_item":data["data"]["user"]["marketplace_commerce_inventory"]["count"],
        "sellerid": data["data"]["user"]["marketplace_user_profile"]["id"],
        "sellername": data["data"]["user"]["name"],
        "nbr_item_page":0,
        "rating":data["data"]["user"]["marketplace_ratings_stats_by_role"],
        })
    if seller_informations[0]["nbr_total_item"] != None:
        first_items =  data["data"]["user"]["marketplace_commerce_inventory"]["edges"]
        #print(seller_informations[0]["sellername"], seller_informations[0]["nbr_total_item"], seller_informations[0]["first_items"])

        for item in first_items:
            seller_informations.append({
                "seller_items":{
                    "item_id": str(item["node"]["id"]),
                    "price": item["node"]["listing_price"]["formatted_amount"],
                    "status": str(item["node"]["is_pending"]),
                    "islive": (item["node"]["is_live"]),
                    "category": item["node"]["marketplace_listing_category_id"],
                    "name": item["node"]["marketplace_listing_title"],
                    "picture": item["node"]["primary_listing_photo"]["image"]["uri"],
                    "delivery": item["node"]["delivery_types"][0],
                    "location": item["node"]["location"]["reverse_geocode"]["city_page"]["display_name"],
                    "category_id":item["node"]["marketplace_listing_category_id"]
                }
            })

            if item["node"]["origin_group"] != None:
                seller_informations.append({
                    "seller_group":{
                        "name":item["node"]["origin_group"]["name"],
                        "id":item["node"]["origin_group"]["id"]
                        }
                    })
    return seller_informations

def location_and_delivery_type(seller_informations):
    """ Extract the location and the delivery type from each item sell profile and check if its already exists."""
    if seller_informations[0]["nbr_total_item"] != 0:
        i = 1
        locations = list()
        deliveries = list()
        while (i < len(seller_informations)):
            location  = seller_informations[i]["seller_items"]["location"]
            delivery = seller_informations[i]["seller_items"]["delivery"]
            if location not in locations:
                locations.append(location)
            if delivery not in deliveries:
                deliveries.append(delivery)
            i +=1
        seller_informations[0]["delivery"]= deliveries
        seller_informations[0]["location"]= location
    else:
        seller_informations[0]["delivery"] = None
        seller_informations[0]["location"] = None
    return seller_informations


def show_seller_informations(seller_informations):
    """ Print the seller informations. """"
    print(f"""
Seller Name : {seller_informations[0]['sellername']},
Seller ID : {seller_informations[0]['sellerid']},
Total items : {seller_informations[0]['nbr_total_item']}
    """)
    location_and_delivery_type(seller_informations)

    if seller_informations[0]['location'] != None:
        print(f"Location(s) {seller_informations[0]['location']}")
    if seller_informations[0]['delivery'] != None:
        print(f"Delivery type {seller_informations[0]['delivery']}")
    if seller_informations[0]['rating']['seller_stats'] != None:
        print(f"""Rating average {seller_informations[0]['rating']['seller_stats']['five_star_ratings_average']} && Number of five stars : {seller_informations [0]['rating']['seller_stats']['five_star_total_rating_count_by_role']}""")
        if seller_informations[0]['rating']['seller_stats']['good_attributes_counts'] != None:
            print("\nGood Attributes:\n")
            for attribute in seller_informations[0]['rating']['seller_stats']['good_attributes_counts']:
                print(f"{attribute['title']['text']} : {attribute['count']}")
        if seller_informations[0]['rating']['seller_stats']['bad_attributes_counts'] != None:
            print("\nBad Attributes:\n")
            for attribute in seller_informations[0]['rating']['seller_stats']['bad_attributes_counts']:
                print(f"{attribute['title']['text']} : {attribute['count']}")

def show_item_informations(seller_informations):
    """ Print the item informations and the url of the marketplace item. """
    i = 1
    while (i < len(seller_informations)):
        print(f"""
Name : {seller_informations[i]['seller_items']['name']} && Price : {seller_informations[i]['seller_items']['price']},
Item ID : {seller_informations[i]['seller_items']['item_id']} && URL : https://www.facebook.com/markteplace/item{seller_informations[i]['seller_items']['item_id']}""")
        #Delivery: {seller_informations[i]['seller_items']['delivery']}
        #Picture: {seller_informations[i]['seller_items']['picture']},

        #print(seller_informations[i]["seller_items"].values())
        i+=1


def main():

    user_id = str(input("entrez userid : "))

    headers = {
        'User-Agent': random.choice(ua["browsers"]["chrome"]),
        'Accept': '*/*',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'X-FB-Friendly-Name': 'MarketplaceSellerProfileDialogQuery',
        'Origin': 'https://www.facebook.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Site': 'same-origin'
    }

    payload = {
        'variables': '{"canViewCustomizedProfile":true,"count":8,"isCOBMOB":false,"scale":1,"sellerId":"'+user_id+'"}',
        'doc_id': '4872548596176106',
    }

    response = requests.post('https://www.facebook.com/api/graphql/', headers=headers, data=payload)
    with open(f"{user_id}_source.txt", 'w') as f:
        f.write(response.text)
    data = response.json()

    if data["data"]['user'] ==  None:
        print("User doesn't exist")
        exit()


    seller_items = list()
    x = 0
    seller_informations = dict()

    seller_informations = general_informations(data, seller_items, seller_informations)
    seller_informations, has_next_page, end_page = new_page(data, seller_informations)
    show_seller_informations(seller_informations)
    show_item_informations(seller_informations)

main()
