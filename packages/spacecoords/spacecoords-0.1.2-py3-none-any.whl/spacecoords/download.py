import sys
import os
from pathlib import Path
import requests

NAIF_URL = "https://naif.jpl.nasa.gov/pub/naif/"

KERNEL_PATHS = {
    "planetary": "generic_kernels/spk/planets/",
}


def naif_kernel(
    kernel_path: str,
    output_file: Path,
    progress: bool = True,
    chunk_size: int = 8192,
):
    url = NAIF_URL + kernel_path
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = r.headers.get("content-length")
        downloaded = 0
        if total_length is None:
            with open(output_file, "wb") as fh:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    fh.write(chunk)
                    if progress:
                        downloaded += len(chunk)
                        sys.stdout.write(f"{downloaded / 1024:.1f} KB")
                        sys.stdout.flush()
            if progress:
                print()
        else:
            total_length = int(total_length)
            prog_width = min(os.get_terminal_size()[0] - 10, 100)
            with open(output_file, "wb") as fh:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if not chunk:
                        continue
                    fh.write(chunk)
                    if progress:
                        downloaded += len(chunk)
                        done = int(prog_width * downloaded / total_length)
                        sys.stdout.write(
                            f"\r[{'=' * done}{' ' * (prog_width - done)}] "
                            f"{downloaded / 1024:.1f} KB / {total_length / 1024:.1f} KB"
                        )
                        sys.stdout.flush()
            if progress:
                print()


def naif_kernel_main(args):
    naif_kernel(
        kernel_path=KERNEL_PATHS[args.kernel_type] + args.kernel_name,
        output_file=args.output_file,
        progress=True,
    )
