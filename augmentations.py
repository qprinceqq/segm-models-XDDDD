import albumentations as A
import cv2
from typing import Tuple, List

__all__ = [
    "crop_transform",
    "safe_augmentations",
    "light_augmentations",
    "medium_augmentations",
    "hard_augmentations",
    "get_augmentations",
]


def crop_transform(image_size: Tuple[int, int], min_scale=0.75, max_scale=1.25, input_size=5000):
    return A.OneOrOther(
        A.RandomSizedCrop(
            (int(image_size[0] * min_scale), int(min(input_size, image_size[0] * max_scale))),
            image_size[0],
            image_size[1],
        ),
        A.CropNonEmptyMaskIfExists(image_size[0], image_size[1]),
    )


def crop_transform_xview2(image_size: Tuple[int, int], min_scale=0.4, max_scale=0.75, input_size=1024):
    return A.OneOrOther(
        A.RandomSizedCrop(
            (int(image_size[0] * min_scale), int(min(input_size, image_size[0] * max_scale))),
            image_size[0],
            image_size[1],
        ),
        A.Compose(
            [A.Resize(input_size * 2, input_size * 2), A.CropNonEmptyMaskIfExists(image_size[0], image_size[1])]
        ),
    )


def safe_augmentations() -> List[A.DualTransform]:
    return [
        # D4 Augmentations
        A.RandomRotate90(p=1),
        A.Transpose(p=0.5),
    ]


def light_augmentations(mask_dropout=True) -> List[A.DualTransform]:
    return [
        # D4 Augmentations
        A.Downscale(0.3, 0.3, always_apply=True),
        A.RandomRotate90(p=1),
        A.Transpose(p=0.5),
        A.RandomBrightnessContrast(),
        A.ShiftScaleRotate(scale_limit=0.05, rotate_limit=15, border_mode=cv2.BORDER_CONSTANT),
    ]


def medium_augmentations(for_3ch_img=True, mask_dropout=True) -> List[A.DualTransform]:
    return [
        A.HorizontalFlip(),
        A.ShiftScaleRotate(scale_limit=0.1, rotate_limit=15, border_mode=cv2.BORDER_CONSTANT),
        # Add occasion blur/sharpening
        A.OneOf([A.GaussianBlur(), A.NoOp()]),  # A.IAASharpen()
        # Spatial-preserving augmentations:
        A.OneOf([A.CoarseDropout(), A.NoOp()]),  #  A.MaskDropout(max_objects=5) if mask_dropout else A.NoOp()
        A.GaussNoise(),
        # Color augmentations
        A.OneOf(
            [
                A.RandomBrightnessContrast(brightness_by_max=True),
                A.CLAHE(),
                A.HueSaturationValue(),
                A.RGBShift(),
                A.RandomGamma(),
            ]
        ) if for_3ch_img else A.OneOf(
            [
                A.RandomBrightnessContrast(brightness_by_max=True),
                # A.CLAHE(),
                # A.HueSaturationValue(),
                # A.RGBShift(),
                A.RandomGamma(),
            ]
        )
        ,
        # Weather effects
        A.RandomFog(fog_coef_lower=0.01, fog_coef_upper=0.3, p=0.1) if for_3ch_img else A.NoOp(),
    ]


def hard_augmentations(for_3ch_img=True, mask_dropout=True) -> List[A.DualTransform]:
    return [
        # D4 Augmentations
        A.RandomRotate90(p=1),
        A.Transpose(p=0.5),
        # Spatial augmentations
        A.OneOf(
            [
                A.ShiftScaleRotate(scale_limit=0.2, rotate_limit=45, border_mode=cv2.BORDER_REFLECT101),
                A.ElasticTransform(border_mode=cv2.BORDER_REFLECT101, alpha_affine=5),
            ]
        ),
        # Color augmentations
        A.OneOf(
            [
                A.RandomBrightnessContrast(brightness_by_max=True),
                A.CLAHE(),
                A.FancyPCA(),
                A.HueSaturationValue(),
                A.RGBShift(),
                A.RandomGamma(),
            ]
        ) if for_3ch_img else A.OneOf(
            [
                A.RandomBrightnessContrast(brightness_by_max=True),
                # A.CLAHE(),
                # A.FancyPCA(),
                # A.HueSaturationValue(),
                # A.RGBShift(),
                A.RandomGamma(),
            ]
        )
        ,
        # Dropout & Shuffle
        A.OneOf(
            [
                A.RandomGridShuffle(),
                A.CoarseDropout(),
                # A.MaskDropout(max_objects=2, mask_fill_value=0) if mask_dropout else A.NoOp(),
            ]
        ),
        # Add occasion blur
        A.OneOf([A.GaussianBlur(), A.GaussNoise()]),
        # Weather effects
        A.RandomFog(fog_coef_lower=0.01, fog_coef_upper=0.3, p=0.1) if for_3ch_img else A.NoOp(),
    ]


def one_augmentations(mask_dropout=True) -> List[A.DualTransform]:
    return [
        A.RandomRotate90(p=1),
        A.Transpose(p=0.5),
        A.RandomBrightnessContrast(brightness_by_max=True),
        A.CLAHE(),
        A.FancyPCA(),
        A.HueSaturationValue(),
        A.RGBShift(),
        A.RandomGamma(),
    ]


def get_augmentations(augmentation: str, for_3ch_img=True) -> List[A.DualTransform]:
    if augmentation == "hard":
        aug_transform = hard_augmentations(for_3ch_img)
    elif augmentation == "medium":
        aug_transform = medium_augmentations(for_3ch_img)
    elif augmentation == "light":
        aug_transform = light_augmentations()
    elif augmentation == "safe":
        aug_transform = safe_augmentations()
    elif augmentation == "one":
        aug_transform = one_augmentations()
    else:
        aug_transform = []

    return aug_transform
