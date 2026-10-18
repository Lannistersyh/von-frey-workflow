import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from tools.private_archive import MAGIC, decrypt_directory, encrypt_directory


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.source.mkdir()
        (self.source / "nested").mkdir()
        (self.source / "notes.txt").write_text("Synthetic test content")
        (self.source / "nested/模拟.bin").write_bytes(bytes(range(256)))
        self.archive = self.base / "snapshot.aesgcm"
        self.key = self.base / "snapshot.key"

    def encrypt(self):
        return encrypt_directory(self.source, self.archive, self.key)

    def test_round_trip_with_manifest_and_private_key_permissions(self):
        meta = self.encrypt()
        self.assertEqual(meta["source_file_count"], 2)
        self.assertEqual(meta["ciphertext_sha256"], hashlib.sha256(self.archive.read_bytes()).hexdigest())
        result = decrypt_directory(self.archive, self.key, self.base / "restored")
        self.assertEqual(result["restored_files"], 2)
        self.assertEqual((self.base / "restored/nested/模拟.bin").read_bytes(), bytes(range(256)))
        self.assertEqual(self.key.stat().st_mode & 0o777, 0o600)

    def test_wrong_key_writes_no_restored_files(self):
        self.encrypt()
        wrong = self.base / "wrong.key"
        wrong.write_bytes(os.urandom(32))
        destination = self.base / "restored"
        with self.assertRaises(InvalidTag):
            decrypt_directory(self.archive, wrong, destination)
        self.assertFalse(destination.exists())

    def test_tampered_ciphertext_is_rejected(self):
        self.encrypt()
        content = bytearray(self.archive.read_bytes())
        content[-1] ^= 1
        self.archive.write_bytes(content)
        with self.assertRaises(InvalidTag):
            decrypt_directory(self.archive, self.key, self.base / "restored")
        self.assertFalse((self.base / "restored").exists())

    def test_existing_key_archive_and_destination_are_protected(self):
        self.encrypt()
        with self.assertRaises(FileExistsError):
            self.encrypt()
        output = self.base / "restored"
        output.mkdir()
        (output / "keep.txt").write_text("keep")
        with self.assertRaises(FileExistsError):
            decrypt_directory(self.archive, self.key, output)
        self.assertEqual((output / "keep.txt").read_text(), "keep")

    def test_key_cannot_be_written_inside_source(self):
        with self.assertRaises(ValueError):
            encrypt_directory(self.source, self.archive, self.source / "bad.key")

    def test_even_authenticated_unsafe_tar_paths_are_rejected(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for name, data in [("manifest.json", b"{}"), ("../escape", b"bad")]:
                member = tarfile.TarInfo(name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        key, nonce = AESGCM.generate_key(bit_length=256), os.urandom(12)
        self.key.write_bytes(key)
        self.archive.write_bytes(MAGIC + nonce + AESGCM(key).encrypt(nonce, buffer.getvalue(), MAGIC))
        with self.assertRaises(ValueError):
            decrypt_directory(self.archive, self.key, self.base / "restored")
        self.assertFalse((self.base / "escape").exists())

    def test_published_ciphertext_matches_metadata(self):
        files = list((ROOT / "private").glob("*.aesgcm.json"))
        self.assertEqual(len(files), 1)
        metadata = json.loads(files[0].read_text())
        encrypted = (ROOT / "private" / metadata["ciphertext_file"]).read_bytes()
        self.assertEqual(hashlib.sha256(encrypted).hexdigest(), metadata["ciphertext_sha256"])
        self.assertEqual(len(encrypted), metadata["ciphertext_bytes"])
        self.assertFalse(metadata["key_in_repository"])


if __name__ == "__main__":
    unittest.main()
