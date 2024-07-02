from . import prompt, tool
from .anthropic import tool_completion


class Assistant:
    def __init__(self, model: str, builder: prompt.Builder):
        self._model = model
        self._builder = builder

    def files_to_review(self):
        system_prompt = prompt.load("overview")
        results = tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.overview(),
            model=self._model,
            tools=[
                tool.review_files,
            ],
            tool_override="review_files",
        )
        return results["files"]

    def review_file(self, filename):
        system_prompt = prompt.load("file-review")
        return tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.file_diff(filename),
            model=self._model,
            tools=[
                tool.post_feedback,
            ],
            tool_override="post_feedback",
        )

    def get_feedback(
            self,
            comments: list[dict[str, str]],
    ) -> dict[str, str]:
        system_prompt = prompt.load("review-summary")
        return tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.review_summary(comments),
            model=self._model,
            tools=[
                tool.submit_review,
            ],
            tool_override="submit_review",
        )
