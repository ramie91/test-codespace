import argparse
import os
import re
import shutil
from pathlib import Path

import filetype  # pip install filetype

# ------------------ Config admonitions ------------------ #

# mapping :::type -> [!TYPE]
ADMONITION_TITLE = {
    "warning": "WARNING",
    "info": "INFO",
    "note": "NOTE",
    "tip": "TIP",
    "danger": "DANGER",
}


ADMONITION_RE = re.compile(
    r":::([a-zA-Z]+)[ \t]*\n(.*?)(?=\n:::\s*(\n|$))\n:::\s*(\n|$)",
    re.DOTALL,
)


def convert_admonition_block(match: re.Match) -> str:
    kind = match.group(1).lower()
    body = match.group(2).rstrip("\n")

    title = ADMONITION_TITLE.get(kind, kind.upper())

    # chaque ligne devient "> ..."
    lines = body.splitlines()
    if not lines:
        content = "> \n"
    else:
        content = "\n".join("> " + line for line in lines)

    # style GitHub:
    # > [!WARNING]
    # > texte...
    return f"> [!{title}]\n{content}\n"


# ------------------ Attachments / assets ------------------ #

# /api/attachments.redirect?id=<UUID>
ATTACH_RE = re.compile(
    r"(/api/attachments\.redirect\?id=([0-9a-fA-F\-]+))"
)


def detect_extension(path: Path) -> str | None:
    """Détecte l'extension d'un fichier (image / autre) via filetype."""
    kind = filetype.guess(str(path))
    if kind is None:
        return None
    return "." + kind.extension


def build_attachment_index(backup_root: Path) -> dict[str, Path]:
    """
    Parcourt backup_root et indexe tous les fichiers dans les dossiers _attachments.
    Les clés de l'index peuvent être :
      - le nom complet du fichier
      - tout UUID trouvé dans le nom
    """
    index: dict[str, Path] = {}

    uuid_re = re.compile(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )

    for dirpath, dirnames, filenames in os.walk(backup_root):
        if "_attachments" not in dirpath.replace("\\", "/"):
            continue

        for name in filenames:
            p = Path(dirpath) / name
            # clé = nom complet
            index[name] = p

            # clés = tous les UUID qui apparaissent dans le nom
            for u in uuid_re.findall(name):
                index[u] = p

    print(f"[INFO] Attachments indexés : {len(index)} entrées")
    return index


def ensure_exported_asset(
    attach_id: str,
    attachment_index: dict[str, Path],
    assets_root: Path,
    exported: dict[str, str],
) -> str | None:
    """
    Pour un id (UUID), trouve le fichier correspondant dans l'index,
    copie dans assets_root avec la bonne extension,
    renvoie le nouveau nom de fichier (ex: 'uuid.png').
    """

    # déjà traité ?
    if attach_id in exported:
        return exported[attach_id]

    # 1) correspondance directe
    src = attachment_index.get(attach_id)

    # 2) sinon, on cherche dans les clés qui contiennent l'id
    if src is None:
        for key, path in attachment_index.items():
            if attach_id in key:
                src = path
                break

    if src is None:
        print(f"[WARN] Aucun fichier trouvé pour attachment id={attach_id}")
        return None

    # extension actuelle ?
    ext = src.suffix
    if not ext:
        # essaie de deviner via le contenu
        guessed = detect_extension(src)
        if guessed:
            ext = guessed
        else:
            ext = ""  # on laisse sans extension si inconnu

    new_name = attach_id + ext
    dest = assets_root / new_name
    assets_root.mkdir(parents=True, exist_ok=True)

    if not dest.exists():
        shutil.copy2(src, dest)
        print(f"[COPY] {src} -> {dest}")
    else:
        print(f"[SKIP] déjà copié : {dest}")

    exported[attach_id] = new_name
    return new_name


def rewrite_attachments_in_text(
    text: str,
    attachment_index: dict[str, Path],
    assets_root: Path,
    exported: dict[str, str],
) -> str:
    """
    Remplace les URLs /api/attachments.redirect?id=... par assets/<nom.ext>
    dans tout le texte Markdown/HTML.
    """

    def repl(match: re.Match) -> str:
        full_url = match.group(1)
        attach_id = match.group(2)

        new_name = ensure_exported_asset(attach_id, attachment_index, assets_root, exported)
        if new_name is None:
            return full_url  # on ne touche pas si on ne trouve pas
        return f"assets/{new_name}"

    return ATTACH_RE.sub(repl, text)


# ------------------ Traitement des fichiers Markdown ------------------ #

def process_md_file(
    src_path: Path,
    dst_path: Path,
    attachment_index: dict[str, Path],
    assets_root: Path,
    exported_assets: dict[str, str],
):
    text = src_path.read_text(encoding="utf-8", errors="ignore")
    original = text

    # 1) Admonitions Outline -> admonitions GitHub
    text = ADMONITION_RE.sub(convert_admonition_block, text)

    # 2) Liens d’attachments -> assets/<uuid.ext>
    text = rewrite_attachments_in_text(text, attachment_index, assets_root, exported_assets)

    if text != original:
        print(f"[MD] Modifié : {src_path}")
    else:
        print(f"[MD] Copié tel quel : {src_path}")

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(text, encoding="utf-8")


# ------------------ Main ------------------ #

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Transforme un export Outline brut en wiki prêt pour GitHub "
            "(content/ + assets/, liens corrigés)."
        )
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Dossier racine de l'export Outline (ex: backup/).",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Dossier de sortie pour le wiki nettoyé (sera créé).",
    )
    args = parser.parse_args()

    src_root = Path(args.input).resolve()
    out_root = Path(args.output).resolve()

    content_root = out_root / "content"
    assets_root = out_root / "assets"

    if not src_root.is_dir():
        raise SystemExit(f"[ERR] Dossier d'entrée invalide : {src_root}")

    print(f"[INFO] Source  : {src_root}")
    print(f"[INFO] Sortie  : {out_root}")

    # Index des attachments (fichiers dans _attachments)
    attachment_index = build_attachment_index(src_root)
    exported_assets: dict[str, str] = {}

    # Parcours de tous les fichiers .md (hors _attachments)
    for dirpath, dirnames, filenames in os.walk(src_root):
        # on ignore le contenu des dossiers _attachments
        if "_attachments" in dirpath.replace("\\", "/"):
            continue

        for name in filenames:
            src = Path(dirpath) / name
            rel = src.relative_to(src_root)

            if src.suffix.lower() in {".md", ".markdown"}:
                dst = content_root / rel
                process_md_file(src, dst, attachment_index, assets_root, exported_assets)
            else:
                # si tu veux copier d'autres types de fichiers non markdown, tu peux le faire ici
                pass

    print("\n[INFO] Terminé.")
    print(f"  - Fichiers d'assets exportés : {len(exported_assets)}")
    print(f"  - Markdown prêt dans        : {content_root}")
    print(f"  - Assets dans               : {assets_root}")


if __name__ == "__main__":
    main()
