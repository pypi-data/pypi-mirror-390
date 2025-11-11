import asyncio
import os
from typing import Any, TypedDict, cast

import aiohttp
import diskcache
from asyncache import cached
from cachetools import Cache
from platformdirs import user_cache_dir

from sifts.core.retry_utils import retry_on_exceptions

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=60)


class RootInfo(TypedDict):
    id: str
    nickname: str


class RootInfoResponse(TypedDict):
    root: RootInfo | None


class RootQueryResponse(TypedDict):
    data: RootInfoResponse


class CloningStatus(TypedDict):
    status: str
    commit: str | None


class GitRoot(TypedDict):
    nickname: str
    id: str
    state: str
    gitignore: str
    cloningStatus: CloningStatus | None


class GroupRoots(TypedDict):
    roots: list[GitRoot]


class GroupResponse(TypedDict):
    group: GroupRoots


class GroupRootsResponse(TypedDict):
    data: GroupResponse


# TypedDicts for root vulnerabilities query
class Vulnerability(TypedDict):
    id: str
    findingId: str
    where: str
    specific: str
    state: str
    source: str
    technique: str


class RootVulnerabilities(TypedDict):
    vulnerabilities: list[Vulnerability]


class RootVulnerabilitiesResponseData(TypedDict):
    root: RootVulnerabilities | None


class RootVulnerabilitiesResponse(TypedDict):
    data: RootVulnerabilitiesResponseData


# TypedDicts for finding query
class Finding(TypedDict):
    title: str
    id: str


class FindingResponseData(TypedDict):
    finding: Finding | None


class FindingResponse(TypedDict):
    data: FindingResponseData


class VulnerabilityResponseData(TypedDict):
    vulnerability: Vulnerability | None


class GraphQLApiError(Exception):
    """Raised when the GraphQL API returns errors."""


class VulnerabilityResponse(TypedDict):
    data: VulnerabilityResponseData


# TypedDicts for file vulnerabilities query
class FileVulnerabilityNode(TypedDict):
    where: str
    state: str
    specific: str
    hacker: str
    reportDate: str


class FileVulnerabilityEdge(TypedDict):
    node: FileVulnerabilityNode


class FileVulnerabilities(TypedDict):
    edges: list[FileVulnerabilityEdge]


class FileFinding(TypedDict):
    title: str
    vulnerabilities: FileVulnerabilities


class FileVulnerabilitiesGroup(TypedDict):
    findings: list[FileFinding]


class FileVulnerabilitiesResponseData(TypedDict):
    group: FileVulnerabilitiesGroup


class FileVulnerabilitiesResponse(TypedDict):
    data: FileVulnerabilitiesResponseData


class FileFindingSummary(TypedDict):
    title: str
    lines: list[int]


if os.environ.get("CACHE_ENABLED") == "true":
    CACHE = diskcache.Cache(user_cache_dir("sifts", "fluidattacks"))
else:
    CACHE = Cache(maxsize=100000)

# GraphQL query for root info
ROOT_QUERY = """
query GetRoot($groupName: String!, $rootId: ID!) {
  root(groupName: $groupName, rootId: $rootId) {
    ... on GitRoot {
      groupName
      id
      nickname
      state
      gitignore
      cloningStatus {
        commit
      }
    }
  }
}
"""

GROUP_ROOTS_QUERY = """
query GroupRoots($groupName: String!) {
  group(groupName: $groupName) {
    roots {
      ... on GitRoot {
        nickname
        id
        state
        gitignore
        cloningStatus {
          status
        }
      }
    }
  }
}
"""

ROOT_VULNERABILITIES_QUERY = """
query GetRootVulnerabilities($groupName: String!, $rootId: ID!) {
  root(groupName: $groupName, rootId: $rootId) {
    ... on GitRoot {
      vulnerabilities {
        id
        findingId
        where
        specific
        state
        source
        technique
      }
    }
  }
}
"""

FINDING_QUERY = """
query GetFinding($identifier: String!) {
  finding(identifier: $identifier) {
    title
    id
  }
}
"""

VULNERABILITY_QUERY = """
query GetVulnerability($uuid: String!) {
  vulnerability(uuid: $uuid) {
    id
    technique
  }
}
"""

FILE_VULNERABILITIES_QUERY = """
query GetFileVulnerabilities($groupName: String!, $where: String!) {
  group(groupName: $groupName) {
    findings(filters: {where: $where}) {
      title
      vulnerabilities(first: 1000) {
        edges {
          node {
            id
            where
            state
            specific
            hacker
            reportDate
          }
        }
      }
    }
  }
}
"""


@retry_on_exceptions(
    exceptions=(asyncio.TimeoutError,),
    max_attempts=5,
)
async def execute_graphql_query(
    session: aiohttp.ClientSession,
    query: str,
    variables: dict[str, Any],
) -> dict[str, Any]:
    payload = {"query": query, "variables": variables}
    async with session.post(
        "/api",
        json=payload,
        timeout=DEFAULT_TIMEOUT,
    ) as response:
        response.raise_for_status()
        result = await response.json()
        if "errors" in result:
            raise GraphQLApiError(result["errors"])
        return result  # type: ignore[no-any-return]


@cached(cache=CACHE, key=lambda *params: f"root-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_root(
    session: aiohttp.ClientSession,
    group_name: str,
    root_id: str,
) -> RootQueryResponse:
    variables = {"groupName": group_name, "rootId": root_id}
    response: RootQueryResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        ROOT_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"group_roots-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_group_roots(
    session: aiohttp.ClientSession,
    group_name: str,
) -> GroupRootsResponse:
    variables = {"groupName": group_name}
    response: GroupRootsResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        GROUP_ROOTS_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"group_roots-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_root_vulnerabilities(
    session: aiohttp.ClientSession,
    group_name: str,
    root_id: str,
) -> RootVulnerabilitiesResponse:
    variables = {"groupName": group_name, "rootId": root_id}
    response: RootVulnerabilitiesResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        ROOT_VULNERABILITIES_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"finding-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_finding(
    session: aiohttp.ClientSession,
    finding_id: str,
) -> FindingResponse:
    variables = {"identifier": finding_id}
    response: FindingResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        FINDING_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"vulnerability-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_vulnerability(
    session: aiohttp.ClientSession,
    uuid: str,
) -> VulnerabilityResponse:
    variables = {"uuid": uuid}
    response: VulnerabilityResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        VULNERABILITY_QUERY,
        variables,
    )
    return response


@cached(cache=CACHE, key=lambda *params: f"file_vulnerabilities-{'-'.join(params[1:])}")  # type: ignore[misc]
async def fetch_file_vulnerabilities(
    session: aiohttp.ClientSession,
    group_name: str,
    root_nickname: str,
    file_path: str,
) -> FileVulnerabilitiesResponse:
    # Construct the where filter combining root_nickname and file_path
    where_filter = f"{root_nickname}/{file_path}"
    variables = {"groupName": group_name, "where": where_filter}
    response: FileVulnerabilitiesResponse = await execute_graphql_query(  # type: ignore[assignment]
        session,
        FILE_VULNERABILITIES_QUERY,
        variables,
    )
    return response


class ApiClient:
    _instance: "ApiClient | None" = None

    def __init__(self, token: str) -> None:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self._session = aiohttp.ClientSession(
            base_url="https://app.fluidattacks.com",
            headers=headers,
        )
        self._token = token
        self._closed = False

    @classmethod
    def get_instance(cls) -> "ApiClient | None":
        token = os.environ.get("INTEGRATES_API_TOKEN")
        if not token:
            return None
        if cls._instance is None or cls._instance._closed or cls._instance._token != token:
            cls._instance = cls(token)
        return cls._instance

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._closed:
            msg = "ApiClient session is closed"
            raise RuntimeError(msg)
        return self._session

    async def aclose(self) -> None:
        if not self._closed:
            await self._session.close()
            self._closed = True

    # Wrapper methods
    async def get_root(self, group_name: str, root_id: str) -> RootQueryResponse:
        return cast(
            RootQueryResponse,
            await fetch_root(self.session, group_name, root_id),
        )

    async def get_group_roots(self, group_name: str) -> GroupRootsResponse:
        return cast(
            GroupRootsResponse,
            await fetch_group_roots(self.session, group_name),
        )

    async def get_root_vulnerabilities(
        self,
        group_name: str,
        root_id: str,
    ) -> RootVulnerabilitiesResponse:
        return cast(
            RootVulnerabilitiesResponse,
            await fetch_root_vulnerabilities(self.session, group_name, root_id),
        )

    async def get_finding(self, finding_id: str) -> FindingResponse:
        return cast(
            FindingResponse,
            await fetch_finding(self.session, finding_id),
        )

    async def get_vulnerability(self, uuid: str) -> VulnerabilityResponse:
        return cast(
            VulnerabilityResponse,
            await fetch_vulnerability(self.session, uuid),
        )

    async def get_file_vulnerabilities(
        self,
        group_name: str,
        root_nickname: str,
        file_path: str,
    ) -> FileVulnerabilitiesResponse:
        return cast(
            FileVulnerabilitiesResponse,
            await fetch_file_vulnerabilities(
                self.session,
                group_name,
                root_nickname,
                file_path,
            ),
        )

    async def get_file_vulnerabilities_simple(
        self,
        group_name: str,
        root_nickname: str,
        file_path: str,
    ) -> list[FileFindingSummary]:
        raw = await self.get_file_vulnerabilities(group_name, root_nickname, file_path)
        findings = raw.get("data", {}).get("group", {}).get("findings", [])

        full_where = f"{root_nickname}/{file_path}"
        summaries: list[FileFindingSummary] = []

        for f in findings:
            title = f.get("title", "")
            edges = (
                f.get("vulnerabilities", {}).get("edges", [])
                if isinstance(f.get("vulnerabilities"), dict)
                else []
            )
            line_set: set[int] = set()
            for e in edges:
                node = e.get("node", {}) if isinstance(e, dict) else {}
                if node.get("where") == full_where and node.get("state") == "VULNERABLE":
                    specific = node.get("specific")
                    if isinstance(specific, str):
                        if specific.isdigit():
                            line_set.add(int(specific))
                    elif isinstance(specific, int):
                        line_set.add(specific)
            if line_set:
                summaries.append({"title": title, "lines": sorted(line_set)})

        return summaries
