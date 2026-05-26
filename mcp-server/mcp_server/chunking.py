from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    source_id: str
    chunk_id: str
    title: str
    section: str
    text: str
    file_path: str


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "document"


def chunk_markdown(path: Path, max_chars: int = 1200) -> list[DocumentChunk]:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    title = path.stem.replace("_", " ").title()

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    source_id = slugify(path.stem)
    sections: list[tuple[str, list[str]]] = []
    current_section = title
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current_lines:
                sections.append((current_section, current_lines))
            current_section = line[3:].strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_section, current_lines))

    chunks: list[DocumentChunk] = []
    chunk_number = 0

    for section, section_lines in sections:
        section_text = "\n".join(section_lines).strip()
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", section_text) if p.strip()]
        buffer = ""

        for paragraph in paragraphs:
            candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
            if len(candidate) <= max_chars:
                buffer = candidate
                continue

            if buffer:
                chunk_number += 1
                chunk_id = f"chunk-{chunk_number:03d}"
                chunks.append(
                    DocumentChunk(
                        id=f"{source_id}:{chunk_id}",
                        source_id=source_id,
                        chunk_id=chunk_id,
                        title=title,
                        section=section,
                        text=buffer,
                        file_path=str(path),
                    )
                )
            buffer = paragraph

        if buffer:
            chunk_number += 1
            chunk_id = f"chunk-{chunk_number:03d}"
            chunks.append(
                DocumentChunk(
                    id=f"{source_id}:{chunk_id}",
                    source_id=source_id,
                    chunk_id=chunk_id,
                    title=title,
                    section=section,
                    text=buffer,
                    file_path=str(path),
                )
            )

    return chunks

