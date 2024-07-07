import unittest
from unittest.mock import Mock, patch

from github.Commit import Commit
from github.File import File
from github.IssueComment import IssueComment
from github.PullRequest import PullRequest
from github.PullRequestComment import PullRequestComment

import ai.schema
import code.model
import code.review.context
import code.review.model


class TestReview(unittest.TestCase):

    def setUp(self):
        self.mock_pr = Mock(spec=PullRequest)
        self.mock_pr.title = "Test PR"
        self.mock_pr.body = "This is a test pull request"

    def test_build_pr_context(self):
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
        self.mock_pr.get_issue_comments.return_value = [mock_issue_comment]

        context = code.review.context.build_pr_context(self.mock_pr)

        self.assertEqual(context.title, "Test PR")
        self.assertEqual(context.description, "This is a test pull request")
        self.assertListEqual(context.commit_messages, ["Test commit"])
        self.assertListEqual(context.review_comments, ["Test review comment"])
        self.assertListEqual(context.issue_comments, ["Test issue comment"])
        self.assertEqual(context.patches, {
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
        })
        self.assertListEqual(context.modified_files, ["test.py"])
        self.assertListEqual(context.added_files, [])
        self.assertListEqual(context.deleted_files, [])

    @patch('code.diff.parse_diff')
    def test_build_file_contexts(self, mock_parse_diff):
        mock_hunk = Mock(spec=code.model.HunkModel)
        mock_hunk.start_line = 1
        mock_hunk.end_line = 4
        mock_hunk.changed_lines = {2}

        mock_patch = Mock(spec=code.model.FilePatchModel)
        mock_patch.filename = "test.py"
        mock_patch.diff = "@@ -1,3 +1,4 @@\n Line 1\n+Line 2\n Line 3\n Line 4"
        mock_patch.hunks = [mock_hunk]

        mock_context = Mock(spec=code.review.model.PullRequestContextModel)
        mock_context.patches = {
            "test.py": mock_patch,
        }

        mock_parse_diff.return_value = [
            code.model.HunkModel(
                start_line=1,
                end_line=4,
                changed_lines={2},
            )
        ]

        request = ai.schema.ReviewRequestsResponseModel(
            files=[
                ai.schema.FileReviewRequestModel(
                    filename="test.py",
                    changes="Added a new line",
                    related_changes="None",
                    reason="Code improvement",
                )
            ]
        )

        results = code.review.context.build_file_contexts(request, mock_context)
        result = results[0]

        self.assertEqual(result.path, "test.py")
        self.assertEqual(result.changes, "Added a new line")
        self.assertEqual(result.related_changes, "None")
        self.assertEqual(result.reason, "Code improvement")
        self.assertEqual(
            result.patch.diff,
            "@@ -1,3 +1,4 @@\n Line 1\n+Line 2\n Line 3\n Line 4",
        )
        self.assertEqual(len(result.patch.hunks), 1)
        self.assertEqual(result.patch.hunks[0].start_line, 1)
        self.assertEqual(result.patch.hunks[0].end_line, 4)
        self.assertSetEqual(result.patch.hunks[0].changed_lines, {2})


if __name__ == '__main__':
    unittest.main()
