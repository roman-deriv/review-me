import unittest

from src.code import diff
from src.model import Hunk
from test import fixture


class TestCodeDiff(unittest.TestCase):
    def test_parse_diff(self):
        patch = fixture.single_hunk_patch
        hunks = diff.parse_diff(patch)
        self.assertEqual(len(hunks), 1)
        self.assertEqual(hunks[0].start_line, 1)
        self.assertEqual(hunks[0].end_line, 4)
        self.assertEqual(hunks[0].changed_lines, {2, 3})

    def test_adjust_comment_to_best_hunk(self):
        hunks = [
            Hunk(start_line=1, end_line=5, changed_lines={2, 3}),
            Hunk(start_line=10, end_line=15, changed_lines={11, 12, 13})
        ]

        # Test comment within a hunk
        comment = {"start_line": 2, "end_line": 4}
        adjusted = diff.adjust_comment_to_best_hunk(hunks, comment)
        self.assertEqual(adjusted["start_line"], 2)
        self.assertEqual(adjusted["end_line"], 3)

        # Test comment between hunks
        comment = {"start_line": 7, "end_line": 9}
        adjusted = diff.adjust_comment_to_best_hunk(hunks, comment)
        self.assertEqual(adjusted["start_line"], 11)
        self.assertEqual(adjusted["end_line"], 13)

        # Test comment outside all hunks
        comment = {"start_line": 20, "end_line": 22}
        adjusted = diff.adjust_comment_to_best_hunk(hunks, comment)
        self.assertEqual(adjusted["start_line"], 11)
        self.assertEqual(adjusted["end_line"], 13)


if __name__ == '__main__':
    unittest.main()
