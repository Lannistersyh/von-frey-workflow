#!/usr/bin/env python3
"""Authenticated, owner-key encryption and verified recovery of a project folder."""

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import tarfile

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


MAGIC = b"VONFREY-ARCHIVE\x00\x01"
NONCE_LENGTH = 12
EXCLUDED_PARTS = {".git", "__pycache__", ".venv", "_github_release"}


def digest(content):
    return hashlib.sha256(content).hexdigest()


def safe_relative(name):
    relative = PurePosixPath(name)
    if (not name or not relative.parts or name == "." or relative.is_absolute() or ".." in relative.parts or
            "\\" in name or relative.as_posix() != name or ":" in name or
            any(ord(char) < 32 for char in name)):
        raise ValueError("Unsafe archive path")
    return relative


def write_new(path, content, mode=0o600):
    """Never overwrite a key, archive or recovered file."""
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode)
    with os.fdopen(fd, "wb") as handle:
        handle.write(content)


def encrypt_directory(source, output, key_file, source_manifest=None):
    source, output, key_file = Path(source).resolve(), Path(output).resolve(), Path(key_file).resolve()
    if not source.is_dir():
        raise ValueError("Source must be a directory")
    if key_file == output or source == key_file or source in key_file.parents:
        raise ValueError("Keep the decryption key outside the source project")
    if output.exists() or key_file.exists() or Path(str(output) + ".json").exists():
        raise FileExistsError("Archive or key exists; choose new paths")
    if source_manifest:
        entries = json.loads(Path(source_manifest).read_text(encoding="utf-8"))["files"]
    else:
        entries = {}
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            if (not path.is_file() or path.is_symlink() or
                    any(part in EXCLUDED_PARTS for part in relative.parts) or
                    path.name == ".DS_Store" or path.suffix == ".pyc" or path.resolve() == output):
                continue
            data = path.read_bytes()
            entries[relative.as_posix()] = {"size": len(data), "sha256": digest(data)}
    payloads = {}
    for name, metadata in entries.items():
        relative = safe_relative(name)
        path = source.joinpath(*relative.parts)
        if path.is_symlink() or source not in path.resolve().parents:
            raise ValueError("Source member is outside the project")
        data = path.read_bytes()
        if len(data) != metadata["size"] or digest(data) != metadata["sha256"]:
            raise ValueError("Source changed since the manifest was captured")
        payloads[name] = data
    if not payloads:
        raise ValueError("Source contains no files")
    manifest = {"format": "von-frey-source-manifest/v1", "files": entries}
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w:gz") as archive:
        items = {"manifest.json": json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode("utf-8")}
        items.update({"project/" + name: data for name, data in payloads.items()})
        for name, data in items.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o600
            info.mtime = 0
            archive.addfile(info, io.BytesIO(data))
    key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(NONCE_LENGTH)
    encrypted = MAGIC + nonce + AESGCM(key).encrypt(nonce, tar_buffer.getvalue(), MAGIC)
    write_new(key_file, key)
    write_new(output, encrypted)
    metadata = {
        "format": "von-frey-archive/v1", "cipher": "AES-256-GCM",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ciphertext_file": output.name, "ciphertext_sha256": digest(encrypted),
        "ciphertext_bytes": len(encrypted), "source_file_count": len(payloads),
        "key_in_repository": False,
    }
    write_new(Path(str(output) + ".json"),
              (json.dumps(metadata, indent=2) + "\n").encode("utf-8"), mode=0o644)
    return metadata


def verified_payloads(archive_file, key_file):
    content = Path(archive_file).read_bytes()
    key = Path(key_file).read_bytes()
    if len(key) != 32:
        raise ValueError("AES-256 key must be exactly 32 bytes")
    if not content.startswith(MAGIC) or len(content) < len(MAGIC) + NONCE_LENGTH + 16:
        raise ValueError("Unsupported or truncated encrypted archive")
    start = len(MAGIC)
    nonce = content[start:start + NONCE_LENGTH]
    plaintext = AESGCM(key).decrypt(nonce, content[start + NONCE_LENGTH:], MAGIC)
    # Authentication completes before parsing the archive or creating output files.
    with tarfile.open(fileobj=io.BytesIO(plaintext), mode="r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(set(names)) != len(names) or "manifest.json" not in names:
            raise ValueError("Duplicate members or missing manifest")
        for member in members:
            safe_relative(member.name)
            if not member.isfile():
                raise ValueError("Archive contains a non-regular member")
        manifest = json.loads(archive.extractfile("manifest.json").read())
        if manifest.get("format") != "von-frey-source-manifest/v1":
            raise ValueError("Unsupported manifest")
        entries = manifest["files"]
        if set(names) != {"manifest.json"} | {"project/" + name for name in entries}:
            raise ValueError("Archive members differ from the manifest")
        payloads = {}
        for name, metadata in entries.items():
            safe_relative(name)
            data = archive.extractfile("project/" + name).read()
            if len(data) != metadata["size"] or digest(data) != metadata["sha256"]:
                raise ValueError("Restored file does not match the source manifest")
            payloads[name] = data
    return payloads


def decrypt_directory(archive_file, key_file, destination):
    payloads = verified_payloads(archive_file, key_file)
    destination = Path(destination).resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise FileExistsError("Recovery destination must be new or empty")
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name, data in payloads.items():
        path = destination.joinpath(*safe_relative(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        write_new(path, data)
    return {"restored_files": len(payloads), "output": str(destination)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for action in ("encrypt", "decrypt"):
        command = commands.add_parser(action)
        command.add_argument("source", type=Path)
        command.add_argument("--key-file", required=True, type=Path)
        command.add_argument("--output", required=True, type=Path)
        if action == "encrypt":
            command.add_argument("--source-manifest", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "encrypt":
            result = encrypt_directory(args.source, args.output, args.key_file, args.source_manifest)
        else:
            result = decrypt_directory(args.source, args.key_file, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except InvalidTag:
        parser.error("Authentication failed: wrong key or modified ciphertext")
    except (ValueError, OSError, KeyError, tarfile.TarError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
