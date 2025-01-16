import requests


def fetch_commits(repo_owner, repo_name):
    commits_url = (
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    )
    response = requests.get(commits_url)
    response.raise_for_status()  # Check for request errors
    return response.json()


def write_commits_to_file(commits, file_path):
    with open(file_path, 'w') as file:
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
    repo_owner = "S0L0GUY"
    repo_name = "NOVA-AI"
    file_path = "commits.md"

    commits = fetch_commits(repo_owner, repo_name)
    write_commits_to_file(commits, file_path)
    print(f"Commits have been written to {file_path}")


if __name__ == "__main__":
    main()
