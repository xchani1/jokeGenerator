"""Pre-generate a pool of jokes per topic into docs/jokes.json for the GitHub Pages site.

Usage: python generate_jokes.py [--per-topic 6]
Credentials come from creds.json, or the GCP_CREDENTIALS env var (GitHub secret).
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from google.genai import types

from main import TOPICS, make_client

OUT_PATH = Path(__file__).with_name("docs") / "jokes.json"


def jokes_for_topic(client, topic, count, model="gemini-2.5-flash"):
    response = client.models.generate_content(
        model=model,
        contents=f"Write {count} different short, original jokes about data analytics, "
                 f"themed on {topic}. Return a JSON array of {count} strings.",
        config=types.GenerateContentConfig(
            temperature=1.2,
            max_output_tokens=2000,
            response_mime_type="application/json",
            response_schema=list[str],
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return [j.strip() for j in json.loads(response.text) if j.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-topic", type=int, default=6)
    args = parser.parse_args()

    client = make_client()
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda t: jokes_for_topic(client, t, args.per_topic), TOPICS))
    jokes = dict(zip(TOPICS, results))

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(jokes, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {sum(map(len, results))} jokes for {len(jokes)} topics to {OUT_PATH}")


if __name__ == "__main__":
    main()
