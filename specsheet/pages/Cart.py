import time

import pandas as pd
import streamlit as st
from pdf_generator.pdf_generator import generate_pdf
from utils.database import (
    delete_image,
    delete_product_from_added_products,
    fetch_added_products,
    fetch_image_details,
    fetch_product,
    fetch_product_images,
    remove_accessory_from_product_list,
    update_image_name,
)
from utils.image_utils import get_image_base64
from utils.styles import load_css

# Load CSS styles
load_css()


# Function to display products in the cart
def display_products():
    st.markdown(
        "<h1 style='text-align: center;'>Product Cart</h1>", unsafe_allow_html=True
    )
    added_products = fetch_added_products()

    manufacturer_df = pd.DataFrame(
        added_products,
        columns=["ID", "Database Name", "Product Code", "Accessory Codes"],
    )

    if not added_products:
        st.markdown(
            "<h4 style='text-align: center;'>Empty</h4>", unsafe_allow_html=True
        )
    else:
        # Fetch additional product details
        product_details = []
        for index, row in enumerate(added_products):
            db_name, product_code = row[1], row[2]
            details = fetch_product(db_name, product_code)
            if details:
                # Assuming fetch_product returns a list of tuples
                product_details.extend(details)

        # Create a new DataFrame with additional product details
        if product_details:
            columns = [
                "product_id",
                "product_code",
                "product_configuration",
                "product_base_code",
                "technical_description",
                "installation",
                "colour",
                "weight",
                "mounting",
                "wiring",
                "notes",
                "technical_data",
                "time_created",
                "created_by",
            ]
            detailed_df = pd.DataFrame(product_details, columns=columns)
        else:
            detailed_df = pd.DataFrame()

        # Display the dataframe with an "X" button for deletion and "View Product" button
        for index, row in pd.DataFrame(
            added_products,
            columns=["ID", "Database Name", "Product Code", "Accessory Codes"],
        ).iterrows():
            if row["Accessory Codes"] is not None:
                cleaned_string = (
                    row["Accessory Codes"]
                    .replace("[", "")
                    .replace("]", "")
                    .replace('"', "")
                )
                accessory_codes_list = [
                    code.strip() for code in cleaned_string.split(",")
                ]
            else:
                accessory_codes_list = []
            product_col, view_product_col, delete_col = st.columns([6, 1, 1])
            with product_col:
                st.markdown(
                    f"""<div class='product-cart'><p>{row['Database Name']} - {row['Product Code']}</p>
                            </div>""",
                    unsafe_allow_html=True,
                )
                with st.expander("Accessories"):
                    if accessory_codes_list:
                        for accessory in accessory_codes_list:
                            access_col, delete_accessory_col = st.columns([20, 1])
                            with access_col:
                                st.write(accessory)
                            with delete_accessory_col:
                                if st.button(
                                    "x", key=f"delete_accessory_{row['ID']}_{accessory}"
                                ):
                                    remove_accessory_from_product_list(
                                        row["ID"], accessory
                                    )
                                    st.success("Accessory Removed")
                                    time.sleep(1)
                                    st.rerun()
                    else:
                        st.write("No Accessories")
            with view_product_col:
                if st.button("View Product", key=f"view_product_{index}"):
                    st.session_state["selected_product_1"] = row.to_dict()
                    st.rerun()
            with delete_col:
                if st.button("Remove Product", key=f"delete_{row['ID']}"):
                    delete_product_from_added_products(row["ID"])
                    st.rerun()

        # Display the additional product details
        # if not detailed_df.empty:
        #     st.dataframe(detailed_df)
        #     st.dataframe(manufacturer_df)

    st.markdown("""---""")
    empty_col, generate_pdf_col = st.columns([3, 1])
    with empty_col:
        st.write(" ")
    with generate_pdf_col:
        if st.button("Generate PDF"):
            pdf_output = generate_pdf(
                detailed_df.to_dict(orient="records"),
                manufacturer_df.to_dict(orient="records"),
            )
            st.success("PDF generated successfully!")
            with open(pdf_output, "rb") as pdf_file:
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name="product_cart.pdf",
                    mime="application/pdf",
                )


def view_product(product):
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


def main():
    selected_product = st.session_state.get("selected_product_1")

    if selected_product is not None:
        view_product(selected_product)
        if st.button("Back to Cart"):
            st.session_state.pop("selected_product_1")
            st.rerun()
    else:
        display_products()


if __name__ == "__main__":
    main()
