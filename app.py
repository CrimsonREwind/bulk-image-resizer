import streamlit as st
import cv2
import numpy as np
import zipfile
import io

st.title("Bulk Image Resizer")

uploaded_files = st.file_uploader("Select images to resize", type=["png", "jpg", "jpeg", "gif", "bmp"], accept_multiple_files=True)

colw, colh = st.columns(2)
with colh:
    resize_height = st.number_input("Select resize height", key="height", value=600, step=10)
with colw:
    resize_width = st.number_input("Select resize width", key="width", value=800, step=10)

stretch_checkbox = st.checkbox("Stretch to fit", value=False)

padding_color = st.color_picker("Select padding color", value="#FFFFFF")

quality = st.slider("Select image quality (1-100)", min_value=1, max_value=100, value=80)

resize_button = st.button("Resize Images", key="resize-button")

if resize_button and uploaded_files:
    resized_images = []
    progress_bar = st.progress(0)
    
    for i, file in enumerate(uploaded_files):
        img_array = np.frombuffer(file.getvalue(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)


        if stretch_checkbox:
            img = cv2.resize(img, (resize_width, resize_height))
        else:
            (h, w) = img.shape[:2]
            aspect_ratio = w / h
            if w > h:
                new_w = resize_width
                new_h = int(new_w / aspect_ratio)
            else:
                new_h = resize_height
                new_w = int(new_h * aspect_ratio)
            img = cv2.resize(img, (new_w, new_h))

        padding_w = resize_width - img.shape[1]
        padding_h = resize_height - img.shape[0]
        if padding_w > 0 or padding_h > 0:
            padding_color_bgr = tuple(int(padding_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            img_bg = np.full((resize_height, resize_width, 3), padding_color_bgr, dtype=np.uint8)
            x = (resize_width - img.shape[1]) // 2
            y = (resize_height - img.shape[0]) // 2
            img_bg[y:y+img.shape[0], x:x+img.shape[1]] = img
            img = img_bg

        _, img_encoded = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        buffer = io.BytesIO(img_encoded.tobytes())

        resized_images.append(buffer)

        progress_bar.progress((i + 1) / len(uploaded_files))

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i, buffer in enumerate(resized_images):
            zip_file.writestr(f"resized_image_{i}.jpg", buffer.getvalue())

    st.markdown("### Download Resized Images")
    st.download_button("Download", zip_buffer.getvalue(), "resized_images.zip", "application/zip")
