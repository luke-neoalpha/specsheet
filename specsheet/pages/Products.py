import time

import streamlit as st
from Homepage import display_added_products
from utils.database import (
    add_accessory_to_product_list,
    add_product_to_product_list,
    check_accessory_exists,
    delete_image,
    delete_product_from_added_products,
    fetch_accessories_for_product,
    fetch_accessory_details,
    fetch_accessory_images,
    fetch_added_products,
    fetch_data_from_db,
    fetch_image_details,
    fetch_product_images,
    product_exists_in_product_list,
    update_image_name,
)
from utils.image_utils import get_image_base64
from utils.styles import load_css

load_css()

# Initialize session state variables
if "filter_text" not in st.session_state:
    st.session_state.filter_text = ""
if "num_records" not in st.session_state:
    st.session_state.num_records = 10
if "selected_manufacturers" not in st.session_state:
    st.session_state.selected_manufacturers = []

# Sidebar filters
st.sidebar.markdown(
    "<h1 style='text-align: center; padding-bottom: 40px;'>Product Filter</h1>",
    unsafe_allow_html=True,
)

# Manufacturer filter
databases = ["Iguzzini", "Linealight", "CDNLight", "PlusLight"]
selected_manufacturers = st.sidebar.multiselect(
    "Select Manufacturer(s)", databases, st.session_state.selected_manufacturers
)

filter_text = st.sidebar.text_input(
    "Filter text (comma-separated keywords)", st.session_state.filter_text
)
num_records = st.sidebar.number_input(
    "Number of records to display", min_value=1, value=st.session_state.num_records
)

# Update session state variables on interaction
if st.sidebar.button("Apply Filters"):
    st.session_state.filter_text = filter_text
    st.session_state.num_records = num_records
    st.session_state.selected_manufacturers = selected_manufacturers

st.sidebar.markdown("---")

# Fetch data based on filters
keywords = [
    keyword.strip().lower() for keyword in filter_text.split(",") if keyword.strip()
]
data = []
for db in databases:
    db_data = fetch_data_from_db(db)
    db_data_with_source = [
        (db, *row)
        for row in db_data
        if (not selected_manufacturers or db in selected_manufacturers)
    ]
    data.extend(db_data_with_source)

filtered_data = []
for row in data:
    row_str = " ".join(map(str, row)).lower()
    if all(keyword in row_str for keyword in keywords):
        filtered_data.append(row)

display_data = filtered_data[:num_records]


def display_product_viewer():  # noqa: C901
    st.title("Product Viewer")

    def display_product_details(product):
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

                    # Show delete confirmation dialog
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

                        # Create two columns for "Save Name" and "Cancel" buttons
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
        accessory_codes = fetch_accessories_for_product(db_name, product_code)
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
                                "Add Accessory",
                                key=f"add_accessory_{accessory_code}_{idx}",
                            ):
                                st.session_state["add_accessory"] = accessory_code
                                if product_exists_in_product_list(
                                    db_name, product_code
                                ):
                                    if not check_accessory_exists(
                                        product_code, accessory_code
                                    ):
                                        add_accessory_to_product_list(
                                            product_code, accessory_code
                                        )
                                        st.success("Accessory added successfully!")
                                        # Rerun the main page
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

        # Check if product_code already exists in the Product_List
        if product_code in [row[2] for row in added_products]:
            st.warning("Product already added")
        else:
            add_product_to_product_list(db_name, product_code)
            st.success("Product added successfully!")
            time.sleep(1)
            st.rerun()

    if "selected_product" in st.session_state:
        selected_product = st.session_state["selected_product"]
        display_product_details(selected_product)
        # Rerun the main page

    elif "add_product" in st.session_state:
        selected_product = st.session_state["add_product"]
        add_product_handler(selected_product)
        st.session_state.pop("add_product")
        st.rerun()  # Rerun the main page

    else:
        num_containers = len(display_data)
        num_columns = 3

        num_columns_needed = num_containers // num_columns + (
            num_containers % num_columns > 0
        )
        columns = [st.columns(num_columns) for _ in range(num_columns_needed)]

        for index, row in enumerate(display_data):
            current_col_index = index % num_columns
            current_col_set_index = index // num_columns

            db_name = row[0]
            product_code = row[2]
            product_configuration = row[3]
            technical_description = row[5]

            images = fetch_product_images(db_name, product_code)

            with columns[current_col_set_index][current_col_index]:
                st.markdown("""---""")
                if len(images) > 0:
                    img_base64 = get_image_base64(images[0][0])
                    st.markdown(
                        f"<div class='image-container'>"
                        f"<img src='data:image/jpeg;base64,{img_base64}' alt='Product Image'/>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    f"<div class='container' style='border: 1px solid white;'>"
                    f"<div class='container-title'>{db_name} - {product_code}</div>"
                    f"<div class='section-title'>Product Configuration</div>"
                    f"<div class='product-configuration-container'>"
                    f"<p>{product_configuration}</p>"
                    f"</div>"
                    f"<div class='section-title'>Technical Description</div>"
                    f"<div class='technical-description-container'>"
                    f"<p>{technical_description}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Product", key=f"view_product_{index}"):
                        st.session_state["selected_product"] = row
                        st.rerun()  # Rerun the main page

                with col2:
                    if st.button("Add Product", key=f"add_product_{index}"):
                        st.session_state["add_product"] = row
                        st.rerun()  # Rerun the main page

    st.success("All containers created successfully!")


display_product_viewer()
display_added_products()
