import streamlit as st
from utils.components import display_added_products  # Import the function
from utils.styles import load_css

# Setting page configuration first
st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
    layout="wide",
)

# Loading CSS styles
load_css()


# Main content of the homepage
def main():
    st.title("Main Page")
    display_added_products()


if __name__ == "__main__":
    main()
