import logger
import model
from . import prompt
from .anthropic import tool_completion
from .tool import get_all_tools


class Assistant:
    def __init__(self, model_name: str, builder: prompt.Builder):
        self._model_name = model_name
        self._builder = builder
        self._tools = get_all_tools()

    async def files_to_review(self) -> list[model.FileReviewRequest]:
        system_prompt = prompt.load("overview")
        results = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.overview(),
            model=self._model_name,
            tools=[self._tools["review_files"]],
            tool_override="review_files",
        )
        files = [
            model.FileReviewRequest(
                path=req["filename"],
                changes=req["changes"],
                related_changed=req["related_changes"],
                reason=req["reason"],
            )
            for req in results["files"]
        ]
        logger.log.debug(f"Files to review: {files}")
        return files

    async def review_file(self, file: model.FileReviewRequest) -> list[model.Comment]:
        system_prompt = prompt.load("file-review")

        with open(file.path, "r") as source_file:
            source_code = source_file.readlines()

        results = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.file_review(file, source_code),
            model=self._model_name,
            tools=[self._tools["post_feedback"]],
            tool_override="post_feedback",
        )

        comments = []
        for comment in results["feedback"]:
            # skip any comment that isn't critical or an improvement
            if comment.pop("severity").lower() in ["minor", "nitpick"]:
                continue

            # override path for determinism
            comment.update(path=file.path)
            if "end_line" in comment:
                if "start_line" in comment:
                    if int(comment["start_line"]) >= int(comment["end_line"]):
                        del comment["start_line"]

                # replace `end_line` with `line`
                comment.update(line=comment.pop("end_line"))
            if "end_side" in comment:
                # replace `end_side` with `side`
                comment.update(side=comment.pop("end_side"))

            comments.append(comment)

        logger.log.debug(f"Finished file review for `{file.path}`")

        return comments

    async def get_feedback(
            self,
            comments: list[model.Comment],
    ) -> model.Feedback:
        system_prompt = prompt.load("review-summary")
        response = await tool_completion(
            system_prompt=system_prompt,
            prompt=self._builder.review_summary(comments),
            model=self._model_name,
            tools=[self._tools["submit_review"]],
            tool_override="submit_review",
        )
        feedback = model.Feedback(
            comments=comments,
            summary=response["summary"],
            overall_comment=response["feedback"],
            evaluation=response["event"],
        )
        return feedback
