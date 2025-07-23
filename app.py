import streamlit as st
from paddleocr import PaddleOCR
import json
from PIL import Image
import numpy as np
import os

# Create output directory if it doesn't exist
if not os.path.exists('output'):
    os.makedirs('output')

# Initialize PaddleOCR
ocr = PaddleOCR(
    use_textline_orientation=True,
    text_detection_model_name='PP-OCRv5_server_det',
    text_recognition_model_name='PP-OCRv5_server_rec',
)

st.title("Invoice OCR with PaddleOCR")

uploaded_file = st.file_uploader("Choose an invoice image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    
    # To convert to a PIL Image object
    image = Image.open(uploaded_file).convert('RGB')
    
    # Display the uploaded image
    st.image(image, caption='Uploaded Invoice', use_container_width=True)
    
    # Convert PIL image to numpy array
    img_array = np.array(image)

    st.write("Processing invoice...")

    # Run OCR
    result = ocr.predict(img_array)

    # Display the raw OCR result for debugging
    st.write("Raw OCR Result:")
    st.write(result)

    # The result is a list of lists, where each inner list contains the bounding box, the text, and the confidence score.
    # Let's process this into a more structured format for JSON.
    
    if result and result[0] is not None:
        processed_result = []
        for i, line in enumerate(result[0]):
            try:
                box = line[0]
                # Add a check to handle cases where recognition might fail
                if isinstance(line[1], tuple) and len(line[1]) == 2:
                    text, confidence = line[1]
                else:
                    # Handle cases where the result for a box is not as expected
                    text = "" # Or some placeholder
                    confidence = 0.0
                
                processed_result.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bounding_box": {
                        "top_left": [int(p) for p in box[0]],
                        "top_right": [int(p) for p in box[1]],
                        "bottom_right": [int(p) for p in box[2]],
                        "bottom_left": [int(p) for p in box[3]],
                    }
                })
            except (ValueError, IndexError) as e:
                st.error(f"Error processing line {i}: {line}")
                st.error(f"Error details: {e}")
                continue


        # Save the result to a JSON file
        output_path = os.path.join('output', 'res.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_result, f, ensure_ascii=False, indent=4)

        st.success(f"OCR result saved to {output_path}")

        # Display the extracted text
        st.write("Extracted Text:")
        for item in processed_result:
            st.write(f"- {item['text']}")
            
        # Display the JSON result
        st.write("JSON Output:")
        st.json(processed_result)
    else:
        st.error("No text detected in the image.")
