import argparse
import os
import re
import shutil
from pathlib import Path
import filetype

# ---------- REGEX ----------

UUID_RE = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

ATTACH_RE = re.compile(
    rf"/api/attachments\.redirect\?id=({UUID_RE})"
)

ADMONITION_RE = re.compile(
    r":::([a-zA-Z]+)[ \t]*\n(.*?)(?=\n:::\s*(\n|$))\n:::\s*(\n|$)",
    re.DOTALL,
)

ADMONITION_MAP = {
    "warning": "WARNING",
    "info": "INFO",
    "tip": "TIP",
    "note": "NOTE",
    "danger": "DANGER",
}

# ---------- FUNCTIONS ----------

def detect_extension(path: Path) -> str:
    kind = filetype.guess(str(path))
    if kind:
        return "." + kind.extension
    return ""


def extract_uuid(name: str) -> str | None:
    m = re.search(UUID_RE, name)
    if not m:
        return None
    return m.group(0)


def copy_all_assets(src_root: Path, assets_root: Path):
    assets_root.mkdir(parents=True, exist_ok=True)

    mapping = {}

    for dirpath, _, filenames in os.walk(src_root):
        if "_attachments" not in dirpath:
            continue

        for f in filenames:
            p = Path(dirpath) / f
            uuid = extract_uuid(f)
            if not uuid:
                continue

            ext = detect_extension(p)
            new_name = uuid + ext

            mapping[uuid] = new_name
            shutil.copy2(p, assets_root / new_name)

            print(f"[ASSET] {p} -> {assets_root/new_name}")

    return mapping


def convert_admonitions(text: str) -> str:
    def repl(match):
        kind = match.group(1).lower()
        body = match.group(2).strip()

        header = ADMONITION_MAP.get(kind, kind.upper())

        lines = body.splitlines()
        body_fixed = "\n".join("> " + l for l in lines)

        return f"> [!{header}]\n{body_fixed}\n"

    return ADMONITION_RE.sub(repl, text)


def fix_relative_path(md_file: Path, uuid: str, new_name: str) -> str:
    depth = len(md_file.parts) - 2  # ignore clean_wiki/content

    prefix = "../" * depth

    return f"{prefix}assets/{new_name}"


def fix_markdown_links(content_root: Path, assets_mapping: dict):
    for md_file in content_root.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        original = text

        # fix admonitions
        text = convert_admonitions(text)

        def repl(match):
            uuid = match.group(1)
            if uuid not in assets_mapping:
                return match.group(0)

            new_name = assets_mapping[uuid]
            new_path = fix_relative_path(md_file, uuid, new_name)
            return new_path

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

    # copy content
    if content_out.exists():
        shutil.rmtree(content_out)
    shutil.copytree(src, content_out)

    assets_mapping = copy_all_assets(src, assets_out)

    fix_markdown_links(content_out, assets_mapping)

    print("\n✅ DONE — Wiki propre pour GitHub ready !")
    print(out)


if __name__ == "__main__":
    main()
