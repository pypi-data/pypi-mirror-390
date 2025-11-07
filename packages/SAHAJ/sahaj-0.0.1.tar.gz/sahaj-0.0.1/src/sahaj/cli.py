#!/usr/bin/env python3
# sahaj.py
import json
import os
import platform
import subprocess
import tempfile
import webbrowser
import shutil
import click
import requests
import yaml
from sahaj.helpers import (
    get_version_string,
    get_config_dir,
    get_config_path,
    read_config,
    write_config,
    run_native,
    run_repo_script,
    write_quickstart_marker,
    read_quickstart_marker,
    get_compose_env,
    _project_from_path,
    _docker_list_lines,
)

DOCKER_COMPOSE_URL = (
    "https://raw.githubusercontent.com/concur-live/docker-yml/main/docker-compose.yml"
)


DOCKER_COMPOSE_QUICKSTART_URL = "https://raw.githubusercontent.com/concur-live/docker-yml/main/docker-compose.quickstart.yml"

REPO_URL = "https://github.com/concur-live/docker-yml.git"
DEFAULT_DIRNAME = "docker-yml"


# -----------------------
# Click CLI
# -----------------------
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """SAHAJ CLI — Open Source Software Installer"""
    pass


# -----------------------
# simple commands
# -----------------------
@cli.command()
def version():
    """Display current version of SAHAJ"""
    click.echo(f"SAHAJ version {get_version_string()} (Last updated: Oct 2025)")


@cli.command()
def update():
    """Check for updates (stub)"""
    click.echo("Checking for updates...")
    click.echo("No updates available right now. You are using the latest version.")


@cli.command()
def license():
    """Show open-source license details (if available)"""
    license_path = os.path.join(os.path.dirname(__file__), "../../LICENSE.md")
    try:
        with open(os.path.abspath(license_path), "r", encoding="utf-8") as f:
            click.echo(f.read())
    except FileNotFoundError:
        click.echo("License file not found.")


@cli.command()
def about():
    """Show information about SAHAJ"""
    click.echo(
        """SAHAJ is an open-source project to simplify installation and management
of community-driven software. It provides an intuitive command-line interface
for deployment, configuration, and discovery of open-source tools.
"""
    )


@cli.command()
def docs():
    """Open documentation in a browser"""
    url = "https://docs.sahaj.live"
    click.echo(f"Opening documentation: {url}")
    webbrowser.open(url)


@cli.command()
def list():
    """List all available open-source modules supported by SAHAJ"""
    modules = [
        "Organization Management – Configure organizational hierarchy, departments, users, and access controls for compliance operations.",
        "Cookie Consent – Automatically scan websites and manage cookie consent to ensure DPDPA compliance.",
        "Data Principal Management – Maintain records and lifecycle of both legacy and new data principals for compliance tracking.",
        "Data Element – Identify, ingest, and classify PII data elements across systems for compliance monitoring.",
        "Purpose Management – Define, manage, and publish data processing purposes aligned with DPDPA consent requirements.",
        "Notice Orchestration – Create and manage Data Principal Notices for transparent data collection and consent communication.",
        "Collection Point – Configure and manage all data collection sources including web, mobile, and offline channels.",
        "Consent Governance – Monitor, search, and administer collected consents aligned with business and legal objectives.",
        "Consent Validation – Validate consent records, scope, and artifacts to ensure lawful and compliant data processing.",
        "Legacy Notice – Collect and regularize consents from existing data principals as mandated under Section 5(2).",
        "Grievance – Track, manage, and resolve data principal grievances in line with BRD-CMS compliance standards.",
        "Data Principal Rights – Handle and fulfill Data Principal access and rights requests efficiently.",
        "Breach Management – Log, assess, and report data breaches, ensuring timely notification to authorities and data principals.",
        "Assets/SKU – Maintain and manage organizational assets, SKUs, and their linkage to consent and cookie compliance activities.",
        "Customer Portal – Deploy a self-service Data Principal portal for managing consents and exercising privacy rights.",
    ]
    click.echo(f"{'No.':<4} {'Module':<25} Description")
    click.echo("-" * 100)
    for i, module in enumerate(modules, start=1):
        if "–" in module:
            name, desc = module.split("–", 1)
        else:
            name, desc = module, ""
        click.echo(f"{i:<4} {name.strip():<25} {desc.strip()}")


@cli.command()
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt.")
@click.option(
    "--into",
    type=click.Path(file_okay=False, dir_okay=True, path_type=str),
    default=None,
    help="Target repo directory (defaults to ./docker-yml and quickstart marker).",
)
def cleanup(yes, into):
    """
    Cleanup SAHAJ-related Docker resources for the current/selected project(s):
    stops & removes containers, removes project-built images, volumes, and networks.
    """
    # 1) Collect candidate project names
    projects = set()

    # explicit target
    if into:
        projects.add(_project_from_path(into))

    # default repo under cwd
    cwd = os.getcwd()
    default_repo = os.path.join(cwd, DEFAULT_DIRNAME)
    if os.path.isdir(default_repo):
        projects.add(_project_from_path(default_repo))

    # quickstart marker (if any): compose path saved earlier
    try:
        q_compose = read_quickstart_marker()
        if q_compose and os.path.exists(q_compose):
            projects.add(_project_from_path(os.path.dirname(q_compose)))
    except Exception:
        pass

    if not projects:
        click.echo(
            "No SAHAJ-managed project detected (no ./docker-yml or quickstart marker). Nothing to clean."
        )
        return

    click.echo("SAHAJ cleanup will target the following project(s):")
    for p in sorted(projects):
        click.echo(f"  - {p}")

    if not yes:
        click.confirm(
            "⚠️ This will stop/remove containers, images, volumes, and networks for the projects above. Continue?",
            abort=True,
        )

    # summary counters
    total = {
        "containers_stopped": 0,
        "containers_removed": 0,
        "images_removed": 0,
        "volumes_removed": 0,
        "networks_removed": 0,
    }

    for proj in projects:
        click.echo(f"\n➡️ Cleaning project: {proj}")

        # --- containers: find by compose project label
        ps_cmd = [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"label=com.docker.compose.project={proj}",
            "--format",
            "{{.ID}}",
        ]
        container_ids = _docker_list_lines(ps_cmd)
        if container_ids:
            click.echo(f"Stopping containers: {len(container_ids)}")
            try:
                subprocess.run(["docker", "stop"] + container_ids, check=False)
                total["containers_stopped"] += len(container_ids)
            except Exception as e:
                click.echo(f"  ⚠️ Failed to stop containers: {e}")

            click.echo("Removing containers...")
            try:
                subprocess.run(["docker", "rm", "-f"] + container_ids, check=False)
                total["containers_removed"] += len(container_ids)
            except Exception as e:
                click.echo(f"  ⚠️ Failed to remove containers: {e}")
        else:
            click.echo("No containers found for this project.")

        # --- images: remove images that match <project>-* (common compose auto-generated tag)
        # list all images and filter
        images_cmd = ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"]
        images = _docker_list_lines(images_cmd)
        matched_images = [img for img in images if img.lower().startswith(f"{proj}-")]
        if matched_images:
            click.echo(f"Removing images: {len(matched_images)}")
            for img in matched_images:
                try:
                    subprocess.run(["docker", "rmi", "-f", img], check=False)
                    total["images_removed"] += 1
                    click.echo(f"  removed {img}")
                except Exception as e:
                    click.echo(f"  ⚠️ failed to remove {img}: {e}")
        else:
            click.echo("No project-built images found (matching '<project>-*').")

        # --- volumes: find by label or by name prefix
        vol_cmd = ["docker", "volume", "ls", "--format", "{{.Name}}"]
        volumes = _docker_list_lines(vol_cmd)
        vol_matches = [
            v for v in volumes if v.startswith(f"{proj}_") or v.startswith(f"{proj}-")
        ]
        # also check volumes with label com.docker.compose.project
        labeled_vol_cmd = [
            "docker",
            "volume",
            "ls",
            "--filter",
            f"label=com.docker.compose.project={proj}",
            "--format",
            "{{.Name}}",
        ]
        labeled = _docker_list_lines(labeled_vol_cmd)
        for v in sorted(set(vol_matches + labeled)):
            try:
                subprocess.run(["docker", "volume", "rm", "-f", v], check=False)
                total["volumes_removed"] += 1
                click.echo(f"  removed volume {v}")
            except Exception as e:
                click.echo(f"  ⚠️ failed to remove volume {v}: {e}")
        if not vol_matches and not labeled:
            click.echo("No volumes found for this project.")

        # --- networks: by label or name prefix
        net_cmd = ["docker", "network", "ls", "--format", "{{.Name}}"]
        networks = _docker_list_lines(net_cmd)
        net_matches = [
            n for n in networks if n.startswith(f"{proj}_") or n.startswith(f"{proj}-")
        ]
        labeled_net_cmd = [
            "docker",
            "network",
            "ls",
            "--filter",
            f"label=com.docker.compose.project={proj}",
            "--format",
            "{{.Name}}",
        ]
        labeled_nets = _docker_list_lines(labeled_net_cmd)
        for n in sorted(set(net_matches + labeled_nets)):
            try:
                subprocess.run(["docker", "network", "rm", n], check=False)
                total["networks_removed"] += 1
                click.echo(f"  removed network {n}")
            except Exception as e:
                click.echo(f"  ⚠️ failed to remove network {n}: {e}")
        if not net_matches and not labeled_nets:
            click.echo("No networks found for this project.")

    # final summary
    click.echo("\n======== SAHAJ cleanup summary ========")
    click.echo(f"Containers stopped: {total['containers_stopped']}")
    click.echo(f"Containers removed: {total['containers_removed']}")
    click.echo(f"Images removed: {total['images_removed']}")
    click.echo(f"Volumes removed: {total['volumes_removed']}")
    click.echo(f"Networks removed: {total['networks_removed']}")
    click.echo("Cleanup finished.")


# -----------------------
# config command
# -----------------------
@cli.command()
@click.option(
    "--overwrite", is_flag=True, help="Overwrite existing config without prompting"
)
def config(overwrite):
    """
    Run config wizard (interactive).
    If --overwrite is provided, the existing config (if any) will be replaced without asking.
    """
    cfg_path = get_config_path()
    cfg_dir = get_config_dir()
    os.makedirs(cfg_dir, exist_ok=True)

    if os.path.exists(cfg_path) and not overwrite:
        # Ask the user if they want to overwrite
        if not click.confirm(f"Config already exists at {cfg_path}. Overwrite?"):
            click.echo("Aborted — existing configuration preserved.")
            return

    # interactive prompts
    click.echo("=== SAHAJ Configuration Setup ===")
    nginx_name = click.prompt("Enter your nginx name", type=str)
    nginx_port = click.prompt("Enter your nginx port", type=int)
    password = click.prompt("Enter your password", type=str)

    config_data = {
        "nginx_name": nginx_name.strip(),
        "nginx_port": nginx_port,
        "password": password.strip(),
    }

    try:
        write_config(config_data)
        click.echo(f"\nConfiguration saved successfully to: {cfg_path}")
    except OSError as e:
        click.echo(f"Error writing config file {cfg_path}: {e}")


# -----------------------
# init command group with subcommands
# -----------------------
@cli.group(invoke_without_command=True)
@click.pass_context
def init(ctx):
    """Initialize SAHAJ | run 'sahaj init --help' for subcommands"""
    if ctx.invoked_subcommand is None:
        click.echo("Running main init logic (no subcommand provided)")
        # stub: replace with actual init implementation


@init.command()
@click.option(
    "--into",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=str),
    default=None,
    help="Directory name (relative) to clone into. Defaults to './docker-yml'.",
)
def dev(into):
    """Initialize dev environment: clone repo into a subfolder (no --clean)."""
    cwd = os.getcwd()
    target_name = into if into else DEFAULT_DIRNAME
    target_path = os.path.join(cwd, target_name)

    if os.path.exists(target_path):
        click.echo(f"Target already exists at {target_path}.")
        click.echo(
            "If you want to replace it, remove the folder manually and re-run this command."
        )
        click.echo(f'To update, run: git -C "{target_path}" pull')
        return

    if shutil.which("git") is None:
        click.echo("Git not found on PATH. Please install git to use 'dev' command.")
        return

    click.echo(f"Cloning {REPO_URL} into {target_path} ...")
    try:
        # Show native git progress
        subprocess.run(["git", "clone", REPO_URL, target_path], check=True)
        click.echo("Clone complete.")
    except subprocess.CalledProcessError as e:
        click.echo(f"git clone failed: exit {e.returncode}")
    except Exception as e:
        click.echo(f"Unexpected error while cloning: {e}")


@init.command()
@click.option(
    "--into",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=str),
    default=None,
    help="Directory where repo was cloned (defaults to './docker-yml').",
)
@click.option(
    "--script",
    type=str,
    default="samplebuild",
    help="Base script name to execute (auto-selects .sh or .bat based on OS)",
)
def build(into, script):
    """
    Run build script inside the repo (samplebuild.sh or samplebuild.bat).
    Loads config.json and passes values as environment variables.
    """
    cwd = os.getcwd()
    target_name = into if into else DEFAULT_DIRNAME
    target_path = os.path.join(cwd, target_name)

    if not os.path.isdir(target_path):
        click.echo(
            f"❌ Repo folder not found at {target_path}. Run 'sahaj init dev' first."
        )
        return

    # 1️⃣ Load config
    repo_cfg_path = os.path.join(target_path, "config.json")
    config = {}
    if os.path.exists(repo_cfg_path):
        try:
            with open(repo_cfg_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            click.echo(f"Loaded config from {repo_cfg_path}")
        except Exception as e:
            click.echo(f"Failed to read config: {e}")
            return
    else:
        try:
            config = read_config()
            if config:
                click.echo("Loaded config from user config (fallback).")
        except NameError:
            config = {}
        if not config:
            click.echo("❌ No config found. Run 'sahaj config' first.")
            return

    # 2️⃣ Prepare env vars
    run_env = os.environ.copy()
    for k, v in config.items():
        key = str(k).upper().replace("-", "_").replace(" ", "_")
        run_env[key] = "" if v is None else str(v)
    run_env["SAHAJ_RUN_ENV"] = "build"

    click.echo("⚙️ Environment variables for build:")
    for k in sorted(config.keys()):
        env_key = k.upper().replace("-", "_").replace(" ", "_")
        val = run_env[env_key]
        if "PASSWORD" in env_key or "SECRET" in env_key:
            click.echo(f"  {env_key}=<hidden>")
        else:
            click.echo(f"  {env_key}={val}")

    # 3️⃣ Run script based on OS
    system = platform.system()
    try:
        if system == "Windows":
            script_path = os.path.join(target_path, script + ".bat")
            if not os.path.exists(script_path):
                click.echo(f"❌ No Windows build script found: {script_path}")
                return

            click.echo(f"🏗️ Running Windows build script: {script_path}")
            subprocess.run(
                ["cmd", "/c", script_path], cwd=target_path, env=run_env, check=True
            )

        else:
            script_path = os.path.join(target_path, script + ".sh")
            if not os.path.exists(script_path):
                click.echo(f"❌ No Unix build script found: {script_path}")
                return

            bash = shutil.which("bash") or shutil.which("sh")
            if not bash:
                click.echo("❌ No shell found (bash/sh).")
                return

            click.echo(f"🏗️ Running shell build script with {bash}: {script_path}")
            subprocess.run(
                [bash, script_path], cwd=target_path, env=run_env, check=True
            )

        click.echo("✅ Build process completed successfully.")

    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️ Build script exited with code {e.returncode}")
    except Exception as e:
        click.echo(f"❌ Failed to execute build script: {e}")


# -----------------------
# rundev group + subcommands
# -----------------------
@init.group(name="rundev", invoke_without_command=True)
@click.option(
    "--into",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=str),
    default=None,
    help="Directory where repo was cloned (defaults to './docker-yml').",
)
@click.option(
    "--script",
    type=str,
    default="sampleexample",
    help="Base script name to execute (auto-selects .sh or .bat based on OS)",
)
@click.pass_context
def rundev(ctx, into, script):
    """
    rundev group — use subcommands: start, stop, restart, status.
    If called without a subcommand, runs 'start'.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(rundev_start, into=into, script=script)


@rundev.command("start")
@click.option("--into", default=None, help="repo directory (defaults to ./docker-yml)")
@click.option("--script", default="sampleexample", help="script base name")
def rundev_start(into, script):
    """Start dev environment (runs repo script or docker compose up)."""
    cwd = os.getcwd()
    target_name = into if into else DEFAULT_DIRNAME
    target_path = os.path.join(cwd, target_name)

    if not os.path.isdir(target_path):
        click.echo(
            f"Repo folder not found at {target_path}. Run 'sahaj init dev' first to clone."
        )
        return

    # load config
    repo_cfg_path = os.path.join(target_path, "config.json")
    config = {}
    if os.path.exists(repo_cfg_path):
        try:
            with open(repo_cfg_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            click.echo(f"Loaded config from {repo_cfg_path}")
        except Exception as e:
            click.echo(f"Failed to read repo config {repo_cfg_path}: {e}")
            return
    else:
        try:
            config = read_config()
            if config:
                click.echo("Loaded config from user config (fallback).")
        except NameError:
            config = {}
        if not config:
            click.echo(
                "No config found (repo-local or global). Run 'sahaj config' or place config.json in the repo."
            )
            return

    # prepare env
    run_env = os.environ.copy()
    for k, v in config.items():
        key = str(k).upper().replace("-", "_").replace(" ", "_")
        run_env[key] = "" if v is None else str(v)
    run_env["SAHAJ_RUN_ENV"] = "dev"

    click.echo("Environment variables to be provided to the script:")
    for k in sorted(config.keys()):
        env_key = k.upper().replace("-", "_").replace(" ", "_")
        val = run_env[env_key]
        if "PASSWORD" in env_key or "SECRET" in env_key:
            click.echo(f"  {env_key}=<hidden>")
        else:
            click.echo(f"  {env_key}={val}")

    # try to run repo script; if not present, fallback to docker compose up -d
    try:
        run_repo_script(target_path, script, run_env)
        click.echo("✅ Dev script executed successfully.")
    except FileNotFoundError:
        # fallback: run docker compose up -d using docker-compose.yml in repo
        compose_file = os.path.join(target_path, "docker-compose.yml")
        if not os.path.exists(compose_file):
            click.echo(
                f"No script found and no compose file at {compose_file}. Nothing to do."
            )
            return
        click.echo(f"No script found; running docker compose with {compose_file}")
        try:
            run_native(
                ["docker", "compose", "-f", compose_file, "up", "-d"],
                cwd=target_path,
                env=run_env,
            )
            click.echo("✅ Containers started (rundev).")
        except subprocess.CalledProcessError as e:
            click.echo(f"⚠️  docker compose failed with code {e.returncode}")


@rundev.command("stop")
@click.option("--into", default=None, help="repo directory (defaults to ./docker-yml)")
def rundev_stop(into):
    """Stop dev environment (docker compose down)."""
    cwd = os.getcwd()
    target_name = into if into else DEFAULT_DIRNAME
    target_path = os.path.join(cwd, target_name)
    compose_file = os.path.join(target_path, "docker-compose.yml")

    if not os.path.isdir(target_path) or not os.path.exists(compose_file):
        click.echo("No repo or compose file found — nothing to stop.")
        return

    repo_cfg_path = os.path.join(target_path, "config.json")
    run_env = get_compose_env(repo_cfg_path, mode="dev")

    try:
        run_native(
            ["docker", "compose", "-f", compose_file, "down"],
            cwd=target_path,
            env=run_env,
        )
        click.echo("✅ Dev containers stopped.")
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️  docker compose down failed: {e.returncode}")


@rundev.command("restart")
@click.option("--into", default=None, help="repo directory (defaults to ./docker-yml)")
@click.option("--script", default="sampleexample", help="script base name")
def rundev_restart(into, script):
    """Restart dev environment (stop then start)."""
    ctx = click.get_current_context()
    ctx.invoke(rundev_stop, into=into)
    ctx.invoke(rundev_start, into=into, script=script)


@rundev.command("status")
@click.option("--into", default=None, help="repo directory (defaults to ./docker-yml)")
def rundev_status(into):
    """Show docker-compose ps for the dev compose file."""
    cwd = os.getcwd()
    target_name = into if into else DEFAULT_DIRNAME
    target_path = os.path.join(cwd, target_name)
    compose_file = os.path.join(target_path, "docker-compose.yml")
    if not os.path.exists(compose_file):
        click.echo("No compose file found for dev.")
        return
    repo_cfg_path = os.path.join(target_path, "config.json")
    run_env = get_compose_env(repo_cfg_path, mode="dev")
    run_native(
        ["docker", "compose", "-f", compose_file, "ps"], cwd=target_path, env=run_env
    )


# -----------------------
# deploy group + subcommands
# -----------------------
@init.group(name="deploy", invoke_without_command=True)
@click.option(
    "--into",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, path_type=str),
    default=None,
    help="Directory where repo was cloned (defaults to './docker-yml').",
)
@click.option(
    "--script",
    type=str,
    default="sampledeploy",
    help="Base script name to execute (auto-selects .sh or .bat based on OS)",
)
@click.pass_context
def deploy(ctx, into, script):
    """deploy group — subcommands: start, stop, restart, status. Default = start."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(deploy_start, into=into, script=script)


@deploy.command("start")
@click.option("--into", default=None, help="repo directory (defaults to ./docker-yml)")
@click.option("--script", default="sampledeploy", help="script base name")
def deploy_start(into, script):
    """Start deployment (ensures images exist then runs deploy script)."""
    cwd = os.getcwd()
    target_name = into if into else DEFAULT_DIRNAME
    target_path = os.path.join(cwd, target_name)
    compose_file = os.path.join(target_path, "docker-compose.builder.yml")

    if not os.path.isdir(target_path):
        click.echo(
            f"❌ Repo folder not found at {target_path}. Run 'sahaj init dev' first."
        )
        return

    if not os.path.exists(compose_file):
        click.echo(f"❌ Missing file: {compose_file}")
        return

    # load config
    repo_cfg_path = os.path.join(target_path, "config.json")
    config = {}
    if os.path.exists(repo_cfg_path):
        with open(repo_cfg_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        click.echo(f"Loaded config from {repo_cfg_path}")
    else:
        try:
            config = read_config()
            if config:
                click.echo("Loaded config from user config (fallback).")
        except NameError:
            config = {}
        if not config:
            click.echo("❌ No config found. Run 'sahaj config' first.")
            return

    # prepare env
    run_env = os.environ.copy()
    for k, v in config.items():
        key = str(k).upper().replace("-", "_").replace(" ", "_")
        run_env[key] = "" if v is None else str(v)
    run_env["SAHAJ_RUN_ENV"] = "deploy"

    # parse compose and check images (including build: contexts -> infer name)
    try:
        with open(compose_file, "r", encoding="utf-8") as f:
            compose_data = yaml.safe_load(f)
    except Exception as e:
        click.echo(f"❌ Failed to parse {compose_file}: {e}")
        return

    services = compose_data.get("services", {}) or {}
    missing_images = []
    for name, svc in services.items():
        image_name = svc.get("image")
        if not image_name and "build" in svc:
            project_name = os.path.basename(os.path.dirname(compose_file))
            image_name = f"{project_name}-{name}".lower()
        if not image_name:
            continue
        result = subprocess.run(
            ["docker", "image", "inspect", image_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            missing_images.append(
                f"{image_name} (build)" if "build" in svc else image_name
            )

    if missing_images:
        click.echo("❌ The following images are missing locally:")
        for img in missing_images:
            click.echo(f"   - {img}")
        click.echo("⚠️  Run 'sahaj init build' first to build these images.")
        return

    click.echo("✅ All required images found locally. Proceeding with deployment.\n")

    # run deploy script if present, else fallback to docker compose -f builder up -d
    try:
        try:
            run_repo_script(target_path, script, run_env)
            click.echo("✅ Deploy script executed successfully.")
            return
        except FileNotFoundError:
            click.echo(
                "No deploy script found, falling back to docker compose command."
            )
            run_native(
                ["docker", "compose", "-f", compose_file, "up", "-d"],
                cwd=target_path,
                env=run_env,
            )
            click.echo("✅ Deployment completed.")
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️ Deploy step failed with code {e.returncode}")


@deploy.command("stop")
@click.option("--into", default=None, help="repo directory (defaults to ./docker-yml)")
def deploy_stop(into):
    """Stop deployed containers (docker compose down using builder compose file)."""
    cwd = os.getcwd()
    target_name = into if into else DEFAULT_DIRNAME
    target_path = os.path.join(cwd, target_name)
    compose_file = os.path.join(target_path, "docker-compose.builder.yml")

    if not os.path.isdir(target_path) or not os.path.exists(compose_file):
        click.echo("No repo or builder compose file found — nothing to stop.")
        return

    repo_cfg_path = os.path.join(target_path, "config.json")
    run_env = get_compose_env(repo_cfg_path, mode="deploy")
    try:
        run_native(
            ["docker", "compose", "-f", compose_file, "down"],
            cwd=target_path,
            env=run_env,
        )
        click.echo("✅ Deploy containers stopped.")
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️ docker compose down failed: {e.returncode}")


@deploy.command("restart")
@click.option("--into", default=None, help="repo directory (defaults to ./docker-yml)")
@click.option("--script", default="sampledeploy", help="script base name")
def deploy_restart(into, script):
    """Restart deploy: stop then start."""
    ctx = click.get_current_context()
    ctx.invoke(deploy_stop, into=into)
    ctx.invoke(deploy_start, into=into, script=script)


@deploy.command("status")
@click.option("--into", default=None, help="repo directory (defaults to ./docker-yml)")
def deploy_status(into):
    """Show status for builder compose (ps)."""
    cwd = os.getcwd()
    target_name = into if into else DEFAULT_DIRNAME
    target_path = os.path.join(cwd, target_name)
    compose_file = os.path.join(target_path, "docker-compose.builder.yml")
    if not os.path.exists(compose_file):
        click.echo("No builder compose file found for deploy.")
        return
    repo_cfg_path = os.path.join(target_path, "config.json")
    run_env = get_compose_env(repo_cfg_path, mode="deploy")
    run_native(
        ["docker", "compose", "-f", compose_file, "ps"], cwd=target_path, env=run_env
    )


# -----------------------
# quickstart group + subcommands
# -----------------------
@init.group(name="quickstart", invoke_without_command=True)
@click.pass_context
def quickstart(ctx):
    """Quickstart group — start, stop, restart, status. Default = start."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(quickstart_start)


@quickstart.command("start")
def quickstart_start():
    """Start quickstart: download templated compose and run up -d, remembers compose path."""
    click.echo("🚀 Starting Quickstart Setup...")

    config = read_config()
    if not config:
        click.echo(
            "❌ Config file not found or empty. Please run `sahaj config` first."
        )
        return

    nginx_name = config.get("nginx_name", "sahaj-nginx")
    nginx_port = str(config.get("nginx_port", "8081"))

    # fetch
    click.echo("📦 Downloading docker-compose.quickstart.yml...")
    try:
        resp = requests.get(DOCKER_COMPOSE_QUICKSTART_URL, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        click.echo(f"❌ Failed to fetch quickstart compose: {e}")
        return

    compose_text = resp.text
    replacements = {"NGINX-NAME": nginx_name, "NGINX-PORT": nginx_port}
    for key, val in replacements.items():
        compose_text = compose_text.replace(f"${{{{{key.upper()}}}}}", val)

    # save to temp dir and remember path
    temp_dir = tempfile.mkdtemp(prefix="sahaj-quickstart-")
    compose_path = os.path.join(temp_dir, "docker-compose.quickstart.yml")
    with open(compose_path, "w", encoding="utf-8") as f:
        f.write(compose_text)
    click.echo(f"✅ Compose file prepared at: {compose_path}")

    # run up
    try:
        run_native(["docker", "compose", "-f", compose_path, "up", "-d"], cwd=temp_dir)
        click.echo("✅ Quickstart complete! Containers are up and running.")
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️ Quickstart docker compose failed: {e.returncode}")
    write_quickstart_marker(compose_path)


@quickstart.command("stop")
def quickstart_stop():
    """Stop quickstart using the last remembered compose file."""
    compose_path = read_quickstart_marker()
    if not compose_path or not os.path.exists(compose_path):
        click.echo(
            "No remembered quickstart compose found. Start quickstart first or re-run start."
        )
        return
    temp_dir = os.path.dirname(compose_path)
    try:
        run_native(["docker", "compose", "-f", compose_path, "down"], cwd=temp_dir)
        click.echo("✅ Quickstart containers stopped.")
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️ docker compose down failed: {e.returncode}")


@quickstart.command("restart")
def quickstart_restart():
    """Restart quickstart (down then up)."""
    ctx = click.get_current_context()
    ctx.invoke(quickstart_stop)
    ctx.invoke(quickstart_start)


@quickstart.command("status")
def quickstart_status():
    """Show status for last quickstart run."""
    compose_path = read_quickstart_marker()
    if not compose_path or not os.path.exists(compose_path):
        click.echo("No remembered quickstart compose found.")
        return
    temp_dir = os.path.dirname(compose_path)
    run_native(["docker", "compose", "-f", compose_path, "ps"], cwd=temp_dir)


# Optional: a real init that fetches compose and runs docker (kept separate)
@init.command(name="run-demo")
@click.option(
    "--template/--no-template",
    default=False,
    help="Replace placeholders in compose with config values",
)
def init_run_demo(template):
    """(Demo) Fetch docker-compose and run containers (careful: this will call docker)."""
    click.echo("Fetching docker-compose file...")
    try:
        response = requests.get(DOCKER_COMPOSE_URL, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        click.echo(f"Error fetching docker-compose file: {e}")
        return

    compose_text = response.text

    if template:
        cfg = read_config()
        # example mapping
        mapping = {
            "ORG_NAME": cfg.get("organization_name", ""),
            "ADMIN_EMAIL": cfg.get("admin_email", ""),
            "REGION": cfg.get("default_region", ""),
        }
        for k, v in mapping.items():
            compose_text = compose_text.replace(f"{{{{{k}}}}}", v)

    tmpdir = tempfile.mkdtemp(prefix="sahaj_")
    compose_path = os.path.join(tmpdir, "docker-compose.yml")
    with open(compose_path, "w", encoding="utf-8") as f:
        f.write(compose_text)
    click.echo(f"docker-compose.yml saved to {compose_path}")

    click.echo("Starting containers with Docker Compose...\n")
    try:
        proc = subprocess.Popen(
            ["docker", "compose", "-f", compose_path, "up", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        # stream stdout
        for line in iter(proc.stdout.readline, ""):
            if line:
                click.echo(line.strip())
        proc.stdout.close()
        rc = proc.wait()
        if rc == 0:
            click.echo("\nContainers started successfully!")
        else:
            click.echo("\nDocker Compose finished with errors.")
    except FileNotFoundError:
        click.echo("Docker not found. Please ensure Docker is installed and in PATH.")


# -----------------------
# CLI entrypoint
# -----------------------
if __name__ == "__main__":
    cli()
