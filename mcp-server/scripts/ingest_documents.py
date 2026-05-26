from __future__ import annotations

from mcp_server.knowledge_base import KnowledgeBase


def main() -> None:
    result = KnowledgeBase().rebuild_index()
    print("Knowledge index rebuilt")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

