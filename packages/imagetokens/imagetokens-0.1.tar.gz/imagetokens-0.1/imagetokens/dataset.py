import os
from typing import List, Tuple, Dict
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms
from tokenization import image_to_token


DEFAULT_CLASS_MAPPING: Dict[str, int] = {
    "covid": 0,
    "normal": 1,
    "pneumonia": 2
}


def get_image_paths_and_labels(
    directory: str,
    class_mapping: Dict[str, int] = DEFAULT_CLASS_MAPPING
) -> Tuple[List[str], List[int]]:
    """
    Retrieve image file paths and corresponding labels based on subfolder names.

    Args:
        directory (str): Root directory containing class subfolders.
        class_mapping (dict): Mapping of class names to integer labels.

    Returns:
        Tuple[List[str], List[int]]: Lists of image paths and labels.
    """
    image_paths, labels = [], []
    valid_exts = (".jpg", ".jpeg", ".png")

    for class_name, label in class_mapping.items():
        class_dir = os.path.join(directory, class_name)
        if not os.path.isdir(class_dir):
            continue
        for file_name in os.listdir(class_dir):
            if file_name.lower().endswith(valid_exts):
                image_paths.append(os.path.join(class_dir, file_name))
                labels.append(label)

    return image_paths, labels


class TokenizedImageDataset(Dataset):
    """
    Custom PyTorch Dataset for loading and tokenizing images.
    """

    def __init__(self, directory: str, transform=None):
        self.image_paths, self.labels = get_image_paths_and_labels(directory)
        if not self.image_paths:
            raise ValueError(f"No images found in directory: {directory}")
        self.transform = transform or transforms.Resize((224, 224))

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx: int):
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        image = Image.open(image_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        token = image_to_token(image)
        image_tensor = transforms.ToTensor()(image)

        return image_tensor, token, label
