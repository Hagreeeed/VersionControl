import os
import hashlib
import json
import argparse
from datetime import datetime


class VersionControlSystem:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo_meta = os.path.join(repo_path, ".vcs")
        self.files_dir = os.path.join(self.repo_meta, "files")
        self.commits_file = os.path.join(self.repo_meta, "commits.json")

        if not os.path.exists(self.repo_meta):
            os.makedirs(self.files_dir)
            with open(self.commits_file, "w") as f:
                json.dump([], f)

    def add_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        with open(file_path, "rb") as f:
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()

        dest_path = os.path.join(self.files_dir, file_hash)
        if not os.path.exists(dest_path):
            with open(dest_path, "wb") as f:
                f.write(content)

        return file_hash

    def commit(self, message, files):
        timestamp = datetime.now().isoformat()
        commit_data = {
            "timestamp": timestamp,
            "message": message,
            "files": files
        }

        with open(self.commits_file, "r") as f:
            commits = json.load(f)

        commits.append(commit_data)

        with open(self.commits_file, "w") as f:
            json.dump(commits, f, indent=4)

        return commit_data

    def get_commits(self):
        with open(self.commits_file, "r") as f:
            return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Version Control System")
    parser.add_argument("command", choices=["init", "add", "commit", "log"], help="Command to execute")
    parser.add_argument("--repo", default="./repo", help="Path to the repository")
    parser.add_argument("--file", help="File to add")
    parser.add_argument("--message", help="Commit message")

    args = parser.parse_args()
    vcs = VersionControlSystem(args.repo)

    if args.command == "init":
        if not os.path.exists(args.repo):
            os.makedirs(args.repo)
        vcs = VersionControlSystem(args.repo)
        print(f"Initialized empty VCS repository in {args.repo}")

    elif args.command == "add":
        if not args.file:
            print("Error: --file argument is required for 'add' command")
        else:
            try:
                file_hash = vcs.add_file(args.file)
                print(f"File {args.file} added with hash: {file_hash}")
            except FileNotFoundError as e:
                print(e)

    elif args.command == "commit":
        if not args.message:
            print("Error: --message argument is required for 'commit' command")
        else:
            with open(vcs.commits_file, "r") as f:
                previous_commits = json.load(f)

            files = []
            if previous_commits:
                files = [file for commit in previous_commits for file in commit["files"]]

            commit_data = vcs.commit(args.message, files)
            print(f"Commit created: {commit_data}")

    elif args.command == "log":
        commits = vcs.get_commits()
        if not commits:
            print("No commits found.")
        else:
            print("Commit log:")
            for commit in commits:
                print(f"Timestamp: {commit['timestamp']}")
                print(f"Message: {commit['message']}")
                print(f"Files: {commit['files']}")
                print("---")
