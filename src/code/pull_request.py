import sys

import github
from github.PullRequest import PullRequest

import config
import logger
from .review.model import Feedback


def get_pr(cfg: config.GitHubConfig):
    try:
        gh = github.Github(cfg.token)
        repo = gh.get_repo(cfg.repository)
        pr = repo.get_pull(cfg.pr_number)
        return pr
    except Exception as e:
        logger.log.critical(f"Couldn't retrieve pull request: {e}")
        sys.exit(69)


def post_comment(pull_request: PullRequest, message: str):
    try:
        pull_request.create_issue_comment(message)
    except github.GithubException as e:
        logger.log.warning(f"Could not post comment to GitHub: {e}")
    except Exception as e:
        logger.log.warning(f"Unknown problem posting comment: {e}")


def submit_review(
        pull_request: PullRequest,
        feedback: Feedback,
):
    comments = [comment.dict(exclude_none=True) for comment in feedback.comments]
    logger.log.debug(f"Submitting review: {comments}")
    pull_request.create_review(
        body=f"{feedback.summary}\n\n"
             f"{feedback.overall_comment}\n\n"
             f"{feedback.evaluation}",
        comments=comments,
        event="COMMENT",
    )
