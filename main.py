import json
import os
import openai
import httpx

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_pr_files(repo, pr_number, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = httpx.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files", headers=headers
    )
    response.raise_for_status()
    return response.json()


def post_pr_comment(repo, pr_number, token, comment):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"body": comment}
    response = httpx.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
        headers=headers, json=data
    )
    response.raise_for_status()
    return response.json()


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
    repo = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    with open(event_path, 'r') as f:
        event = json.load(f)

    pr_number = event["issue"]["number"]

    github_token = os.getenv("GITHUB_TOKEN")

    files = get_pr_files(repo, pr_number, github_token)

    review_comment = generate_code_review(files)

    post_pr_comment(repo, pr_number, github_token, review_comment)


if __name__ == "__main__":
    main()
