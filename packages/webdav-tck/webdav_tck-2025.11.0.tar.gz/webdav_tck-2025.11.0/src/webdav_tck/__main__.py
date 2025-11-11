"""CLI entry point for litmus test suite."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click

from webdav_tck.framework import TestRunner
from webdav_tck.session import WebdavTckSession
from webdav_tck.suites.basic import create_basic_suite
from webdav_tck.suites.copymove import create_copymove_suite
from webdav_tck.suites.locks import create_locks_suite
from webdav_tck.suites.props import create_props_suite


async def run_litmus(
    url: str,
    username: str | None,
    password: str | None,
    proxy: str | None,
    system_proxy: bool,
    client_cert: str | None,
    insecure: bool,
    quiet: bool,
    colour: bool | None,
    suites: str | None,
) -> int:
    """Run litmus test suites.

    Args:
        url: WebDAV server URL
        username: Optional username
        password: Optional password
        proxy: Optional proxy URL
        system_proxy: Use system proxy
        client_cert: Optional client certificate
        insecure: Ignore SSL verification
        quiet: Abbreviated output
        colour: Force color output (None = auto)
        suites: Comma-separated list of suites

    Returns:
        Exit code (0 = success, 1 = failures)
    """
    # Determine which suites to run
    available_suites = ["basic", "copymove", "props", "locks"]
    if suites:
        suite_list = [s.strip() for s in suites.split(",")]
        suite_list = [s for s in suite_list if s in available_suites]
    else:
        suite_list = available_suites

    if not suite_list:
        click.echo("No valid test suites specified", err=True)
        return 1

    # Set up debug log
    debug_log = Path("debug.log")

    # Create session
    session = WebdavTckSession(
        url=url,
        username=username,
        password=password,
        verify_ssl=not insecure,
        proxy=proxy if not system_proxy else None,
        client_cert=client_cert,
        debug_log=debug_log,
    )

    # Create test runner
    with TestRunner(quiet=quiet, use_color=colour, debug_log=debug_log) as runner:
        try:
            # Initialize session
            async with session:
                click.echo(f"Testing WebDAV server: {url}")
                if username:
                    click.echo(f"Using authentication: {username}")

                # Discover capabilities
                runner.log_debug(f"Connecting to {url}")
                await session.discover_capabilities()

                if session.class2:
                    click.echo("Server supports WebDAV Class 2 (locking)")
                else:
                    click.echo("Server supports WebDAV Class 1 (basic)")

                # Create test collection
                await session.create_test_collection()
                runner.log_debug(f"Created test collection: {session.base_path}")

                # Run test suites
                for suite_name in suite_list:
                    if suite_name == "basic":
                        suite = create_basic_suite(session)
                        await runner.run_suite(suite)
                    elif suite_name == "copymove":
                        suite = create_copymove_suite(session)
                        await runner.run_suite(suite)
                    elif suite_name == "props":
                        suite = create_props_suite(session)
                        await runner.run_suite(suite)
                    elif suite_name == "locks":
                        suite = create_locks_suite(session)
                        await runner.run_suite(suite)

                # Cleanup
                await session.cleanup_test_collection()

            # Print summary
            runner.print_summary()

            return runner.get_exit_code()

        except KeyboardInterrupt:
            click.echo("\n\nInterrupted by user", err=True)
            return 130
        except Exception as e:
            click.echo(f"\n\nFatal error: {e}", err=True)
            runner.log_debug(f"Fatal error: {e}")
            return 1


@click.command()
@click.argument("url")
@click.argument("username", required=False)
@click.argument("password", required=False)
@click.option("--proxy", "-p", help="Proxy server URL")
@click.option(
    "--system-proxy", "-s", is_flag=True, help="Use system proxy configuration"
)
@click.option("--client-cert", "-c", help="PKCS#12 client certificate path")
@click.option(
    "--insecure", "-i", is_flag=True, help="Ignore TLS certificate verification"
)
@click.option("--quiet", "-q", is_flag=True, help="Use abbreviated output")
@click.option(
    "--colour/--no-colour",
    default=None,
    help="Force color output on/off (default: auto-detect)",
)
@click.option("--suites", help="Comma-separated list of test suites to run")
@click.version_option()
def main(
    url: str,
    username: str | None,
    password: str | None,
    proxy: str | None,
    system_proxy: bool,
    client_cert: str | None,
    insecure: bool,
    quiet: bool,
    colour: bool | None,
    suites: str | None,
) -> None:
    """Run litmus WebDAV test suite against URL.

    \b
    Examples:
        litmus http://localhost/webdav/
        litmus http://localhost/webdav/ user password
        litmus --insecure https://localhost/webdav/
        litmus --quiet --suites=basic http://localhost/webdav/

    The test suite will create a collection called 'litmus' at the
    specified URL and run various WebDAV protocol compliance tests.
    """
    # Validate URL
    if not url.startswith("http://") and not url.startswith("https://"):
        click.echo("Error: URL must start with http:// or https://", err=True)
        sys.exit(1)

    # Validate credentials
    if username and not password:
        click.echo("Error: Password required when username is provided", err=True)
        sys.exit(1)

    if password and not username:
        click.echo("Error: Username required when password is provided", err=True)
        sys.exit(1)

    # Run async main
    exit_code = asyncio.run(
        run_litmus(
            url=url,
            username=username,
            password=password,
            proxy=proxy,
            system_proxy=system_proxy,
            client_cert=client_cert,
            insecure=insecure,
            quiet=quiet,
            colour=colour,
            suites=suites,
        )
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
