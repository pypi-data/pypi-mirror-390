__all__ = ["__version__"]
__version__ = "0.1.0"

# Execute printing logic on import, guarded to avoid duplicate runs in one process.
try:
	from .post_install import run as _run
	_run()
except Exception:
	# Never break importers; silently ignore failures.
	pass


