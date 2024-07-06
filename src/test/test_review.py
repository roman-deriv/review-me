import unittest
from unittest.mock import Mock, patch
from github.PullRequest import PullRequest
from github.File import File
from github.Commit import Commit
from github.IssueComment import IssueComment
from github.PullRequestComment import PullRequestComment

import model
import review


class TestReview(unittest.TestCase):

    def setUp(self):
        self.mock_pr = Mock(spec=PullRequest)
        self.mock_pr.title = "Test PR"
        self.mock_pr.body = "This is a test pull request"

    def test_build_context(self):
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

        context = review.build_context(self.mock_pr)

        self.assertEqual(context.title, "Test PR")
        self.assertEqual(context.description, "This is a test pull request")
        self.assertListEqual(context.commit_messages, ["Test commit"])
        self.assertListEqual(context.review_comments, ["Test review comment"])
        self.assertListEqual(context.issue_comments, ["Test issue comment"])
        self.assertDictEqual(context.diffs, {
            "test.py": "@@ -1,3 +1,4 @@\n Line 1\n+Line 2\n Line 3\n Line 4"
        })
        self.assertListEqual(context.modified_files, ["test.py"])
        self.assertListEqual(context.added_files, [])
        self.assertListEqual(context.deleted_files, [])

    @patch('review.code.diff.parse_diff')
    def test_parse_review_request(self, mock_parse_diff):
        mock_context = Mock(spec=model.ReviewContext)
        mock_context.diffs = {
            "test.py": "@@ -1,3 +1,4 @@\n Line 1\n+Line 2\n Line 3\n Line 4",
        }

        mock_parse_diff.return_value = [
            model.Hunk(
                start_line=1,
                end_line=4,
                changed_lines={2},
            )
        ]

        request = {
            "filename": "test.py",
            "changes": "Added a new line",
            "related_changes": "None",
            "reason": "Code improvement"
        }

        result = review.parse_review_request(request, mock_context)

        self.assertEqual(result.path, "test.py")
        self.assertEqual(result.changes, "Added a new line")
        self.assertEqual(result.related_changed, "None")
        self.assertEqual(result.reason, "Code improvement")
        self.assertEqual(
            result.diff,
            "@@ -1,3 +1,4 @@\n Line 1\n+Line 2\n Line 3\n Line 4",
        )
        self.assertEqual(len(result.hunks), 1)
        self.assertEqual(result.hunks[0].start_line, 1)
        self.assertEqual(result.hunks[0].end_line, 4)
        self.assertSetEqual(result.hunks[0].changed_lines, {2})

        mock_parse_diff.assert_called_once_with(
            "@@ -1,3 +1,4 @@\n Line 1\n+Line 2\n Line 3\n Line 4"
        )


if __name__ == '__main__':
    unittest.main()
