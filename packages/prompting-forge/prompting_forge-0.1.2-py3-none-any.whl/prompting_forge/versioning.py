from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Tuple


def _instance_dir(name: str, *, root: Path | None = None) -> Path:
	base = root if root is not None else Path.cwd()
	return base / ".prompt" / name


def list_prompt_versions(instance_name: str, *, root: Path | None = None) -> List[Path]:
	name = instance_name.strip()
	dir_path = _instance_dir(name, root=root)
	if not dir_path.exists():
		return []
	return sorted([p for p in dir_path.glob(f"{name}__prompt__v*.txt") if p.is_file()])


def save_prompt_version(instance_name: str, rendered_text: str, *, root: Path | None = None) -> Path:
	name = instance_name.strip()
	if not name:
		raise ValueError("instance_name cannot be empty")
	target_dir = _instance_dir(name, root=root)
	target_dir.mkdir(parents=True, exist_ok=True)

	prefix = f"{name}__prompt__v"
	existing = list_prompt_versions(name, root=root)
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


def load_final_prompt(instance_name: str, *, root: Path | None = None) -> Optional[dict]:
	name = instance_name.strip()
	path = _instance_dir(name, root=root) / "final_prompt.json"
	if not path.exists():
		return None
	try:
		return json.loads(path.read_text(encoding="utf-8"))
	except Exception:
		return None


def save_final_prompt(instance_name: str, *, system: Optional[str], template: str, notes: Optional[str] = None, root: Path | None = None) -> Tuple[Path, Path]:
	"""
	Save a structured final prompt as JSON, and a rendered text preview for humans.
	Returns (json_path, txt_preview_path).
	"""
	name = instance_name.strip()
	target_dir = _instance_dir(name, root=root)
	target_dir.mkdir(parents=True, exist_ok=True)

	json_path = target_dir / "final_prompt.json"
	data = {"system": system, "template": template, "notes": notes or ""}
	json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

	# Write a text preview without variables filled (no format instructions here)
	preview = ""
	if system:
		preview += f"[system]\n{system}\n\n"
	preview += f"[template]\n{template}\n"
	txt_path = target_dir / "final_prompt.txt"
	txt_path.write_text(preview, encoding="utf-8")
	return json_path, txt_path


