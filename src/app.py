import asyncio

import github
from github.PullRequest import PullRequest

import ai.assistant
import ai.tool
import config
import logger
import model


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
    def __init__(
            self,
            pull_request: PullRequest,
            assistant: ai.assistant.Assistant,
            debug: bool = False,
    ):
        self._pr = pull_request
        self._assistant = assistant
        self._debug = debug

    async def _generate_feedback(self) -> model.Feedback:
        review_requests = await self._assistant.files_to_review()

        async def review_file(req, delay):
            await asyncio.sleep(delay)
            file_comments = await self._assistant.review_file(req.path)
            for comment in file_comments:
                print(comment)
                print("--------")
            return file_comments

        tasks = []
        for i, req in enumerate(review_requests):
            delay = i * 1.5  # Stagger start times by 1.5 seconds
            task = asyncio.create_task(review_file(req, delay))
            tasks.append(task)

        file_reviews = await asyncio.gather(*tasks)

        # Flatten the list of comments
        comments: list[model.Comment] = [
            comment for file_comments in file_reviews for comment in file_comments
        ]

        feedback = await self._assistant.get_feedback(comments)
        logger.log.debug(f"Overall Feedback: {feedback}")
        return feedback

    def _submit_review(self, feedback: model.Feedback):
        if self._debug:
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
