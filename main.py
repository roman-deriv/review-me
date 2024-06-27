import json
import os

import openai
from github import Github

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_file_diffs(pr):
    file_diffs = {}

    for file in pr.get_files():
        if file.status != "modified":
            continue
        file_diffs[file.filename] = file.patch

    return file_diffs


def generate_code_review(file_diffs, model):
    system_prompt = (
        "Your job is to review GitHub Pull Requests. "
        "You must act as an expert software engineer. "
        "You will be given a diff of the changes from the PR, "
        "and you must review the code changes in order to "
        "provide feedback as needed."
    )
    prompt = f"PR Diff:\n{file_diffs}"
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1_000,
    )
    return response.choices[0].message.content.strip()


def get_pr(github_token, repo, pr_number):
    gh = Github(github_token)
    repo = gh.get_repo(repo)
    pr = repo.get_pull(pr_number)
    return pr


def main():
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    event_path = os.environ.get("GITHUB_EVENT_PATH")

    with open(event_path, 'r') as f:
        event = json.load(f)

    pr_number = event["issue"]["number"]

    pr = get_pr(github_token, repo, pr_number)
    file_diffs = get_file_diffs(pr)

    review_comment = generate_code_review(file_diffs, "gpt-4o")

    pr.create_issue_comment(review_comment)


def test():
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr = get_pr(github_token, repo, 1)
    file_diffs = get_file_diffs(pr)
    review_comment = generate_code_review(file_diffs, "gpt-3.5-turbo")
    print(review_comment)


if __name__ == "__main__":
    test()
