#!/usr/bin/python3

import json
import os
from urllib import parse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import base64

DATA_PATH = os.path.join(os.getcwd(), "data")
API_URL = "https://api.github.com/search/repositories?"
API_USERNAME = "raygervais"
API_TOKEN = ""
REQUEST_TIMEOUT = 20
LANGUAGES = [
    "Bash",
    "C",
    "C#",
    "C++",
    "Clojure",
    "CoffeeScript",
    "D",
    "Dart",
    "Elixir",
    "Elm",
    "Erlang",
    "F#",
    "Fortran",
    "Go",
    "Groovy",
    "Haskell",
    "Java",
    "JavaScript",
    "Julia",
    "Kotlin",
    "Lisp",
    "Lua",
    "Perl",
    "PHP",
    "PowerShell",
    "Python",
    "Ruby",
    "Rust",
    "Scala",
    "Shell",
    "Swift",
    "TypeScript",
    "Vala",
    "Wasm",
]

YEARS = [
    "2022",
    "2021",
    "2020",
    "2019",
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
    "2013",
]


def execute_request_with_auth(url: str):
    basic = base64.b64encode("{}:{}".format(API_USERNAME, API_TOKEN).encode("ascii"))

    headers = {"Authorization": f"Basic {basic.strip().decode('ascii')}"}
    try:
        with urlopen(
            Request(url, headers=headers), timeout=REQUEST_TIMEOUT
        ) as response:
            return response.read()
    except HTTPError as error:
        print(error.status, error.reason)
    except URLError as error:
        print(error.reason)
    except TimeoutError:
        print("Request timed out")


def get_repositories(search_term: str) -> list:
    # Build the query string
    query_string = parse.urlencode({"q": search_term, "per_page": 100})

    # Make the request
    response = execute_request_with_auth(f"{API_URL}{query_string}")

    if response == None:
        print("Github Ratelimit exceeded")
        exit(0)
    # Parse the response
    return json.loads(response.decode("utf-8"))


# get the repositories for the search term paginated by 100
def get_repositories_paginated(search_term: str, page: int) -> list:
    # Build the query string
    query_string = parse.urlencode(
        {
            "q": search_term,
            "page": page,
            "per_page": 100,
        }
    )

    # Make the request
    response = execute_request_with_auth(f"{API_URL}{query_string}")

    if response == None:
        return None

    # Parse the response
    return json.loads(response.decode("utf-8"))["items"]


# Get repositories which comply with search term and quarter


def get_and_cache_language_repositories(language: str, search_query: str) -> None:
    for year in YEARS:
        repos = {}
        path = f"{DATA_PATH}/language-repositories-{language}-{year}.json".strip()
        if not os.path.exists(path):
            print(
                f"Getting page for language {language} from {year} with query: 'created:>={year}-01-01..{int(year)+1}-01-01 language:{language} {search_query}'"
            )
            repos = get_repositories(
                f"created:{year}-01-01..{year}-12-31 language:{language} {search_query}"
            )
            if repos == None:
                print("Github Ratelimit exceeded")
                exit(0)

            with open(
                f"data/language-repositories-{language}-{year}.json",
                "w",
            ) as f:
                json.dump(repos, f)
        else:
            if os.path.exists(f"data/language-repositories-{language}-{year}.json"):
                with open(
                    f"data/language-repositories-{language}-{year}.json", "r"
                ) as f:
                    repos = json.load(f)

        if repos["total_count"] > 100:
            for page in range(1, int(repos["total_count"] / 100)):
                if page > 10:
                    return
                if not os.path.exists(
                    f"data/language-repositories-{language}-{year}-{page}.json"
                ):
                    print(
                        f"Getting subpages for language {language} from {year} with query: 'created:>={year}-01-01..{year}-12-31 language:{language} {search_query}'"
                    )
                    repos = get_repositories_paginated(
                        f"created:{year}-01-01..{year}-12-31 language:{language} {search_query}",
                        page,
                    )
                    if repos == None:
                        print("Github Ratelimit exceeded")
                        exit(0)

                    with open(
                        f"data/language-repositories-{language}-{year}-{page}.json",
                        "w",
                    ) as f:
                        json.dump(repos, f)
                


if __name__ == "__main__":
    for language in LANGUAGES:
        print(f"Processing repositories for {language}")
        get_and_cache_language_repositories(language, "blazingly-fast")
    exit()

    # Determine initial amount of repositories
    repos = get_repositories("blazingly fast")
    print(f"Found {repos['total_count']} repositories")

    # Determine amount of repositories with pagination
    # total_pages = int(repos["total_count"] % 100)

    # So we can use without authentication
    total_pages = int(repos["total_count"] / 100)
    last_page = 0
    print(total_pages)

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
                    f"- [{repo['name']}]({parse.quote(repo['html_url'])}) - {repo['description']} - ⭐ {repo['stargazers_count']}\n"
                )
            f.write("\n")
