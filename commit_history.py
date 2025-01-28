"""
GitHub Commit History Module

This module provides functionality to fetch commit history from GitHub
repositories and write it to a markdown file. It uses GitHub's REST API to
retrieve commit information and formats it into a readable markdown document.

Functions:
    fetch_commits(repo_owner, repo_name): Fetches commit data from GitHub
    write_commits_to_file(commits, file_path): Writes commits to markdown
    main(): Entry point that demonstrates the module usage
"""

import requests


def fetch_commits(repo_owner, repo_name):
    """
    Module for fetching commit history from GitHub repositories using the
    GitHub API. This module provides functionality to interact with GitHub's
    REST API to retrieve commit information for specified repositories.
    """

    commits_url = (
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    )
    response = requests.get(commits_url, timeout=10)
    response.raise_for_status()  # Check for request errors
    return response.json()


def write_commits_to_file(commits, file_path):
    """
    Module for handling Git commit history and writing it to a file in
    Markdown format. This module provides functionality to create a formatted
    commit history log.
    """

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("# Commit History\n\n")
        for commit in commits:
            sha = commit['sha']
            message = commit['commit']['message']
            author = commit['commit']['author']['name']
            url = commit['html_url']
            file.write(f"- **Commit:** [{sha[:7]}]({url})\n")
            file.write(f"  **Author:** {author}\n")
            file.write(f"  **Message:** {message}\n\n")


def main():
    """
    Main function to fetch and write GitHub repository commits to a file.
    The function uses predefined repository details:
    - Repository owner: "S0L0GUY"
    - Repository name: "NOVA-AI"
    - Output file path: "commits.md"
    It fetches all commits from the specified repository and writes them to a
    markdown file.
    Requires:
    - fetch_commits() function to get commits from GitHub
    - write_commits_to_file() function to write commits to file
    Prints a confirmation message once the commits are written to the file.
    """

    repo_owner = "S0L0GUY"
    repo_name = "NOVA-AI"
    file_path = "commits.md"

    commits = fetch_commits(repo_owner, repo_name)
    write_commits_to_file(commits, file_path)
    print(f"Commits have been written to {file_path}")


if __name__ == "__main__":
    main()
