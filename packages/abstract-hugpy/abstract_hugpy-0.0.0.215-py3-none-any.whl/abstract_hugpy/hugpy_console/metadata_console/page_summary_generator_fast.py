#!/usr/bin/env python3
"""
Fast Page Summary Generator (Env-Aware + Auto-Detect)
-----------------------------------------------------
Summarizes each PDF page text (~150 words, SEO-optimized),
compares new summaries with existing ones via DeepZero,
and updates manifest.json.

It auto-detects a working base directory based on:
    - Environment variables
    - Host-specific defaults
    - Fallback to CWD

Usage
-----
    from abstract_hugpy.hugpy_console.metadata_console.page_summary_generator_fast import run_page_summary_generator_fast
    run_page_summary_generator_fast()              # auto-detects base_dir
    run_page_summary_generator_fast("/custom/path")
"""


from .imports import *
from .manifest_utils import *
from .metadata_utils import scan_matadata_from_pdf_dirs
from .summary_judge import SummaryJudge

N_PROCESSES    = max(1, os.cpu_count() // 2)
judge          = SummaryJudge()

# ------------------------------------------------------------------
# Environment detection helpers
# ------------------------------------------------------------------
def get_env_value_or_none(key: str, path: str | None = None) -> str | None:
    """Pull a variable from env file or system environment."""
    try:
        val = get_env_value(key=key, path=path)
        return val if val and os.path.exists(val) else None
    except Exception:
        return None

def get_env_basedirs(env_path: str | None = None) -> list[Path]:
    """Return list of candidate base paths in order of preference."""
    prod   = get_env_value_or_none(BASE_DIR_KEY_PROD, env_path)
    server = get_env_value_or_none(BASE_DIR_KEY_SERVER, env_path)
    local  = get_env_value_or_none(BASE_DIR_KEY_LOCAL, env_path)
    return [p for p in [prod, server, local] if p]

def detect_base_dir(env_path: str | None = None) -> Path:
    """Choose a valid base directory using environment + defaults."""
    for path_str in get_env_basedirs(env_path):
        if os.path.exists(path_str):
            return path_str

    # Fallback defaults
    home = str(Path.home())
    cwd = str(Path.cwd())
    candidates = [
        "/mnt/24T/media/thedailydialectics/pdfs",
        "/var/www/media/thedailydialectics/pdfs",
        os.path.join(cwd,"Documents/pythonTools/data/pdfs"),
        cwd,
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return Path.cwd()

# ------------------------------------------------------------------
# Core utilities
# ------------------------------------------------------------------
def truncate_text(text: str, max_chars: int = CHARS_LIMIT) -> str:
    return text[:max_chars]

def summarize_text(text: str) -> str:
    try:
        summary = get_summarizer_summary(
            text=text,
            summary_mode="medium",
            max_chunk_tokens=200,
            summary_words=SUMMARY_WORDS,
        ).strip()
        if len(summary.split()) < 30:
            summary += " (short)"
        return summary
    except Exception as e:
        return f"[Summarizer error: {e}]"

def build_seo_json(page_id: str, summary: str,pdf_dir:str) -> dict:
    summary_spl = summary.split()
    desc = " ".join(summary_spl[:SUMMARY_WORDS])
    title = get_pdf_title(pdf_dir)
    title_page_no = f"{title} {page_id}"
    title_page_no_text = f"{title} Page {page_id}"
    return {
        "page_id": page_id,
        "title": f"{title_page_no} | {title_page_no_text} Summary",
        "description": desc,
        "alt":  f"{title_page_no_text} abstract",
        "summary": summary,
        "length_words": len(summary_spl),
    }

# ------------------------------------------------------------------
# Page processing
# ------------------------------------------------------------------
def process_page(txt_path):
    pdf_dir = get_pdf_dir(txt_path)
    txt_parts = get_file_parts(txt_path)
    summary_dir_parts = get_file_parts(pdf_dir)
    out_json = get_manifest_path(pdf_dir)
    summary_filename = summary_dir_parts.get('filename')
    summary_basename = summary_dir_parts.get('basename')
    
    os.makedirs(pdf_dir,exist_ok=True)
    out_json = get_manifest_path
    out_txt  = os.path.join(pdf_dir,f"{summary_filename}.txt")
    text = read_from_file(txt_path)
    text = truncate_text(text)
    text = clean_text(text)
    if len(text) < 40:
        return None

    new_summary = summarize_text(text)
    seo_json    = build_seo_json(basename, new_summary)

    # Compare or create
    if os.path.exists(out_json):
        existing = safe_load_json(out_json)
        old_summary = existing.get("summary") or existing.get("text") or ""
        best_summary, best_score, other_score = judge.compare(text, new_summary, old_summary)
        if best_summary == new_summary:
            
            write_to_file(contents=new_summary,file_path=out_txt)
            action = "replaced"
        else:
            action = "kept_old"
    else:
        safe_dump_to_json(data=seo_json,file_path=out_json)
        write_to_file(contents=new_summary,file_path=out_txt)
        best_score, other_score, action = 1.0, 0.0, "new"

    return {"id": txt_parts.get('filename'), "action": action,
            "best_score": best_score, "other_score": other_score}


# ------------------------------------------------------------------
# Directory processing
# ------------------------------------------------------------------
# ------------------------ Directory Worker -----------------------
def _init_worker():
    """Initializer for each subprocess in the pool."""
    import os
    # Disable tokenizer thread parallelism (avoids fork warnings / deadlocks)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

def process_pdf_dir(pdf_dir):
    pdf_dir = get_pdf_dir(pdf_dir)
    path_parts = get_file_parts(pdf_dir)
    basename = path_parts.get('basename')
    txt_files = get_files_and_dirs(str(pdf_dir),allowed_exts=['.txt'])[-1]
    if not txt_files:
        scan_matadata_from_pdf_dirs([pdf_dir],output_dir=pdf_dir)
        txt_files = get_files_and_dirs(str(pdf_dir),allowed_exts=['.txt'])[-1]
        if not txt_files:
            return
    
    print(f"\n📄 Processing {basename} ({len(txt_files)} pages)...")
    results = []
    title = get_pdf_title(pdf_dir)

    ctx = safe_mp_context()
    with ctx.Pool(processes=N_PROCESSES, initializer=_init_worker) as pool:
        for res in tqdm(pool.imap_unordered(process_page, txt_files),
                        total=len(txt_files), desc=basename):
            if res:
                results.append(res)
    update_manifest(pdf_dir, results)
    print(f"✅ Updated manifest for {basename}")

# ------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------
def run_page_summary_generator_fast(base_dir: str | Path = None, env_path: str | None = None):
    base_dir = base_dir if base_dir else detect_base_dir(env_path)
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Base directory not found: {base_dir}")

    pdf_dirs = [p for p in get_files_and_dirs(str(base_dir),allowed_exts=['.pdf'])[-1] if '_page_' not in p]
    if not pdf_dirs:
        print(f"⚠️ No subdirectories found in {base_dir}")
        return

    print(f"🏗 Using base directory: {base_dir}")
    for item in pdf_dirs:
        process_pdf_dir(item)
    print("🏁 All summaries complete.")
