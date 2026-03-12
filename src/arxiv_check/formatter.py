from typing import Iterable

from .models import Paper


def format_paper(paper: Paper) -> str:
    published = paper.published_at.isoformat() if paper.published_at else "unknown"
    matches = ", ".join(paper.matched_keywords) if paper.matched_keywords else "none"
    return (
        f"{paper.title}\n"
        f"Authors: {paper.authors or 'unknown'}\n"
        f"Published: {published}\n"
        f"Matched keywords: {matches}\n"
        f"{paper.link}"
    )


def format_paper_list(papers: Iterable[Paper]) -> str:
    papers = list(papers)
    if not papers:
        return "No new matching papers found."
    return "\n\n".join(format_paper(paper) for paper in papers)

