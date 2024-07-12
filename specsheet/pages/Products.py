import streamlit as st
from utils.components import add_product_handler, display_added_products, view_product
from utils.database import fetch_data_from_db, fetch_product_images
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
if "added_products_rerun" not in st.session_state:
    st.session_state.added_products_rerun = False

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


def main_view():
    st.title("Product Viewer")

    if "selected_product" in st.session_state:
        selected_product = st.session_state["selected_product"]
        view_product(selected_product)

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
                        st.experimental_rerun()

                with col2:
                    if st.button(
                        "Add Product",
                        key=f"add_product_{index}",
                        on_click=add_product_handler,
                        args=(row,),
                    ):
                        st.session_state.added_products_rerun = True

        st.success("All containers created successfully!")


def display_added_products_wrapper():
    if st.session_state.added_products_rerun:
        st.session_state.added_products_rerun = False
        st.experimental_rerun()
    display_added_products()


def main():
    main_view()
    display_added_products_wrapper()


if __name__ == "__main__":
    main()
