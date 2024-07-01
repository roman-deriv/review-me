import github

import ai.prompt
import ai.service
import ai.tool
import config
import model
import review.manager


def get_pr(cfg: config.GitHubConfig):
    gh = github.Github(cfg.token)
    repo = gh.get_repo(cfg.repository)
    return repo.get_pull(cfg.pr_number)


class App:
    def __init__(self, app_config: config.AppConfig):
        self._config = app_config
        self._pr = get_pr(self._config.github)
        self._chat_completion = ai.service.chat_completion(self._config.llm.strategy)
        self._tool_completion = ai.service.tool_completion(self._config.llm.strategy)

    def _files_to_review(self, overview: str) -> list[dict[str, str]]:
        system_prompt = ai.prompt.load("system-prompt-overview")
        results = self._tool_completion(
            system_prompt=system_prompt,
            prompt=overview,
            model=self._config.llm.model,
            tools=[
                ai.tool.review_files,
            ],
            tool_override="review_files",
        )
        files = results["files"]
        return files

    def _generate_comments(self, manager, file):
        filename = file["filename"]

        system_prompt = ai.prompt.load("system-prompt-code-file")
        results = self._tool_completion(
            system_prompt=system_prompt,
            prompt=manager.file_diff(filename),
            model=self._config.llm.model,
            tools=[
                ai.tool.post_feedback,
            ],
            tool_override="post_feedback",
        )

        comments = results["feedback"]
        for comment in comments:
            comment.update(path=filename)
            print(comment)
            print("--------")

        return comments

    def _generate_review_summary(
            self,
            manager: review.manager.ReviewManager,
            comments: list[dict[str, str]],
    ) -> dict[str, str]:
        system_prompt = ai.prompt.load("system-prompt-review-summary")
        results = self._tool_completion(
            system_prompt=system_prompt,
            prompt=manager.review_summary(comments),
            model=self._config.llm.model,
            tools=[
                ai.tool.submit_review,
            ],
            tool_override="submit_review",
        )

        return results

    def _generate_feedback(self) -> model.Feedback:
        context = review.manager.build_context(self._pr)
        manager = review.manager.ReviewManager(context)
        overview = manager.overview()
        files = self._files_to_review(overview)
        print("We should review these files")
        for file in files:
            print("Filename:", file["filename"])
            print("Reason:", file["reason"])
            print()

        comments: list[dict[str, str]] = []
        for file in files:
            comments += self._generate_comments(manager, file)

        review_summary = self._generate_review_summary(manager, comments)
        overall_comment = review_summary["feedback"]
        evaluation = review_summary["event"]
        print()
        print("OVERALL FEEDBACK")
        print()
        print(overall_comment)
        print(evaluation)

        return model.Feedback(
            comments=comments,
            overall_comment=overall_comment,
            evaluation=evaluation,
        )

    def _submit_review(self, feedback: model.Feedback):
        if self._config.debug:
            return

        self._pr.create_review(
            body=feedback.overall_comment,
            comments=feedback.comments,
            event=feedback.evaluation,
        )

    def run(self):
        feedback = self._generate_feedback()
        self._submit_review(feedback)
