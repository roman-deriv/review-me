import unittest
from unittest.mock import Mock

from github.Commit import Commit
from github.File import File
from github.IssueComment import IssueComment
from github.PullRequest import PullRequest
from github.PullRequestComment import PullRequestComment

import code.model
import code.pull_request
import code.review.model


class TestReview(unittest.TestCase):
    def setUp(self):
        self.mock_pr = Mock(spec=PullRequest)
        self.mock_pr.title = "Test PR"
        self.mock_pr.body = "This is a test pull request"

    async def test_build_pr_context(self):
        mock_file = Mock(spec=File)
        mock_file.filename = "test.py"
        mock_file.patch = "@@ -1,3 +1,4 @@\n Line 1\n+Line 2\n Line 3\n Line 4"
        mock_file.status = "modified"

        mock_commit = Mock(spec=Commit)
        mock_commit.commit.message = "Test commit"

        mock_review_comment = Mock(spec=PullRequestComment)
        mock_review_comment.body = "Test review comment"

        mock_issue_comment = Mock(spec=IssueComment)
        mock_issue_comment.body = "Test issue comment"

        self.mock_pr.get_files.return_value = [mock_file]
        self.mock_pr.get_commits.return_value = [mock_commit]
        self.mock_pr.get_review_comments.return_value = [mock_review_comment]

        context = await code.pull_request.build_pr_context(self.mock_pr)

        self.assertEqual(context.title, "Test PR")
        self.assertEqual(context.description, "This is a test pull request")
        self.assertListEqual(context.commit_messages, ["Test commit"])
        self.assertListEqual(context.review_comments, ["Test review comment"])
        self.assertEqual(
            context.patches,
            {
                "test.py": code.model.FilePatchModel(
                    filename="test.py",
                    diff="@@ -1,3 +1,4 @@\n Line 1\n+Line 2\n Line 3\n Line 4",
                    hunks=[
                        code.model.HunkModel(
                            start_line=1,
                            end_line=4,
                            changed_lines={2},
                        ),
                    ],
                )
            },
        )
        self.assertListEqual(context.modified_files, ["test.py"])
        self.assertListEqual(context.added_files, [])
        self.assertListEqual(context.deleted_files, [])


if __name__ == "__main__":
    unittest.main()
