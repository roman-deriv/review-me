import model
from . import prompt, tool
from .anthropic import tool_completion


class Assistant:
    def __init__(self, model_name: str, builder: prompt.Builder):
        self._model_name = model_name
        self._builder = builder

    def files_to_review(self) -> list[model.FileReviewRequest]:
        system_prompt = prompt.load("overview")
        results = tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.overview(),
            model=self._model_name,
            tools=[
                tool.review_files,
            ],
            tool_override="review_files",
        )
        return [
            model.FileReviewRequest(
                path=req["filename"],
                reason=req["reason"],
            )
            for req in results["files"]
        ]

    def review_file(self, filename: str) -> list[model.Comment]:
        system_prompt = prompt.load("file-review")
        results = tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.file_diff(filename),
            model=self._model_name,
            tools=[
                tool.post_feedback,
            ],
            tool_override="post_feedback",
        )

        comments = []
        for comment in results["feedback"]:
            # override path for determinism
            comment.update(path=filename)
            # replace `end_line` with `line`
            comment.update(line=comment.pop("end_line"))
            # replace `end_side` with `side`
            comment.update(side=comment.pop("end_side"))

            comments.append(comment)

        return comments

    def get_feedback(
            self,
            comments: list[dict[str, str]],
    ) -> model.Feedback:
        system_prompt = prompt.load("review-summary")
        response = tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.review_summary(comments),
            model=self._model_name,
            tools=[
                tool.submit_review,
            ],
            tool_override="submit_review",
        )
        return model.Feedback(
            comments=comments,
            overall_comment=response["feedback"],
            evaluation=response["event"],
        )
