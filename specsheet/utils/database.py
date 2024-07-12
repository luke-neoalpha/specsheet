import json

import mysql.connector


def get_db_connection(db_name):
    return mysql.connector.connect(
        host="localhost", user="root", password="", database=db_name
    )


def fetch_added_products():
    conn = get_db_connection("Neoalpha_Product_Record")
    cursor = conn.cursor()
    query = "SELECT id, manufacturer, product_code, accessory_codes FROM Product_List"
    cursor.execute(query)
    added_products = cursor.fetchall()
    conn.close()
    return added_products


def add_product_to_product_list(db_name, product_code):
    conn = get_db_connection("Neoalpha_Product_Record")
    cursor = conn.cursor()
    query = "INSERT INTO Product_List (manufacturer, product_code) VALUES (%s, %s)"
    cursor.execute(query, (db_name, product_code))
    conn.commit()
    conn.close()


def delete_product_from_added_products(product_id):
    conn = get_db_connection("Neoalpha_Product_Record")
    cursor = conn.cursor()
    query = "DELETE FROM Product_List WHERE id = %s"
    cursor.execute(query, (product_id,))
    conn.commit()
    conn.close()


def fetch_data_from_db(db_name):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product")
    data = cursor.fetchall()
    conn.close()
    return data


def fetch_product_images(db_name, product_code):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT photo FROM Images WHERE product_code = %s", (product_code,))
    images = cursor.fetchall()
    conn.close()
    return images


def fetch_image_details(db_name, product_code):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    query = "SELECT id, image_name FROM Images WHERE product_code = %s"
    cursor.execute(query, (product_code,))
    image_details = cursor.fetchall()
    conn.close()
    return image_details


# Function to update image names in the database based on image ID
def update_image_name(db_name, image_id, new_name):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    query = "UPDATE Images SET image_name = %s WHERE id = %s"
    cursor.execute(query, (new_name, image_id))
    conn.commit()
    conn.close()


# Function to delete an image from the database
def delete_image(db_name, image_id):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    query = "DELETE FROM Images WHERE id = %s"
    cursor.execute(query, (image_id,))
    conn.commit()
    conn.close()


def fetch_product(db_name, product_code):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    query = "SELECT * FROM Product WHERE product_code = %s"
    cursor.execute(query, (product_code,))
    product_details = cursor.fetchall()
    conn.close()
    return product_details


# Check if product code exist in list
def product_exists_in_product_list(db_name, product_code):
    conn = get_db_connection("Neoalpha_Product_Record")
    cursor = conn.cursor()
    query = "SELECT EXISTS(SELECT 1 FROM Product_List WHERE product_code = %s)"
    cursor.execute(query, (product_code,))
    exists_result = cursor.fetchone()[0]
    conn.close()
    return exists_result == 1


# Accessories


def fetch_accessories_for_product(db_name, product_code):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT accessory_code FROM Product_Accessories WHERE product_code = %s",
        (product_code,),
    )
    accessories = cursor.fetchall()
    conn.close()
    return [accessory[0] for accessory in accessories]


def fetch_accessory_details(db_name, accessory_code):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Accessory WHERE accessory_code = %s", (accessory_code,)
    )
    accessory = cursor.fetchone()
    conn.close()
    return accessory


def fetch_accessory_images(db_name, accessory_code):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT photo FROM Accessory_Images WHERE accessory_code = %s",
        (accessory_code,),
    )
    images = cursor.fetchall()
    conn.close()
    return images


# Check existing accessory list by product_code
def check_added_accessories(product_code):
    conn = get_db_connection("Neoalpha_Product_Record")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT accessory_codes FROM Product_List WHERE product_code = %s",
        (product_code,),
    )
    accessories = cursor.fetchone()
    conn.close()
    return accessories


# Add accessory to product_code
def add_accessory_to_product_list(product_code, accessory_code):
    conn = get_db_connection("Neoalpha_Product_Record")
    cursor = conn.cursor()

    # Check if product exists in Product_List
    if not product_exists_in_product_list("Neoalpha_Product_Record", product_code):
        print(
            f"Product '{product_code}' does not exist in Product List. Please add it first."
        )
        return False

    # Fetch existing accessories
    cursor.execute(
        "SELECT accessory_codes FROM Product_List WHERE product_code = %s",
        (product_code,),
    )
    fetch_accessories = cursor.fetchone()

    if fetch_accessories:
        existing_accessories = fetch_accessories[0]
        if existing_accessories:
            try:
                accessory_codes = json.loads(existing_accessories)
                accessory_codes.append(accessory_code)
                updated_accessory_codes = json.dumps(accessory_codes)
                cursor.execute(
                    "UPDATE Product_List SET accessory_codes = %s WHERE product_code = %s",
                    (updated_accessory_codes, product_code),
                )
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {existing_accessories}")
        else:
            updated_accessory_codes = json.dumps([accessory_code])
            cursor.execute(
                "UPDATE Product_List SET accessory_codes = %s WHERE product_code = %s",
                (updated_accessory_codes, product_code),
            )
    else:
        print(f"No accessories found for product_code: {product_code}")

    conn.commit()
    conn.close()


def check_accessory_exists(product_code, accessory_code):
    conn = get_db_connection("Neoalpha_Product_Record")
    cursor = conn.cursor()

    query = "SELECT accessory_codes FROM Product_List WHERE product_code = %s"
    cursor.execute(query, (product_code,))
    result = cursor.fetchone()

    if result:
        accessory_codes_json = result[0]
        if accessory_codes_json:
            try:
                accessory_codes = json.loads(accessory_codes_json)
                return accessory_code in accessory_codes
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {accessory_codes_json}")
                return False
        else:
            print(f"accessory_codes is empty for product_code: {product_code}")
            return False
    else:
        print(f"No results found for product_code: {product_code}")
        return False


def remove_accessory_from_product_list(id, accessory_code):
    conn = get_db_connection("Neoalpha_Product_Record")
    cursor = conn.cursor()

    # Fetch current accessory codes JSON
    query_select = "SELECT accessory_codes FROM Product_List WHERE ID = %s"
    cursor.execute(query_select, (id,))
    result = cursor.fetchone()

    if result:
        accessory_codes_json = result[0]
        if accessory_codes_json:
            # Attempt to parse JSON data
            try:
                accessory_codes = json.loads(accessory_codes_json)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {accessory_codes_json}. {e}")
                cursor.close()
                conn.close()
                return False

            # Remove accessory_code if present
            if accessory_code in accessory_codes:
                accessory_codes.remove(accessory_code)

            # Convert list back to JSON
            updated_accessory_codes_json = json.dumps(accessory_codes)

            # Update the database
            if updated_accessory_codes_json == "[]":
                query_update = (
                    "UPDATE Product_List SET accessory_codes = NULL WHERE ID = %s"
                )
                cursor.execute(query_update, (id,))
            else:
                query_update = (
                    "UPDATE Product_List SET accessory_codes = %s WHERE ID = %s"
                )
                cursor.execute(query_update, (updated_accessory_codes_json, id))

            conn.commit()
            print(f"Accessory code '{accessory_code}' removed from product ID {id}.")
        else:
            print(f"Accessory codes is empty for product ID {id}.")
    else:
        print(f"No results found for product ID {id}.")

    cursor.close()
    conn.close()
