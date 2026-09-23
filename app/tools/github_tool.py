import io
import zipfile
import requests


class GitHubTool:
    """
    GitHub repository tool.

    Uses GitHub's public codeload ZIP endpoint instead
    of relying on the GitHub REST API for source files.
    """

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "RepoInsight-Agent/1.0",
            "Accept": "*/*"
        })

        # Cache downloaded repositories
        self.repo_cache = {}

    # =========================================================
    # DOWNLOAD REPOSITORY
    # =========================================================

    def _download_repository(
        self,
        owner: str,
        repo: str,
        branch: str = "main"
    ):
        """
        Download the public GitHub repository as a ZIP.
        """

        cache_key = f"{owner}/{repo}/{branch}"

        if cache_key in self.repo_cache:
            return self.repo_cache[cache_key]

        url = (
            f"https://codeload.github.com/"
            f"{owner}/{repo}/zip/refs/heads/{branch}"
        )

        print(
            f"[DOWNLOAD] Fetching repository archive..."
        )

        response = self.session.get(
            url,
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"GitHub repository download failed "
                f"with status {response.status_code}"
            )

        try:
            archive = zipfile.ZipFile(
                io.BytesIO(response.content)
            )

        except zipfile.BadZipFile:
            raise RuntimeError(
                "Downloaded GitHub archive is invalid."
            )

        self.repo_cache[cache_key] = archive

        print(
            f"[DOWNLOAD] Repository downloaded successfully."
        )

        return archive

    # =========================================================
    # GET REPOSITORY INFORMATION
    # =========================================================

    def get_repo_info(
        self,
        owner: str,
        repo: str
    ) -> dict:

        # Try common branches.
        branches = [
            "main",
            "master"
        ]

        archive = None
        selected_branch = None

        last_error = None

        for branch in branches:

            try:

                archive = self._download_repository(
                    owner,
                    repo,
                    branch
                )

                selected_branch = branch
                break

            except Exception as error:
                last_error = error

        if archive is None:
            raise RuntimeError(
                f"Could not download repository: "
                f"{last_error}"
            )

        # Infer primary language from source files.
        language = self._detect_language(
            archive
        )

        return {
            "name": f"{owner}/{repo}",
            "description": (
                "Public GitHub repository analyzed "
                "by RepoInsight."
            ),
            "stars": "Unavailable without GitHub API",
            "language": language,
            "default_branch": selected_branch
        }

    # =========================================================
    # DETECT PRIMARY LANGUAGE
    # =========================================================

    def _detect_language(
        self,
        archive
    ) -> str:

        extension_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".go": "Go",
            ".rs": "Rust",
            ".php": "PHP",
            ".rb": "Ruby"
        }

        counts = {}

        for name in archive.namelist():

            lower_name = name.lower()

            for extension, language in extension_map.items():

                if lower_name.endswith(extension):

                    counts[language] = (
                        counts.get(language, 0) + 1
                    )

                    break

        if not counts:
            return "Unknown"

        return max(
            counts,
            key=counts.get
        )

    # =========================================================
    # LIST FILES
    # =========================================================

    def list_files(
        self,
        owner: str,
        repo: str,
        path: str = ""
    ) -> list:

        archive = self._download_repository(
            owner,
            repo,
            "main"
        )

        results = []

        prefix = path.strip("/")

        for archive_name in archive.namelist():

            normalized = archive_name.replace(
                "\\",
                "/"
            )

            parts = normalized.split("/")

            # Remove root folder from ZIP
            if len(parts) <= 1:
                continue

            relative_path = "/".join(
                parts[1:]
            )

            if prefix:

                if not relative_path.startswith(
                    prefix.rstrip("/") + "/"
                ):
                    continue

                remaining = relative_path[
                    len(prefix.rstrip("/")) + 1:
                ]

            else:

                remaining = relative_path

            if "/" in remaining:
                first = remaining.split("/")[0]

                results.append({
                    "name": first,
                    "path": (
                        f"{prefix}/{first}"
                        if prefix
                        else first
                    ),
                    "type": "dir",
                    "download_url": None
                })

            else:

                results.append({
                    "name": remaining,
                    "path": relative_path,
                    "type": "file",
                    "download_url": None
                })

        # Remove duplicates
        unique = {}

        for item in results:

            key = (
                item["path"],
                item["type"]
            )

            unique[key] = item

        return list(
            unique.values()
        )

    # =========================================================
    # RECURSIVE SOURCE FILE DISCOVERY
    # =========================================================

    def list_source_files(
        self,
        owner: str,
        repo: str,
        path: str = ""
    ) -> list:

        archive = self._download_repository(
            owner,
            repo,
            "main"
        )

        source_extensions = (
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
            ".php",
            ".rb"
        )

        ignored_directories = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "dist",
            "build",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            "site-packages"
        }

        files = []

        for archive_name in archive.namelist():

            normalized = archive_name.replace(
                "\\",
                "/"
            )

            parts = normalized.split("/")

            if len(parts) <= 1:
                continue

            relative_path = "/".join(
                parts[1:]
            )

            # Skip directories
            if normalized.endswith("/"):
                continue

            # Skip unwanted directories
            if any(
                directory in ignored_directories
                for directory in parts
            ):
                continue

            if not relative_path.lower().endswith(
                source_extensions
            ):
                continue

            files.append({
                "name": parts[-1],
                "path": relative_path,
                "type": "file",
                "download_url": None
            })

        return files

    # =========================================================
    # GET FILE CONTENT
    # =========================================================

    def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: str = "main"
    ) -> str:

        archive = self._download_repository(
            owner,
            repo,
            branch
        )

        normalized_path = path.replace(
            "\\",
            "/"
        ).lstrip("/")

        # GitHub ZIP contains a root folder.
        candidates = []

        for archive_name in archive.namelist():

            normalized_name = archive_name.replace(
                "\\",
                "/"
            )

            if normalized_name.endswith(
                "/" + normalized_path
            ):
                candidates.append(
                    normalized_name
                )

        if not candidates:
            raise RuntimeError(
                f"File not found in repository: "
                f"{path}"
            )

        archive_path = candidates[0]

        try:

            data = archive.read(
                archive_path
            )

            return data.decode(
                "utf-8",
                errors="replace"
            )

        except Exception as error:

            raise RuntimeError(
                f"Could not read file {path}: "
                f"{error}"
            )