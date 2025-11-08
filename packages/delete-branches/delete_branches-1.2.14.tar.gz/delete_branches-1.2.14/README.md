# delete-branches

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/11071/badge)](https://www.bestpractices.dev/projects/11071)
[![CI](https://github.com/tagdots/delete-branches/actions/workflows/ci.yaml/badge.svg)](https://github.com/tagdots/delete-branches/actions/workflows/ci.yaml)
[![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/delete-branches/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/delete-github-branches)
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/delete-branches/refs/heads/badges/badges/coverage.json)](https://github.com/tagdots/delete-branches/actions/workflows/cron-tasks.yaml)

<br>

## ✅ What does delete-branches do?
**delete-branches** deletes idle branches in GitHub repository.

_**exemptions**_: `default branch`, `protected branches`, `head branches in PR`, and `user-specified exclude branches`

<br>

## ⭐ Why switch to delete-branches?
- we reduce your supply chain risks with [openssf best practices](https://best.openssf.org) in our SDLC and operations.
- we share evidence of code coverage results in action (click _Code Coverage » cron-tasks » badge-coverage_).
- we can run using [command line](https://github.com/tagdots/delete-branches?tab=readme-ov-file#-running-delete-branches-from-command-line) or GitHub Action [Delete GitHub Branches](https://github.com/marketplace/actions/delete-github-branches).

<br>

## 🏃 Running _delete-branches_ in GitHub action
Use the workflow examples below to create your own workflow inside `.github/workflows/`.

<br>

### Example 1 - Summary (MOCK delete)

| Input | Workflow Spec | Notes
|-------|-------------|----------|
| `scheduled run` | `- cron: '30 17 * * *'` | Run daily at 5:30 pm UTC
| `github token permissions` | `contents: read`<br>`pull-requests: read` | MOCK delete requires read permission |
| `dry-run` | `true` | MOCK delete |
| `exclude-branches` | `badges` | Branch `badges` is found and excluded |
| `max-idle-days` | `10` | Without new commits longer than 10 days |

### Example 1 - Workflow (MOCK delete)
```yml
name: delete-github-branches

on:
  schedule:
    - cron: '30 17 * * *'

permissions:
  contents: read
  pull-requests: read

jobs:
  delete-branches:
    runs-on: ubuntu-latest

    permissions:
      contents: read
      pull-requests: read

    - name: Run delete-branches
      id: delete-branches
      uses: tagdots/delete-branches@774994b535b7853251f338762a0b5fe829eece09 # 1.1.1
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        repo-url: ${{ github.repository }}
        max-idle-days: 10
        exclude-branches: 'badges'
        dry-run: true
```

<br>

### Example 2 - Summary (Permanent delete)
| Input | Workflow Spec | Notes
|-------|-------------|----------|
| `scheduled run` | `- cron: '30 17 * * *'` | Run daily at 5:30 pm UTC
| `github token permissions` | `contents: write`<br>`pull-requests: read`| Delete requires write permission in `contents` |
| `dry-run` | `false` | Permanent delete |
| `exclude-branches` | `badges` | Branch `badges` is found and excluded |
| `max-idle-days` | `10` | Without new commits longer than 10 days |

### Example 2 - Workflow (Permanent delete)
```yml
name: delete-github-branches

on:
  schedule:
    - cron: '30 17 * * *'

permissions:
  contents: read
  pull-requests: read

jobs:
  delete-branches:
    runs-on: ubuntu-latest

    permissions:
      contents: write
      pull-requests: read

    - name: Run delete-branches
      id: delete-branches
      uses: tagdots/delete-branches@774994b535b7853251f338762a0b5fe829eece09 # 1.1.1
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        repo-url: ${{ github.repository }}
        max-idle-days: 10
        exclude-branches: 'badges'
        dry-run: false
```

<br>

## 🖥 Running _delete-branches_ from command line

### Prerequisites
```
* Python (3.12+)
* GitHub fine-grained token (contents: write)
```

<br>

### Setup _delete-branches_
```
~/work/test $ workon test
(test) ~/work/test $ export GH_TOKEN=github_pat_xxxxxxxxxxxxx
(test) ~/work/test $ pip install -U delete-branches
```

<br>

### Example 1 - Run for help
```
(test) ~/work/test $ delete-branches --help
Usage: delete-branches [OPTIONS]

Options:
  --dry-run BOOLEAN        default: true
  --repo-url TEXT          e.g. https://github.com/{owner}/{repo}  [required]
  --exclude-branches TEXT  e.g. 'exclude-branch-1, exclude-branch-2'
  --max-idle-days INTEGER  Max. no. of idle days (without commits)  [required]
  --version                Show the version and exit.
  --help                   Show this message and exit.
```

<br>

### Example 2 - MOCK delete branches without new commits longer than 10 days
| Input | Input Detail | Result
|-------|-------------|----------|
| `repo-url` | `https://github.com/tagdots/test` | process repository `tagdots/test` |
| `max-idle-days` | `10` | Without new commits longer than 10 days |
| `exclude-branches` | `test-1`, `test-2`, `badges` | Only branch `badges` is found and excluded |
| `dry-run` | `true` | a. 3 branches exempted from delete: `main`, `badges`, `pr-branch-01`<br>b. 6 branches `NOT exempt from delete`<br>c. MOCK delete 2 of 6 `NOT-exempt-from-delete` branches |

<br>

```
(test) ~/work/test $ delete-branches --dry-run true --max-idle-days 10 --exclude-branches "test-1, test-2, badges" --repo-url https://github.com/tagdots/test

🚀 Starting Delete GitHub Branches (dry-run: True, exclude-branches: {'test-1', 'test-2', 'badges'}, max-idle-days: 10)

Current Time (UTC): 2025-08-20 17:08:32

Refined User Exclude Branch(es): {'badges'}
Default Branch                 : main
Protected Branch               : main
Pull Request Head Branch       : pr-branch-01

Total Number of Branches                         : 9
Total Number of Branches (Exempt-From-Delete)    : 3
Total Number of Branches (Not-Exempt-From-Delete): 6

From 6 Not-Exempt-From-Delete Branch(es),  2 branch is idle more than 10 day(s)
-------------------------------------------------------------------------------------------------
(MOCK) Delete branch - last update UTC 2025-08-09 13:49:34: branch-test-001
(MOCK) Delete branch - last update UTC 2025-08-08 03:29:34: branch-test-005
```

<br>

### Example 3 - Delete branches permanently without new commits longer than 10 days
| Input | Input Detail | Result
|-------|-------------|----------|
| `repo-url` | `https://github.com/tagdots/test` | process repository `tagdots/test` |
| `max-idle-days` | `10` | Without new commits longer than 10 days |
| `exclude-branches` | `badges` | Branch `badges` is found and excluded |
| `dry-run` | `false` | a. 3 branches exempted from delete: `main`, `badges`, `pr-branch-01`<br>b. 6 branches `NOT exempt from delete`<br>c. Delete 2 of 6 `NOT-exempt-from-delete` branches permanently |

<br>

```
(test) ~/work/test $ delete-branches --dry-run false --max-days 10 --exclude-branches "badges" --repo-url https://github.com/tagdots/test

🚀 Starting Delete GitHub Branches (dry-run: False, exclude-branches: {'badges'}, max-idle-days: 10)

Current Time (UTC): 2025-08-20 17:26:55

Refined User Exclude Branch(es): {'badges'}
Default Branch                 : main
Protected Branch               : main
Pull Request Head Branch       : pr-branch-01

Total Number of Branches                         : 9
Total Number of Branches (Exempt-From-Delete)    : 3
Total Number of Branches (Not-Exempt-From-Delete): 6

From 6 Not-Exempt-From-Delete Branch(es),  2 branch is idle more than 10 day(s)
-------------------------------------------------------------------------------------------------
✅ Delete branch - last update UTC 2025-08-09 13:49:34: branch-test-001
✅ Delete branch - last update UTC 2025-08-08 03:29:34: branch-test-005
```

<br>

## 🔧 delete-branches command line options

| Input | Description | Default | Required | Notes |
|-------|-------------|----------|----------|----------|
| `repo-url` | Repository URL | `None` | Yes | e.g. https://github.com/{owner}/{repo} |
| `dry-run` | Dry-Run | `True` | No | - |
| `max-idle-days` | Maximum number of days without new commits | `None` | Yes | enter number of days |
| `exclude-branches` | Branches excluded from deletion | `None` | No | comma seperated branches e.g. "branch1, branch2" |

<br>

## 😕  Troubleshooting

Open an [issue][issues]

<br>

## 🙏  Contributing

For pull requests to be accepted on this project, you should follow [PEP8][pep8] when creating/updating Python codes.

See [Contributing][contributing]

<br>

## 🙌 Appreciation
If you find this project helpful, please ⭐ star it.  **Thank you**.

<br>

## 📚 References

[How to fork a repo](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

<br>

[contributing]: https://github.com/tagdots/delete-branches/blob/main/CONTRIBUTING.md
[issues]: https://github.com/tagdots/delete-branches/issues
[pep8]: https://google.github.io/styleguide/pyguide.html
