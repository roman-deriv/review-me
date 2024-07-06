import unittest

from src.code import diff
from src.model import Hunk
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
            Hunk(start_line=5, end_line=10, changed_lines={7, 8}),
            Hunk(start_line=15, end_line=20, changed_lines={16, 17, 18})
        ]

    def test_comment_within_hunk(self):
        comment = {"start_line": 7, "end_line": 9}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 7)
        self.assertEqual(adjusted["end_line"], 8)

    def test_comment_between_hunks(self):
        comment = {"start_line": 12, "end_line": 14}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 16)
        self.assertEqual(adjusted["end_line"], 18)

    def test_comment_after_all_hunks(self):
        comment = {"start_line": 25, "end_line": 27}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 16)
        self.assertEqual(adjusted["end_line"], 18)

    def test_comment_before_all_hunks(self):
        comment = {"start_line": 1, "end_line": 3}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 7)
        self.assertEqual(adjusted["end_line"], 8)

    def test_comment_spanning_multiple_hunks(self):
        comment = {"start_line": 8, "end_line": 17}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 7)
        self.assertEqual(adjusted["end_line"], 8)

    def test_comment_on_unchanged_line_within_hunk(self):
        comment = {"start_line": 9, "end_line": 9}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 8)
        self.assertEqual(adjusted["end_line"], 8)

    def test_comment_with_single_line(self):
        comment = {"start_line": 16, "end_line": 16}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 16)
        self.assertEqual(adjusted["end_line"], 16)

    def test_comment_with_no_overlap_closer_to_second_hunk(self):
        comment = {"start_line": 13, "end_line": 14}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 16)
        self.assertEqual(adjusted["end_line"], 17)

    def test_comment_with_partial_overlap(self):
        comment = {"start_line": 9, "end_line": 11}
        adjusted = diff.adjust_comment_to_best_hunk(self.hunks, comment)
        self.assertEqual(adjusted["start_line"], 7)
        self.assertEqual(adjusted["end_line"], 8)


if __name__ == '__main__':
    unittest.main()
