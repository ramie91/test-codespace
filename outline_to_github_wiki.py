import argparse
import os
import re
import shutil
from pathlib import Path
import filetype


UUID_RE = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

ATTACH_RE = re.compile(
    rf"/api/attachments\.redirect\?id=({UUID_RE})"
)


def detect_extension(path: Path) -> str:
    kind = filetype.guess(str(path))
    if kind:
        return "." + kind.extension
    return ""


def clean_filename(name: str) -> str:
    m = re.search(UUID_RE, name)
    if not m:
        return None
    uuid = m.group(0)
    return uuid


def process_assets(src_root: Path, dst_root: Path):
    dst_root.mkdir(parents=True, exist_ok=True)
    mapping = {}

    for dirpath, _, filenames in os.walk(src_root):
        if "_attachments" not in dirpath:
            continue

        for f in filenames:
            p = Path(dirpath) / f
            clean = clean_filename(f)
            if not clean:
                continue

            ext = detect_extension(p)
            new_name = clean + ext
            mapping[clean] = new_name

            shutil.copy2(p, dst_root / new_name)
            print(f"[COPY] {p} -> {dst_root/new_name}")

    return mapping


def fix_markdown(content_root: Path, assets_mapping: dict):
    for md_file in content_root.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        original = text

        def repl(match):
            uuid = match.group(1)
            if uuid not in assets_mapping:
                return match.group(0)
            return f"assets/{assets_mapping[uuid]}"

        text = ATTACH_RE.sub(repl, text)

        if text != original:
            print(f"[FIX] {md_file}")
            md_file.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    src = Path(args.input)
    out = Path(args.output)
    content_out = out / "content"
    assets_out = out / "assets"

    if content_out.exists():
        shutil.rmtree(content_out)
    shutil.copytree(src, content_out)

    mapping = process_assets(src, assets_out)
    fix_markdown(content_out, mapping)

    print("\n[DONE] Wiki prêt pour GitHub :")
    print(out)


if __name__ == "__main__":
    main()
