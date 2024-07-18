import pandas as pd
import streamlit as st
from utils.database import (
    add_accessory_to_product_list,
    add_product_to_product_list,
    check_accessory_exists,
    count_product_list,
    delete_image,
    delete_product_from_added_products,
    fetch_accessories_for_product,
    fetch_accessory_details,
    fetch_accessory_images,
    fetch_added_products,
    fetch_image_details,
    fetch_product,
    fetch_product_images,
    product_exists_in_product_list,
    update_image_name,
)
from utils.image_utils import get_image_base64
from utils.styles import load_css


# Function to display the Product Cart in the sidebar
def display_added_products():
    total_added_products = count_product_list()
    st.sidebar.markdown(
        f"<h4 style='text-align: center;'>Total Products: {total_added_products}</h4>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        "<h1 style='text-align: center;'>Product Cart</h1>", unsafe_allow_html=True
    )
    added_products = fetch_added_products()

    if not added_products:
        st.sidebar.markdown(
            "<h4 style='text-align: center;'>Empty</h4>", unsafe_allow_html=True
        )
    else:
        df = pd.DataFrame(
            added_products,
            columns=["ID", "Database Name", "Product Code", "Accessory Codes"],
        )

        for index, row in df.iterrows():

            product_col, delete_col = st.sidebar.columns([6, 1])
            with product_col:
                st.header(f"{row['Database Name']} - {row['Product Code']}")
            with delete_col:
                if st.button("X", key=f"delete_{row['ID']}"):
                    delete_product_from_added_products(row["ID"])
                    st.rerun()
        st.sidebar.markdown("""---""")


def view_product_in_cart(product):
    db_name = product["Database Name"]
    product_code = product["Product Code"]
    # Fetch detailed information about the product based on db_name and product_code
    product_details = fetch_product_images(db_name, product_code)
    product_information = fetch_product(db_name, product_code)

    st.markdown(
        f"""
            <div class="product-container">
                <div class="product-column">
                    <div class="side-by-side">
                        <div><p>Product Code:</p> {product_code}</div>
                        <div><p>Product Configuration:</p> {product_information[0][2]}</div>
                    </div>
                    <hr/>
                    <div class="side-by-side">
                        <div><p>Product Base Code:</p> {product_information[0][3]}</div>
                        <div><p>Installation:</p> {product_information[0][5]}</div>
                    </div>
                    <hr/>
                    <div class="side-by-side">
                        <div><p>Colour:</p> {product_information[0][6]}</div>
                        <div><p>Weight:</p> {product_information[0][7]}</div>
                    </div>
                    <hr/>
                    <div><p>Notes:</p> {product_information[0][10]}</div>
                    <hr/>
                    <div class="side-by-side">
                        <div><p>Time Added:</p> {product_information[0][12]}</div>
                        <div><p>Added By:</p> {product_information[0][13]}</div>
                    </div>
                </div>
                <div class="product-column-wide">
                    <div><p>Technical Description:</p> {product_information[0][4]}</div>
                    <hr/>
                     <div class="side-by-side">
                        <div><p>Mounting:</p> {product_information[0][8]}</div>
                        <div><p>Wiring:</p> {product_information[0][9]}</div>
                    </div>
                    <hr/>
                    <div><p>Technical Data:</p> {product_information[0][11]}</div>
                </div>
            </div>
            <hr/>
        """,
        unsafe_allow_html=True,
    )

    if product_details:
        num_columns = 4
        columns = st.columns(num_columns)
        image_details = fetch_image_details(db_name, product_code)

        for idx, image in enumerate(product_details):
            with columns[idx % num_columns]:
                img_base64 = get_image_base64(image[0])
                st.markdown(
                    f"<div class='details-image-container'>"
                    f"<img class='image-container' src='data:image/jpeg;base64,{img_base64}' alt='Product Image'/>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if idx < len(image_details):
                    current_id, current_name = image_details[idx]
                else:
                    current_id, current_name = None, ""

                edit_col, delete_col = st.columns(2)
                with edit_col:
                    if st.button("Edit Name", key=f"edit_name_{idx}"):
                        st.session_state[f"edit_{idx}"] = True

                with delete_col:
                    if st.button("Delete Image", key=f"delete_image_{idx}"):
                        st.session_state[f"delete_{idx}"] = True

                if st.session_state.get(f"delete_{idx}", False):
                    if st.button("Confirm Delete", key=f"confirm_delete_{idx}"):
                        if current_id is not None:
                            delete_image(db_name, current_id)
                            st.success("Image deleted successfully!")
                        st.session_state[f"delete_{idx}"] = False
                    if st.button("Cancel Delete", key=f"cancel_delete_{idx}"):
                        st.session_state[f"delete_{idx}"] = False

                if st.session_state.get(f"edit_{idx}", False):
                    new_name = st.text_input(
                        "Image Name", key=f"new_name_{idx}", value=current_name
                    )
                    save_col, cancel_col = st.columns(2)
                    with save_col:
                        if st.button("Save Name", key=f"save_name_{idx}"):
                            if current_id is not None:
                                update_image_name(db_name, current_id, new_name)
                                st.success("Image name updated successfully!")
                            st.session_state[f"edit_{idx}"] = False
                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_{idx}"):
                            st.session_state[f"edit_{idx}"] = False
                else:
                    st.write(current_name)


def view_product(product):  # noqa: C901
    db_name = product[0]
    product_code = product[2]
    product_configuration = product[3]
    technical_description = product[5]
    images = fetch_product_images(db_name, product_code)

    st.markdown(
        f"""
        <div class="product-container">
            <div class="product-column">
                <div class="side-by-side">
                    <div><p>Product Code:</p> {product_code}</div>
                    <div><p>Product Configuration:</p> {product_configuration}</div>
                </div>
                <hr/>
                <div class="side-by-side">
                    <div><p>Product Base Code:</p> {product[4]}</div>
                    <div><p>Installation:</p> {product[6]}</div>
                </div>
                <hr/>
                <div class="side-by-side">
                    <div><p>Colour:</p> {product[7]}</div>
                    <div><p>Weight:</p> {product[8]}</div>
                </div>
                <hr/>
                <div><p>Notes:</p> {product[11]}</div>
                <hr/>
                <div class="side-by-side">
                    <div><p>Time Added:</p> {product[13]}</div>
                    <div><p>Added By:</p> {product[14]}</div>
                </div>
            </div>
            <div class="product-column-wide">
                <div><p>Technical Description:</p> {technical_description}</div>
                <hr/>
                <div class="side-by-side">
                    <div><p>Mounting:</p> {product[9]}</div>
                    <div><p>Wiring:</p> {product[10]}</div>
                </div>
                <hr/>
                <div><p>Technical Data:</p> {product[12]}</div>
            </div>
        </div>
        <hr/>
    """,
        unsafe_allow_html=True,
    )

    add_product_col, space_col, back_to_products_col = st.columns([1, 7, 1])

    with add_product_col:
        if st.button("Add Product"):
            add_product_handler(product)

    with space_col:
        st.markdown(" ")

    with back_to_products_col:
        if st.button("Back to Products"):
            st.session_state.pop("selected_product")
            st.rerun()

    st.markdown("---")

    if images:
        num_columns = 4
        columns = st.columns(num_columns)
        image_details = fetch_image_details(db_name, product_code)

        for idx, image in enumerate(images):
            with columns[idx % num_columns]:
                img_base64 = get_image_base64(image[0])
                st.markdown(
                    f"<div class='details-image-container'>"
                    f"<img class='image-container' src='data:image/jpeg;base64,{img_base64}' alt='Product Image'/>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if idx < len(image_details):
                    current_id, current_name = image_details[idx]
                else:
                    current_id, current_name = None, ""

                edit_col, delete_col = st.columns(2)
                with edit_col:
                    if st.button("Edit Name", key=f"edit_name_{idx}"):
                        st.session_state[f"edit_{idx}"] = True

                with delete_col:
                    if st.button("Delete Image", key=f"delete_image_{idx}"):
                        st.session_state[f"delete_{idx}"] = True

                if st.session_state.get(f"delete_{idx}", False):
                    if st.button("Confirm Delete", key=f"confirm_delete_{idx}"):
                        if current_id is not None:
                            delete_image(db_name, current_id)
                            st.success("Image deleted successfully!")
                        st.session_state[f"delete_{idx}"] = False
                    if st.button("Cancel Delete", key=f"cancel_delete_{idx}"):
                        st.session_state[f"delete_{idx}"] = False

                if st.session_state.get(f"edit_{idx}", False):
                    new_name = st.text_input(
                        "Image Name", key=f"new_name_{idx}", value=current_name
                    )

                    save_col, cancel_col = st.columns(2)
                    with save_col:
                        if st.button("Save Name", key=f"save_name_{idx}"):
                            if current_id is not None:
                                update_image_name(db_name, current_id, new_name)
                                st.success("Image name updated successfully!")
                            st.session_state[f"edit_{idx}"] = False

                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_{idx}"):
                            st.session_state[f"edit_{idx}"] = False
                else:
                    st.write(current_name)

    st.markdown("---")

    st.markdown("## Accessories")

    product_base_code = product[4]

    accessory_codes = fetch_accessories_for_product(db_name, product_base_code)
    if accessory_codes:
        for accessory_code in accessory_codes:
            accessory_details = fetch_accessory_details(db_name, accessory_code)
            accessory_images = fetch_accessory_images(db_name, accessory_code)

            if accessory_details:
                st.markdown("<hr/>", unsafe_allow_html=True)
                for idx, image in enumerate(accessory_images):
                    accessory_img, accessory_info, accessory_button = st.columns(
                        [1, 4, 1]
                    )

                    with accessory_img:
                        img_base64 = get_image_base64(image[0])
                        st.markdown(
                            f"<div class='accessory-image-container'>"
                            f"<img class='image-container' src='data:image/jpeg;base64,{img_base64}' alt='Accessory Image'/>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                    with accessory_info:
                        st.markdown(
                            f"""
                            <div class="accessory-details-container">
                                <p><strong>Accessory Code:</strong> {accessory_details[1]}</p>
                                <p><strong>Accessory Configuration:</strong> {accessory_details[2]}</p>
                                <p><strong>Technical Description:</strong> {accessory_details[3]}</p>
                            </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    with accessory_button:
                        if st.button(
                            "Add Accessory", key=f"add_accessory_{accessory_code}_{idx}"
                        ):
                            st.session_state["add_accessory"] = accessory_code
                            if product_exists_in_product_list(db_name, product_code):
                                if not check_accessory_exists(
                                    product_code, accessory_code
                                ):
                                    add_accessory_to_product_list(
                                        product_code, accessory_code
                                    )
                                    st.success("Accessory added successfully!")
                                else:
                                    st.warning("Accessory already added")
                            else:
                                st.warning(
                                    f"Product '{product_code}' does not exist in Product List. Please add it first."
                                )

                        if st.button(
                            "View Accessory",
                            key=f"view_accessory_{accessory_code}_{idx}",
                        ):
                            st.session_state["view_accessory"] = accessory_code
                            st.rerun()  # Rerun the main page

            else:
                st.markdown("No accessory details found.")
    else:
        st.markdown("No accessories found for this product.")

    st.markdown("---")


def add_product_handler(product):
    db_name = product[0]
    product_code = product[2]

    added_products = fetch_added_products()

    if product_code in [row[2] for row in added_products]:
        st.warning("Product already added")
    else:
        add_product_to_product_list(db_name, product_code)
        st.success("Product added successfully!")
        st.rerun()
