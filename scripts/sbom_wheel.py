#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Write an SPDX 2.3 JSON SBOM for one wheel, or read it back against that wheel."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from email.parser import Parser
from pathlib import Path


def _metadata(wheel: Path) -> dict[str, str]:
    with zipfile.ZipFile(wheel) as archive:
        name = next(item for item in archive.namelist() if item.endswith(".dist-info/METADATA"))
        text = archive.read(name).decode("utf-8")
    message = Parser().parsestr(text)
    return {"name": message["Name"], "version": message["Version"], "license": message["License"] or ""}


def _files(wheel: Path) -> list[dict]:
    records = []
    with zipfile.ZipFile(wheel) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            digest = hashlib.sha256(archive.read(info.filename)).hexdigest()
            records.append(
                {
                    "fileName": info.filename,
                    "SPDXID": "SPDXRef-File-" + hashlib.sha256(info.filename.encode("utf-8")).hexdigest()[:12],
                    "checksums": [{"algorithm": "SHA256", "checksumValue": digest}],
                }
            )
    return records


def generate(wheel: Path, output: Path) -> None:
    meta = _metadata(wheel)
    document = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"{meta['name']}-{meta['version']}",
        "documentNamespace": f"https://github.com/szl-holdings/szl-sovereign-os/sbom/{meta['name']}-{meta['version']}",
        "packages": [
            {
                "SPDXID": "SPDXRef-Package",
                "name": meta["name"],
                "versionInfo": meta["version"],
                "licenseDeclared": meta["license"],
                "filesAnalyzed": True,
                "downloadLocation": "NOASSERTION",
            }
        ],
        "files": _files(wheel),
        "relationships": [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": "SPDXRef-Package",
            }
        ],
    }
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"sbom wrote {output} files={len(document['files'])} name={meta['name']} version={meta['version']}")


def readback(wheel: Path, document_path: Path) -> int:
    document = json.loads(document_path.read_text(encoding="utf-8"))
    meta = _metadata(wheel)
    package = document["packages"][0]
    if package["name"] != meta["name"] or package["versionInfo"] != meta["version"]:
        print("sbom readback failed: package name or version differs from wheel METADATA", file=sys.stderr)
        return 1
    if package["name"] != "szl-os" or package["versionInfo"] != "0.1.0":
        print("sbom readback failed: expected szl-os 0.1.0", file=sys.stderr)
        return 1
    expected = {item["fileName"]: item["checksums"][0]["checksumValue"] for item in document["files"]}
    actual = {item["fileName"]: item["checksums"][0]["checksumValue"] for item in _files(wheel)}
    if expected != actual:
        print("sbom readback failed: file hashes differ from the wheel", file=sys.stderr)
        return 1
    print(f"sbom readback ok files={len(actual)} name={package['name']} version={package['versionInfo']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--readback", type=Path)
    args = parser.parse_args()
    if args.readback:
        return readback(args.wheel, args.readback)
    if not args.out:
        print("pass --out or --readback", file=sys.stderr)
        return 2
    generate(args.wheel, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
