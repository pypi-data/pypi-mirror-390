import argparse


def main():
    import spacecoords as sc

    parser = argparse.ArgumentParser(description="Download files")
    subparsers = parser.add_subparsers(help="Available download interfaces", dest="command")

    naif_parser = subparsers.add_parser("naif_kernel", help="Download NAIF Kernels")
    naif_parser.add_argument(
        "kernel_type",
        choices=list(sc.download.KERNEL_PATHS.keys()),
        help="Type of kernel (determines location on server)",
    )
    naif_parser.add_argument("kernel_name", help="Kernel filename")
    naif_parser.add_argument("output_file", help="Path to output file")

    args = parser.parse_args()

    if args.command == "naif_kernel":
        sc.download.naif_kernel_main(args)
