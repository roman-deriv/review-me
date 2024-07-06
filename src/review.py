import typing

from github.PullRequest import PullRequest

import code.diff
import logger
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


def parse_review_requests(
        requests: dict[str, list[dict[str, typing.Any]]],
        context: model.ReviewContext,
) -> list[model.FileReviewRequest]:
    return [
        parse_review_request(request, context)
        for request in requests["files"]
    ]


def parse_review(
        review: dict[str, list[dict[str, typing.Any]]],
        review_request: model.FileReviewRequest,
        severity_limit: int,
) -> list[model.Comment]:
    comments = review["feedback"]
    filtered_comments = []
    for comment in comments:
        severity = model.Severity.from_string(comment.pop("severity"))
        if severity > severity_limit:
            logger.log.debug(f"Skipping {severity} comment: {comment}")
            continue

        if "start_line" not in comment:
            comment["start_line"] = comment["end_line"]

        adjusted_comment = code.diff.adjust_comment_to_best_hunk(
            review_request.hunks,
            comment,
        )
        if not adjusted_comment:
            logger.log.debug(f"No suitable hunk for comment: {comment}")
            continue
        else:
            comment = adjusted_comment

        # override path for determinism
        comment.update(path=review_request.path)

        if "end_line" in comment:
            if "start_line" in comment:
                if int(comment["start_line"]) >= int(comment["end_line"]):
                    del comment["start_line"]

            comment.update(line=comment.pop("end_line"))

        if "end_side" in comment:
            # replace `end_side` with `side`
            comment.update(side=comment.pop("end_side"))

        logger.log.debug(f"File comment ({severity}): {comment}")
        filtered_comments.append(comment)

    logger.log.debug(f"Finished file review for `{review_request.path}`")

    return filtered_comments


def parse_feedback(
        feedback: dict[str, typing.Any],
        comments: list[model.Comment]
) -> model.Feedback:
    return model.Feedback(
        comments=comments,
        summary=feedback["summary"],
        overall_comment=feedback["feedback"],
        evaluation=feedback["event"],
    )