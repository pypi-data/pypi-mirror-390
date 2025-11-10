#!/usr/bin/env python3
import subprocess
import tarfile
from pathlib import Path
from getpass import getpass
import tempfile

def main():
    archive_path = Path("downloads.tar.gpg")
    if not archive_path.exists():
        print(f"Archive not found: {archive_path}")
        return

    password = getpass("Archive password: ")
    if not password:
        print("No password provided.")
        return

    output_dir = Path("./downloads_restored")
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = Path(tmpdir) / archive_path.with_suffix("").name  # remove .gpg suffix
        try:
            subprocess.run(
                [
                    "gpg",
                    "--batch",
                    "--yes",
                    "--passphrase", password,
                    "--decrypt",
                    "-o", str(tar_path),
                    str(archive_path),
                ],
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            print(f"gpg decryption failed: {exc}")
            return

        try:
            with tarfile.open(tar_path, "r") as tar:
                tar.extractall(path=output_dir)
        except tarfile.TarError as exc:
            print(f"Failed to extract tar archive: {exc}")
            return

    print(f"Decrypted contents extracted to: {output_dir.resolve()}")

if __name__ == "__main__":
    main()
