import asyncio
import json
import logging
import logging.config
import os
import sys
import tempfile
from pathlib import Path

import aioboto3
import aiofiles
import bugsnag
import click
from fluidattacks_core.logging import PRODUCT_LOGGING
from platformdirs import user_data_dir

import sifts
from sifts.analysis.orchestrator import scan_projects
from sifts.config import SiftsConfig
from sifts.core.sarif_result import get_sarif
from sifts.io.api import ApiClient
from taxonomy import TaxonomyIndex

os.environ["AWS_REGION_NAME"] = os.environ.get("AWS_REGION_NAME", "us-east-1")

LOGGING_CONFIG = {
    **PRODUCT_LOGGING,
}

logging.config.dictConfig(LOGGING_CONFIG)

LOGGER = logging.getLogger(__name__)
bugsnag.configure(
    api_key="78f25bb5dab62944e52ceffd694cd7e0",
    project_root=str(Path(__file__).parent.parent.parent),
)


# Detect if running in AWS Batch
def _get_base_dir() -> Path:
    """
    Get the base directory for sifts data.

    In AWS Batch, use a temporary directory to avoid issues with user_data_dir.
    Otherwise, use the standard user data directory.
    """
    if os.getenv("AWS_BATCH_JOB_ID"):
        # Running in AWS Batch, use a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="sifts_")
        return Path(temp_dir)

    # Running locally, use user data directory
    return Path(user_data_dir(appname="sifts", appauthor="fluidattacks", ensure_exists=True))


@click.command()
@click.argument("group-name")
@click.argument("root")
@click.option(
    "--output-path",
    type=click.Path(),
    default="sarif.json",
    help="Path to output SARIF file",
)
def main_cli(group_name: str, root: str, output_path: str) -> None:
    """Analyze a root by fetching from integrates, pulling repos, and generating SARIF."""
    try:
        asyncio.run(_run_root_analysis(group_name, root, Path(output_path)))
    except Exception:
        LOGGER.exception("Error during root analysis")
        sys.exit(1)


async def _run_root_analysis(
    group_name: str,
    nickname: str,
    output_path: Path,
) -> None:
    """Run the root analysis workflow."""
    integrates_client = ApiClient.get_instance()
    if integrates_client is None:
        LOGGER.error("Failed to initialize integrates client")
        return
    LOGGER.info("Fetching group roots for %s %s", group_name, nickname)
    data = await integrates_client.get_group_roots(group_name)
    root_id = next(
        (
            x["id"]
            for x in data["data"]["group"]["roots"]
            if (x["nickname"]).lower() == nickname.lower()
        ),
        None,
    )

    if not root_id:
        LOGGER.error("Root ID not found")
        return

    base_dir = _get_base_dir()
    Path(base_dir, "groups").mkdir(parents=True, exist_ok=True)
    process = await asyncio.create_subprocess_exec(
        "melts",
        "pull-repos",
        "--group",
        group_name,
        "--root",
        nickname,
        cwd=base_dir,
    )
    await process.wait()
    if process.returncode != 0:
        LOGGER.error("Failed to pull repos")
        return
    working_dir = Path(base_dir, "groups", group_name, nickname)
    if not working_dir.exists() or not any(working_dir.iterdir()):
        LOGGER.warning("Working directory not found")
        return

    await TaxonomyIndex.load()

    config = SiftsConfig.create_with_overrides(
        root_nickname=nickname,
        group_name=group_name,
        root_dir=working_dir,
        split_subdirectories=False,
        enable_navigation=False,
        include_vulnerabilities_subcategories=["SQL Injection", "Cross-Site Scripting"],
        model="gpt-4.1-mini",
        database_backend="dynamodb",
    )
    LOGGER.info("Scanning projects for %s %s", group_name, nickname)
    LOGGER.info("Using database backend: %s", config.database_backend)
    if config.database_backend == "sqlite":
        LOGGER.info("SQLite database path: %s", config.sqlite_database_path)

    await scan_projects(config)
    db_backend = config.get_database()
    analyses = [
        x
        for x in await db_backend.get_analyses_by_root(group_name, nickname, sifts.__version__)
        if x.vulnerable
    ]
    sarif = await get_sarif(analyses, config)
    async with aiofiles.open(output_path, "w") as f:
        await f.write(json.dumps(sarif, indent=2))
    async with aioboto3.Session().client("s3") as s3_client:
        key = f"results/{group_name}_{nickname}_sifts_{sifts.__version__}.sarif"
        await s3_client.put_object(
            Bucket="machine.data",
            Key=key,
            Body=json.dumps(sarif, indent=2),
        )
        LOGGER.info("Uploaded SARIF file to %s", key)


if __name__ == "__main__":
    main_cli()
