#!/usr/bin/env python3
"""Download and verify Zenodo MCG GPR dataset."""

from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
CNS_ROOT = BENCH_ROOT.parents[0]
ASSET_DIR = CNS_ROOT / "external_assets" / "zenodo_mcg_gpr_14270869"
ARCHIVE = ASSET_DIR / "MCG_GPR_dataset.zip"
EXTRACT_DIR = ASSET_DIR / "extracted"
OUT_DIR = BENCH_ROOT / "reports" / "zenodo_mcg_gpr_download_20260811"

RECORD_ID = "14270869"
DOI = "10.5281/zenodo.14270869"
FILE_NAME = "MCG_GPR_dataset.zip"
EXPECTED_MD5 = "b43fd0e8840930f36b1003368736f936"
DOWNLOAD_URL = "https://zenodo.org/api/records/14270869/files/MCG_GPR_dataset.zip/content"


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists() and md5(ARCHIVE) == EXPECTED_MD5:
        return
    tmp = ARCHIVE.with_suffix(".zip.part")
    if tmp.exists():
        tmp.unlink()
    with urllib.request.urlopen(DOWNLOAD_URL, timeout=120) as response, tmp.open("wb") as handle:
        shutil.copyfileobj(response, handle, length=1024 * 1024)
    tmp_md5 = md5(tmp)
    if tmp_md5 != EXPECTED_MD5:
        raise RuntimeError(f"MD5 mismatch for {tmp}: observed={tmp_md5} expected={EXPECTED_MD5}")
    tmp.replace(ARCHIVE)


def extract() -> dict[str, int]:
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    marker = EXTRACT_DIR / ".extract_complete_20260811"
    if marker.exists():
        return count_extracted()
    with zipfile.ZipFile(ARCHIVE) as zf:
        zf.extractall(EXTRACT_DIR)
    marker.write_text("complete\n", encoding="utf-8")
    return count_extracted()


def count_extracted() -> dict[str, int]:
    files = [path for path in EXTRACT_DIR.rglob("*") if path.is_file()]
    image_suffixes = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    return {
        "extracted_file_count": len(files),
        "image_file_count": sum(path.suffix.lower() in image_suffixes for path in files),
        "mask_file_count": sum("mask" in path.name.lower() or "label" in path.name.lower() for path in files),
        "extracted_bytes": sum(path.stat().st_size for path in files),
    }


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Zenodo MCG GPR Download",
        "",
        f"Record: {RECORD_ID}",
        f"DOI: {DOI}",
        f"Archive: {ARCHIVE}",
        f"MD5 verified: {summary['md5_verified']}",
        f"Extracted files: {summary['extracted_file_count']}",
        f"Image files: {summary['image_file_count']}",
        "",
        "## Boundary",
        "",
        "This is a public Zenodo asset. It can support non-blind stress tests,",
        "but it cannot close the hard blind external validation gate.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    download()
    observed_md5 = md5(ARCHIVE)
    counts = extract()
    summary = {
        "run_id": "20260811_E37_zenodo_mcg_gpr_download",
        "record_id": RECORD_ID,
        "doi": DOI,
        "file_name": FILE_NAME,
        "download_url": DOWNLOAD_URL,
        "archive_path": str(ARCHIVE),
        "archive_size_bytes": ARCHIVE.stat().st_size,
        "expected_md5": EXPECTED_MD5,
        "observed_md5": observed_md5,
        "md5_verified": observed_md5 == EXPECTED_MD5,
        "extract_dir": str(EXTRACT_DIR),
        **counts,
        "blind_external_eligible": False,
        "status": "complete_public_mcg_gpr_download_verified_extracted" if observed_md5 == EXPECTED_MD5 else "fail_md5",
    }
    (OUT_DIR / "zenodo_mcg_gpr_download_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(OUT_DIR / "zenodo_mcg_gpr_download_summary.md", summary)
    print(json.dumps({"status": summary["status"], "image_file_count": summary["image_file_count"]}, ensure_ascii=False))
    if summary["status"].startswith("fail"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
