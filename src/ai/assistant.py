import model
import logs
from . import prompt, tool
from .anthropic import tool_completion


class Assistant:
    def __init__(self, model_name: str, builder: prompt.Builder):
        logs.debug("creating Builder start")
        self._model_name = model_name
        self._builder = builder
        logs.debug("creating Builder finish")

    def files_to_review(self) -> list[model.FileReviewRequest]:
        logs.debug("files_to_review start")
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
        files = [
            model.FileReviewRequest(
                path=req["filename"],
                reason=req["reason"],
            )
            for req in results["files"]
        ]
        logs.debug("files_to_review finish")
        return files

    def review_file(self, filename: str) -> list[model.Comment]:
        logs.debug("review_file start")
        system_prompt = prompt.load("file-review")

        with open(filename, "r") as file:
            source_code = file.readlines()

        results = tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.file_diff(filename, source_code),
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
            if "end_line" in comment:
                # replace `end_line` with `line`
                comment.update(line=comment.pop("end_line"))
            if "end_side" in comment:
                # replace `end_side` with `side`
                comment.update(side=comment.pop("end_side"))

            comments.append(comment)

        logs.debug("review_file finish")
        return comments

    def get_feedback(
            self,
            comments: list[model.Comment],
    ) -> model.Feedback:
        logs.debug("get_feedback start")
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
        feedback = model.Feedback(
            comments=comments,
            overall_comment=response["feedback"],
            evaluation=response["event"],
        )
        logs.debug("get_feedback finish")
        return feedback
