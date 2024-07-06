import sys

import github
from github.PullRequest import PullRequest

import config
import logger
import model


def get_pr(cfg: config.GitHubConfig):
    try:
        gh = github.Github(cfg.token)
        repo = gh.get_repo(cfg.repository)
        pr = repo.get_pull(cfg.pr_number)
        return pr
    except Exception as e:
        logger.log.critical(f"Couldn't retrieve pull request: {e}")
        sys.exit(69)


def comment(pull_request: PullRequest, message: str):
    try:
        pull_request.create_issue_comment(message)
    except github.GithubException as e:
        logger.log.warning(f"Could not post comment to GitHub: {e}")
    except Exception as e:
        logger.log.warning(f"Unknown problem posting comment: {e}")


def submit_review(pull_request: PullRequest, feedback: model.Feedback):
    pull_request.create_review(
        body=f"{feedback.summary}\n\n"
             f"{feedback.overall_comment}\n\n"
             f"{feedback.evaluation}",
        comments=feedback.comments,
        event="COMMENT",
    )
