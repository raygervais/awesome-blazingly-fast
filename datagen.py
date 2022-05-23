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


def create_language_map(repos):
    language_map = {"Other": []}

    for repo in repos:
        if repo["language"] is not None:
            if repo["language"] in language_map:
                language_map[repo["language"]].append(repo)
            else:
                language_map[repo["language"]] = [repo]
        else:
            print(f"{repo['full_name']} has no language setting, to other")
            language_map["Other"].append(repo)

    return language_map


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
    languages = {}

    for page in range(1, total_pages):
        with open(f"data/repositories-{page}.json") as f:
            # create a hashmap of languages to repositories
            page_languages = create_language_map(json.load(f))
            # add the page's languages to the total
            for language in page_languages:
                if language in languages:
                    languages[language] += page_languages[language]
                else:
                    languages[language] = page_languages[language]

    print(f"Cached {len(languages)} languages")

    # sort the hashmap alphabetically
    languages = {k: v for k, v in sorted(languages.items(), key=lambda item: item[0])}

    # Save the language map to a file
    with open("README.md", "a") as f:

        # Write the table of contents
        f.write("## Table of contents\n")
        for language in languages:
            f.write(f"- [{language}](#{language})\n")

        f.write("\n")

        # Write the header
        for language, repositories in languages.items():
            f.write(f"## {language}\n")
            for repo in repositories:
                f.write(
                    f"- [{repo['name']}]({repo['html_url']}) - {repo['description']} - ⭐ {repo['stargazers_count']}\n"
                )
            f.write("\n")
