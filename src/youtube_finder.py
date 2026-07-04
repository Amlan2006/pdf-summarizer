from urllib.parse import quote_plus

import requests


YOUTUBE_SEARCH_ENDPOINT = "https://www.googleapis.com/youtube/v3/search"


def youtube_search_url(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def recommend_videos(
    topics: list[dict],
    api_key: str | None,
    videos_per_topic: int = 2,
) -> list[dict]:
    recommendations = []

    for topic in topics:
        query = topic.get("search_query") or f"{topic['topic']} explained"

        if not api_key:
            recommendations.append(
                {
                    "topic": topic["topic"],
                    "why_relevant": topic.get("why_relevant", ""),
                    "title": "Open YouTube search",
                    "channel": "",
                    "url": youtube_search_url(query),
                    "thumbnail": "",
                }
            )
            continue

        recommendations.extend(
            _search_youtube(
                query=query,
                topic=topic,
                api_key=api_key,
                max_results=videos_per_topic,
            )
        )

    return recommendations


def _search_youtube(query: str, topic: dict, api_key: str, max_results: int) -> list[dict]:
    params = {
        "part": "snippet",
        "q": query,
        "key": api_key,
        "type": "video",
        "maxResults": max_results,
        "safeSearch": "moderate",
        "videoEmbeddable": "true",
        "relevanceLanguage": "en",
    }
    response = requests.get(YOUTUBE_SEARCH_ENDPOINT, params=params, timeout=10)
    response.raise_for_status()

    recommendations = []
    for item in response.json().get("items", []):
        video_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        thumbnails = snippet.get("thumbnails", {})
        thumbnail = thumbnails.get("medium") or thumbnails.get("default") or {}

        if not video_id:
            continue

        recommendations.append(
            {
                "topic": topic["topic"],
                "why_relevant": topic.get("why_relevant", ""),
                "title": snippet.get("title", "YouTube video"),
                "channel": snippet.get("channelTitle", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": thumbnail.get("url", ""),
            }
        )

    return recommendations
