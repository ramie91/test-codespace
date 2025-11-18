import os
import re
from pathlib import Path

import requests
from outline_wiki_api import OutlineWiki


# ========= À CONFIGURER =========
OUTLINE_URL = "https://mibwiki.one"          # <-- ton URL Outline
OUTLINE_TOKEN = "ol_api_ChCWGwz9YhlboSo3ErfX9BflKvMwpy8VzmDtaI"              # <-- colle ton token API (NE LE PARTAGE JAMAIS)
OUTPUT_DIR = r"backup"  # <-- où tu veux sauvegarder
# =================================


def safe_filename(name: str) -> str:
    """Nettoie un nom pour l'utiliser comme nom de fichier/dossier."""
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^\w\-_.]", "_", name)
    return name[:100] or "untitled"


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def extract_attachment_paths(markdown: str):
    """
    Récupère les URLs trouvées dans les images/liens markdown:
    ![alt](URL) ou [texte](URL)
    """
    pattern = r"!\[[^\]]*\]\(([^)]+)\)|\[[^\]]*\]\(([^)]+)\)"
    matches = re.findall(pattern, markdown or "")
    urls = []
    for m in matches:
        url = m[0] or m[1]
        if url and not url.startswith("#"):
            urls.append(url)
    return list(set(urls))


def download_attachment(session: requests.Session, base_url: str, url: str, dest_path: Path):
    """Tente de télécharger une pièce jointe (image/fichier)."""
    try:
        if not (url.startswith("http://") or url.startswith("https://")):
            full_url = base_url.rstrip("/") + url
        else:
            full_url = url

        resp = session.get(full_url, timeout=20)
        if resp.status_code == 200:
            ensure_dir(dest_path.parent)
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            print(f"    -> Pièce jointe téléchargée : {dest_path}")
        else:
            print(f"    !! Impossible de télécharger {full_url} (status {resp.status_code})")
    except Exception as e:
        print(f"    !! Erreur en téléchargeant {url} : {e}")


def api_call(session: requests.Session, method: str, payload: dict):
    """Appelle l’API Outline : /api/<method> en POST JSON."""
    url = OUTLINE_URL.rstrip("/") + "/api/" + method
    resp = session.post(url, json=payload)
    try:
        data = resp.json()
    except Exception:
        raise RuntimeError(f"Réponse non JSON pour {method}: {resp.status_code} {resp.text}")

    if not data.get("ok", True) and "error" in data:
        raise RuntimeError(
            f"Erreur API {method}: {data.get('error')} / {data.get('message')} (status {data.get('status')})"
        )
    return data


def main():
    base_path = Path(OUTPUT_DIR)
    ensure_dir(base_path)

    # Session HTTP avec le token
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {OUTLINE_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })

    print("🔌 Test du token avec auth.info …")
    auth_info = api_call(session, "auth.info", {})
    user = auth_info.get("data", {}).get("user", {})
    print(f"✅ Connecté en tant que : {user.get('name')} ({user.get('email')})")

    # 1) Récupérer les collections (pour classer les fichiers proprement)
    print("\n📚 Récupération des collections…")
    coll_resp = api_call(session, "collections.list", {"limit": 100, "offset": 0})
    collections = coll_resp.get("data", []) or []
    print(f"  → {len(collections)} collection(s)")

    coll_by_id = {}
    for c in collections:
        coll_id = c.get("id")
        coll_name = c.get("name") or f"collection_{coll_id}"
        coll_by_id[coll_id] = safe_filename(coll_name)

    # 2) Récupérer tous les documents visibles pour ton compte
    print("\n📄 Récupération des documents…")
    all_docs = []
    offset = 0
    limit = 100

    while True:
        docs_resp = api_call(session, "documents.list", {
            "limit": limit,
            "offset": offset,
            "sort": "updatedAt",
            "direction": "DESC",
        })
        docs_batch = docs_resp.get("data", []) or []
        print(f"  → batch {offset} : {len(docs_batch)} docs")
        all_docs.extend(docs_batch)
        if len(docs_batch) < limit:
            break
        offset += limit

    print(f"\n✅ Total documents : {len(all_docs)}")

    # 3) Sauvegarde de chaque document en Markdown
    for doc in all_docs:
        try:
            title = doc.get("title") or "untitled"
            text = doc.get("text") or ""
            coll_id = doc.get("collectionId")
            coll_folder_name = coll_by_id.get(coll_id, "Sans_collection")

            collection_dir = base_path / coll_folder_name
            ensure_dir(collection_dir)

            filename = safe_filename(title) + ".md"
            file_path = collection_dir / filename

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(text)

            print(f"📝 {file_path}")

            # 4) Tentative de téléchargement des pièces jointes référencées
            attachment_urls = extract_attachment_paths(text)
            if attachment_urls:
                attach_dir = collection_dir / "_attachments"
                for url in attachment_urls:
                    fname = safe_filename(url.split("/")[-1] or "file")
                    dest = attach_dir / fname
                    download_attachment(session, OUTLINE_URL, url, dest)

        except Exception as e:
            print(f"❌ Erreur pour le doc {doc.get('id')}: {e}")


if __name__ == "__main__":
    main()