from PIL import Image, ImageDraw, ImageFont
import torch
import torchvision.transforms as transforms
import numpy as np
import albumentations as A
from torch import nn
from torchvision import models
import time

classes = {
    0: "Angry",
    1: "Disgust",
    2: "Fear",
    3: "Happy",
    4: "Sad",
    5: "Surprise",
    6: "Neutral",
}


class CustomModel(torch.nn.Module):
    def __init__(self, device="cpu"):
        super(CustomModel, self).__init__()

        self.resnet = models.vit_b_16(weights=models.ViT_B_16_Weights.IMAGENET1K_SWAG_E2E_V1)
        # Replace the final fully connected layer
        self.head = nn.Sequential(
            nn.Linear(in_features=1000, out_features=512),
            nn.ReLU(),
            nn.Linear(in_features=512, out_features=64),
            nn.ReLU(),
            nn.Linear(in_features=64, out_features=7),
        ).to(device)

        for param in list(self.resnet.parameters())[:-5]:
            param.requires_grad = False

        for param in list(self.resnet.parameters())[-5:]:
            param.requires_grad = True

        for param in self.head.parameters():
            param.requires_grad = True

    def forward(self, x):
        x = self.resnet(x)
        x = self.head(x)

        return x


def preprocess_image(image, device="cpu"):
    image_size = 384

    # Convert the image to grayscale
    gray_image = image.convert('L')

    inputs = np.array(gray_image).squeeze()

    def l_repeat(image, **kwargs):
        image = image.reshape((-1, 1, image_size, image_size))
        return torch.tensor(np.repeat(image, 3, axis=1))

    transform = A.Compose([
        A.Resize(image_size, image_size),
        A.Normalize((0.5,), (0.5,)),
        A.Lambda(name='l_repeat', image=l_repeat, p=1),
    ])

    image = transform(image=inputs)

    image = image['image'].to(device)

    return image


def write_label_on_image(image, label, output_path, position=(10, 10), font_size=20):
    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # # Load a font
    # try:
    #     # You can specify a TTF font file path if you have a specific font in mind
    #     font = ImageFont.truetype("arial.ttf", font_size)
    # except IOError:
    #     # If the specified font is not found, load the default font
    font_size = 40
    font = ImageFont.load_default(font_size)

    # Write the label on the image at the specified position
    draw.text(position, label, fill="red", font=font)  # You can change 'white' to any color you want

    # Save the modified image
    image.save(output_path)

def process_image(model_path, image_path):
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    image = Image.open(image_path)

    inputs = preprocess_image(image, device=device)
    inputs.to(device)

    model = CustomModel()
    model.to(device)
    state_dict = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()

    with torch.no_grad():
        prediction = model(inputs)
    label = np.argmax(prediction.detach().cpu().numpy())
    label = classes[label]
    new_image_path = image_path.split(".")[0] + "_labeled." + image_path.split(".")[-1]
    write_label_on_image(image, label, new_image_path)

