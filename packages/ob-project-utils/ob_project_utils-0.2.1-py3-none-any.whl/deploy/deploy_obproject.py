import re
import subprocess
import os
import datetime
import json
import sys
import glob
import requests

try:
    # python >= 3.11
    import tomllib as toml
except ImportError:
    import toml

PROJECT_SPEC = "project_spec.json"


# CI Environment Registry
class CIEnvironment:
    """Base class for CI environment handlers"""

    @staticmethod
    def is_active():
        raise NotImplementedError

    @staticmethod
    def get_branch():
        return ""

    @staticmethod
    def get_urls():
        raise NotImplementedError

    @staticmethod
    def post_comment(url, token, comment):
        raise NotImplementedError

    @staticmethod
    def write_summary(markdown):
        pass


class GitHubEnvironment(CIEnvironment):
    @staticmethod
    def is_active():
        return os.getenv("GITHUB_ACTIONS") == "true"

    @staticmethod
    def get_branch():
        # Try PR head ref first, then push ref
        return os.getenv("GH_HEAD_REF") or os.getenv("GH_REF", "")

    @staticmethod
    def get_urls():
        repo = os.getenv("GITHUB_REPOSITORY", "")
        return {
            "commit_url": f"https://github.com/{repo}/commit/",
            "ci_url": f"https://github.com/{repo}/actions/runs/{os.getenv('GITHUB_RUN_ID', '')}",
            "comments_api": os.getenv("COMMENTS_URL"),
            "token": os.getenv("GH_TOKEN"),
            "pr_number": os.getenv("GITHUB_EVENT_NAME") == "pull_request",
        }

    @staticmethod
    def post_comment(url, token, comment):
        requests.post(
            url=url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {token}",
            },
            json={"body": comment},
        )

    @staticmethod
    def write_summary(markdown):
        if "GITHUB_STEP_SUMMARY" in os.environ:
            with open(os.environ["GITHUB_STEP_SUMMARY"], "w") as f:
                f.write(markdown)


class AzureDevOpsEnvironment(CIEnvironment):
    
    @staticmethod
    def is_active():
        return bool(os.getenv("SYSTEM_COLLECTIONURI"))

    @staticmethod
    def get_branch():
        # For PRs: refs/pull/1/merge -> extract source branch name
        branch = os.getenv("BUILD_SOURCEBRANCH", "")
        if branch.startswith("refs/pull/"):
            # In PR context, get the actual source branch name
            return os.getenv("SYSTEM_PULLREQUEST_SOURCEBRANCH", "").replace(
                "refs/heads/", ""
            )
        else:
            # Direct push: refs/heads/main -> main
            return branch.replace("refs/heads/", "")

    @staticmethod
    def get_urls():
        collection_uri = os.getenv("SYSTEM_COLLECTIONURI", "").rstrip("/")
        team_project = os.getenv("SYSTEM_TEAMPROJECT", "")
        repo_name = os.getenv("BUILD_REPOSITORY_NAME", "")

        # Comments API only available in PR context
        pr_id = os.getenv("SYSTEM_PULLREQUEST_PULLREQUESTID")
        comments_api = None
        if pr_id:
            repo_id = os.getenv("BUILD_REPOSITORY_ID", "")
            comments_api = (
                f"{collection_uri}/{team_project}/_apis/git/repositories/"
                f"{repo_id}/pullRequests/{pr_id}/threads?api-version=6.0"
            )

        return {
            "commit_url": f"{collection_uri}/{team_project}/_git/{repo_name}/commit/",
            "ci_url": f"{collection_uri}/{team_project}/_build/results?buildId={os.getenv('BUILD_BUILDID', '')}&view=results",
            "comments_api": comments_api,
            "token": os.getenv("SYSTEM_ACCESSTOKEN"),
            "pr_number": pr_id is not None,
        }

    @staticmethod
    def post_comment(url, token, comment):
        requests.post(
            url=url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={
                "comments": [
                    {"parentCommentId": 0, "content": comment, "commentType": 1}
                ],
                "status": 1,
            },
        )

    @staticmethod
    def write_summary(markdown):
        # Azure DevOps uses ##vso commands for markdown summaries
        summary_file = os.path.abspath("deployment_summary.md")
        with open(summary_file, "w") as f:
            f.write(markdown)
        print(f"##vso[task.uploadsummary]{summary_file}")


CI_ENVIRONMENTS = {
    "github": GitHubEnvironment,
    "azuredevops": AzureDevOpsEnvironment,
}

# Global CI environment detection (cached)
_CI_ENV = None
_CI_HANDLER = None


def detect_ci_environment():
    """
    Detect which CI/CD environment we're running in.
    Returns the CI environment name or None if running locally.
    Caches the result to avoid repeated detection.
    """
    global _CI_ENV, _CI_HANDLER

    if _CI_ENV is not None:
        return _CI_ENV

    detected_envs = []

    # Check each CI environment handler
    for name, handler in CI_ENVIRONMENTS.items():
        if handler.is_active():
            detected_envs.append(name)

    # Validate we don't have conflicting environments
    if len(detected_envs) > 1:
        raise RuntimeError(
            f"Multiple CI environments detected: {', '.join(detected_envs)}. "
            f"This usually happens when CI-specific environment variables are manually set. "
            f"Please ensure only one set of CI environment variables is present."
        )

    _CI_ENV = detected_envs[0] if detected_envs else "local"
    _CI_HANDLER = CI_ENVIRONMENTS.get(_CI_ENV, None)
    return _CI_ENV


def get_ci_handler():
    """Get the CI handler for the current environment."""
    if _CI_HANDLER is None:
        detect_ci_environment()
    return _CI_HANDLER


def get_ci_urls():
    """
    Get CI/CD-specific URLs and tokens based on the detected environment.
    Returns a dict with commit_url, ci_url, comments_api, and token.
    """
    handler = get_ci_handler()
    if handler:
        return handler.get_urls()
    else:
        # Local or unknown environment
        return {
            "commit_url": os.getenv("COMMIT_URL", "https://no-commit-url/"),
            "ci_url": os.getenv("CI_URL"),
            "comments_api": None,
            "token": None,
            "pr_number": False,
        }


def listdir(root):
    if os.path.exists(root):
        return os.listdir(root)
    else:
        return []


def read_toml_config(filename):
    with open(filename) as f:
        return toml.loads(f.read())


def get(key, default=None):
    config = read_toml_config("obproject.toml")
    return config.get(key, default)


def project():
    project_name = get("project")
    if project_name:
        return re.sub(r"[-/]", "_", project_name).lower()

    try:
        repo_path = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        project_name = os.path.basename(repo_path)
        return re.sub(r"[-/]", "_", project_name).lower()
    except subprocess.CalledProcessError:
        raise RuntimeError("No project name found in obproject.toml or git repo!")


def git_branch():
    try:
        # Try CI environment first
        handler = get_ci_handler()
        if handler:
            ci_branch = handler.get_branch()
            if ci_branch:
                return ci_branch

        # Fall back to local git
        current_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return current_branch
    except subprocess.CalledProcessError:
        return ""


def is_main_branch():
    branch_name = get("branch") or git_branch()
    return branch_name in ("main", "master")


def branch():
    branch_name = get("branch") or git_branch()
    if is_main_branch():
        print("Deploying to the main branch (aka --production)")
        return branch_name
    elif branch_name:
        trimmed_branch = re.sub(r"[-/]", "_", branch_name).lower()
        print(f"Deploying to branch {trimmed_branch}")
        return trimmed_branch
    else:
        raise Exception("Branch not found - is this a Git repo?")


def version():
    ver = get("version")
    if ver:
        return ver

    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        return git_sha
    except subprocess.CalledProcessError:
        raise RuntimeError(
            "No version found in obproject.toml and not in a git repository!"
        )


def current_perimeter():
    try:
        result = subprocess.check_output(
            ["outerbounds", "perimeter", "show-current", "-o", "json"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        data = json.loads(result)
        return data["data"]["current_perimeter"]
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        config = read_toml_config("obproject.toml")
        return config.get("perimeter", os.environ.get("PERIMETER_NAME", "default"))


def created_at():
    created_at_ts = get("created_at")
    if created_at_ts:
        return created_at_ts

    try:
        root_commit = (
            subprocess.check_output(
                ["git", "rev-list", "--max-parents=0", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            .strip()
            .split("\n")[0]
        )

        first_commit_timestamp = subprocess.check_output(
            ["git", "show", "-s", "--format=%at", root_commit],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()

        dt = datetime.datetime.fromtimestamp(
            int(first_commit_timestamp), tz=datetime.timezone.utc
        )
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    except subprocess.CalledProcessError:
        pass
    return "2025-01-01T00:00:00.000000Z"


PROJECT_ROOT = os.path.abspath(os.getcwd())
DEPLOYED_AT = datetime.datetime.now(datetime.timezone.utc).strftime(
    "%Y-%m-%dT%H:%M:%S.%fZ"
)
PROJECT = project()
GIT_BRANCH = git_branch()
BRANCH = branch()
VERSION = version()
PERIMETER = current_perimeter()


def pyproject_cmd(flag):
    conf = read_toml_config(os.path.join(PROJECT_ROOT, "obproject.toml"))
    include_pyproject = conf.get("dependencies", {}).get("include_pyproject_toml", True)
    project_deps = os.path.join(PROJECT_ROOT, "pyproject.toml")
    if os.path.exists(project_deps) and include_pyproject:
        return flag + [project_deps]
    else:
        return []


def deploy_flows(flows):
    project_config = os.path.abspath("obproject.toml")
    project_spec = os.path.abspath(PROJECT_SPEC)

    if is_main_branch():
        project_branch = "--production"
    else:
        project_branch = f"--branch={BRANCH}"
    for flow_dir, flow_file, flow_spec in flows:
        cmd = [
            sys.executable,
            os.path.basename(flow_file),
            project_branch,
            "--config",
            "project_spec",
            project_spec,
            "--config",
            "project_config",
            project_config,
            "--package-suffixes=.html",
            "--environment=fast-bakery",
        ] + pyproject_cmd(["--config", "project_deps"])
        cmd += [
            "argo-workflows",
            "create",
        ]
        print(f"⚙️ Deploying flow at {flow_dir}:")
        subprocess.run(cmd, check=True, cwd=flow_dir)


def deploy_apps():
    num_apps = 0
    cwd = os.getcwd()
    try:
        for app_dir in listdir("deployments"):
            num_apps += 1
            root = os.path.join(cwd, "deployments", app_dir)
            os.chdir(root)

            # TODO: Include packages under src/ automatically,
            # similar to flows

            app_config = "config.yml"
            if os.path.exists(app_config):
                cmd = [
                    "outerbounds",
                    "app",
                    "deploy",
                    "--no-loader",
                    "--config-file",
                    app_config,
                    f"--project={PROJECT}",
                    f"--branch={BRANCH}",
                    "--readiness-condition=async",
                    "--readiness-wait-time=0",
                    "--env",
                    f"OB_PROJECT={PROJECT}",
                    "--env",
                    f"OB_BRANCH={BRANCH}",
                ] + pyproject_cmd(["--dep-from-pyproject"])
                print(f"⚙️ Deploying app at {app_dir}:")
                subprocess.run(cmd, check=True)
            else:
                raise FileNotFoundError(
                    f"App config '{app_config}' for app '{app_dir}' not found!"
                )
        return num_apps
    finally:
        os.chdir(cwd)


"""
def persist_asset(config, previous_version=None, asset_dir=None):
    def _config_hash(config):
        json_cfg = json.dumps(config, sort_keys=True)
        return hashlib.sha256(json_cfg.encode('utf-8')).hexdigest()

    config_hash = _config_hash(config)
    if asset_dir:
        files = config['files']
    else:
        new_ver = f'version:{config_hash}'
"""


def register_assets():
    from obproject.assets import Asset

    def ensure_types(d):
        for k, v in d.items():
            if not (isinstance(k, str) and isinstance(v, str)):
                raise AttributeError(
                    f"Invalid property '{k}': Both the key and value need to be strings"
                )
        return d

    # FIXME entity_ref should be more meaningful for CI/CD - fix kind and id
    entity_ref = {
        "entity_kind": "task",
        "entity_id": f"deployer",
    }
    asset = Asset(project=PROJECT, branch=BRANCH, entity_ref=entity_ref)

    def register(asset_type, register_func):
        for asset_dir in listdir(asset_type):
            root = os.path.join(asset_type, asset_dir)
            try:
                config = read_toml_config(os.path.join(root, "asset_config.toml"))
                markdown = ""
                readme = os.path.join(root, "README.md")
                if os.path.exists(readme):
                    with open(readme) as f:
                        markdown = f.read().strip()

                # note that we don't add an instance-level description here,
                # we just populate the top-level info in the project spec
                register_func(
                    config["id"],
                    kind=config.get("kind", asset_type.strip("s")),
                    blobs=config.get("blobs", []),
                    tags=ensure_types(config.get("tags", {})),
                    annotations=ensure_types(config.get("properties", {})),
                )
                # pass down information for the spec
                yield {
                    "display_name": config["name"],
                    "id": config["id"],
                    "card_markdown": markdown,
                    "description": config.get("description", ""),
                    "icon": config.get("icon"),
                }
                print(f"📝 Registered {asset_type.strip('s')}: {config['id']}")
            except:
                print(f"❌ parsing {root} failed:")
                raise

    return list(register("models", asset.register_model_asset)), list(
        register("data", asset.register_data_asset)
    )


def git_log():
    # Format: SHA | Timestamp | Author | Subject | Body
    format_str = "%H|%aI|%ae|%s|%b"
    result = subprocess.run(
        ["git", "log", "-20", f"--pretty=format:{format_str}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )

    # Get commit URL from CI environment
    ci_urls = get_ci_urls()
    repo = ci_urls.get("commit_url", "https://no-commit-url/")

    commits = []
    for line in result.stdout.split("\n"):
        parts = line.split("|", 4)
        if len(parts) < 5:
            continue
        sha, timestamp, email, title, body = parts

        commit = {
            "commit_sha": sha,
            "commit_link": f"{repo}{sha}",
            # "container_image": f"some.container:image:{sha}",  # Placeholder logic
            "owner": email,
            "pr_description": body.strip().replace("\n", " "),
            "pr_title": title.strip(),
            "timestamp": timestamp,
        }
        commits.append(commit)

    return commits


def summary(conf):
    platform = get("platform")
    spec = conf.get("spec", {})
    project_title = conf.get("title", conf.get("project"))
    project_name = conf.get("project")
    branch_name = conf.get("branch", "main")
    updated_at = spec.get("updated_at", "Unknown")
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        formatted_deployed = dt.strftime("%Y-%m-%d %H:%M UTC")
    except:
        formatted_deployed = updated_at

    markdown_lines = [
        f"### 🚧 {project_title} updated!",
        f"→ [Open in Outerbounds](https://ui.{platform}/dashboard/p/{PERIMETER}/j/{project_name}/b/{branch_name}/overview)",
        "",
        f"🗂️ **Project:** `{project_title}`",
        f"🌿 **Branch:** `{branch_name}`",
        f"🕒 **Last deployed:** {formatted_deployed}",
        "",
        "| Category         | Name/ID                                  | Description                                  |",
        "|------------------|-------------------------------------------|----------------------------------------------|",
    ]

    models = spec.get("models", [])
    if models:
        for i, model in enumerate(models):
            prefix = "🧠 **Models**" if i == 0 else ""
            name = model.get(
                "display_name",
                model.get(
                    "id",
                ),
            )
            description = model.get("description", "AI model for inference")
            model_id = model.get("id")
            model_url = f"https://ui.{platform}/dashboard/p/{PERIMETER}/j/{project_name}/b/{branch_name}/models/{model_id}"
            markdown_lines.append(
                f"| {prefix:<15} | [`{name}`]({model_url}) | {description[:42]}{'...' if len(description) > 42 else ''} |"
            )

    data_assets = spec.get("data", [])
    if data_assets:
        for i, data in enumerate(data_assets):
            prefix = "📦 **Data Assets**" if i == 0 else ""
            name = data.get("display_name", data.get("id"))
            description = data.get(
                "description", "Dataset for model training/evaluation"
            )
            data_id = data.get("id")
            data_url = f"https://ui.{platform}/dashboard/p/{PERIMETER}/j/{project_name}/b/{branch_name}/data/{data_id}"
            markdown_lines.append(
                f"| {prefix:<15} | [`{name}`]({data_url}) | {description[:42]}{'...' if len(description) > 42 else ''} |"
            )

    workflows = spec.get("workflows", [])
    if workflows:
        for i, workflow in enumerate(workflows):
            prefix = "⚙️ **Workflows**" if i == 0 else ""
            name = workflow.get("flow_name")
            description = workflow.get("markdown_description")
            template_id = workflow.get("flow_template_id", name.lower())
            workflow_url = (
                f"https://ui.{platform}/dashboard/flows/p/{PERIMETER}/{template_id}"
            )
            markdown_lines.append(
                f"| {prefix:<15} | [`{name}`]({workflow_url}) | {description[:42]}{'...' if len(description) > 42 else ''} |"
            )

    # markdown_lines.extend(
    #     [
    #         f"| {'🚀 **Deployments**':<15} | [`staging`](https://staging.example.com) | Model deployed to staging environment |",
    #         f"| {'':<15} | [`production`](https://prod.example.com) | Live production model endpoint |",
    #     ]
    # )

    markdown = "\n".join(markdown_lines)

    # Write summary based on CI environment
    handler = get_ci_handler()
    if handler:
        handler.write_summary(markdown)

    comment_pr(markdown)

    return markdown


def comment_pr(comment):
    handler = get_ci_handler()
    ci_urls = get_ci_urls()

    token = ci_urls.get("token")
    url = ci_urls.get("comments_api")

    if not token:
        print(
            f"No auth token for {detect_ci_environment()} environment. Skipping PR commenting."
        )
        return
    if not url:
        print("Not in PR context. Skipping PR commenting.")
        return

    try:
        if handler:
            handler.post_comment(url, token, comment)
    except Exception as ex:
        print(f"Posting comment to {detect_ci_environment()} failed:", str(ex))


def check_evaluation_flow(flow_src):
    EVAL_CARD_RE = re.compile(
        r"""
        @card                       # Match @card decorator
        \s*                         # Optional whitespace
        \(                          # Opening parenthesis
        \s*
        (                           # Capture args (for further parsing)
            [^)]*?                  #   Non-greedy: everything until...
            \bid\s*=\s*             #   ...id =
            (['"]{1,3})             #   ...with matching quotes
            project_eval            #   ...the target id value
            \2                      #   ...closing quote matches opening
            [^)]*                   #   ...and other optional args
        )
        \)                          # Closing parenthesis
        \s+@step\s+def\s+           # Followed by @step and def
        (\w+)                       # Capture method name
        \s*\(                       # Followed by (
    """,
        re.VERBOSE | re.MULTILINE | re.DOTALL,
    )
    CARD_TYPE_RE = re.compile(r'type\s*=\s*([\'"]{1,3})(.*?)\1')
    matches = EVAL_CARD_RE.findall(flow_src)
    if len(matches) > 1:
        raise Exception("Specify at most one @card(id='project_eval')")
    elif matches:
        [(args, _, step_name)] = matches
        [(_, card_type)] = CARD_TYPE_RE.findall(args)
        return {"card_type": card_type, "is_eval_flow": True, "step_name": step_name}


def get_metaflow_branch():
    if is_main_branch():
        return "prod"
    else:
        return f"test.{BRANCH}"


def discover_flows():
    # find a flow class that subclasses from ProjectFlow (amongst other superclasses)
    FLOW_RE = re.compile(
        r"^class\s+(\w+)\s*\([^)]*?\bProjectFlow\b[^)]*\)\s*:", re.MULTILINE
    )
    # find steps with a @highlight decorator
    HIGHLIGHT_RE = re.compile(
        r"@highlight\s+(?:@\w+(?:\([^)]*\))?\s+)*@step\s+def\s+(\w+)\s*\(", re.MULTILINE
    )
    metaflow_branch = get_metaflow_branch()
    evals = []
    flows = []

    for flow_dir in listdir("flows"):
        root = os.path.join("flows", flow_dir)
        flowfile = os.path.join(root, "flow.py")
        try:
            # read flow
            with open(flowfile) as f:
                src = f.read()

            # flow_name
            matches = FLOW_RE.search(src)
            if matches:
                flow_name = matches.group(1)
            else:
                raise Exception(
                    f"Could not find a flow subclassing from ProjectFlow in {flowfile}"
                )
            flow_template_id = (
                f"{PROJECT}.{metaflow_branch}.{flow_name.lower()}".replace("_", "")
            )

            # highlights
            hl_steps = HIGHLIGHT_RE.findall(src)
            if len(hl_steps) > 1:
                raise Exception(
                    "Currently you can have at most one @highlight per flow"
                )
            elif hl_steps:
                highlight_step_name = hl_steps[0]
            else:
                highlight_step_name = None

            # markdown description
            markdown = ""
            readme = os.path.join(root, "README.md")
            if os.path.exists(readme):
                with open(readme) as f:
                    markdown = f.read().strip()

            # check if this flow is an evaluation flow
            eval_info = check_evaluation_flow(src)
            if eval_info:
                eval_info.update(
                    {
                        "metaflow_branch": metaflow_branch,
                        "metaflow_project": PROJECT,
                        "workflow_name": flow_name,
                    }
                )
                evals.append(eval_info)

            flows.append(
                (
                    root,
                    flowfile,
                    {
                        "flow_name": flow_name,
                        "flow_template_id": flow_template_id,
                        "highlight_step_name": highlight_step_name,
                        "markdown_description": markdown,
                        "metaflow_branch": metaflow_branch,
                        "metaflow_project": PROJECT,
                        "tags": [],
                    },
                )
            )
            print(f"🌀 Found flow: {flow_name}")
            if highlight_step_name:
                print(f"    ✨ @highlight included from the {highlight_step_name} step")
            if eval_info:
                print(f"    📊 this flow is an evaluation flow")

        except:
            print(f"❌ parsing a flow at {flowfile} failed:")
            raise
    return flows, evals


def create_spec(flows, evals, data, models):
    commits = git_log()
    first = commits[0]
    code = {
        "display_name": f"{first['pr_title']} ({first['commit_sha'][:6]})",
        "url": first["commit_link"],
    }
    # Get CI URL from environment detection
    ci_urls = get_ci_urls()
    ci_url = ci_urls.get("ci_url")
    # should match schema https://github.com/outerbounds/obp-foundation/blob/master/utqiagvik/backend/internal/services/assets_api/internal/api_types/api_types.go#L47
    # and spec should be https://github.com/outerbounds/obp-foundation/blob/master/utqiagvik/backend/internal/services/assets_api/internal/api_types/api_types.go#L54

    if os.path.exists("README.md"):
        with open("README.md") as f:
            markdown = f.read()
    else:
        markdown = None

    conf = {
        "perimeter": current_perimeter(),
        "project": PROJECT,
        "branch": BRANCH,
        "version_id": VERSION,
        "spec": {
            "metaflow_project": PROJECT,
            "metaflow_branch": get_metaflow_branch(),
            "card_info": evals,
            "ci_url": ci_url,
            "code": [code],
            "created_at": datetime.datetime.fromisoformat(
                created_at().replace("Z", "+00:00")
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": data,
            "deployment_events": commits[:10],
            "markdown": markdown,
            "models": models,
            "perimeter": current_perimeter(),
            "project_branch": BRANCH,
            "project_name": PROJECT,
            "title": get("title"),
            "updated_at": datetime.datetime.fromisoformat(
                DEPLOYED_AT.replace("Z", "+00:00")
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "workflows": [f for _, _, f in flows],
        },
    }

    def clean(obj):
        return (
            {k: clean(v) for k, v in obj.items() if v is not None}
            if isinstance(obj, dict)
            else (
                [clean(item) for item in obj if item is not None]
                if isinstance(obj, list)
                else obj if obj is not None else None
            )
        )

    spec = clean(conf)
    with open(PROJECT_SPEC, "w") as f:
        json.dump(spec, f)
    print(f"Config written to {PROJECT_SPEC}")
    return spec


def register_spec(spec):
    cmd = ["outerbounds", "flowproject", "set-metadata", json.dumps(spec)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def main():
    print("🟩🟩🟩 Registering Assets")
    models, data = register_assets()
    print(
        f"✅ {len(data)} data assets and {len(models)} models registered successfully"
    )

    print("🟩🟩🟩 Discovering Flows")
    flows, evals = discover_flows()
    print(
        f"✅ {len(flows)} flows parsed successfully - found {len(evals)} evaluation flows"
    )

    print("🟩🟩🟩 Updating Project Specification")
    spec = create_spec(flows, evals, data, models)
    print(f"✅ project specification ok")

    if not os.environ.get("SPEC_ONLY"):
        print("🟩🟩🟩 Deploying flows")
        deploy_flows(flows)
        print(f"✅ {len(flows)} flows deployed successfully")

        print("🟩🟩🟩 Deploying apps and endpoints")
        num_apps = deploy_apps()
        print(f"✅ {num_apps} endpoints and apps deployed successfully")

        print("🟩🟩🟩 Pushing Project Specification")
        register_spec(spec)
        print(f"✅ project updated successfully")

        summary(spec)
        print("✅✅✅ Deployment successful!")


if __name__ == "__main__":
    main()
