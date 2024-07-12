import base64
import io

from PIL import Image, UnidentifiedImageError


def get_image_base64(image):
    try:
        image_io = io.BytesIO(image)
        image_io.seek(0)
        image = Image.open(image_io)

        buffered = io.BytesIO()
        if image.format == "PNG":
            image.save(buffered, format="PNG")
        elif image.format == "JPEG":
            image.save(buffered, format="JPEG")
        elif image.format == "JPG":
            image.save(buffered, format="JPG")
        else:
            raise UnidentifiedImageError("Unsupported image format")

        return base64.b64encode(buffered.getvalue()).decode()
    except UnidentifiedImageError as e:
        print(f"Error: Cannot identify image file. {e}")

        return None
    except Exception as e:
        print(f"Unexpected error: {e}")

        return None
