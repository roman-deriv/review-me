import unittest

import code.model
from code import diff
from test import fixture


class TestCodeDiff(unittest.TestCase):
    def test_parse_single_hunk_diff(self):
        patch = fixture.single_hunk_patch
        hunks = diff.parse_diff(patch)
        self.assertEqual(len(hunks), 1)
        self.assertEqual(hunks[0].start_line, 1)
        self.assertEqual(hunks[0].end_line, 4)
        self.assertEqual(hunks[0].changed_lines, {2, 3})

    def test_parse_modified_file_diff(self):
        patch = fixture.load_fixture("modified-file-patch.md")
        hunks = diff.parse_diff(patch)
        self.assertEqual(len(hunks), 2)

        self.assertEqual(hunks[0].start_line, 6)
        self.assertEqual(hunks[0].end_line, 23)
        self.assertEqual(hunks[0].changed_lines, {9, 12, 13, 19, 20})

        self.assertEqual(hunks[1].start_line, 26)
        self.assertEqual(hunks[1].end_line, 33)
        self.assertEqual(hunks[1].changed_lines, {29, 30})

    def test_parse_new_file_diff(self):
        patch = fixture.load_fixture("new-file-patch.md")
        hunks = diff.parse_diff(patch)
        self.assertEqual(len(hunks), 1)
        self.assertEqual(hunks[0].start_line, 1)
        self.assertEqual(hunks[0].end_line, 31)
        self.assertEqual(hunks[0].changed_lines, set(range(1, 32)))  # All lines are new

    def test_parse_empty_diff(self):
        patch = ""
        hunks = diff.parse_diff(patch)
        self.assertEqual(len(hunks), 0)


class TestAdjustCommentToBestHunk(unittest.TestCase):
    def setUp(self):
        self.hunks = [
            code.model.HunkModel(start_line=5, end_line=10, changed_lines={7, 8}),
            code.model.HunkModel(
                start_line=15, end_line=20, changed_lines={16, 17, 18}
            ),
        ]

    def test_comment_within_hunk(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=7,
            line=9,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 7)
        self.assertEqual(adjusted.line, 8)

    def test_comment_between_hunks(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=12,
            line=14,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 16)
        self.assertEqual(adjusted.line, 18)

    def test_comment_after_all_hunks(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=25,
            line=27,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 16)
        self.assertEqual(adjusted.line, 18)

    def test_comment_before_all_hunks(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=1,
            line=3,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 7)
        self.assertEqual(adjusted.line, 8)

    def test_comment_spanning_multiple_hunks(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=8,
            line=17,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 7)
        self.assertEqual(adjusted.line, 8)

    def test_comment_on_unchanged_line_within_hunk(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=9,
            line=9,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 8)
        self.assertEqual(adjusted.line, 8)

    def test_comment_with_single_line(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=16,
            line=16,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 16)
        self.assertEqual(adjusted.line, 16)

    def test_comment_with_no_overlap_closer_to_second_hunk(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=13,
            line=14,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 16)
        self.assertEqual(adjusted.line, 17)

    def test_comment_with_partial_overlap(self):
        comment = code.model.GitHubCommentModel(
            path="test.txt",
            body="Test comment",
            start_line=9,
            line=11,
        )
        hunk = diff.closest_hunk(self.hunks, comment)
        adjusted = diff.adjust_comment_bounds_to_hunk(hunk, comment)
        self.assertEqual(adjusted.start_line, 7)
        self.assertEqual(adjusted.line, 8)


if __name__ == "__main__":
    unittest.main()
