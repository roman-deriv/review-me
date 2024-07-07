from github.PullRequest import PullRequest

import ai.schema
from . import model
from ..diff import parse_diff


def build_pr_context(pull_request: PullRequest) -> model.PullRequestContextModel:
    files = pull_request.get_files()
    context = model.PullRequestContextModel(
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
        patches={
            file.filename: model.FilePatchModel(
                filename=file.filename,
                diff=file.patch,
                hunks=parse_diff(file.patch)
            )
            for file in files
        },
        added_files=[file.filename for file in files if file.status == 'added'],
        modified_files=[file.filename for file in files if file.status == 'modified'],
        deleted_files=[file.filename for file in files if file.status == 'removed']
    )
    return context


def build_file_contexts(
        requests: ai.schema.ReviewRequestsResponseModel,
        context: model.PullRequestContextModel,
) -> list[model.FileContextModel]:
    return [
        model.FileContextModel(
            path=request.filename,
            changes=request.changes,
            related_changes=request.related_changes,
            reason=request.reason,
            patch=context.patches[request.filename],
        )
        for request in requests.files
    ]
