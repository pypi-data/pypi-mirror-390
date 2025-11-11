from os import getenv
from typing import Optional, Self

from github import Auth, Github, GithubException, UnknownObjectException
from github.ContentFile import ContentFile


class GithubUtils:
    """Utility class for interacting with GitHub repositories.

    Attributes:
        _GITHUB_RAW_TEMPLATE: Template for constructing raw GitHub URLs.
        repository: The GitHub repository object.
        branch: The branch object of the repository.
        url_template: The base URL for accessing raw files in the repository.
    """

    _GITHUB_RAW_TEMPLATE = "https://raw.githubusercontent.com/{}/refs/heads/{}/"

    def __init__(self: Self, repository_name: str, branch_name: Optional[str] = None) -> None:
        """Initializes the GitHub utility with the specified repository and branch.

        Args:
            repository_name: The name of the GitHub repository.
            branch_name: The name of the branch to use. If not provided, the default branch is used.

        Raises:
            AttributeError: If the repository or branch cannot be accessed.
        """
        auth_token = getenv("GITHUB_AUTH_TOKEN")
        auth = None
        if auth_token is not None:
            auth = Auth.Token(auth_token)

        self._github = Github(auth=auth)
        try:
            self.repository = self._github.get_repo(repository_name)
            self.branch = self.repository.get_branch(branch_name if branch_name else self.repository.default_branch)
            self.url_template = self._GITHUB_RAW_TEMPLATE.format(repository_name, self.branch.name)
        except (UnknownObjectException, GithubException):
            raise AttributeError

    def get_raw_url(self: Self) -> str:
        """Returns the base URL for accessing raw files in the repository.

        Returns:
            str: The base URL for raw files.
        """
        return self.url_template

    def list_directories(self: Self, path: str) -> Optional[list[str]]:
        """Lists directories in the specified path of the repository.

        Args:
            path: The path within the repository to list directories from.

        Returns:
            Optional[list[str]]: A list of directory paths, or None if the path is invalid or contains no directories.
        """
        try:
            content = self.repository.get_contents(path, self.branch.name)
        except UnknownObjectException:
            return None

        if isinstance(content, ContentFile):
            return None

        dirs = []
        for element in content:
            if element.type == "dir":
                dirs.append(element.path)

        return dirs

    def list_files(self: Self, path: str) -> Optional[list[str]]:
        """Lists files in the specified path of the repository.

        Args:
            path: The path within the repository to list files from.

        Returns:
            Optional[list[str]]: A list of file paths, or None if the path is invalid or contains no files.
        """
        try:
            content = self.repository.get_contents(path, self.branch.name)
        except UnknownObjectException:
            return None

        if isinstance(content, ContentFile):
            return [content.path]

        files = []
        for element in content:
            if element.type == "file":
                files.append(element.path)

        return files
