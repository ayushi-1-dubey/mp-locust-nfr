import json
from random import randint
import random, string

def create_inv_data(len):

    create_inv_dict = []
    update_inv_dict = []
    get_available_lots_dict = []
    update_inv_using_fkh_lot_id_dict = []
    update_sold_qty_using_fkh_lot_id_dict = []
    update_sold_qty_using_external_lot_id_dict = []

    with open("createInv_data.json", "w") as outfile:
        for val in range(0, len):

            payload =  {
                "apob_id": "nfr_"+''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                'lot_attributes': {
                    "batch_id": "nfr_"+''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                    "product_id": "nfr_"+''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                    "expiry_date": {
                        "seconds": randint(2219364912, 2619364912),
                        "nanos": 356000000
                         },
                    "mfg_date": {
                        "seconds": randint(1088212912, 1588212912),
                        "nanos": 356000000
                         },
                    "quantity":randint(50, 100),
                    "sold_quantity":randint(0, 50),
                    "mrp": float(random.randrange(155, 389))/100
                },
                "external_lot_id": {
                    "name": "pk_lot",
                    "value": "nfr_"+''.join(random.choices(string.ascii_letters + string.digits, k=16))
                }
            }

            create_inv_dict.append(payload)
            updated_payload = payload
            updated_payload["lot_attributes"]["quantity"] = payload["lot_attributes"]["quantity"]+1
            update_inv_dict.append(updated_payload)

            # Get available lots
            get_available_lots_payload = {
                "apob_id": payload["apob_id"],
                "product_id": payload["lot_attributes"]["product_id"],
            }
            get_available_lots_dict.append(get_available_lots_payload)

            # Update inventory using fkh lot id
            update_inv_using_fkh_lot_id_payload = {
                "fkh_lot_id": "fkh34788a8f-9279-4da4-8ef6-8df321c5a1ae",
                "distributor_apob_id": payload["apob_id"],
                "lot_attributes": payload["lot_attributes"],
                "external_lot_id": payload["external_lot_id"]
            }
            update_inv_using_fkh_lot_id_dict.append(update_inv_using_fkh_lot_id_payload)

            # Update sold quantity using fkh lot id
            update_sold_qty_using_fkh_lot_id_payload = {
                "fkh_lot_id": "fkh34788a8f-9279-4da4-8ef6-8df321c5a1ae",
                "distributor_apob_id": payload["apob_id"],
                "sold_quantity": payload["lot_attributes"]["sold_quantity"]+1
            }
            update_sold_qty_using_fkh_lot_id_dict.append(update_sold_qty_using_fkh_lot_id_payload)

            # Update sold quantity using external lot id
            update_sold_qty_using_external_lot_id_payload = {
                "distributor_apob_id": payload["apob_id"],
                "sold_quantity": payload["lot_attributes"]["sold_quantity"]+2,
                "external_lot_id": payload["external_lot_id"]
            }
            update_sold_qty_using_external_lot_id_dict.append(update_sold_qty_using_external_lot_id_payload)

        obj = {"request": create_inv_dict}
        outfile.write(json.dumps(obj, indent=4))

    with open("update_inv_using_external_lot_id.json", "w") as outfile:
        outfile.write(json.dumps({"request": update_inv_dict}, indent=4))

    with open("get_available_lots.json", "w") as outfile:
        outfile.write(json.dumps({"request": get_available_lots_dict}, indent=4))

    with open("update_inv_using_fkh_lot_id.json", "w") as outfile:
        outfile.write(json.dumps({"request": update_inv_using_fkh_lot_id_dict}, indent=4))

    with open("update_sold_qty_using_fkh_lot_id.json", "w") as outfile:
        outfile.write(json.dumps({"request": update_sold_qty_using_fkh_lot_id_dict}, indent=4))

    with open("update_sold_qty_using_external_lot_id.json", "w") as outfile:
        outfile.write(json.dumps({"request": update_sold_qty_using_external_lot_id_dict}, indent=4))


def create_req_payload( file):
    with open(file, "r") as jsonfile:
        data = json.load(jsonfile)
        # print(data["request"])

    for req in range(0, len(data["request"])):
        print(data["request"][req])
        print(type(data["request"][req]))
        dict = data["request"][req]
        distributor_apob_id = dict["apob_id"]
        lot_attributes = dict["lot_attributes"]["batch_id"]
        print(distributor_apob_id, lot_attributes)

def extract_fkh_lot_id():
    with open("fkh_lot_ids.json", "r") as jsonfile:
        data = json.load(jsonfile)
        print(data)

if __name__ == "__main__":
    create_inv_data(200)
    # create_req_payload("createInv_data.json")
    # extract_fkh_lot_id()


