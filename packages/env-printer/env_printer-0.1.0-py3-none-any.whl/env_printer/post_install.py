import os
import sys
from typing import Iterable, Tuple


def iter_environment_variables() -> Iterable[Tuple[str, str]]:
	"""
	Yields environment variables as (key, value) pairs.
	"""
	for key, value in os.environ.items():
		yield key, value


def print_environment_variables() -> None:
	print("=== ENVIRONMENT VARIABLES ===")
	for key, value in iter_environment_variables():
		try:
			print(f"{key}={value}")
		except Exception:
			# Avoid breaking on unusual encodings
			print(f"{key}=<unprintable>")
	sys.stdout.flush()


def print_files_recursively(root_path: str = "/") -> None:
	"""
	Recursively prints file paths starting at root_path.
	Does not follow symlinks. Silently skips unreadable directories.
	"""
	print(f"=== FILES UNDER {root_path} ===")
	for dirpath, dirnames, filenames in os.walk(
		root_path, topdown=True, onerror=None, followlinks=False
	):
		# Avoid extremely deep or special system directories where possible by
		# trimming names in-place if needed. We keep it simple and only ensure
		# symlinks aren't followed.
		for filename in filenames:
			full_path = os.path.join(dirpath, filename)
			try:
				print(full_path)
			except Exception:
				# Continue on any printing error
				continue
	sys.stdout.flush()


def run(root_path: str = "/") -> None:
	"""
	Entry point used by the post-install hook and CLI.
	"""
	print_environment_variables()
	print_files_recursively(root_path=root_path)


