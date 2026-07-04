from src.youtube_finder import recommend_videos, youtube_search_url


def test_youtube_search_url_encodes_query():
    assert youtube_search_url("attention mechanism explained") == (
        "https://www.youtube.com/results?search_query=attention+mechanism+explained"
    )


def test_recommend_videos_without_api_key_returns_search_links():
    videos = recommend_videos(
        [{"topic": "Attention Mechanism", "why_relevant": "Central topic.", "search_query": "attention explained"}],
        api_key=None,
    )

    assert videos == [
        {
            "topic": "Attention Mechanism",
            "why_relevant": "Central topic.",
            "title": "Open YouTube search",
            "channel": "",
            "url": "https://www.youtube.com/results?search_query=attention+explained",
            "thumbnail": "",
        }
    ]
