import hashlib
from PIL import Image
from torchvision import transforms


# Canonical transform to ensure consistent hashing
_CANONICAL_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


def image_to_token(image: Image.Image, token_length: int = 64) -> str:
    """
    Convert an image into a deterministic token by hashing its pixel data.

    Args:
        image (PIL.Image.Image): Input image to tokenize.
        token_length (int): Length of the token (default: 64).

    Returns:
        str: Hexadecimal token derived from the image content.
    """
    tensor = _CANONICAL_TRANSFORM(image)
    tensor_bytes = tensor.numpy().tobytes()
    return hashlib.sha256(tensor_bytes).hexdigest()[:token_length]
