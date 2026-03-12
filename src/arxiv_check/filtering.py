from typing import Iterable, List

from .models import Paper


def match_keywords(paper: Paper, keywords: Iterable[str]) -> List[str]:
    haystack = f"{paper.title}\n{paper.summary}".lower()
    return [keyword for keyword in keywords if keyword.lower() in haystack]

