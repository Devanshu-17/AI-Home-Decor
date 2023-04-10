# Import necessary libraries
import streamlit as st


st.title('Saved collections of images')

# Get the uploaded and output images from the session state
uploaded_image = st.session_state.get('original_image')
output_image = st.session_state.get('output_image')


col1, col2 = st.columns(2)
# Display the uploaded image
if uploaded_image is not None:
    col1.image(uploaded_image, caption='Uploaded Image', use_column_width=True)

# Display the output image
if output_image is not None:
    col2.image(output_image, caption='Output Image', use_column_width=True)
