import requests


def fetch_commits(repo_owner: str, repo_name: str) -> list:
    """
    Fetch the commit history of a given GitHub repository.
    Args:
        repo_owner (str): The owner of the GitHub repository (username or
        organization name).
        repo_name (str): The name of the GitHub repository.
    Returns:
        list: A list of commit data in JSON format, where each item represents
        a commit.
    Raises:
        requests.exceptions.RequestException: If the HTTP request fails or
        encounters an error.
    """

    commits_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    response = requests.get(commits_url, timeout=10)
    response.raise_for_status()

    return response.json()


def write_commits_to_file(commits: list, file_path: str) -> None:
    """
    Writes a list of commit information to a markdown file.
    Args:
        commits (list): A list of dictionaries containing commit information.
                        Each dictionary should have the following keys:
                        - 'sha' (str): The commit SHA hash.
                        - 'commit' (dict): A dictionary containing:
                            - 'message' (str): The commit message.
                            - 'author' (dict): A dictionary containing:
                                - 'name' (str): The author's name.
                        - 'html_url' (str): The URL to the commit on a
                        repository hosting service.
        file_path (str): The path to the file where the commit history will be
        written.
    The output file will be in markdown format, with each commit including:
    - A short SHA hash linked to the commit URL.
    - The author's name.
    - The commit message.
    """

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("# Commit History\n\n")
        for commit in commits:
            sha = commit["sha"]
            message = commit["commit"]["message"]
            author = commit["commit"]["author"]["name"]
            url = commit["html_url"]
            file.write(f"- **Commit:** [{sha[:7]}]({url})\n")
            file.write(f"  **Author:** {author}\n")
            file.write(f"  **Message:** {message}\n\n")


def main() -> None:
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
