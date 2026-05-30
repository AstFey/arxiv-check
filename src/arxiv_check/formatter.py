from typing import Iterable

from .models import Paper


def format_paper(paper: Paper, index: int | None = None) -> str:
    published = paper.published_at.isoformat() if paper.published_at else "unknown"
    matches = ", ".join(paper.matched_keywords) if paper.matched_keywords else "none"
    title = f"{index}. {paper.title}" if index is not None else paper.title
    return (
        f"{title}\n"
        f"Authors: {paper.authors or 'unknown'}\n"
        f"Published: {published}\n"
        f"Matched keywords: {matches}\n"
        f"{paper.link}"
    )


def format_paper_list(papers: Iterable[Paper], numbered: bool = False) -> str:
    papers = list(papers)
    if not papers:
        return "No new matching papers found."
    if numbered:
        return "\n\n".join(format_paper(paper, index) for index, paper in enumerate(papers, start=1))
    return "\n\n".join(format_paper(paper) for paper in papers)
