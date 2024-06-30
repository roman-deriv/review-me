import json

import github

import ai.prompt
import ai.service
import ai.tool
import config
import model
import review.manager


def files_to_review(
        llm_config: config.LlmConfig,
        overview: str
) -> list[dict[str, str]]:
    tool_completion = ai.service.tool_completion(llm_config.strategy)
    system_prompt = ai.prompt.load("system-prompt-overview")
    results = tool_completion(
        system_prompt=system_prompt,
        prompt=overview,
        model=llm_config.model,
        tools=[
            ai.tool.review_files,
        ],
        tool_override="review_files",
    )
    files = results["files"]
    return files


def review_files(files, debug=False):
    system_prompt = ai.prompt.load("system-prompt-code-file")
    for filename in files:
        if debug:
            continue
        yield filename


def get_pr(cfg: config.GitHubConfig):
    gh = github.Github(cfg.token)
    repo = gh.get_repo(cfg.repository)
    return repo.get_pull(cfg.pr_number)


class App:
    def __init__(self, app_config: config.AppConfig):
        self._config = app_config
        self._pr = get_pr(self._config.github)
        self._chat_completion = ai.service.chat_completion(self._config.llm.strategy)

    def _generate_feedback(self) -> model.Feedback:
        context = review.manager.build_context(self._pr)
        manager = review.manager.ReviewManager(context)
        overview = manager.overview()
        files = files_to_review(self._config.llm, overview)
        print("We should review these files")
        for file in files:
            print("Filename:", file["filename"])
            print("Reason:", file["reason"])
            print()

        comments = {}
        system_prompt = ai.prompt.load("system-prompt-code-file")
        for file in files:
            filename = file["filename"]
            if self._config.debug:
                continue

            comment = self._chat_completion(
                system_prompt=system_prompt,
                prompt=manager.file_diff(filename),
                model=self._config.llm.model,
            )

            comments[filename] = comment

        overall_comment = ""

        return model.Feedback(
            comments=comments,
            overall_comment=overall_comment,
        )

    def _submit_review(self, feedback: model.Feedback):
        for filename, comment in feedback.comments.items():
            print(filename)
            print("--------")
            print(comment)
            print("========")
            print()
            if self._config.debug:
                continue

            self._pr.create_review_comment(comment)

    def run(self):
        review = self._generate_feedback()
        self._submit_review(review)
