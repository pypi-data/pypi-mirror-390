import os
import subprocess
import time
from pathlib import Path


class GitAutoCommitter:
    """Committer.

    A class to automatically commit changes in a Git repository.
    Supports both direct Git commands and custom aliases like 'acp'.
    """

    def __init__(self, repo_path):
        """Initialize the auto-committer with a repository path.

        Args:
            repo_path (str): Path to the Git repository
        """
        self.repo_path = Path(repo_path).resolve()
        self.original_dir = Path.cwd()

    def check_git_repo(self) -> bool:
        """Check if the given path is a valid Git repository.

        Returns:
            bool: True if it's a Git repository, False otherwise
        """
        git_dir = self.repo_path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def has_changes(self) -> bool:
        """Check if there are uncommitted changes in the repository.

        Returns:
            bool: True if there are changes, False otherwise
        """
        try:
            os.chdir(self.repo_path)
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            return bool(result.stdout.strip())
        finally:
            os.chdir(self.original_dir)

    def auto_check(self, remote="origin", branch=None) -> bool:
        """Check if local repository is in sync with remote repository.

        Args:
            remote (str): Remote repository name (default: "origin")
            branch (str): Branch name to check. If None, uses current branch.

        Returns:
            bool: True if local and remote are in sync, False if there are differences
        """
        if not self.check_git_repo():
            print(f"Error: {self.repo_path} is not a Git repository")
            return False

        try:
            os.chdir(self.repo_path)

            # Get current branch if not specified
            if branch is None:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True, text=True, check=True
                )
                branch = branch_result.stdout.strip()

            # Fetch latest remote information
            subprocess.run(["git", "fetch", remote], check=True, capture_output=True)

            # Compare local and remote commits
            local_ref = f"refs/heads/{branch}"
            remote_ref = f"refs/remotes/{remote}/{branch}"

            # Get commit hashes
            local_hash = subprocess.run(
                ["git", "rev-parse", local_ref],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            remote_hash = subprocess.run(
                ["git", "rev-parse", remote_ref],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Return True if hashes are identical
            return local_hash == remote_hash

        except subprocess.CalledProcessError as e:
            print(f"Error checking repository sync: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during sync check: {e}")
            return False
        finally:
            os.chdir(self.original_dir)

    def auto_pull(self, remote="origin", branch=None) -> bool:
        """Automatically pull the latest changes from the remote repository.

        Args:
            remote (str): Remote repository name (default: "origin")
            branch (str): Branch name to pull from. If None, uses current branch.

        Returns:
            bool: True if pull was successful, False otherwise
        """
        if not self.check_git_repo():
            print(f"Error: {self.repo_path} is not a Git repository")
            return False

        try:
            os.chdir(self.repo_path)

            # Get current branch if not specified
            if branch is None:
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True, text=True, check=True
                )
                branch = branch_result.stdout.strip()

            # Build pull command
            pull_command = ["git", "pull"]
            pull_command.extend([remote, branch])

            print(f"Pulling from {remote}/{branch}...")
            result = subprocess.run(pull_command, check=True, text=True)

            if result.returncode == 0:
                print(f"Successfully pulled from {remote}/{branch}")
                return True
            else:
                print(f"Pull completed with return code: {result.returncode}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"Git pull failed: {e}")
            if "conflict" in e.stderr.lower() or "conflict" in e.stdout.lower():
                print("Merge conflicts detected! Please resolve them manually.")
            return False
        except Exception as e:
            print(f"An error occurred during pull: {e}")
            return False
        finally:
            os.chdir(self.original_dir)

    def auto_commit(self, commit_message=None) -> bool:
        """Automatically commit changes using direct Git commands.

        Args:
            commit_message (str, optional): Commit message. If None, uses auto-generated message.

        Returns:
            bool: True if commit was successful, False otherwise
        """
        if not self.check_git_repo():
            print(f"Error: {self.repo_path} is not a Git repository")
            return False

        if not self.has_changes():
            print("No changes to commit")
            return True

        # Generate default commit message if none provided
        if not commit_message:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto commit {timestamp}"

        try:
            os.chdir(self.repo_path)

            # Execute git add . to stage all changes
            subprocess.run(["git", "add", "."], check=True)

            # Execute git commit with the provided message
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            print(f"Successfully committed: {commit_message}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            os.chdir(self.original_dir)

    def auto_push(self, remote="origin", branch="main") -> bool:
        """Automatically push to remote repository.

        Args:
            remote (str): Remote repository name (default: "origin")
            branch (str): Branch name (default: "main")

        Returns:
            bool: True if push was successful, False otherwise
        """
        if not self.check_git_repo():
            print(f"Error: {self.repo_path} is not a Git repository")
            return False

        try:
            os.chdir(self.repo_path)

            # Push to remote repository
            subprocess.run(["git", "push", remote, branch], check=True)

            print(f"Successfully pushed to {remote}/{branch}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Git push failed: {e}")
            return False
        except Exception as e:
            print(f"An error occurred during push: {e}")
            return False
        finally:
            os.chdir(self.original_dir)
