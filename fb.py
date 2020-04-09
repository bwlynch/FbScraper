#!/usr/bin/env python

import sys
import pathlib
import subprocess
import argparse
import fb_site
import pugsql
import os
import multiprocessing
import time
from fbscraper.settings import (
    SITE_DEFAULT_LIMIT_SEC,
    POST_DEFAULT_LIMIT_SEC,
)

queries = pugsql.module("queries/")
queries.connect(os.getenv("DB_URL"))


def discover(args):
    sites = queries.get_sites_to_discover()
    for site in sites:
        fb_site.discover(site["site_id"], limit_sec=SITE_DEFAULT_LIMIT_SEC)


def update(args):
    sites = queries.get_sites_to_discover()
    for site in sites:
        fb_site.update(site["site_id"], limit_sec=POST_DEFAULT_LIMIT_SEC)


def try_subcommands(skip_commands=[]):
    """
    Try git-style subcommands.
    """
    if len(sys.argv) > 1 and sys.argv not in skip_commands:
        binname = pathlib.Path(__file__)
        sub_cmd = (
            binname.parent.resolve() / f"{binname.stem}-{sys.argv[1]}{binname.suffix}"
        )
        try:
            sys.exit(subprocess.run([sub_cmd, *sys.argv[2:]]).returncode)
        except FileNotFoundError:
            pass


def main(args):
    target_func = None
    if args.command == "discover":
        target_func = discover
    elif args.command == "update":
        target_func = update

    if target_func:
        p = multiprocessing.Process(target=target_func, args=(args,))
        p.start()

        time.sleep(args.limit_sec)
        # terminate
        p.terminate()
        # Cleanup
        p.join()


if __name__ == "__main__":
    try_subcommands(skip_commands=["post", "site"])

    parser = argparse.ArgumentParser()
    cmds = parser.add_subparsers(title="sub command", dest="command", required=True)
    discover_cmd = cmds.add_parser("discover", help="do discover")
    discover_cmd.add_argument(
        "--limit-sec", type=int, help="process run time limit in seconds", default=3000
    )

    update_cmd = cmds.add_parser("update", help="do update")
    update_cmd.add_argument(
        "--limit-sec", type=int, help="process run time limit in seconds", default=3000
    )

    args = parser.parse_args()

    main(args)
