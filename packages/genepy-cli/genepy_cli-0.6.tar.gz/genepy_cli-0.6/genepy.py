"""Genepy command line interface."""

import argparse
import configparser
import json
import logging
import sys
from contextlib import suppress
from functools import cached_property
from getpass import getpass
from json import JSONDecodeError
from pathlib import Path
from textwrap import dedent, indent
from urllib.parse import urljoin, urlparse

import requests
from rich.console import Console
from rich.table import Table
from rich.text import Text
from slugify import slugify
from websocket import create_connection

DEFAULT_BACKEND = "https://genepy.org/"
logger = logging.getLogger(__name__)


def unslugify(slug):
    return slug.replace("-", " ").title()


class APIError(Exception): ...


class GenepyAPI:
    def __init__(self, instance, auth, language="en"):
        self.session = requests.session()
        self.language = language
        self.instance = instance
        self.auth = auth

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def request(self, method, url, data=None, params=None, json=None):
        try:
            response = self.session.request(
                method, url, params=params, data=data, auth=self.auth, json=json
            )
            response.raise_for_status()
        except requests.RequestException as err:
            try:
                json_response = err.response.json()
                if "detail" in json_response:
                    raise APIError(json_response["detail"]) from err
                raise APIError(json_response)
            except JSONDecodeError:
                pass
            raise
        else:
            return response.json()

    def get(self, url, params=None):
        return self.request("GET", url, params=params)

    def post(self, url, data):
        return self.request("POST", url, json=data)

    def put(self, url, data):
        return self.request("PUT", url, json=data)

    @property
    def language(self):
        return self.session.headers["Accept-Language"]

    @language.setter
    def language(self, value):
        self.session.headers.update({"Accept-Language": value})

    @cached_property
    def root(self):
        return self.get(urljoin(self.instance, "/api/"))

    def ping(self):
        """Just test if the API can be joined.

        return a tuple: (bool, reason), the boolean value is True if
        the API can be reached, False otherwise with a reason given.
        """
        try:
            root = self.root
        except requests.RequestException as err:
            try:
                return False, err.response.json()["detail"]
            except (LookupError, json.JSONDecodeError):
                return False, err
        if "exercises" not in root:
            return False, "Can't find 'exercises' in the provided API"
        return True, "OK"

    def ping_or_die(self):
        reacheable, reason = self.ping()
        if not reacheable:
            print(f"{self.instance}: {reason}", file=sys.stderr)
            exit(1)

    def get_all(self, endpoint, params=None):
        while endpoint:
            response = self.get(endpoint, params=params)
            yield from response["results"]
            endpoint = response.get("next")
            if params and "limit" in params:
                break

    def exercises(self, page=None, **kwargs):
        yield from self.get_all(self.root["exercises"], params={"page": page} | kwargs)

    def pages(self):
        yield from self.get_all(self.root["pages"])

    def answers(self, is_valid=None):
        yield from self.get_all(self.root["answers"], params={"is_valid": is_valid})

    def profile(self):
        return self.get(self.root["me"])


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog=dedent(
            """
    These are common genepy commands used in various situations:

    Before using:
       login     To save your login/password (account creation happen online).

    To learn:
        next     Easy way to get an unsolved exercise to work on.
        list     Show some exercises.
        get      Download an exercise to do it.
        check    Validate your answer.

    To teach:
        new     Create a new exericse.
        pull    Download all your exercises to edit/version them locally.
        push    Upload your exercises back to the website.

    Misc:
        profile  Show infos about the currently logged-in user.
    """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    verbosities = [logging.ERROR, logging.INFO, logging.DEBUG]

    class IncreaseVerbosity(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            namespace.verbosity += 1

    class DecreaseVerbosity(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            namespace.verbosity -= 1

    parser.add_argument(
        "--verbose",
        "-v",
        action=IncreaseVerbosity,
        nargs=0,
        dest="verbosity",
        default=1,
    )
    parser.add_argument(
        "--quiet", "-q", action=DecreaseVerbosity, nargs=0, dest="verbosity", default=1
    )

    subparsers = parser.add_subparsers()
    login_parser = subparsers.add_parser("login")
    login_parser.set_defaults(func=CLI.do_login)

    profile_parser = subparsers.add_parser("profile")
    profile_parser.set_defaults(func=CLI.do_profile)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument(
        "page", nargs="?", help="Page (list of exercises) to show."
    )
    list_parser.set_defaults(func=CLI.do_list)

    get_parser = subparsers.add_parser("get")
    get_parser.set_defaults(func=CLI.do_get)
    get_parser.add_argument("name", nargs="+", help="Exercise name")

    check_parser = subparsers.add_parser("check")
    check_parser.set_defaults(func=CLI.do_check)
    check_parser.add_argument("exercise_path", type=Path, help="File to check")

    pull_parser = subparsers.add_parser("pull", description=CLI.do_pull.__doc__)
    pull_parser.add_argument(
        "exercises",
        nargs="*",
        type=Path,
        help="Only download those exercises. "
        """To download a full page: `genepy pull 'exercises/*'`, """
        "(note the simple quotes to avoid bash expansion, else only already "
        "downloaded exercises would be downloaded), "
        """to download a single exercise: `genepy pull exercises/hello-world/`. """
        "All exercises are downloaded by default.",
    )
    pull_parser.set_defaults(func=CLI.do_pull)

    new_parser = subparsers.add_parser("new", description=CLI.do_new.__doc__)
    new_parser.add_argument(
        "path",
        help="Path to create for the new exercise, kind of you're using mkdir. "
        "Use as: genepy new page_name/exercise_slug",
    )
    new_parser.set_defaults(func=CLI.do_new)

    push_parser = subparsers.add_parser("push", description=CLI.do_push.__doc__)
    push_parser.add_argument(
        "exercises",
        nargs="*",
        type=Path,
        help="Only upload those exercises. "
        """To upload a full page: `genepy push exercises/*`, """
        """to upload a single exercise: `genepy push exercises/hello-world/`. """
        "All exercises are uploaded by default.",
    )
    push_parser.set_defaults(func=CLI.do_push)

    args = parser.parse_args()
    args.verbosity = verbosities[max(min(args.verbosity, 2), 0)]
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    return args


def get_config():
    config_file = Path("~/.genepy.conf").expanduser()
    config_file.touch()
    config_file.chmod(0o600)
    config = configparser.RawConfigParser()
    config.config_file = config_file
    config.read(config_file)
    if "backend" not in config:
        config["backend"] = {"URL": DEFAULT_BACKEND}
        with open(config.config_file, "w", encoding="UTF-8") as configfile:
            config.write(configfile)
    if DEFAULT_BACKEND not in config:
        config[DEFAULT_BACKEND] = {}
        with open(config.config_file, "w", encoding="UTF-8") as configfile:
            config.write(configfile)
    return config


def normalize(text):
    if not text:
        return ""
    if text[-1] != "\n":
        text += "\n"
    return text.replace("\r\n", "\n")


def save_exercise(translations) -> Path:
    """Save the given exercise, returns the Path in which it has been written."""
    exercise = list(translations.values())[0]  # Easy access to common attributes
    path = Path(urlparse(exercise["html"]).path[1:])
    path.mkdir(exist_ok=True, parents=True)

    # Consistency check before writing
    with suppress(FileNotFoundError):
        old_meta = json.loads((path / "meta").read_text(encoding="UTF-8"))
        if old_meta["url"] != exercise["url"]:
            raise RuntimeError(
                f"Exercise {old_meta['url']} and exercise {exercise['url']} "
                "have the same slug and are the same page, please fix it.",
            )

    meta = {
        "author": exercise["author"],
        "tags": [tag["slug"] for tag in exercise["tags"]],
        "created_at": exercise["created_at"],
        "is_published": exercise["is_published"],
        "page": exercise["page"],
        "points": exercise["points"],
        "position": exercise["position"],
        "slug": exercise["slug"],
        "url": exercise["url"],
    }

    # Handle translations:
    for language, exercise in translations.items():
        meta[f"title_{language}"] = exercise["title"]
        (path / f"wording_{language}.md").write_text(
            normalize(exercise["wording"]), encoding="UTF-8"
        )

    (path / "check.py").write_text(normalize(exercise["check_py"]), encoding="UTF-8")
    (path / "initial_solution").write_text(
        normalize(exercise["initial_solution"]), encoding="UTF-8"
    )
    (path / "meta").write_text(
        json.dumps(meta, indent=4, ensure_ascii=False, sort_keys=True) + "\n"
    )
    return path


def get_wordings_translations(path: Path):
    """Given an exercise Path find all wording translations in wording_*.md files."""
    for wording in path.glob("wording_*.md"):
        yield wording.name[len("wording_") : -3], wording.read_text(encoding="UTF-8")


def input_or_default(message, *, default=None, input_function=input):
    if isinstance(default, (list, tuple)):
        if len(default) == 0:
            default = None
        elif len(default) == 1:
            default = default[0]
    if default is None:
        return input_function(f"{message}: ").strip()
    if isinstance(default, (list, tuple)):
        choice = input_function(
            f"{message} (give {', '.join(f'{pk} for {value}' for pk, value in enumerate(default))}, or type a new one): "
        ).strip()
        if choice.isdecimal():
            try:
                return default[int(choice)]
            except IndexError:
                print("No, not this one :D")
                return input_or_default(
                    message, input_function=input_function, default=default
                )
        return choice
    if input_function is getpass:
        choice = input_function(
            f"{message} (leave empty to keep the known password): "
        ).strip()
    else:
        choice = input_function(f"{message} (default to {default!r}): ").strip()
    if not choice:
        return default
    return choice


class CLI:
    def __init__(self, api, languages):
        self.api = api
        self.languages = languages

    def dispatch(self, args: dict):
        try:
            args.pop("func")(self, **args)
        except KeyboardInterrupt:
            return

    def do_new(self, path):
        """Create a new exerise at the given path."""
        try:
            page, slug = path.strip("/").split("/", maxsplit=1)
        except ValueError:
            print("Expected path to be like page/slug, so just one slash.")
            return

        all_pages = {page["slug"]: page for page in self.api.pages()}
        if page not in all_pages:
            print("Unknown page, use one of:")
            for page in all_pages.keys():
                print("-", page)
            print("Or create it via the admin web interface.")
            return

        try:
            created = self.api.post(
                self.api.root["exercises"],
                {
                    "page": all_pages[page]["url"],
                    "title": unslugify(slug),
                    "slug": slug,
                },
            )
        except requests.RequestException as err:
            try:
                print(err.response.json())
            except Exception:
                raise err
        else:
            path = self._pull_exercise_by_url(created["url"])
            print(f"Created {path}")

    def _pull_exercise_by_url(self, url) -> Path:
        translations = {}
        for language in self.languages:
            self.api.language = language
            translations[language] = self.api.get(url)
        return save_exercise(translations)

    def do_push(self, exercises=()):
        """Push exercises (previously pulled) to the website."""
        if not exercises:  # Upload all by default
            exercises = [path.parent for path in Path(".").glob("*/*/meta")]
        for exercise in exercises:
            try:
                meta = json.loads((exercise / "meta").read_text())
                meta["check_py"] = (exercise / "check.py").read_text(encoding="UTF-8")
                meta["initial_solution"] = (exercise / "initial_solution").read_text(
                    encoding="UTF-8"
                )
            except FileNotFoundError as err:
                logging.error("Skipping %s: %s", exercise, err)
                continue
            for language, wording in get_wordings_translations(exercise):
                self.api.language = language
                meta["wording"] = wording
                meta["title"] = meta.get("title_" + language, "(untitled)")
                logger.info("[%s] Uploading %r", language, meta["title"])
                try:
                    self.api.put(meta["url"], meta)
                except APIError as err:
                    print(err)

    def _should_pull(self, exercise_path: Path, exercises):
        """Returns True if exercise_path should be downloaded
        according to what user asked in exercises.
        """
        # Default case, when used did not provided an 'exercises'
        # argument, download everything:
        if not exercises:
            return True
        # Easy case, the exercise is literally asked for:
        if exercise_path in exercises:
            return True
        # Cases with globs like 'exercises/*'
        if any(exercise_path.match(str(exercise)) for exercise in exercises):
            return True
        # And finally for directory-like pulls like `exercises/`.
        if any(str(exercise_path).startswith(str(exercise)) for exercise in exercises):
            return True
        return False

    def do_pull(self, exercises=()):
        """Pull exercises from the website, store them in a directory per page."""
        for exercise in self.api.exercises():
            exercise_path = Path(urlparse(exercise["html"]).path[1:])
            if not self._should_pull(exercise_path, exercises):
                logger.debug("Skipped %s", exercise_path)
                continue
            logger.info("Downloading %s", exercise_path)
            self._pull_exercise_by_url(exercise["url"])

    def do_login(self):
        config = get_config()
        known_hosts = [host for host in config.sections() if host.startswith("http")]
        backend = input_or_default("Website URL", default=known_hosts)
        config["backend"] = {"URL": backend}
        already_known_username = config.get(backend, "username", fallback=None)
        already_known_password = config.get(backend, "password", fallback=None)
        username = input_or_default("Username", default=already_known_username)
        password = input_or_default(
            "Password", default=already_known_password, input_function=getpass
        )
        config[backend] = {
            "username": username,
            "password": password,
            "languages": "en, fr",
        }
        with open(config.config_file, "w", encoding="UTF-8") as configfile:
            config.write(configfile)

    def do_profile(self):
        console = Console()
        profile = self.api.profile()
        console.print("#", profile["username"], style="bold")
        console.print()
        console.print("## Teams", style="bold")
        console.print()
        for membership in self.api.get_all(profile["memberships"]):
            team = self.api.get(membership["team"])
            print(f"- {membership['role']} in {team['name']}")

    def do_list(self, page=None):
        if page is None:
            print("Please choose a exercise list first.")
            print("Public exercises lists are:")
            show_pages(self.api)
            print(
                """\nUse 'genepy list <page>' to list exercise from a given page (by title)."""
            )
            return
        answers = self.api.answers(is_valid=True)
        succeeded_exercises = {answer["exercise"] for answer in answers}
        check = Text("✓", style="green")
        table = Table(title="Exercises")
        table.add_column("Done", justify="center")
        table.add_column("Title")
        for exercise in self.api.exercises(page=page):
            table.add_row(
                check if exercise["url"] in succeeded_exercises else "",
                exercise["title"],
            )
        Console().print(table)

    def do_get(self, name):
        name = " ".join(name)
        exercise = self._find_exercise(name)
        exercise_path = exercise["slug"] + ".py"
        with open(exercise_path, "w", encoding="UTF-8") as exercise_file:
            exercise_file.write("# " + exercise["title"] + "\n\n")
            exercise_file.write(indent(exercise["wording_en"], "# ", lambda l: True))
            exercise_file.write("\n\n")
            exercise_file.write(exercise["initial_solution"])
        print(
            f"Downloaded {exercise_path}, you can upload it back using:",
            f"    genepy check {exercise_path}",
            sep="\n\n",
        )

    def do_check(self, exercise_path):
        def dot():
            print(".", end="")
            sys.stdout.flush()

        source_code = exercise_path.read_text(encoding="UTF-8")
        title = source_code.splitlines()[0].lstrip("#").strip()
        exercise = self._find_exercise(title)
        endpoint = f"wss://genepy.org/ws/exercises/{exercise['id']}/"
        dot()
        ws = create_connection(endpoint)
        dot()
        ws.send(json.dumps({"type": "answer", "source_code": source_code}))
        while True:
            dot()
            result = json.loads(ws.recv())
            if result["is_corrected"]:
                print("\n", result["correction_message"])
                break
        ws.close()

    def _find_exercise(self, name):
        exercises = self.api.session.get("https://genepy.org/api/exercises/").json()
        for exercise in exercises["results"]:
            if name == exercise["title"]:
                full_exercise = self.api.session.get(exercise["url"]).json()
                full_exercise["id"] = full_exercise["url"].split("/")[-2]
                return full_exercise
        raise ValueError("Cannot find exercise " + name)


def show_pages(api):
    table = Table()
    table.add_column("title")
    table.add_column("description")
    for page in api.pages():
        if list(api.exercises(page=page["slug"], limit=1)):
            table.add_row(page["slug"], page["title"])
    Console().print(table)


def main():
    args = vars(parse_args())
    logging.basicConfig(level=args.pop("verbosity"))
    config = get_config()
    try:
        backend = config[config["backend"]["URL"]]
    except KeyError:
        backend = {}
    with GenepyAPI(
        config["backend"]["URL"],
        (backend.get("username"), backend.get("password")),
    ) as api:
        if args["func"] != CLI.do_login:
            api.ping_or_die()
        languages = [lang.strip(" ,") for lang in backend.get("languages", "").split()]
        cli = CLI(api, languages=languages)
        cli.dispatch(args)


if __name__ == "__main__":
    main()
