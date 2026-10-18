# Research data protection and recovery

## What is available in the repository

Plaintext content presents the workflow, a curated copy of the entry panel, the existing preview module, and synthetic examples. The panel's original batch-derived demo was replaced with synthetic records, and its browser database names were changed to avoid loading the original panel's drafts.

`private/` contains an encrypted snapshot of the complete original project. Its protected contents include original data, spreadsheets, treatment/group identifiers, result tables, historical exports, all original scripts, research notes, and reference files. A filename and SHA-256 manifest is stored **inside** the encrypted archive. Public metadata describes only the format, ciphertext checksum, byte size, and file count.

Operating-system metadata (`.DS_Store`) and Python bytecode caches are not part of the research snapshot. The original working files remain untouched by publication.

## Encryption format

`tools/private_archive.py` uses the `cryptography` library's AES-256-GCM implementation, a random 32-byte key, and a fresh 12-byte nonce. The versioned file header is authenticated as additional data. The encrypted payload is a gzip-compressed tar containing the source files and their SHA-256 manifest. Decryption authenticates the whole payload before any restored file is written; manifest verification is also performed before extraction.

The key is generated into a separate owner-controlled location with restrictive permissions. **The repository does not contain the key or a password.** Neither the key contents nor an unencrypted source manifest should be committed. Git ignore rules are an additional guard, not encryption.

## Recover the original project

Install the dependency in a virtual environment, then supply the separately stored key:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/private_archive.py decrypt \
  private/project-snapshot-2026-10-18.tar.gz.aesgcm \
  --key-file /secure/path/to/project-snapshot-2026-10-18.key \
  --output /secure/path/to/restored-von-frey-project
```

Use a new or empty destination directory. The recovery utility rejects invalid authentication tags, unsafe archive paths, unexpected members, and file-hash mismatches. It refuses to overwrite an existing nonempty recovery directory.

Keep an offline backup of the key in a separate secure location. A ciphertext backup without its key cannot restore the project. Sharing the key grants access to the entire snapshot, including research data and archived third-party files; share it only with intended recipients under the applicable permissions.

## Future updates

Use `encrypt` to produce a new dated snapshot and a new key outside the repository. The command refuses to overwrite an existing archive or key. Verify recovery before uploading the ciphertext. Review source code, embedded examples, generated HTML, and commit history for experimental records as well as ordinary secret patterns.

Keep real study exports out of `examples/`; that directory is reserved for synthetic fixtures. The panel itself stores data locally, while uploading a CSV to the linked external calculator is an explicit separate action.

## 中文恢复说明

完整原始科研项目已加密，密钥在仓库外单独保存；仓库里只有密文和校验信息。使用上面的 `decrypt` 命令，指定密钥和新的恢复目录，即可在完整性验证通过后还原原始目录结构。不要把密钥、原始清单或解密后的真实数据提交到 Git。请另外离线备份密钥；密钥丢失后无法从密文恢复项目。
