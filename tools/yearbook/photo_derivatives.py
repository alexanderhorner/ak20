"""Create bounded, high-quality sRGB derivatives without touching originals."""
from pathlib import Path
import hashlib
import io
import math

from PIL import Image, ImageCms


def derivative(package, item, target_size_pt, destination, crop=True):
    path = package / item['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
    with Image.open(path) as original:
        image = original.copy()
        profile = original.info.get('icc_profile')
    # IDML records the actual layout orientation, including manual rotations.
    # Using EXIF a second time here would rotate certain portraits twice.
    rotations = {90: Image.Transpose.ROTATE_270, -90: Image.Transpose.ROTATE_90,
                 180: Image.Transpose.ROTATE_180, -180: Image.Transpose.ROTATE_180}
    rotation = item['layout_rotation_degrees_clockwise']
    if item.get('layout_reflected_vertical_before_rotation', False):
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if rotation in rotations:
        image = image.transpose(rotations[rotation])
    uncropped_size = image.size
    bounds = item['crop_normalized'] if crop else [0, 0, 1, 1]
    box = tuple(round(v * image.size[i % 2]) for i, v in enumerate(bounds))
    if crop:
        image = image.crop(box)
    crop_size = image.size
    # 240 ppi is the target, with no upsampling of small archival snapshots.
    limit = tuple(math.ceil(v * 240 / 72) for v in target_size_pt)
    image.thumbnail(limit, Image.Resampling.LANCZOS)
    if profile and image.mode != 'RGBA':
        image = ImageCms.profileToProfile(image, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                                          ImageCms.createProfile('sRGB'), outputMode='RGB')
    alpha = image.mode == 'RGBA' or 'transparency' in image.info
    if alpha:
        image = image.convert('RGBA')
    else:
        image = image.convert('RGB')
    suffix = '.png' if alpha or path.suffix.lower() == '.png' else '.jpg'
    if suffix == '.jpg':
        image.save(destination.with_suffix(suffix), quality=91, subsampling=0, optimize=True)
    else:
        image.save(destination.with_suffix(suffix), optimize=True)
    destination = destination.with_suffix(suffix)
    return destination, {'file': item['file'], 'original_sha256': item['sha256'],
                         'layout_rotation_degrees_clockwise': rotation,
                         'layout_reflected_vertical_before_rotation': item.get('layout_reflected_vertical_before_rotation', False),
                         'original_layout_pixels': list(uncropped_size),
                         'crop_normalized': bounds, 'crop_pixels': list(box),
                         'cropped_source_pixels': list(crop_size),
                         'export_pixels': list(image.size),
                         'effective_ppi': round(min(image.width / target_size_pt[0],
                                                    image.height / target_size_pt[1]) * 72, 1),
                         'jpeg_quality': 91 if suffix == '.jpg' else None,
                         'export_bytes': destination.stat().st_size}
