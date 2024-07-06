import pathlib

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"

single_hunk_patch = """@@ -1,3 +1,4 @@
 Line 1
-Line 2
+Line 2 modified
+Line 2.5 added
 Line 3"""


def load_fixture(filename: str) -> str:
    with open(FIXTURES_DIR / filename, "r") as f:
        return f.read()
