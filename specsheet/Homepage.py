import pandas as pd
import streamlit as st
from utils.database import delete_product_from_added_products, fetch_added_products
from utils.styles import load_css

# Setting page configuration first
st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
    layout="wide",
)

# Loading CSS styles
load_css()


# Function to display the Product Cart in the sidebar
def display_added_products():
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

        # Display the dataframe with an "X" button for deletion
        for index, row in df.iterrows():
            # Create two columns with different widths in the sidebar
            product_col, delete_col = st.sidebar.columns(
                [6, 1]
            )  # col1 is 6 times wider than col2
            with product_col:
                st.header(f"{row['Database Name']} - {row['Product Code']}")
            with delete_col:
                if st.button("X", key=f"delete_{row['ID']}"):
                    delete_product_from_added_products(row["ID"])
                    st.rerun()  # Refresh the page after deletion
        st.sidebar.markdown("""---""")


# Main content of the homepage
def main():
    st.title("Main Page")
    display_added_products()


if __name__ == "__main__":
    main()
