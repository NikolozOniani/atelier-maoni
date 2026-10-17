#!/usr/bin/env python3
"""Create missing responsive WebP variants from the original photo archive."""
from io import BytesIO
from html import escape
import json
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageCms, ImageOps


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "_studio/data/photo-inventory.json"
PORTFOLIO_PATH = ROOT / "_studio/data/portfolio.json"
OUTPUT = ROOT / "assets/images"


def srgb_image(source):
    image = ImageOps.exif_transpose(source)
    profile = image.info.get("icc_profile")
    if profile:
        return ImageCms.profileToProfile(
            image,
            ImageCms.ImageCmsProfile(BytesIO(profile)),
            ImageCms.createProfile("sRGB"),
            outputMode="RGB",
        )
    return image.convert("RGB")


inventory = json.loads(INVENTORY_PATH.read_text())
projects = json.loads(PORTFOLIO_PATH.read_text())
portfolio_ids = [photo_id for project in projects for photo_id in project["images"]]
expected_ids = {photo_id for photo_id in range(1, 35) if photo_id != 13}
if set(portfolio_ids) != expected_ids or len(portfolio_ids) != len(expected_ids):
    raise ValueError("Every garment photograph must appear exactly once in the portfolio data.")
primary_ids = {project["images"][0] for project in projects}
project_by_image = {
    image_id: project["id"] for project in projects for image_id in project["images"]
}
created = 0
for photo in inventory:
    if photo["id"] == 13:
        photo["usage"] = "logo"
        photo["publication_review"] = "Logo retained for website branding."
        continue
    photo["group"] = project_by_image[photo["id"]]
    photo["usage"] = (
        "hero"
        if photo["id"] == 4
        else "selected"
        if photo["id"] in primary_ids
        else "supporting"
    )
    photo["publication_review"] = (
        "Approved for portfolio use by the owner; parent or guardian consent "
        "confirmed where applicable."
    )
    if photo.get("variants"):
        continue
    with Image.open(ROOT / photo["path"]) as source:
        image = srgb_image(source)
        widths = sorted({min(width, image.width) for width in (480, 960, 1440)})
        photo["variants"] = []
        for width in widths:
            resized = image.resize(
                (width, round(image.height * width / image.width)),
                Image.Resampling.LANCZOS,
            )
            filename = f'{photo["group"]}-{photo["id"]:02}-{width}.webp'
            resized.save(OUTPUT / filename, "WEBP", quality=86, method=6)
            photo["variants"].append(
                {"file": filename, "width": resized.width, "height": resized.height}
            )
            created += 1

INVENTORY_PATH.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")

review = [
    '<!doctype html><html lang="en"><meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<title>MAONI — internal photo review</title>',
    '<style>body{font:15px/1.6 system-ui;background:#f8f6f2;color:#272521;max-width:1400px;margin:35px auto;padding:20px}a{color:#683c45}h1{font-weight:400}img{max-width:100%;height:auto}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px}figure{margin:0;background:white;padding:16px}figure img{width:100%;height:330px;object-fit:contain}p{overflow-wrap:anywhere}small{color:#60564f}.sheets{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:45px}.sheets img{width:100%}</style>',
    '<h1>MAONI / internal photograph review</h1>',
    '<p>All 34 originals. The logo is used for branding; all 33 garment photographs are included in the portfolio. Owner approval and relevant parent or guardian consent are confirmed.</p>',
    '<div class="sheets">',
]
for number in range(1, 5):
    review.append(
        f'<a href="sheet-{number}.jpg"><img src="sheet-{number}.jpg" '
        f'alt="Numbered contact sheet {number}"></a>'
    )
review.append('</div><section>')
for photo in inventory:
    source = "../../" + quote(photo["path"])
    review.append(
        f'<figure><a href="{source}"><img src="{source}" '
        f'alt="{escape(photo["description"], quote=True)}" loading="lazy"></a>'
        f'<figcaption><h2>{photo["id"]:02} / {photo["usage"]}</h2>'
        f'<p>{escape(photo["description"])}</p><p>{escape(photo["quality"])}</p>'
        f'<small>{photo["width"]} × {photo["height"]} / {photo["orientation"]}<br>'
        f'{escape(photo["path"])}</small><p>{escape(photo["publication_review"])}</p>'
        '</figcaption></figure>'
    )
review.append('</section></html>')
(ROOT / "_studio/review/index.html").write_text("".join(review))
print(f"Created {created} responsive WebP files for previously unused photographs.")
