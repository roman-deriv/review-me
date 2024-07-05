import typing

from github.PullRequest import PullRequest

import code.diff
import model


def build_context(pull_request: PullRequest) -> model.ReviewContext:
    files = pull_request.get_files()
    context = model.ReviewContext(
        title=pull_request.title,
        description=pull_request.body,
        commit_messages=[
            commit.commit.message
            for commit in pull_request.get_commits()
        ],
        review_comments=[
            comment.body
            for comment in pull_request.get_review_comments()
        ],
        issue_comments=[
            comment.body
            for comment in pull_request.get_issue_comments()
        ],
        diffs={
            file.filename: file.patch
            for file in files
        },
        added_files=[file.filename for file in files if file.status == 'added'],
        modified_files=[file.filename for file in files if file.status == 'modified'],
        deleted_files=[file.filename for file in files if file.status == 'removed']
    )
    return context


def parse_review_request(
        request: dict[str, typing.Any],
        context: model.ReviewContext,
) -> model.FileReviewRequest:
    diff = context.diffs[request["filename"]]
    return model.FileReviewRequest(
        path=request["filename"],
        changes=request["changes"],
        related_changed=request["related_changes"],
        reason=request["reason"],
        diff=diff,
        hunks=code.diff.parse_diff(diff)
    )
