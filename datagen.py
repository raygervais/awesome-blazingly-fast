#!/usr/bin/python3

import json
import os
from urllib import parse, request

DATA_PATH = os.path.join(os.getcwd(), "data")
API_URL = "https://api.github.com/search/repositories?"


def get_repositories(search_term: str) -> list:
    # Build the query string
    query_string = parse.urlencode({"q": search_term, "per_page": 100})

    # Make the request
    response = request.urlopen(f"{API_URL}{query_string}")

    # Parse the response
    return json.loads(response.read().decode("utf-8"))


# get the repositories for the search term paginated by 100
def get_repositories_paginated(search_term: str, page: int) -> list:
    # Build the query string
    query_string = parse.urlencode({"q": search_term, "page": page, "per_page": 100})

    # Make the request
    response = request.urlopen(f"{API_URL}{query_string}")

    # Parse the response
    return json.loads(response.read().decode("utf-8"))["items"]


def get_and_cache_repositories(get_repositories_paginated, total_pages, last_page):
    for page in range(last_page, total_pages):
        print(f"confirming page {page} is already cached")

        # Check if page already exists
        if not os.path.exists(f"data/repositories-{page}.json"):
            # Get repositories
            repos = get_repositories_paginated("blazingly fast", page)
            print(repos)

            # Save to file
            with open(f"data/repositories-{page}.json", "w") as f:
                json.dump(repos, f)

            print(f"Saved page {page}")

        else:
            print(f"Page {page} already exists")


if __name__ == "__main__":
    # Determine initial amount of repositories
    repos = get_repositories("blazingly fast")
    print(f"Found {repos['total_count']} repositories")

    # Determine amount of repositories with pagination
    # total_pages = int(repos["total_count"] % 100)

    # So we can use without authentication
    total_pages = 10
    last_page = 0

    # Create the data directory if it doesn't exist
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    else:
        # Determine where to start
        last_page = len(os.listdir(DATA_PATH))

    get_and_cache_repositories(get_repositories_paginated, total_pages, last_page)

    # Parse the data files
    repos = []
    for page in range(1, total_pages):
        with open(f"data/repositories-{page}.json") as f:
            repos += json.load(f)

    print(f"Cached {len(repos)} repositories")

    # Sort the repositories by stars
    repos.sort(key=lambda r: r["stargazers_count"], reverse=True)

    # Print the first 10 repositories
    with open("README.md", "a") as f:
        for repo in repos:
            f.write(
                f"- [{repo['name']}]({repo['html_url']}) - {repo['description']} - ⭐ {repo['stargazers_count']}\n"
            )
