import streamlit as st
import base64


# Define a function to display an image as a card
def display_image_card(image_data):
    _, ext = image_data.name.split(".")
    encoded_image = base64.b64encode(image_data.read()).decode()
    return f"""
        <style>
            .card {{
                background-color: #F4F6F6;
                border-radius: 5px;
                padding: 5px;
                width: 210px;
                height: 210px;
                margin: 10px;
            }}
        </style>
        <div class="card">
            <div>
                <h5 style="color: #333333; font-weight: bold;"><img src="data:image/{ext};base64,{encoded_image}" style="width: 200px; height: 200px;"></h5>
            </div>
        </div>

       
    """


# Define the Streamlit app
def main():
    # Set the app title
    st.set_page_config(page_title="Upload and Save Images")

    # Add a title and instructions
    st.title("Upload and Save Images")
    st.write("Please upload the images you want to save below.")

    # Allow users to upload multiple images
    uploaded_files = st.file_uploader(
        "Upload images", accept_multiple_files=True, type=["png", "jpg", "jpeg"]
    )

    # Add a save button
    if st.button("Save Images"):
        # Display the uploaded images as cards
        for image in uploaded_files:
            st.markdown(display_image_card(image), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
