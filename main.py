import json
import os

from github import Github

import ai.service


def generate_overall_comment():
    system_prompt = (
        "Your job is to review GitHub Pull Requests. "
        "You must act as an expert software engineer. "
        "You will be given a diff of the changes from the PR, "
        "and you must review the code changes in order to "
        "provide feedback as needed."
    )
    # TODO: Implement
    pass


def generate_file_comments(pr, strategy, model, debug=False):
    chat_completion = ai.service.chat_completion(strategy)
    system_prompt = (
        "Your job is to review a single file diff from a GitHub Pull Request. "
        "You must act as an expert software engineer. "
        "You will be given the PR title and description, as well as a diff of the "
        "changes from the a single file in the PR."
        "You must review the code changes and provide meaningful feedback when "
        "necessary. You are *NOT* reviewing the entire PR, just this single file. "
        "Keep your comment as CONCISE as possible and clear. "
        "Only provide feedback if there is something CONCRETE and SPECIFIC to say. "
        "If it's okay as is, simply reply with the exact phrase 'LGTM.'"
    )
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
