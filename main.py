import json
import os

import openai
from github import Github

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_code_review(files):
    prompt = "Review the following code changes and provide feedback:\n"
    for file in files:
        prompt += f"\nFile: {file['filename']}\n"
        prompt += file['patch']
        prompt += "\n\n"

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1_000,
    )
    return response.choices[0].message.content.strip()


def main():
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    with open(event_path, 'r') as f:
        event = json.load(f)

    pr_number = event["issue"]["number"]

    gh = Github(github_token)
    repo = gh.get_repo(repo)
    pr = repo.get_pull(pr_number)
    files = pr.get_files()

    review_comment = generate_code_review(files)

    pr.create_issue_comment(review_comment)


if __name__ == "__main__":
    main()
