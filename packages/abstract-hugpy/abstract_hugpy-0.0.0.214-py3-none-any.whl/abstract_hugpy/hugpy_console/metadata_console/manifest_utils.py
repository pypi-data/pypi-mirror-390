from .imports import *
from .summary_judge import detect_pdf_title
def get_pdf_path(pdf_path):
    pdf_path = str(pdf_path)
    if os.path.isdir(pdf_path):
        dirlist = os.listdir(pdf_path)
        pdfs = [os.path.join(pdf_path,item) for item in dirlist if item and item.endswith('.pdf') and '_page_' not in item ]
        if pdfs and len(pdfs)>0:
            pdf_path = pdfs[0]
    if pdf_path and os.path.isfile(pdf_path) and pdf_path.endswith('.pdf'):
        return pdf_path
def get_pdf_dir(pdf_dir):
    pdf_dir = str(pdf_dir)
    if os.path.isdir(pdf_dir):
        dirlist = os.listdir(pdf_dir)
        pdfs = [os.path.join(pdf_dir,item) for item in dirlist if item and item.endswith('.pdf') and '_page_' not in item ]
        if pdfs and len(pdfs)>0:
            return pdf_dir
    if pdf_dir and os.path.isfile(pdf_dir) and pdf_dir.endswith('.pdf'):
        return os.path.dirname(pdf_dir)
    if pdf_dir and os.path.isfile(pdf_dir) and (pdf_dir.endswith('.txt') or pdf_dir.endswith('.png')):
        file_parts = get_file_parts(pdf_dir)
        return file_parts.get('parent_dirname')    
def get_manifest_path(pdf_dir):
    pdf_dir = str(pdf_dir)
    pdf_dir = get_pdf_dir(pdf_dir)
    manifest_path = os.path.join(str(pdf_dir),MANIFEST_NAME)
    return manifest_path
def load_manifest(pdf_dir=None,manifest_path=None):
    pdf_dir = str(pdf_dir) if pdf_dir else pdf_dir
    manifest_path = str(manifest_path) if manifest_path else manifest_path
    if pdf_dir==None and manifest_path==None:
        return {}
    manifest_path = manifest_path or get_manifest_path(pdf_dir)
    if not os.path.isfile(manifest_path):
        safe_dump_to_json(data={},file_path=manifest_path)
    manifest = safe_load_json(manifest_path)
    return manifest
def save_manifest_data(data=None,pdf_dir=None,override=False):
    pdf_dir = str(pdf_dir) if pdf_dir else pdf_dir
    manifest_path = get_manifest_path(pdf_dir)
    if data in [None,{}] and override == True:
        data = load_manifest(pdf_dir,manifest_path=manifest_path)
    else:
        data = {}
    safe_dump_to_json(data=data,file_path=manifest_path)

def get_title_retrun_manifest(pdf_dir):
    pdf_path = get_pdf_path(pdf_dir)
    manifest = load_manifest(pdf_dir)
    title = manifest.get('title')
    if not title:
        manifest['title'] = detect_pdf_title(pdf_path)
        save_manifest_data(data=manifest,pdf_dir=pdf_dir)
    return manifest
def get_pdf_title(pdf_dir):
    pdf_dir = str(pdf_dir)
    manifest = get_title_retrun_manifest(pdf_dir)
    return manifest.get('title')
# ------------------------------------------------------------------
# Manifest update
# ------------------------------------------------------------------
def update_manifest(pdf_dir, new_entries: list):
    manifest = get_title_retrun_manifest(pdf_dir)
    manifest.setdefault("pages", {})
    for entry in new_entries:
        if not entry or "error" in entry:
            continue
        manifest["pages"][entry["id"]] = entry.get("data", {})
    save_manifest_data(data=manifest,pdf_dir=pdf_dir)

