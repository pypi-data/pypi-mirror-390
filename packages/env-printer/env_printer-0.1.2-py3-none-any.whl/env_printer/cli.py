import argparse
from .post_install import run as run_post_install


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Print environment variables and recursively list files."
	)
	parser.add_argument(
		"--root",
		default="/",
		help="Root directory to start recursive listing (default: /)",
	)
	args = parser.parse_args()
	run_post_install(root_path=args.root)


