import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "hooks" / "enforce.py"


def run(agent, tool, tool_input, tests_glob=None):
    with tempfile.TemporaryDirectory() as project:
        if tests_glob is not None:
            (pathlib.Path(project) / "agentic.toml").write_text(
                f'[paths]\ntests = ["{tests_glob}"]\n')
        event = {"cwd": project, "tool_name": tool, "tool_input": tool_input}
        if agent:
            event["agent_type"] = agent
        done = subprocess.run([sys.executable, str(SCRIPT)],
                              input=json.dumps(event), capture_output=True,
                              text=True)
        assert done.returncode == 0, done.stderr
        if not done.stdout.strip():
            return None
        out = json.loads(done.stdout)["hookSpecificOutput"]
        assert out["hookEventName"] == "PreToolUse"
        return out["permissionDecision"], out["permissionDecisionReason"]


def edit(agent, path, tests="tests/**"):
    return run(agent, "Edit", {"file_path": path}, tests)


def bash(agent, command):
    return run(agent, "Bash", {"command": command})


class MainSession(unittest.TestCase):
    def test_a_call_with_no_agent_passes(self):
        self.assertIsNone(run(None, "Bash", {"command": "git push"}))

    def test_an_unlisted_agent_passes(self):
        self.assertIsNone(bash("Explore", "git push"))


class FileRules(unittest.TestCase):
    def test_tdd_maestro_may_edit_a_test_file(self):
        self.assertIsNone(edit("tdd-maestro", "tests/unit/a_test.py"))

    def test_tdd_maestro_may_not_edit_other_files(self):
        self.assertEqual(edit("tdd-maestro", "src/a.py")[0], "deny")

    def test_code_fu_may_edit_other_files(self):
        self.assertIsNone(edit("code-fu", "src/a.py"))

    def test_code_fu_may_not_edit_a_test_file(self):
        self.assertEqual(edit("code-fu", "tests/unit/a_test.py")[0], "deny")

    def test_without_paths_tests_both_are_denied(self):
        for agent in ("tdd-maestro", "code-fu"):
            result = run(agent, "Edit", {"file_path": "src/a.py"}, None)
            self.assertEqual(result[0], "deny")
            self.assertIn("paths.tests", result[1])

    def test_a_plugin_scoped_agent_name_is_recognised(self):
        self.assertEqual(edit("agentic:code-fu", "tests/a_test.py")[0], "deny")

    def test_the_reason_names_the_agent(self):
        self.assertIn("code-fu", edit("code-fu", "tests/a_test.py")[1])

    def test_other_agents_cannot_edit_but_are_not_checked_here(self):
        self.assertIsNone(edit("test-runner", "src/a.py"))


class CommandRules(unittest.TestCase):
    def test_task_scoper_may_use_gh_issue(self):
        self.assertIsNone(bash("task-scoper", "gh issue create --title x"))

    def test_task_scoper_may_use_the_sub_issues_endpoint(self):
        self.assertIsNone(bash(
            "task-scoper",
            "gh api -X POST repos/o/r/issues/1/sub_issues -F sub_issue_id=2"))

    def test_task_scoper_may_not_use_git_push(self):
        self.assertEqual(bash("task-scoper", "git push")[0], "deny")

    def test_coders_may_not_push_or_use_gh(self):
        for agent in ("tdd-maestro", "code-fu"):
            self.assertEqual(bash(agent, "git push origin x")[0], "deny")
            self.assertEqual(bash(agent, "gh pr create")[0], "deny")
            self.assertIsNone(bash(agent, "pytest -q"))

    def test_test_runner_may_not_use_git_or_gh(self):
        self.assertEqual(bash("test-runner", "git status")[0], "deny")
        self.assertEqual(bash("test-runner", "gh pr view")[0], "deny")
        self.assertIsNone(bash("test-runner", "ctest --preset debug"))

    def test_pr_evaluator_is_read_only_git(self):
        self.assertIsNone(bash("pr-evaluator", "git diff main...HEAD"))
        self.assertEqual(bash("pr-evaluator", "git commit -m x")[0], "deny")

    def test_committer_may_add_and_commit_but_not_push(self):
        self.assertIsNone(bash("committer", "git add a.py && git commit -m x"))
        self.assertEqual(bash("committer", "git push")[0], "deny")

    def test_pr_create_may_push_and_create(self):
        self.assertIsNone(bash("pr-create", "git push -u origin x"))
        self.assertIsNone(bash("pr-create", "gh pr create --title x"))
        self.assertEqual(bash("pr-create", "gh pr merge 1")[0], "deny")

    def test_pr_reviewer_reads_only(self):
        self.assertIsNone(bash("pr-reviewer", "gh pr diff 1"))
        self.assertEqual(bash("pr-reviewer", "gh pr merge 1")[0], "deny")

    def test_merge_evaluator_reads_only(self):
        self.assertIsNone(bash("merge-evaluator", "gh pr checks 1"))
        self.assertEqual(bash("merge-evaluator", "gh pr merge 1")[0], "deny")

    def test_merger_mage_merges_and_closes(self):
        self.assertIsNone(bash("merger-mage", "gh pr merge 1 --rebase"))
        self.assertIsNone(bash("merger-mage", "gh issue close 2"))
        self.assertEqual(bash("merger-mage", "git push")[0], "deny")

    def test_every_part_of_a_compound_command_is_checked(self):
        self.assertEqual(
            bash("pr-evaluator", "git status && git push")[0], "deny")
        self.assertEqual(bash("code-fu", "pytest | git push")[0], "deny")

    def test_a_leading_assignment_is_skipped(self):
        self.assertEqual(bash("code-fu", "A=1 git push")[0], "deny")


class Worktree(unittest.TestCase):
    def test_agentic_toml_is_found_in_the_main_checkout(self):
        with tempfile.TemporaryDirectory() as root:
            main = pathlib.Path(root) / "main"
            tree = pathlib.Path(root) / "tree"
            main.mkdir()
            git = lambda *a: subprocess.run(
                ["git", "-C", str(main), "-c", "user.name=t",
                 "-c", "user.email=t@t", *a], check=True, capture_output=True)
            git("init", "-q")
            git("commit", "-q", "--allow-empty", "-m", "x")
            git("worktree", "add", "-q", str(tree))
            (main / "agentic.toml").write_text('[paths]\ntests = ["tests/**"]\n')
            event = {"cwd": str(tree), "agent_type": "tdd-maestro",
                     "tool_name": "Edit",
                     "tool_input": {"file_path": "tests/a_test.py"}}
            done = subprocess.run([sys.executable, str(SCRIPT)],
                                  input=json.dumps(event), capture_output=True,
                                  text=True)
            self.assertEqual(done.stdout.strip(), "")


def dry(tool, tool_input, agent=None, runs=".agentic", config=None):
    """Run the hook in a project that has a dry-run marker."""
    with tempfile.TemporaryDirectory() as project:
        root = pathlib.Path(project)
        if config:
            (root / "agentic.toml").write_text(config)
        marker = root / runs / "123-x" / "dry-run"
        marker.parent.mkdir(parents=True)
        marker.write_text("")
        event = {"cwd": project, "tool_name": tool, "tool_input": tool_input}
        if agent:
            event["agent_type"] = agent
        done = subprocess.run([sys.executable, str(SCRIPT)],
                              input=json.dumps(event), capture_output=True,
                              text=True)
        assert done.returncode == 0, done.stderr
        if not done.stdout.strip():
            return None
        return json.loads(done.stdout)["hookSpecificOutput"][
            "permissionDecision"]


def dry_bash(command, agent=None, **kw):
    return dry("Bash", {"command": command}, agent, **kw)


class DryRun(unittest.TestCase):
    def test_remote_commands_are_denied_for_the_main_session(self):
        for command in ("git push origin x", "gh pr create", "gh pr merge 1",
                        "gh issue create --title x", "gh issue edit 1",
                        "gh issue comment 1 -b x", "gh issue close 1",
                        "gh label create x"):
            self.assertEqual(dry_bash(command), "deny", command)

    def test_remote_commands_are_denied_for_an_agent_that_may_run_them(self):
        self.assertEqual(dry_bash("git push", "pr-create"), "deny")
        self.assertEqual(dry_bash("gh pr merge 1", "merger-mage"), "deny")

    def test_reads_and_local_work_still_pass(self):
        for command in ("git commit -m x", "git status", "pytest -q",
                        "gh issue view 1", "gh issue list", "gh pr view 1",
                        "gh repo view",
                        "gh api repos/o/r/issues/1/sub_issues"):
            self.assertIsNone(dry_bash(command), command)

    def test_gh_api_that_changes_something_is_denied(self):
        for command in ("gh api -X POST repos/o/r/issues/1/sub_issues",
                        "gh api --method PATCH repos/o/r/issues/1",
                        "gh api repos/o/r/issues -f title=x",
                        "gh api repos/o/r/issues -F title=x"):
            self.assertEqual(dry_bash(command), "deny", command)

    def test_saving_to_memory_is_denied(self):
        self.assertEqual(
            dry("mcp__plugin_engram_engram__mem_save", {}), "deny")

    def test_memory_search_still_passes(self):
        self.assertIsNone(
            dry("mcp__plugin_engram_engram__mem_search", {}))

    def test_the_marker_is_found_under_paths_runs(self):
        self.assertEqual(
            dry_bash("git push", runs="runs",
                     config='[paths]\nruns = "runs"\n'), "deny")

    def test_the_reason_says_dry_run(self):
        with tempfile.TemporaryDirectory() as project:
            marker = pathlib.Path(project) / ".agentic" / "t" / "dry-run"
            marker.parent.mkdir(parents=True)
            marker.write_text("")
            event = {"cwd": project, "tool_name": "Bash",
                     "tool_input": {"command": "git push"}}
            done = subprocess.run([sys.executable, str(SCRIPT)],
                                  input=json.dumps(event),
                                  capture_output=True, text=True)
            self.assertIn("dry run", done.stdout)

    def test_without_a_marker_nothing_changes(self):
        self.assertIsNone(run(None, "Bash", {"command": "git push"}))


if __name__ == "__main__":
    unittest.main()
