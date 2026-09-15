# SPDX-License-Identifier: AGPL-3.0-or-later
"""Bootstrapper for appending payload to executables."""

import struct
from pathlib import Path
from typing import Optional
import json


class Bootstrapper:
    """Appends payload data to executables."""
    
    MAGIC = b"CHIMERA"
    VERSION = 1

    def append_payload(self, exe_path: Path, payload_path: Path, output_path: Path) -> bool:
        """
        Append a payload (ZIP file) to an executable.
        
        The resulting file can be run as a normal executable,
        and the payload can be extracted at runtime.
        """
        if not exe_path.exists() or not payload_path.exists():
            return False

        try:
            exe_data = exe_path.read_bytes()
            payload_data = payload_path.read_bytes()

            with open(output_path, "wb") as f:
                # Write original executable
                f.write(exe_data)

                # Write magic bytes
                f.write(self.MAGIC)

                # Write version
                f.write(struct.pack("<I", self.VERSION))

                # Write payload length
                f.write(struct.pack("<Q", len(payload_data)))

                # Write payload
                f.write(payload_data)

            return True

        except Exception as e:
            print(f"Failed to append payload: {e}")
            return False

    def extract_payload(self, exe_path: Path, output_dir: Path) -> Optional[Path]:
        """Extract the payload from an executable."""
        if not exe_path.exists():
            return None

        try:
            with open(exe_path, "rb") as f:
                # Find the magic bytes
                data = f.read()
                magic_pos = data.rfind(self.MAGIC)
                if magic_pos == -1:
                    return None

                # Read version
                version = struct.unpack("<I", data[magic_pos + len(self.MAGIC):magic_pos + len(self.MAGIC) + 4])[0]

                # Read payload length
                payload_len = struct.unpack("<Q", data[magic_pos + len(self.MAGIC) + 4:magic_pos + len(self.MAGIC) + 12])[0]

                # Extract payload
                payload_start = magic_pos + len(self.MAGIC) + 12
                payload_data = data[payload_start:payload_start + payload_len]

                # Write to output
                output_dir.mkdir(parents=True, exist_ok=True)
                payload_path = output_dir / "payload.zip"
                payload_path.write_bytes(payload_data)

                return payload_path

        except Exception as e:
            print(f"Failed to extract payload: {e}")
            return None

    def has_payload(self, exe_path: Path) -> bool:
        """Check if an executable has an appended payload."""
        if not exe_path.exists():
            return False

        try:
            with open(exe_path, "rb") as f:
                # Read last 1024 bytes to check for magic
                f.seek(-1024, 2)
                tail = f.read()
                return self.MAGIC in tail
        except Exception:
            return False
