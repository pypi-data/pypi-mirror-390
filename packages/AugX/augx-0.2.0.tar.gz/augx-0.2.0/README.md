# AugX

AugX is a lightweight image augmentation utility for computer vision projects.  
It provides a simple interface to generate multiple augmented image variants, as well as a dedicated sharpening function with adjustable intensity.

---

## Features

- Horizontal flipping
- Gaussian blur
- Median blur
- Sharpening (standard + adjustable strength)
- High-pass enhancement
- Dilation & erosion
- Returns augmentations as a list for easy saving or training

---

## Installation

```bash
pip install augx
```

---

## Usage

### Importing
```python
import cv2
from augx import augment_image, display_images
```

### Generate Multiple Augmentations
Load Image:
```python

img = cv2.imread("sample.jpg")
```

To generate Augmented images:
```python
augmented_images = augment_image(img)
for name, img in augmented_images:
    cv2.imwrite(f"{name}.jpg", img)
```

To Display the images:
```python
augmented_images = augment_image(img)
display_images(augmented_images)
```

---

## Function Overview

### `augment_image(img)`
Returns a list of augmented images, including:
- Original image
- Horizontally flipped
- Sharpened
- Gaussian blur applied
- Median blur applied
- High-pass filtered version
- Dilated image
- Eroded image

### `display_images(named_images)`
Displays each augmented image one-by-one in a separate window, along with the name of the applied transformation.

---

## License

Licensed under the **MIT License**.  
See the full text in [`LICENSE.txt`](LICENSE.txt).

## Author

**Xopse**  
🌐 [GitHub](https://github.com/Xopse)
