import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Literal

import frontmatter
import markdown2
import questionary
from bs4 import BeautifulSoup
from langchain_text_splitters import MarkdownHeaderTextSplitter

Repo = Literal['pydantic-ai', 'logfire']
repos: tuple[Repo, ...] = 'pydantic-ai', 'logfire'

REPO_URLS = {
    'pydantic-ai': 'https://github.com/pydantic/pydantic-ai.git',
    'logfire': 'https://github.com/pydantic/logfire.git',
}


def get_docs_base_dir() -> Path:
    """Get the base directory for storing documentation."""
    docs_dir = Path.home() / '.ask-pydantic' / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)
    return docs_dir


def get_docs_dir(repo: Repo) -> Path:
    """Get the docs directory for a specific repo."""
    result = get_docs_base_dir() / repo / 'docs'
    if not result.exists():
        # Try to clone the docs
        if not prompt_and_clone_docs():
            raise ValueError(
                f'Documentation for {repo} not found. '
                f'Please run the tool again and allow it to download the documentation.'
            )
    return result


def docs_exist() -> bool:
    """Check if any documentation has been cloned."""
    base_dir = get_docs_base_dir()
    for repo in repos:
        docs_dir = base_dir / repo / 'docs'
        if docs_dir.exists() and list(docs_dir.rglob('*.md')):
            return True
    return False


def prompt_and_clone_docs() -> bool:
    """
    Prompt the user for consent to clone documentation repositories.
    Returns True if docs were cloned or already exist, False if user declined.
    """
    if docs_exist():
        return True

    print('\n📚 Documentation not found')
    print(
        f'   This tool needs to download documentation from Pydantic AI and Logfire repositories.'
    )
    print(f'   Total size: ~20MB (docs only, not full repositories)')
    print()

    should_clone = questionary.confirm(
        'Download documentation now?',
        default=True,
    ).ask()

    if not should_clone:
        print('❌ Cannot proceed without documentation')
        return False

    print('\n📥 Downloading documentation...')
    success = True
    for repo in repos:
        if not clone_repo_docs(repo):
            success = False

    if success:
        print('✅ Documentation downloaded successfully\n')
    else:
        print('❌ Failed to download some documentation\n')

    return success


def clone_repo_docs(repo: Repo) -> bool:
    """
    Clone only the docs directory from a repository using sparse checkout.
    Returns True on success, False on failure.
    """
    base_dir = get_docs_base_dir()
    repo_dir = base_dir / repo

    # Check if already cloned
    docs_dir = repo_dir / 'docs'
    if docs_dir.exists() and list(docs_dir.rglob('*.md')):
        return True

    try:
        print(f'   Cloning {repo} docs...')

        # Remove repo dir if it exists but is incomplete
        if repo_dir.exists():
            import shutil

            shutil.rmtree(repo_dir)

        # Initialize git repo
        subprocess.run(
            ['git', 'init', str(repo_dir)],
            check=True,
            capture_output=True,
        )

        # Configure sparse checkout
        subprocess.run(
            ['git', '-C', str(repo_dir), 'config', 'core.sparseCheckout', 'true'],
            check=True,
            capture_output=True,
        )

        # Specify docs directory only
        sparse_checkout_file = repo_dir / '.git' / 'info' / 'sparse-checkout'
        sparse_checkout_file.write_text('docs/\n')

        # Add remote
        subprocess.run(
            [
                'git',
                '-C',
                str(repo_dir),
                'remote',
                'add',
                'origin',
                REPO_URLS[repo],
            ],
            check=True,
            capture_output=True,
        )

        # Pull docs only
        subprocess.run(
            [
                'git',
                '-C',
                str(repo_dir),
                'pull',
                '--depth=1',
                'origin',
                'main',
            ],
            check=True,
            capture_output=True,
        )

        return True

    except subprocess.CalledProcessError as e:
        print(f'   ⚠️  Failed to clone {repo}: {e}')
        return False
    except Exception as e:
        print(f'   ⚠️  Unexpected error cloning {repo}: {e}')
        return False


IGNORED_FILES = 'release-notes.md', 'help.md', '/api/', '/legal/'


def get_docs_files(repo: Repo) -> list[Path]:
    return [
        file
        for file in get_docs_dir(repo).rglob('*.md')
        if not any(ignored in str(file) for ignored in IGNORED_FILES)
    ]


def get_markdown(path: Path) -> str:
    markdown_string = path.read_text()
    markdown_string = frontmatter.loads(markdown_string).content
    return markdown_string


def get_table_of_contents(repo: Repo):
    """Get a list of all docs files and a preview of the sections within."""
    result = ''
    for file in get_docs_files(repo):
        markdown_string = get_markdown(file)
        markdown_string = re.sub(
            r'^```\w+ [^\n]+$', '```', markdown_string, flags=re.MULTILINE
        )
        html_output = markdown2.markdown(markdown_string, extras=['fenced-code-blocks'])  # type: ignore
        soup = BeautifulSoup(html_output, 'html.parser')
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        result += f'{file.relative_to(get_docs_dir(repo))}\n'
        result += '\n'.join(
            '#'
            * int(
                header.name[1]  # type: ignore
            )
            + ' '
            + header.get_text()
            for header in headers
        )
        result += '\n\n'
    return result


headers_to_split_on = [('#' * n, f'H{n}') for n in range(1, 7)]


def get_docs_rows(repo: Repo) -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = []
    for file in get_docs_files(repo):
        markdown_document = get_markdown(file)
        rel_path = str(file.relative_to(get_docs_dir(repo)))

        unique: set[tuple[tuple[str, ...], str]] = set()
        for num_headers in range(len(headers_to_split_on)):
            splitter = MarkdownHeaderTextSplitter(headers_to_split_on[:num_headers])
            splits = splitter.split_text(markdown_document)
            for split in splits:
                metadata: dict[str, Any] = split.metadata  # type: ignore
                headers = [
                    f'{prefix} {metadata[header_type]}'
                    for prefix, header_type in headers_to_split_on
                    if header_type in metadata
                ]
                content = '\n\n'.join([rel_path, *headers, split.page_content])
                if len(content.encode()) > 16384:
                    continue
                unique.add((tuple(headers), content))

        counts = Counter[tuple[str, ...]]()
        for headers, content in sorted(unique):
            counts[headers] += 1
            count = str(counts[headers])
            data.append(
                dict(
                    path=rel_path,
                    headers=headers,
                    text=content,
                    count=count,
                )
            )

    return data


if __name__ == '__main__':
    print(get_table_of_contents('logfire'))
    rows = get_docs_rows('logfire')
    print(f'Generated {len(rows)} rows')
