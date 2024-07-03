import asyncio
from asyncio import Semaphore

import github
from github.PullRequest import PullRequest

import ai.assistant
import ai.prompt
import ai.tool
import config
import model
import logger


def get_pr(cfg: config.GitHubConfig):
    gh = github.Github(cfg.token)
    repo = gh.get_repo(cfg.repository)
    pr = repo.get_pull(cfg.pr_number)
    logger.log.debug(f"Pull request retrieved: {pr.number}")
    return pr


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
    logger.log.debug(f"Context built sucessfully: {context.title}")
    return context


class App:
    def __init__(self, app_config: config.AppConfig):
        self._config = app_config
        self._pr = get_pr(self._config.github)

        context = build_context(self._pr)
        builder = ai.prompt.Builder(context)
        self._assistant = ai.assistant.Assistant(app_config.llm.model, builder)

    async def _generate_feedback(self) -> model.Feedback:
        review_requests = await self._assistant.files_to_review()

        # Use a semaphore to limit the rate of requests
        semaphore = Semaphore(1)

        async def rate_limited_review(req):
            async with semaphore:
                file_comments = await self._assistant.review_file(req.path)
                for comment in file_comments:
                    print(comment)
                    print("--------")
                await asyncio.sleep(1.5)  # Wait 1.5 seconds between requests
                return file_comments

        # Run file reviews in parallel with rate limiting
        file_reviews = await asyncio.gather(*[
            rate_limited_review(req) for req in review_requests
        ])

        # Flatten the list of comments
        comments: list[model.Comment] = [
            comment for file_comments in file_reviews for comment in file_comments
        ]

        feedback = await self._assistant.get_feedback(comments)
        logger.log.debug(f"Overall Feedback: {feedback}")
        return feedback

    def _submit_review(self, feedback: model.Feedback):
        if self._config.debug:
            logger.log.debug("Running in debug, no review submitted")
            return
        
        self._pr.create_review(
            body=feedback.overall_comment,
            comments=feedback.comments,
            event="COMMENT",
        )

    async def run(self):
        feedback = await self._generate_feedback()
        self._submit_review(feedback)
