import os
from github import Github
from datetime import datetime
from variables import token, org, IGNORE_LIST

# Initialize GitHub client with your bot's access token
#token = "YOUR_PERSONAL_ACCESS_TOKEN"
g = Github(token)

def check_readme_and_description(repo):
    """
    Check if a repository has a README.md file and a description.
    If not, open an issue on the repository.
    """
    if not repo.get_readme():
        issue = repo.create_issue(
            title="Missing README.md",
            body="This repository is missing a README.md file and/or a description.",
        )
        print("Creating issue because of missing README.md")
        # Notify contributors about the issue
        notify_contributors(repo, issue)
    else:
        # Check if the legal disclaimer is present in README.md
        readme_content = repo.get_readme().decoded_content.decode("utf-8")
        legal_disclaimer = get_legal_disclaimer()
        if legal_disclaimer not in readme_content:
            issue = repo.create_issue(
                title="Missing Legal Disclaimer",
                body="The README.md file does not contain the required legal disclaimer section.",
            )
            print("Creating issue because of missing Legal Disclaimer in README.md")
            # Notify contributors about the issue
            notify_contributors(repo, issue)

def get_legal_disclaimer():
    """
    Read the content of the "legal.md" file.
    """
    # Load the content of the legal disclaimer file
    legal_disclaimer_path = os.path.join(os.path.dirname(__file__), "legal.md")
    with open(legal_disclaimer_path, "r", encoding="utf-8") as legal_file:
        legal_disclaimer = legal_file.read()
    return legal_disclaimer

def check_legal_disclaimer(repo):
    """
    Check if a repository's README.md file contains a legal disclaimer section.
    If not, open an issue on the repository.
    """
    # Get the README.md content
    readme = repo.get_readme().decoded_content.decode("utf-8")

    # Define the expected legal disclaimer content (you can customize this)
    expected_disclaimer = "Legal Disclaimer:"

    # Check if the expected disclaimer is present in the README.md content
    if expected_disclaimer not in readme:
        # If the disclaimer is missing, create an issue
        issue_title = "Missing Legal Disclaimer"
        issue_body = (
            "The README.md file does not contain the required legal disclaimer section.\n"
            "Please ensure that the repository includes an appropriate legal disclaimer."
        )
        issue = repo.create_issue(title=issue_title, body=issue_body)
        # Notify contributors about the issue
        notify_contributors(repo, issue)


def check_last_contribution(repo):
    """
    Check if there has been a code contribution in the last 12 months.
    If not, archive the repository.
    """
    last_commit = repo.get_commits()[0].commit.author.date
    if (datetime.now() - last_commit).days > 365:
        repo.edit(archived=True)
        print(f"Archived repository: {repo.full_name}")

def notify_contributors(repo, issue):
    """
    Assign all repository contributors as assignees to an issue.
    """
    collaborators = [c.login for c in repo.get_collaborators()]

    # Get a list of contributors
    contributors = [contributor.login for contributor in repo.get_contributors()]

    # Filter contributors who are also collaborators
    assignees = [contributor for contributor in contributors if contributor in collaborators]

    # Assign the contributors as assignees to the issue
    issue.edit(assignees=assignees)

if __name__ == "__main__":
    # Replace 'YOUR_ORGANIZATION' with the organization or username where your repositories are located.
    organization = g.get_organization(org)

    for repo in organization.get_repos():
        if repo.archived:
            print(f"Skipping archived repository: {repo.full_name}")
            continue

        if repo.name in IGNORE_LIST:
            print(f"Skipping ignored repository: {repo.full_name}")
            continue

        print("Working on " + str(repo.full_name))
        check_readme_and_description(repo)
        check_legal_disclaimer(repo)
        check_last_contribution(repo)