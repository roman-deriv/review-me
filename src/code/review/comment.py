import ai.schema

import logger
from . import model
from ..diff import adjust_comment_bounds_to_hunk, closest_hunk
from ..model import Category, GitHubCommentModel, PullRequestContextModel, Severity


def parse_overview(
    response: ai.schema.ReviewRequestsResponseModel,
    context: PullRequestContextModel,
) -> model.OverviewModel:
    return model.OverviewModel(
        initial_assessment=model.InitialAssessmentModel(
            status=model.Status[response.initial_assessment.status],
            summary=response.initial_assessment.summary,
        ),
        observations=[
            model.ObservationModel(
                comment=observation.comment,
                tag=model.ObservationTag[observation.tag],
            )
            for observation in response.observations or []
        ],
        file_contexts=[
            model.FileContextModel(
                path=request.filename,
                changes=request.changes,
                related_changes=request.related_changes,
                reason=request.reason,
                patch=context.patches[request.filename],
            )
            for request in response.files_for_review or []
        ],
    )


def prioritize_comments(
    comments: dict[Category, list[GitHubCommentModel]],
) -> tuple[list[GitHubCommentModel], list[GitHubCommentModel]]:
    prioritized_comments = []
    remaining_comments = []

    prioritized_categories = [
        Category.FUNCTIONALITY,
        Category.PERFORMANCE,
        Category.SECURITY,
    ]
    remaining_categories = [
        Category.MAINTAINABILITY,
        Category.READABILITY,
        Category.BEST_PRACTICES,
    ]

    for category in prioritized_categories:
        prioritized_comments += comments.get(category, [])

    for category in remaining_categories:
        if len(prioritized_comments) == 0:
            prioritized_comments += comments.get(category, [])[:2]
            remaining_comments += comments.get(category, [])[2:]
        else:
            remaining_comments += comments.get(category, [])

    return prioritized_comments, remaining_comments


def extract_comments(
    response: ai.schema.FileReviewResponseModel,
    file_context: model.FileContextModel,
    severity_limit: int,
) -> tuple[list[GitHubCommentModel], list[GitHubCommentModel]]:
    filtered_comments = {}
    for comment in response.feedback:
        severity = Severity.from_string(comment.severity)
        if severity > severity_limit:
            logger.log.debug(f"Skipping  comment: {comment}")
            continue

        start_line, end_line = comment.bounds()

        hunk = closest_hunk(file_context.patch.hunks, (start_line, end_line))
        if not hunk:
            logger.log.debug(f"No suitable hunk for comment: {comment}")
            continue

        adjusted_start, adjusted_end = adjust_comment_bounds_to_hunk(
            hunk=hunk,
            start_line=start_line,
            end_line=end_line,
        )

        code_comment = GitHubCommentModel(
            path=file_context.path,
            body=comment.body,
            line=end_line,
            start_line=start_line,
            side=comment.end_side,
            start_side=comment.start_side,
        )

        code_comment.start_line = adjusted_start
        code_comment.line = adjusted_end
        if adjusted_start == adjusted_end:
            code_comment.start_line = None

        logger.log.debug(f"File comment ({severity}): {code_comment}")

        category = Category[comment.category]
        if comment.category not in filtered_comments:
            filtered_comments[category] = []
        filtered_comments[category].append(code_comment)

    logger.log.debug(f"Finished file review for `{file_context.path}`")

    return prioritize_comments(filtered_comments)


def parse_feedback(
    response: ai.schema.ReviewResponseModel,
    comments: list[GitHubCommentModel],
) -> model.Feedback:
    return model.Feedback(
        comments=comments,
        overall_comment=response.feedback,
        evaluation=response.event,
        justification=response.justification,
    )
