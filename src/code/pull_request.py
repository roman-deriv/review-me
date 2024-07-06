import github
import sys

import config
import logger


def get_pr(cfg: config.GitHubConfig):
    try:
        gh = github.Github(cfg.token)
        repo = gh.get_repo(cfg.repository)
        pr = repo.get_pull(cfg.pr_number)
        return pr
    except Exception as e:
        logger.log.critical(f"Couldn't retrieve pull request: {e}")
        sys.exit(69)
        

def comment(pr, message):
    try:
        pr.create_issue_comment(message)
    except Exception as e:
        logger.log.error(f"Problem posting comment: {e}")