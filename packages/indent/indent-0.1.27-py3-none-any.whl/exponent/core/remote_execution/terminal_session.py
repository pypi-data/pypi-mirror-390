import asyncio
import fcntl
import logging
import os
import pty
import signal
import struct
import sys
import termios
import time
import traceback
from collections.abc import Callable

from exponent.core.remote_execution.terminal_types import (
    TerminalMessage,
    TerminalOutput,
    TerminalResetSessions,
)

logger = logging.getLogger(__name__)


class TerminalSession:
    """
    Manages a PTY session for terminal emulation.
    Runs on the CLI machine and streams output back to server.
    """

    def __init__(
        self,
        session_id: str,
        output_callback: Callable[[str], None],
        cols: int = 80,
        rows: int = 24,
    ):
        self.session_id = session_id
        self.output_callback = output_callback  # Called with terminal output
        self.cols = cols
        self.rows = rows
        self.master_fd: int | None = None
        self.pid: int | None = None
        self._running = False
        self._read_task: asyncio.Task[None] | None = None

    async def start(
        self,
        command: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        """Start the terminal session with PTY"""
        if self._running:
            raise RuntimeError(f"Terminal session {self.session_id} already running")

        # Default to bash if no command specified
        if command is None:
            command = ["/bin/bash"]

        # Spawn process with PTY
        try:
            self.pid, self.master_fd = pty.fork()
        except OSError as e:
            logger.error(
                "Failed to fork PTY",
            )
            raise RuntimeError(f"Failed to fork PTY: {e}") from e

        if self.pid == 0:
            # Child process - execute command
            try:
                # Set up environment
                if env:
                    for key, value in env.items():
                        os.environ[key] = value

                # Set terminal environment
                os.environ["TERM"] = "xterm-256color"
                os.environ["COLORTERM"] = "truecolor"

                # Execute command
                os.execvp(command[0], command)
            except Exception as e:
                # If exec fails, log and exit child process
                traceback.print_exc()
                sys.stderr.write(f"Failed to execute command {command}: {e}\n")
                sys.stderr.flush()
                os._exit(1)
        else:
            # Parent process - set up non-blocking I/O
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            # Set initial size
            self.resize(self.cols, self.rows)

            # Start reading from PTY
            self._running = True
            self._read_task = asyncio.create_task(self._read_from_pty())

    async def _read_from_pty(self) -> None:
        """Continuously read from PTY using event loop's add_reader (non-blocking)"""
        if self.master_fd is None:
            return

        loop = asyncio.get_event_loop()
        read_queue: asyncio.Queue[bytes | None] = asyncio.Queue()

        def read_callback() -> None:
            """Called by event loop when data is available on the FD"""
            if self.master_fd is None:
                return
            try:
                data = os.read(self.master_fd, 4096)
                if data:
                    # Put data in queue to be processed by async task
                    read_queue.put_nowait(data)
                else:
                    # EOF - PTY closed
                    read_queue.put_nowait(None)
            except OSError as e:
                if e.errno == 11:  # EAGAIN - shouldn't happen with add_reader
                    pass
                else:
                    read_queue.put_nowait(None)
            except Exception:
                logger.error(
                    "Unexpected error in PTY read callback",
                )
                read_queue.put_nowait(None)

        # Register the FD with the event loop
        loop.add_reader(self.master_fd, read_callback)

        try:
            while self._running:
                # Wait for data from the queue (non-blocking for event loop)
                data = await read_queue.get()

                if data is None:
                    # EOF or error
                    break

                # Process the data
                decoded = data.decode("utf-8", errors="replace")
                self.output_callback(decoded)
        finally:
            # Unregister the FD from the event loop
            loop.remove_reader(self.master_fd)

    async def write_input(self, data: str) -> None:
        """Write user input to PTY"""
        if not self._running or self.master_fd is None:
            raise RuntimeError(f"Terminal session {self.session_id} not running")

        try:
            os.write(self.master_fd, data.encode("utf-8"))
        except OSError:
            logger.error(
                "Error writing to PTY",
            )
            raise

    def resize(self, cols: int, rows: int) -> None:
        """Resize the PTY to match terminal dimensions"""
        if self.master_fd is None:
            return

        self.cols = cols
        self.rows = rows

        try:
            size = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, size)
        except Exception:
            logger.error(
                "Error resizing PTY",
            )

    async def stop(self) -> tuple[bool, int | None]:
        """
        Stop the terminal session and clean up resources.
        Returns (success, exit_code)
        """
        if not self._running:
            return True, None

        self._running = False

        # Cancel read task
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        exit_code = None

        # Close file descriptor
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except Exception:
                logger.error(
                    "Error closing PTY fd",
                )
            self.master_fd = None

        # Kill child process
        if self.pid is not None:
            try:
                os.kill(self.pid, signal.SIGTERM)
                # Wait for process to terminate (with timeout)
                for _ in range(10):  # Wait up to 1 second
                    try:
                        pid, status = os.waitpid(self.pid, os.WNOHANG)
                        if pid != 0:
                            exit_code = os.WEXITSTATUS(status)
                            break
                    except ChildProcessError:
                        break
                    await asyncio.sleep(0.1)
                else:
                    # Force kill if still running
                    try:
                        os.kill(self.pid, signal.SIGKILL)
                        os.waitpid(self.pid, 0)
                    except Exception:
                        pass
            except Exception:
                logger.error(
                    "Error killing PTY process",
                )
            self.pid = None

        logger.info(
            "Terminal session stopped",
        )

        return True, exit_code

    @property
    def is_running(self) -> bool:
        """Check if terminal session is running"""
        return self._running and self.master_fd is not None


class TerminalSessionManager:
    """Manages multiple terminal sessions"""

    def __init__(self, output_queue: asyncio.Queue[TerminalMessage]) -> None:
        self._sessions: dict[str, TerminalSession] = {}
        self._lock = asyncio.Lock()
        self._websocket: object | None = None
        self._output_queue = output_queue

        # Send reset message immediately to clear stale sessions
        try:
            reset_message = TerminalResetSessions()
            self._output_queue.put_nowait(reset_message)
            logger.info("Sent TerminalResetSessions message")
        except asyncio.QueueFull:
            logger.error("Failed to queue terminal reset message - queue full")

    def set_websocket(self, websocket: object) -> None:
        """Set the websocket for sending output"""
        self._websocket = websocket

    async def start_session(
        self,
        websocket: object,
        session_id: str,
        command: list[str] | None = None,
        cols: int = 80,
        rows: int = 24,
        env: dict[str, str] | None = None,
    ) -> str:
        """Start a new terminal session"""
        async with self._lock:
            if session_id in self._sessions:
                raise RuntimeError(f"Terminal session {session_id} already exists")

            # Store websocket reference
            self._websocket = websocket

            # Create output callback that queues data to be sent
            def output_callback(data: str) -> None:
                # Queue the output to be sent asynchronously
                try:
                    terminal_output = TerminalOutput(
                        session_id=session_id,
                        data=data,
                        timestamp=time.time(),
                    )
                    self._output_queue.put_nowait(terminal_output)
                except asyncio.QueueFull:
                    logger.error(
                        "Terminal output queue full",
                    )

            session = TerminalSession(
                session_id=session_id,
                output_callback=output_callback,
                cols=cols,
                rows=rows,
            )

            await session.start(command=command, env=env)
            self._sessions[session_id] = session

            return session_id

    async def send_input(self, session_id: str, data: str) -> bool:
        """Send input to a terminal session"""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False

            try:
                await session.write_input(data)
                return True
            except Exception:
                logger.error(
                    "Failed to send input to terminal",
                )
                return False

    async def resize_terminal(self, session_id: str, rows: int, cols: int) -> bool:
        """Resize a terminal session"""
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return False

            try:
                session.resize(cols, rows)
                return True
            except Exception:
                logger.error(
                    "Failed to resize terminal",
                )
                return False

    async def stop_session(self, session_id: str) -> bool:
        """Stop a terminal session"""
        async with self._lock:
            session = self._sessions.pop(session_id, None)
            if session is None:
                return True  # Already stopped

            try:
                await session.stop()
                return True
            except Exception:
                logger.error(
                    "Failed to stop terminal",
                )
                return False

    async def stop_all_sessions(self) -> None:
        """Stop all terminal sessions (cleanup on disconnect)"""
        async with self._lock:
            session_ids = list(self._sessions.keys())
            for session_id in session_ids:
                session = self._sessions.pop(session_id, None)
                if session:
                    try:
                        await session.stop()
                        logger.info(
                            "Stopped terminal session on cleanup",
                        )
                    except Exception:
                        logger.error(
                            "Error stopping terminal session on cleanup",
                        )
