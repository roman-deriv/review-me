import json
import os

from github import Github

import ai.prompt
import ai.service


def generate_file_comments(pr, strategy, model, debug=False):
    chat_completion = ai.service.chat_completion(strategy)
    system_prompt = ai.prompt.load("system-prompt-code-file")
    commit_msgs = [commit.commit.message for commit in pr.get_commits()]

    file_comments = {}
    for file in pr.get_files():
        if file.status != "modified":
            continue
        prompt = (
            f"PR Title: {pr.title}\n\n"
            f"PR Commits: - {"\n- ".join(commit_msgs)}\n\n"
            f"PR Body:\n{pr.body}\n\n"
            f"Filename: {file.filename}\n\n"
            f"Diff:\n{file.patch}"
        )
        if debug:
            continue
        comment = chat_completion(system_prompt, prompt, model)
        file_comments[file.filename] = comment
    return file_comments


def get_pr(github_token, repo, pr_number):
    gh = Github(github_token)
    repo = gh.get_repo(repo)
    pr = repo.get_pull(pr_number)
    return pr


def main():
    strategy = "openai"
    model = os.environ.get(f"{strategy.upper()}_MODEL")
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    event_path = os.environ.get("GITHUB_EVENT_PATH")

    with open(event_path, 'r') as f:
        event = json.load(f)

    pr_number = event["issue"]["number"]

    pr = get_pr(github_token, repo, pr_number)

    review_comments = generate_file_comments(pr, strategy, model)

    for comment in review_comments.values():
        pr.create_issue_comment(comment)


def test():
    strategy = "openai"
    model = os.environ.get(f"{strategy.upper()}_TEST_MODEL")
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

    pr = get_pr(github_token, repo, 2)

    review_comments = generate_file_comments(pr, strategy, model, debug=True)
    for filename, comment in review_comments.items():
        print(filename)
        print("--------")
        print(comment)
        print("========")
        print()


if __name__ == "__main__":
    test()
