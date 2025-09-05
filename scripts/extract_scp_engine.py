"""
SCP Engine Extractor

Requirements:
- Pillow
"""

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from PIL import Image


def extract_file(zf: zipfile.ZipFile, src: str, dst: Path):
    """Extract a file from the zip to a destination path."""
    with zf.open(src.lstrip("/")) as f_src, open(dst, "wb") as f_dst:
        shutil.copyfileobj(f_src, f_dst)


def convert_to_png(src: Path, dst: Path):
    """Convert an image to PNG."""
    with Image.open(src) as img:
        img.convert("RGBA").save(dst, "PNG")


def save_json(data: dict, dst: Path):
    """Save dictionary as JSON file."""
    dst.write_text(json.dumps(data, indent=4), encoding="utf-8")


def process_resource(zf: zipfile.ZipFile, resource: dict, resource_type: str, out_root: Path):
    name = resource["name"]
    folder_name = f"{resource_type}_{name}"
    res_dir = out_root / folder_name
    res_dir.mkdir(parents=True, exist_ok=True)

    # Resource JSON
    res_json = {
        "version": resource["version"],
        "title": resource["title"],
        "subtitle": resource.get("subtitle", ""),
        "author": resource.get("author", "")
    }
    save_json(res_json, res_dir / "resource.json")

    # Extract files
    for key, value in resource.items():
        if isinstance(value, dict) and "url" in value:
            url = value["url"]
            if key == "thumbnail":
                extract_file(zf, url, res_dir / f"{key}.png")
            elif key == "configuration":
                extract_file(zf, url, res_dir / f"{key}.json.gz")
            elif key == "image" and resource_type == "background":
                # Convert background image to PNG
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                extract_file(zf, url, tmp_path)
                convert_to_png(tmp_path, res_dir / f"{key}.png")
                tmp_path.unlink(missing_ok=True)
            else:
                extract_file(zf, url, res_dir / key)
    return res_dir


def extract_engine(scp_path: Path, out_root: Path):
    out_root.mkdir(exist_ok=True)

    with zipfile.ZipFile(scp_path, "r") as zf:
        with zf.open("sonolus/levels/list") as f:
            levels_data = json.load(f)

        first_level = levels_data["items"][0]
        engine = first_level["engine"]

        engine_dir = out_root / engine["name"]
        engine_dir.mkdir(parents=True, exist_ok=True)

        # Engine JSON
        engine_json = {
            "version": engine["version"],
            "title": engine["title"],
            "subtitle": engine.get("subtitle", ""),
            "author": engine.get("author", ""),
            "skin_name": engine["skin"]["name"],
            "background_name": engine["background"]["name"],
            "effect_name": engine["effect"]["name"],
            "particle_name": engine["particle"]["name"],
        }
        if "description" in engine:
            engine_json["description"] = engine["description"]
        save_json(engine_json, engine_dir / "engine.json")

        # Extract top-level files
        top_keys = ["thumbnail", "playData", "watchData", "previewData", "tutorialData", "configuration"]
        for key in top_keys:
            if key in engine:
                url = engine[key]["url"]
                if key == "thumbnail":
                    extract_file(zf, url, engine_dir / f"{key}.png")
                elif key == "configuration":
                    extract_file(zf, url, engine_dir / f"{key}.json.gz")
                else:
                    extract_file(zf, url, engine_dir / key)

        # Process resources
        for resource_type in ["skin", "background", "effect", "particle"]:
            if resource_type in engine:
                process_resource(zf, engine[resource_type], resource_type, engine_dir)


def main():
    parser = argparse.ArgumentParser(description="Extract first level engine from SCP file.")
    parser.add_argument("scp", type=Path, help="Path to .scp file")
    parser.add_argument("--out", type=Path, default=Path("extracted_engine"), help="Output folder")
    args = parser.parse_args()

    extract_engine(args.scp, args.out)


if __name__ == "__main__":
    main()