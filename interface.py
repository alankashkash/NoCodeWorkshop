import streamlit as st
import requests
import json
import base64
import os
from PIL import Image
from io import BytesIO

# Set up the imgbb API and WordWare API keys
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
WORDWARE_API_KEY = os.getenv("WORDWARE_API_KEY")

# Function to upload image to imgbb and return the URL
def upload_to_imgbb(image_base64):
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": image_base64
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        st.error("Failed to upload image to imgbb.")
        return None

# Updated function to call WordWare API and get alt text
def generate_alt_text(image_url):
    wordware_url = "https://app.wordware.ai/api/released-app/0081a6fd-4218-4233-a4b5-2d58674eaf6a/run"
    headers = {
        "Authorization": f"Bearer {WORDWARE_API_KEY}"
    }
    payload = {
        "inputs": {
            "image": {
                "type": "image",
                "image_url": image_url
            }
        },
        "version": "^1.0"
    }

    # Send POST request to the WordWare API
    response = requests.post(wordware_url, headers=headers, json=payload, stream=True)

    if response.status_code == 200:
        # Initialize an empty string to accumulate the alt text
        alt_text = ""

        # Process the response chunk by chunk
        for line in response.iter_lines():
            if line:
                # Parse each chunk
                chunk = json.loads(line.decode('utf-8'))
                
                # Check if this is a text chunk and append it to alt_text
                if chunk.get('value', {}).get('type') == 'chunk':
                    alt_text += chunk['value']['value']

        # Return the final concatenated alt text
        return alt_text if alt_text else "No Alt Text Generated"

# Function to convert image to base64
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # Convert to PNG or other format if needed
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_base64

# Streamlit UI setup
st.title("Alt Text Generator")

# File uploader for image input
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # Display the uploaded image
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Button to start the alt text generation process
    if st.button("Generate Alt Text"):
        with st.spinner("Please wait while we generate the alt text..."):
            # Convert image to base64
            image_base64 = image_to_base64(image)
            
            # Upload image to imgbb
            img_url = upload_to_imgbb(image_base64)
            print(img_url)
            if img_url:
                # Call WordWare API to generate alt text
                alt_text = generate_alt_text(img_url)
                print(alt_text)
                if alt_text:
                    st.success("Alt Text Generation Complete!")
                    # Display the alt text
                    st.write("Generated Alt Text: ", alt_text)
