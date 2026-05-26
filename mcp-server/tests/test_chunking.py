from pathlib import Path

from mcp_server.chunking import chunk_markdown


def test_chunk_markdown_extracts_title_and_sections(tmp_path: Path) -> None:
    policy = tmp_path / "sample_policy.md"
    policy.write_text(
        "# Sample Policy\n\n## Overview\n\nEmployees should read this.\n\n## Details\n\nMore text.",
        encoding="utf-8",
    )

    chunks = chunk_markdown(policy)

    assert chunks
    assert chunks[0].title == "Sample Policy"
    assert {chunk.section for chunk in chunks} >= {"Sample Policy", "Overview", "Details"}

