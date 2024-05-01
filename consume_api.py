import requests
from datetime import datetime
import os

TOKEN = os.getenv("TOKEN")

if TOKEN == None:
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
else:
    headers = {
        "Authorization": f"bearer {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def format_date(date):
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return date.strftime("%Y-%m-%d")


def pull_request_state(condition, start_date, end_date, pull_request):
    return (
        pull_request.get(condition) != None
        and start_date <= format_date(pull_request.get(condition)) <= end_date
    )


def owner_verification(owner):
    if (
        requests.head(
            f"https://api.github.com/users/{owner}", headers=headers
        ).status_code
        == 404
    ):
        raise ValueError("Error 404 User Not Found")


def repo_verification(owner, repo_name):
    if (
        requests.head(
            f"https://api.github.com/repos/{owner}/{repo_name}", headers=headers
        ).status_code
        == 404
    ):
        raise ValueError("Error 404 Repo Not Found")


def make_get_request(owner, repo_name, params):
    return requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/pulls",
        headers=headers,
        params=params,
    )


def format_pull_request_data(pull_request):
    return {
        "id": pull_request.get("user")["id"],
        "user": pull_request.get("user")["login"],
        "title": pull_request.get("title"),
        "state": pull_request.get("state"),
        "created_at": format_date(pull_request.get("created_at")),
    }


def filter_pull_requests(start_date, end_date, pull_request):
    if (
        (pull_request_state("created_at", start_date, end_date, pull_request))
        or (pull_request_state("updated_at", start_date, end_date, pull_request))
        or (pull_request_state("closed_at", start_date, end_date, pull_request))
        or (pull_request_state("merged_at", start_date, end_date, pull_request))
    ):
        return True


def get_pull_requests(owner, repo_name, start_date, end_date):
    params = {"state": "all", "per_page": 100}
    pull_requests_list = []
    owner_verification(owner)
    repo_verification(owner, repo_name)
    response = make_get_request(owner, repo_name, params)
    pull_requests = response.json()
    while True:
        for pull_request in pull_requests:
            if filter_pull_requests(start_date, end_date, pull_request) == True:
                pull_requests_list.append(format_pull_request_data(pull_request))
        if "next" in response.links.keys():
            response = requests.get(
                response.links["next"]["url"], headers=headers, params=params
            )
            pull_requests = response.json()
        else:
            break
    return pull_requests_list


if __name__ == "__main__":
    print(get_pull_requests("Umuzi-org", "ACN-syllabus", "2022-03-01", "2022-03-10"))
