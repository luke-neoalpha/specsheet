import base64
import io

from PIL import Image, UnidentifiedImageError


def get_image_base64(image):
    try:
        image_io = io.BytesIO(image)
        image_io.seek(0)  # Ensure the pointer is at the start
        image = Image.open(image_io)

        buffered = io.BytesIO()
        if image.format == "PNG":
            image.save(buffered, format="PNG")
        elif image.format == "JPEG":
            image.save(buffered, format="JPEG")
        else:
            raise UnidentifiedImageError("Unsupported image format")

        return base64.b64encode(buffered.getvalue()).decode()
    except UnidentifiedImageError as e:
        print(f"Error: Cannot identify image file. {e}")
        # Optionally, return a placeholder image or an error message
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Optionally, return a placeholder image or an error message
        return None
