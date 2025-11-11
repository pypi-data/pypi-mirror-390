import asyncio
import codecs
import fcntl
import logging
import os
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

    def _cleanup_fds(self, master_fd: int | None, slave_fd: int | None) -> None:
        """Clean up file descriptors on error."""
        if master_fd is not None:
            try:
                os.close(master_fd)
            except OSError:
                pass
        if slave_fd is not None:
            try:
                os.close(slave_fd)
            except OSError:
                pass

    def _setup_child_process(
        self, slave_fd: int, command: list[str], env: dict[str, str] | None
    ) -> None:
        """Set up child process with PTY slave as controlling terminal."""
        # Create new session and set controlling terminal
        os.setsid()
        fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)

        # Redirect stdin/stdout/stderr to slave PTY
        os.dup2(slave_fd, 0)
        os.dup2(slave_fd, 1)
        os.dup2(slave_fd, 2)

        # Close the slave fd after duplication
        if slave_fd > 2:
            os.close(slave_fd)

        # Close master fd in child
        if self.master_fd is not None:
            os.close(self.master_fd)

        # Set up environment
        if env:
            for key, value in env.items():
                os.environ[key] = value

        # Set terminal environment
        os.environ["TERM"] = "xterm-256color"
        os.environ["COLORTERM"] = "truecolor"
        os.environ["TERM_PROGRAM"] = "indent"
        # Remove TERM_PROGRAM_VERSION if it exists
        os.environ.pop("TERM_PROGRAM_VERSION", None)

        # Execute command
        os.execvp(command[0], command)

    async def start(  # noqa: PLR0915
        self,
        command: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        """Start the terminal session with PTY"""
        if self._running:
            raise RuntimeError(f"Terminal session {self.session_id} already running")

        # Default to user's shell if no command specified
        if command is None:
            # Get user's default shell from environment, fallback to /bin/bash
            default_shell = os.environ.get("SHELL", "/bin/bash")
            command = [default_shell]

        # Create PTY with window size set BEFORE fork to eliminate race condition
        master_fd = None
        slave_fd = None
        try:
            # Open PTY pair
            master_fd, slave_fd = os.openpty()

            # Set window size on PTY before forking
            # This ensures the child process sees correct dimensions from the start
            size = struct.pack("HHHH", self.rows, self.cols, 0, 0)
            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, size)

            # Fork process
            self.pid = os.fork()
            self.master_fd = master_fd
        except OSError as e:
            # Clean up FDs if anything failed
            self._cleanup_fds(master_fd, slave_fd)
            logger.error(
                "Failed to create PTY or fork",
            )
            raise RuntimeError(f"Failed to create PTY or fork: {e}") from e

        if self.pid == 0:
            # Child process - set up PTY slave as controlling terminal
            try:
                self._setup_child_process(slave_fd, command, env)
            except Exception as e:
                # If exec fails, log and exit child process
                traceback.print_exc()
                sys.stderr.write(f"Failed to execute command {command}: {e}\n")
                sys.stderr.flush()
                os._exit(1)
        else:
            # Parent process - close slave fd (only child needs it)
            os.close(slave_fd)

            # Set up non-blocking I/O on master
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            # Configure terminal attributes
            try:
                attrs = termios.tcgetattr(self.master_fd)

                # Local flags (lflags)
                # Enable: icanon isig iexten echo echoe echoke echoctl pendin
                attrs[3] |= (
                    termios.ICANON
                    | termios.ISIG
                    | termios.IEXTEN
                    | termios.ECHO
                    | termios.ECHOE
                    | termios.ECHOKE
                    | termios.ECHOCTL
                )
                # Disable: echok echonl echoprt noflsh tostop
                attrs[3] &= ~(
                    termios.ECHOK
                    | termios.ECHONL
                    | termios.ECHOPRT
                    | termios.NOFLSH
                    | termios.TOSTOP
                )
                if hasattr(termios, "PENDIN"):
                    attrs[3] |= termios.PENDIN

                # Input flags (iflags)
                # Enable: icrnl ixon ixany imaxbel brkint
                attrs[0] |= (
                    termios.ICRNL
                    | termios.IXON
                    | termios.IXANY
                    | termios.IMAXBEL
                    | termios.BRKINT
                )
                # Disable: istrip inlcr igncr ixoff ignbrk inpck ignpar parmrk
                attrs[0] &= ~(
                    termios.ISTRIP
                    | termios.INLCR
                    | termios.IGNCR
                    | termios.IXOFF
                    | termios.IGNBRK
                    | termios.INPCK
                    | termios.IGNPAR
                    | termios.PARMRK
                )

                # Output flags (oflags)
                # Enable: opost onlcr
                attrs[1] |= termios.OPOST | termios.ONLCR
                # Disable: onocr onlret
                attrs[1] &= ~(termios.ONOCR | termios.ONLRET)

                # Control flags (cflags)
                # Enable: cread cs8 hupcl
                attrs[2] |= termios.CREAD | termios.CS8 | termios.HUPCL
                # Disable: parenb parodd clocal cstopb crtscts
                attrs[2] &= ~(
                    termios.PARENB | termios.PARODD | termios.CLOCAL | termios.CSTOPB
                )
                if hasattr(termios, "CRTSCTS"):
                    attrs[2] &= ~termios.CRTSCTS

                # Control characters (cchars)
                attrs[6][termios.VEOF] = ord("\x04")  # ^D
                attrs[6][termios.VERASE] = 0x7F  # ^? (DEL)
                attrs[6][termios.VINTR] = ord("\x03")  # ^C
                attrs[6][termios.VKILL] = ord("\x15")  # ^U
                attrs[6][termios.VQUIT] = ord("\x1c")  # ^\
                attrs[6][termios.VSUSP] = ord("\x1a")  # ^Z
                attrs[6][termios.VSTART] = ord("\x11")  # ^Q
                attrs[6][termios.VSTOP] = ord("\x13")  # ^S
                attrs[6][termios.VMIN] = 1
                attrs[6][termios.VTIME] = 0

                termios.tcsetattr(self.master_fd, termios.TCSANOW, attrs)
            except Exception as e:
                logger.warning(f"Failed to set terminal attributes: {e}")

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

        # Use incremental decoder to handle partial UTF-8 sequences

        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")

        try:
            while self._running:
                # Wait for data from the queue (non-blocking for event loop)
                data = await read_queue.get()

                if data is None:
                    # EOF or error - flush any remaining bytes in decoder
                    final = decoder.decode(b"", final=True)
                    if final:
                        self.output_callback(final)
                    break

                # Process the data with incremental decoder
                # This handles partial UTF-8 sequences correctly
                decoded = decoder.decode(data, final=False)
                if decoded:
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
