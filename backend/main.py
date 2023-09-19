from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import os
from photo_restorer import predict_image

app = FastAPI()
UPLOAD_DIR = "uploads"  # Directory to store uploaded images

from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Ensure the directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Specify the model and version you want to use
GFPGAN_MODEL = "your_model_name"
GFPGAN_VERSION = "your_model_version"


@app.get("/", response_class=HTMLResponse)
async def main():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Image</title>
    </head>
    <body>
        <form method="post" enctype="multipart/form-data" action="/upload/" onsubmit="return uploadImage()">
            <input type="file" name="image" accept="image/*">
            <input type="submit" value="Upload">
        </form>
        <div id="imageContainer"></div> <!-- Container for displaying the uploaded image -->
        <script>
            function uploadImage() {
                const fileInput = document.querySelector('input[type="file"]');
                const imageContainer = document.getElementById("imageContainer");
                const formData = new FormData();
                formData.append("image", fileInput.files[0]);

                fetch("/upload/", {
                    method: "POST",
                    body: formData,
                })
                .then((response) => response.text())
                .then((html) => {
                    // Replace the content of imageContainer with the uploaded image HTML
                    imageContainer.innerHTML = html;
                });

                return false; // Prevent the form from submitting traditionally
            }
        </script>
    </body>
    </html>
    """


@app.post("/upload/", response_class=HTMLResponse)
async def upload_image(image: UploadFile = File(...)):
    # Check if the file is an image (you can add more robust checks here)
    if not image.filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
        return "Uploaded file is not an image"

    # Save the uploaded image to the UPLOAD_DIR
    image_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(image_path, "wb") as img:
        img.write(image.file.read())

    # Enhance the uploaded image using Tencent ARC GFPGAN with the specified model and version
    enhanced_image = predict_image(image_path)
    print(enhanced_image)
    
    # # Convert the enhanced image to a BytesIO object and save it
    # enhanced_image_io = BytesIO()
    # enhanced_image.save(enhanced_image_io, format="PNG")

    # # Create HTML to display both the original and enhanced images
    # original_image_data_uri = f"/uploads/{image.filename}"
    # enhanced_image_data_uri = f"data:image/png;base64,{base64.b64encode(enhanced_image_io.getvalue()).decode()}"

    # Create HTML to display the image
    image_data_uri = f"/uploads/{image.filename}"
    html_content = f'<h1>Uploaded Image:</h1><img src="{image_data_uri}" alt="Uploaded Image" width="350" height="500"><br /><h1>Enchanced Image:</h1><img src="{enhanced_image}" alt="Enchanced Image" width="350" height="500">'

    return html_content


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
