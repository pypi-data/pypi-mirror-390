from typing import Literal

from pydantic import BaseModel, Field

from rock import env_vars
from rock.actions import (
    BashAction,
    CloseBashSessionRequest,
    Command,
    CreateBashSessionRequest,
    InitDockerEnvRequest,
    ReadFileRequest,
    WriteFileRequest,
)


class SandboxStartRequest(BaseModel):
    image: str = ""
    """image"""
    auto_clear_time_minutes: int = env_vars.ROCK_DEFAULT_AUTO_CLEAR_TIME_MINUTES
    """The time for automatic container cleaning, with the unit being minutes"""
    pull: Literal["never", "always", "missing"] = "missing"
    """When to pull docker images."""
    memory: str = "8g"
    """The amount of memory to allocate for the container."""
    cpus: float = 2
    """The amount of CPUs to allocate for the container."""

    def transform(self) -> InitDockerEnvRequest:
        res = InitDockerEnvRequest(**self.model_dump())
        res.auto_clear_time = self.auto_clear_time_minutes
        return res


class SandboxCommand(BaseModel):
    command: str | list[str]
    """The command to run. Should be a list of strings (recommended because
    of automatic escaping of spaces etc.) unless you set `shell=True`
    (i.e., exactly like with `subprocess.run()`).
    """
    timeout: float | None = 1200
    """The timeout for the command. None means no timeout."""
    shell: bool = False
    """Same as the `subprocess.run()` `shell` argument."""
    check: bool = False
    """Whether to check for the exit code. If True, we will raise a
    `CommandFailedError` if the command fails.
    """
    error_msg: str = ""
    """This error message will be used in the `NonZeroExitCodeError` if the
    command has a non-zero exit code and `check` is True.
    """
    env: dict[str, str] | None = None
    """Environment variables to pass to the command."""
    cwd: str | None = None
    """The current working directory to run the command in."""
    sandbox_id: str | None = None
    """The id of the sandbox."""

    def transform(self) -> Command:
        res = Command(**self.model_dump())
        res.container_name = self.sandbox_id
        return res


class SandboxCreateBashSessionRequest(BaseModel):
    startup_source: list[str] = []
    """Source the following files before running commands.
    The reason this gets a special treatment is that these files
    often overwrite PS1, which we need to reset.
    """
    session: str = "default"
    startup_timeout: float = 1.0
    """The timeout for the startup commands."""
    sandbox_id: str | None = None
    """The id of the sandbox."""
    max_read_size: int = 2000
    env_enable: bool = False
    env: dict[str, str] | None = Field(default=None)

    def transform(self) -> CreateBashSessionRequest:
        res = CreateBashSessionRequest(**self.model_dump())
        res.container_name = self.sandbox_id
        res.session_type = "bash"
        return res


class SandboxBashAction(BaseModel):
    command: str
    """The command to run."""
    session: str = "default"
    """The session to run the command in."""
    sandbox_id: str | None = None
    """The id of the sandbox."""
    timeout: float | None = None
    """The timeout (seconds) for the command. None means no timeout."""
    is_interactive_command: bool = False
    """For a non-exiting command to an interactive program
    (e.g., gdb), set this to True."""
    is_interactive_quit: bool = False
    """This will disable checking for exit codes, since the command won't terminate.
    If the command is something like "quit" and should terminate the
    interactive program, set this to False.
    """
    check: Literal["silent", "raise", "ignore"] = "raise"
    """Whether to check for the exit code.
    If "silent", we will extract the exit code, but not raise any errors. If there is an error extracting the exit code, it will be set to None.
    If "raise", we will raise a `NonZeroExitCodeError` if the command has a non-zero exit code or if there is an error extracting the exit code.
    If "ignore", we will not attempt to extract the exit code, but always leave it as None.
    """
    error_msg: str = ""
    """This error message will be used in the `NonZeroExitCodeError` if the
    command has a non-zero exit code and `check` is True.
    """
    expect: list[str] = []
    """Outputs to expect in addition to the PS1"""

    def transform(self) -> BashAction:
        res = BashAction(**self.model_dump())
        res.container_name = self.sandbox_id
        res.action_type = "bash"
        return res


class SandboxCloseBashSessionRequest(BaseModel):
    session: str = "default"
    sandbox_id: str | None = None

    def transform(self) -> CloseBashSessionRequest:
        res = CloseBashSessionRequest(**self.model_dump())
        res.container_name = self.sandbox_id
        res.session_type = "bash"
        return res


class SandboxReadFileRequest(BaseModel):
    path: str
    """Path to read from."""
    encoding: str | None = None
    """Encoding to use when reading the file. None means default encoding.
    This is the same as the `encoding` argument of `Path.read_text()`."""
    errors: str | None = None
    """Error handling to use when reading the file. None means default error handling.
    This is the same as the `errors` argument of `Path.read_text()`."""
    sandbox_id: str | None = None

    def transform(self) -> ReadFileRequest:
        res = ReadFileRequest(**self.model_dump())
        res.container_name = self.sandbox_id
        return res


class SandboxWriteFileRequest(BaseModel):
    content: str
    """Content to write."""
    path: str
    """Path to write to."""
    sandbox_id: str | None = None

    def transform(self) -> WriteFileRequest:
        res = WriteFileRequest(**self.model_dump())
        res.container_name = self.sandbox_id
        return res


class WarmupRequest(BaseModel):
    image: str = "hub.docker.alibaba-inc.com/chatos/python:3.11"
