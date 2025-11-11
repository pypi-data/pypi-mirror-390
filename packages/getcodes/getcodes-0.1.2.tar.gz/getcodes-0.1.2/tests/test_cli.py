import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch
import subprocess
import json


def fake_repo_mapping():
    # Minimal tree with versions and nested directories
    return {
        "": [
            {"name": "DSA", "path": "DSA", "type": "dir"},
            {"name": "CNS", "path": "CNS", "type": "dir"},
            {"name": "DBMS", "path": "DBMS", "type": "dir"},
        ],
        "DSA": [
            {"name": "v1", "path": "DSA/v1", "type": "dir"},
            {"name": "v3", "path": "DSA/v3", "type": "dir"},
            {"name": "DSA Viva.pdf", "path": "DSA/DSA Viva.pdf", "type": "file"},
        ],
        "DSA/v1": [
            {"name": "B6_BSTops.cpp", "path": "DSA/v1/B6_BSTops.cpp", "type": "file"},
            {"name": "A1_Telephone_HashTable.py", "path": "DSA/v1/A1_Telephone_HashTable.py", "type": "file"},
        ],
        "DSA/v3": [
            {"name": "B6_BSTops.cpp", "path": "DSA/v3/B6_BSTops.cpp", "type": "file"},
            {"name": "C13_DFSnBFS.cpp", "path": "DSA/v3/C13_DFSnBFS.cpp", "type": "file"},
        ],
        "CNS": [
            {"name": "programs", "path": "CNS/programs", "type": "dir"},
        ],
        "CNS/programs": [
            {"name": "tcp_hello.py", "path": "CNS/programs/tcp_hello.py", "type": "file"},
            {"name": "udp_file_transfer.py", "path": "CNS/programs/udp_file_transfer.py", "type": "file"},
            {"name": "sliding_window.py", "path": "CNS/programs/sliding_window.py", "type": "file"},
        ],
        "DBMS": [
            {"name": "assignment_3_ddl_constraints.sql", "path": "DBMS/assignment_3_ddl_constraints.sql", "type": "file"},
            {"name": "assignment_2_sql_dml_queries.sql", "path": "DBMS/assignment_2_sql_dml_queries.sql", "type": "file"},
        ],
    }


class FakeGitHubClient:
    def __init__(self, *args, **kwargs):
        self.map = fake_repo_mapping()

    def list_dir(self, path: str):
        key = path.strip("/")
        if key in self.map:
            return self.map[key]
        # emulate file lookup: return [file_obj] if exact path exists
        for entries in self.map.values():
            for e in entries:
                if e.get("type") == "file" and e.get("path") == key:
                    return [e]
        return []

    def get_raw(self, content_obj: dict) -> bytes:
        p = content_obj.get("path", content_obj.get("name", "unknown"))
        return ("content-of:" + p).encode("utf-8")


class TestCLI(unittest.TestCase):
    def run_cli(self, argv):
        from getcode import cli
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(argv)
        return rc, out.getvalue(), err.getvalue()

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    @patch("getcode.cli.copy_text", lambda text: True)
    def test_get_copy_flag(self):
        # Copy by match
        rc, out, err = self.run_cli(["get", "-s", "DSA", "-m", "bst", "--copy"])
        self.assertEqual(rc, 0)
        self.assertIn("copied to clipboard", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    @patch("getcode.cli.copy_text", lambda text: True)
    def test_shorthand_multiple_lists_options(self):
        rc, out, err = self.run_cli(["dsa", "bst", "--copy"])  # multiple matches across versions
        self.assertEqual(rc, 0)
        self.assertIn("Multiple matches", out)
        self.assertIn("DSA/v3/B6_BSTops.cpp", out)
        self.assertIn("DSA/v1/B6_BSTops.cpp", out)
        self.assertNotIn("copied to clipboard", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    @patch.dict(os.environ, {"GETCODE_DEFAULT_ACTION": "copy"}, clear=False)
    @patch("getcode.cli.copy_text", lambda text: True)
    def test_env_default_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Even without --copy flag, with env default, copies instead of saving
            rc, out, err = self.run_cli(["get", "-s", "DSA", "-n", "B6_BSTops.cpp", "--to", tmp])
            self.assertEqual(rc, 0)
            self.assertIn("copied to clipboard", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_subjects(self):
        rc, out, err = self.run_cli(["subjects"])
        self.assertEqual(rc, 0)
        # order follows SUBJECTS constant; both should be present
        self.assertIn("CNS", out)
        self.assertIn("DSA", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_list_latest_version_only(self):
        rc, out, err = self.run_cli(["list", "DSA"])
        self.assertEqual(rc, 0)
        self.assertIn("B6_BSTops.cpp", out)
        self.assertIn("C13_DFSnBFS.cpp", out)
        self.assertNotIn("A1_Telephone_HashTable.py", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_list_all_versions(self):
        rc, out, err = self.run_cli(["list", "DSA", "--all-versions"]) 
        self.assertEqual(rc, 0)
        self.assertIn("[v1]", out)
        self.assertIn("[v3]", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_list_recurses_nested(self):
        rc, out, err = self.run_cli(["list", "CNS"])
        self.assertEqual(rc, 0)
        self.assertIn("tcp_hello.py", out)
        self.assertIn("udp_file_transfer.py", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_search_latest_only(self):
        rc, out, err = self.run_cli(["search", "bst", "--subject", "DSA"]) 
        self.assertEqual(rc, 0)
        # latest path
        self.assertIn("DSA/v3/B6_BSTops.cpp", out)
        self.assertNotIn("DSA/v1/B6_BSTops.cpp", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_search_all_versions(self):
        rc, out, err = self.run_cli(["search", "bst", "--subject", "DSA", "--all-versions"]) 
        self.assertEqual(rc, 0)
        self.assertIn("DSA/v3/B6_BSTops.cpp", out)
        self.assertIn("DSA/v1/B6_BSTops.cpp", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    @patch("getcode.cli.copy_text", lambda text: True)
    def test_shorthand_subject_fetch_copy(self):
        rc, out, err = self.run_cli(["dbms", "ddl", "--copy"])  # shorthand now fetches
        self.assertEqual(rc, 0)
        self.assertIn("copied to clipboard", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_case_insensitive_subject_flags(self):
        rc, out, err = self.run_cli(["list", "dbms"])  # lower-case accepted
        self.assertEqual(rc, 0)
        self.assertIn("assignment_3_ddl_constraints.sql", out)
        rc, out, err = self.run_cli(["search", "ddl", "--subject", "dbms"])  # lower-case flag
        self.assertEqual(rc, 0)
        self.assertIn("assignment_3_ddl_constraints.sql", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    @patch("getcode.cli.copy_text", lambda text: True)
    def test_get_subject_pattern_shorthand(self):
        # Use explicit get with subject+pattern (fetch best match)
        rc, out, err = self.run_cli(["get", "dbms", "ddl", "--copy"]) 
        self.assertEqual(rc, 0)
        self.assertIn("copied to clipboard", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_get_by_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = self.run_cli(["get", "DSA/v3/B6_BSTops.cpp", "--to", tmp])
            self.assertEqual(rc, 0)
            p = Path(tmp) / "DSA" / "v3" / "B6_BSTops.cpp"
            self.assertTrue(p.exists(), f"expected file at {p}")

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_shorthand_path_get(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = self.run_cli(["DSA/v3/B6_BSTops.cpp", "--to", tmp])  # path shorthand
            self.assertEqual(rc, 0)
            p = Path(tmp) / "DSA" / "v3" / "B6_BSTops.cpp"
            self.assertTrue(p.exists())

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_get_subject_exact_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = self.run_cli(["get", "cns", "sliding_window.py", "--to", tmp])
            self.assertEqual(rc, 0)
            p = Path(tmp) / "CNS" / "programs" / "sliding_window.py"
            # Our FakeGitHubClient returns files under CNS/programs; since we save with repo path, ensure exists
            # However, subject exact filename fetch saves according to content path from fake mapping
            self.assertTrue(any(p.name == f.name for f in Path(tmp).rglob("sliding_window.py")), "sliding_window.py not saved")

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_get_by_subject_name_latest(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = self.run_cli(["get", "-s", "DSA", "-n", "B6_BSTops.cpp", "--to", tmp])
            self.assertEqual(rc, 0)
            p = Path(tmp) / "DSA" / "v3" / "B6_BSTops.cpp"
            self.assertTrue(p.exists())

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_get_by_match_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = self.run_cli(["get", "-s", "DSA", "-m", "bst", "--to", tmp])
            self.assertEqual(rc, 0)
            p = Path(tmp) / "DSA" / "v3" / "B6_BSTops.cpp"
            self.assertTrue(p.exists())

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_get_flatten_conflict_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            # save latest first without suffix
            rc, out, err = self.run_cli(["get", "-s", "DSA", "-n", "B6_BSTops.cpp", "-v", "v3", "--to", tmp, "--flatten"]) 
            self.assertEqual(rc, 0)
            p1 = Path(tmp) / "B6_BSTops.cpp"
            self.assertTrue(p1.exists())
            # now save older version; should suffix with -v1
            rc, out, err = self.run_cli(["get", "-s", "DSA", "-n", "B6_BSTops.cpp", "-v", "v1", "--to", tmp, "--flatten"]) 
            self.assertEqual(rc, 0)
            p2 = Path(tmp) / "B6_BSTops-v1.cpp"
            self.assertTrue(p2.exists())

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_info_summary_and_subject(self):
        rc, out, err = self.run_cli(["info", "--all-versions"]) 
        self.assertEqual(rc, 0)
        self.assertIn("DSA: total", out)
        self.assertIn("CNS: total", out)
        rc, out, err = self.run_cli(["info", "--subject", "DSA", "--all-versions"]) 
        self.assertEqual(rc, 0)
        self.assertIn("Subject: DSA", out)
        self.assertIn("Versions:", out)

    @patch("getcode.cli.get_latest_version", lambda: "9.9.9")
    def test_ver_check(self):
        rc, out, err = self.run_cli(["v", "--check"]) 
        self.assertEqual(rc, 0)
        self.assertIn("getcode version:", out)
        self.assertIn("latest: 9.9.9", out)

    @patch("getcode.cli.get_latest_version", lambda: "9.9.9")
    @patch("getcode.cli.upgrade_self")
    def test_ver_upgrade(self, m_up):
        m_up.return_value = subprocess.CompletedProcess(args=["python","-m","pip","install","-U","getcode-cli"], returncode=0, stdout="", stderr="")
        rc, out, err = self.run_cli(["v", "--upgrade"]) 
        self.assertEqual(rc, 0)
        self.assertIn("Upgrading...", out)

    @patch("platform.system", lambda: "Windows")
    @patch("getcode.cli._is_admin_windows", lambda: True)
    def test_wifi_runs_powershell(self):
        # simulate successful powershell toggle via fake run
        def fake_run(args, **kwargs):
            self.assertTrue(isinstance(args, list) and args and "powershell" in args[0].lower())
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="Wi-Fi enabled\n", stderr="")

        with patch("subprocess.run", side_effect=fake_run):
            rc, out, err = self.run_cli(["wifi"]) 
            self.assertEqual(rc, 0)
            self.assertIn("Wi-Fi enabled", out)

    @patch("getcode.cli.GitHubClient", FakeGitHubClient)
    def test_all_subject_downloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = self.run_cli(["all", "DBMS", "--to", tmp])
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmp) / "DBMS" / "assignment_3_ddl_constraints.sql").exists())

    def test_del_deletes_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            # create fake file
            p = Path(tmp) / "keep.txt"
            p.write_text("x")
            # create target dir inside tmp to delete
            target = Path(tmp) / "getcodes"
            target.mkdir()
            rc, out, err = self.run_cli(["del", "--to", str(target)])
            self.assertEqual(rc, 0)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
