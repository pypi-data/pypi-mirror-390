from __future__ import annotations

from pathlib import Path


def save_prompt_version(instance_name: str, rendered_text: str, *, root: Path | None = None) -> Path:
	"""
	Save a rendered prompt under `.prompt/<instance_name>/<instance_name>__prompt__vN.txt`.
	Windows-safe file names. Returns the saved file path.
	"""
	name = instance_name.strip()
	if not name:
		raise ValueError("instance_name cannot be empty")

	base = root if root is not None else Path.cwd()
	target_dir = base / ".prompt" / name
	target_dir.mkdir(parents=True, exist_ok=True)

	prefix = f"{name}__prompt__v"
	existing = sorted([p for p in target_dir.glob(f"{name}__prompt__v*.txt") if p.is_file()])
	next_version = 1
	if existing:
		last = existing[-1].stem
		try:
			v_str = last.split("__prompt__v", 1)[1]
			next_version = int(v_str) + 1
		except Exception:
			next_version = 1

	target = target_dir / f"{prefix}{next_version}.txt"
	target.write_text(rendered_text, encoding="utf-8")
	return target


