import atexit
import datetime
import hashlib
import inspect
import json
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import uuid
import fcntl
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Optional

# TODO: figure out an elegant way to handle stale runs where the results were generated with old code/config
# TODO: dump small manifest of experiment row into run folder. warn if mismatch with database on start.


class ExperimentStatus(IntEnum):
    INCOMPLETE = 0
    COMPLETE = 1
    STALE = 2


@dataclass(frozen=True, slots=True)
class Spool:
    id: int
    name: str
    timestamp: datetime.datetime
    end_timestamp: datetime.datetime | None
    run_config: dict
    folder: Path
    notes: str
    vc_hash: str | None = None
    status: ExperimentStatus = ExperimentStatus.INCOMPLETE

    def short_print(self):
        status_str = {
            0: "Incomplete",
            1: "Complete",
            2: "Stale",
        }.get(self.status, "Unknown")
        return f"{self.id} | {self.name} -> {self.folder} | {status_str}"

    def __str__(self):
        import pprint

        def format_ts(ts_value):
            if isinstance(ts_value, datetime.datetime):
                return ts_value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return "N/A"

        def format_pformatted_dict(data_dict, max_pformat_len=250, pformat_options=None):
            if pformat_options is None:
                # Controls internal indentation of pprint and line width
                pformat_options = {"indent": 2, "width": 70, "compact": True}

            if not data_dict:
                return " None"

            s = pprint.pformat(data_dict, **pformat_options)

            truncation_suffix = "... (truncated)"

            if len(s) > max_pformat_len:
                content_allowance = max_pformat_len - len(truncation_suffix)
                if content_allowance < 10:  # Not enough space for meaningful content + suffix
                    # Replace with a simple truncation marker if pformat output is too short to cut nicely
                    s = truncation_suffix
                else:
                    # Try to cut at a newline for prettier truncation
                    # We look for a newline within the allowed content space
                    cut_at = s.rfind("\n", 0, content_allowance)
                    if cut_at != -1:  # Sensible place to cut found
                        # Add the suffix on a new line, respecting existing indent logic
                        s = s[:cut_at] + "\n" + truncation_suffix
                    else:  # No newline in the allowed part, or very long first line
                        s = s[:content_allowance] + truncation_suffix

            # Add a leading newline (to separate from the label like "Run Config:")
            # and then indent all lines of the (potentially truncated) pformat string by two spaces.
            return "\n" + "\n".join(["  " + line for line in s.splitlines()])

        status_str = {
            0: "Incomplete",
            1: "Complete",
            2: "Stale",
        }.get(self.status, "Unknown")
        start_ts_str = format_ts(self.timestamp)
        end_ts_str = "N/A"

        if self.status == ExperimentStatus.COMPLETE:
            end_ts_str = format_ts(self.end_timestamp if self.end_timestamp else "N/A")

        notes_display = self.notes.strip() if self.notes else "N/A"
        if len(notes_display) > 80:
            notes_display = notes_display[:77] + "..."

        run_config_str = format_pformatted_dict(self.run_config, max_pformat_len=300)

        header = f"Experiment {self.name} (ID: {self.id})"
        # footer = "-" * len(header)

        return f"""{header}
  Status: {status_str}
  Folder: {self.folder}
  Started: {start_ts_str}
  Ended: {end_ts_str}
  Notes: {notes_display}
  Commit: {self.vc_hash if self.vc_hash else "N/A"}
  Config:{run_config_str}"""


SCHEMA_VERSION = 3


class Theseus:
    class LogLevel(IntEnum):
        NONE = 0
        INFO = 1
        DEBUG = 2

    def __init__(
        self,
        db_path: str | Path,
        exp_dir: str | Path = Path.cwd(),
        loglevel: LogLevel = LogLevel.INFO,
    ):
        self.db_path = Path(db_path).resolve()
        self.root = self.db_path.parent
        # exp_dir is relative to the db file
        self.exp_dir = Path(os.path.relpath(exp_dir, self.root))
        self.loglevel = loglevel

        self.__interrupted = False
        self._init_db(self.db_path)

        self._validate()

    def _setup(self, db_id: int, temp_run_folder: Path, run_folder: Path):
        def signal_handler(signum, frame):
            self.__interrupted = True
            sys.exit(1)

        def excepthook(exc_type, exc_value, exc_traceback):
            self.__interrupted = True
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = excepthook
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, signal_handler)
        atexit.register(self._cleanup, db_id, temp_run_folder, run_folder)

    def _setup_batch(
        self,
        db_id: int,
        temp_run_folder: Path,
        run_folder: Path,
        worker_id: int,
        batch_metadata_folder: Path,
    ):
        def signal_handler(signum, frame):
            self.__interrupted = True
            sys.exit(1)

        def excepthook(exc_type, exc_value, exc_traceback):
            self.__interrupted = True
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = excepthook
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, signal_handler)
        atexit.register(
            self._cleanup_batch,
            db_id,
            temp_run_folder,
            run_folder,
            worker_id,
            batch_metadata_folder,
        )

    def _cleanup(self, id: int, temp_run_folder: Path, run_folder: Path):
        atexit.unregister(self._cleanup)
        if self.__interrupted:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE experiments
                SET end_timestamp = ?, status = ?
                WHERE id = ? AND status = ?
                """,
                (
                    datetime.datetime.now().isoformat(),
                    int(ExperimentStatus.COMPLETE),
                    id,
                    int(ExperimentStatus.INCOMPLETE),
                ),
            )
        # rename temp folder to final folder
        if self.loglevel >= Theseus.LogLevel.INFO:
            print(
                f"INFO(Ariadne): Experiment ID {id} marked as completed in the database, moving temp folder to final location."
            )
        try:
            os.rename(temp_run_folder, run_folder)
        except OSError as e:
            if self.loglevel >= Theseus.LogLevel.DEBUG:
                print(f"DEBUG(Ariadne): Failed to rename run folder: {e}")
            shutil.rmtree(run_folder)
            os.rename(temp_run_folder, run_folder)
            if self.loglevel >= Theseus.LogLevel.DEBUG:
                print(
                    "DEBUG(Ariadne): Successfully moved temp folder to final location after cleanup."
                )

    def _cleanup_batch(
        self,
        id: int,
        temp_run_folder: Path,
        run_folder: Path,
        worker_id: int,
        batch_metadata_folder: Path,
    ):
        atexit.unregister(self._cleanup_batch)
        lockfile = str(batch_metadata_folder.resolve()) + ".lock"
        with open(lockfile, "r") as _f:
            fcntl.flock(_f, fcntl.LOCK_EX)
            try:
                with open(batch_metadata_folder / "metadata.json", "r") as f:
                    metadata = json.load(f)

                    if self.__interrupted:
                        metadata["failed_workers"].append(worker_id)
                    else:
                        metadata["completed_workers"].append(worker_id)

                with open(batch_metadata_folder / "metadata.json", "w") as f:
                    json.dump(metadata, f, indent=2)
            except Exception as e:
                raise e
            finally:
                fcntl.flock(_f, fcntl.LOCK_UN)

        if (
            len(metadata["failed_workers"]) + len(metadata["completed_workers"])
            == metadata["expected_total_workers"]
        ):
            # last worker
            os.remove(lockfile)
            os.rename(
                batch_metadata_folder / "metadata.json", temp_run_folder / "batch_metadata.json"
            )
            shutil.rmtree(batch_metadata_folder)

            if len(metadata["failed_workers"]) > 0:
                if self.loglevel >= Theseus.LogLevel.INFO:
                    print(
                        f"INFO(Ariadne): Experiment ID {id} marked as INCOMPLETE in the database due to {len(metadata['failed_workers'])} failed workers."
                    )
            else:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        UPDATE experiments
                        SET end_timestamp = ?, status = ?
                        WHERE id = ? AND status = ?
                        """,
                        (
                            datetime.datetime.now().isoformat(),
                            int(ExperimentStatus.COMPLETE),
                            id,
                            int(ExperimentStatus.INCOMPLETE),
                        ),
                    )
                if self.loglevel >= Theseus.LogLevel.INFO:
                    print(
                        f"INFO(Ariadne): Experiment ID {id} marked as completed in the database, moving temp folder to final location."
                    )
                try:
                    os.rename(temp_run_folder, run_folder)
                except OSError as e:
                    if self.loglevel >= Theseus.LogLevel.DEBUG:
                        print(f"DEBUG(Ariadne): Failed to rename run folder: {e}")
                    shutil.rmtree(run_folder)
                    os.rename(temp_run_folder, run_folder)
                    if self.loglevel >= Theseus.LogLevel.DEBUG:
                        print(
                            "DEBUG(Ariadne): Successfully moved temp folder to final location after cleanup."
                        )

    def _init_db(self, db_path: str | Path):
        if self.loglevel >= Theseus.LogLevel.DEBUG:
            print(f"DEBUG(Ariadne): Initializing database at {db_path}")

        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_timestamp DATETIME,
                    run_config TEXT,
                    path_to_folder TEXT NOT NULL,
                    folder TEXT NOT NULL,
                    notes TEXT,
                    vc_hash TEXT,
                    status INTEGER DEFAULT 0
                )
            """)

        with sqlite3.connect(db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                id INTEGER PRIMARY KEY check (id = 1),
                os TEXT,
                host TEXT,
                user TEXT,
                python_version TEXT,
                env_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                schema_version INTEGER DEFAULT 1
            )
            """)
            conn.execute(
                """
            INSERT OR IGNORE INTO meta (id, os, host, user, python_version, env_hash, created_at, schema_version)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    os.uname().sysname + " " + os.uname().release,
                    os.uname().nodename,
                    os.getenv("USER") or os.getenv("USERNAME") or "unknown",
                    sys.version.split(" ")[0],
                    "N/A",  # TODO: compute env hash
                    datetime.datetime.now().isoformat(),
                    SCHEMA_VERSION,
                ),
            )

    def _validate(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT host, user, python_version, schema_version FROM meta WHERE id = 1"
            )
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("Database metadata is missing.")
            db_host, db_user, db_python_version, db_schema_version = row

            if db_schema_version != SCHEMA_VERSION:
                # print(
                #     f"WARNING(Ariadne): Database schema version {db_schema_version} does not match expected version {SCHEMA_VERSION}. "
                #     "Please migrate the database or create a new one."
                # )
                raise RuntimeError(
                    f"Database schema version {db_schema_version} does not match expected version {SCHEMA_VERSION}. "
                    "Please migrate the database or create a new one."
                )

            if db_host != os.uname().nodename and self.loglevel >= Theseus.LogLevel.DEBUG:
                print(
                    f"""WARNING(Ariadne): Database was created on host '{db_host}' by user '{db_user}',
                        but is being accessed on host '{os.uname().nodename}' by user '{os.getenv("USER") or os.getenv("USERNAME") or "unknown"}'.
                      """
                )

            if (
                db_python_version != sys.version.split(" ")[0]
                and self.loglevel >= Theseus.LogLevel.DEBUG
            ):
                print(
                    f"""WARNING(Ariadne): Database was created with Python version '{db_python_version}',
                        but is being accessed with Python version '{sys.version}'.
                      """
                )

    def start(
        self,
        run_config: dict,
        name: Optional[str] = None,
        notes: str = "",
        name_keys: Optional[list[str]] = None,
        max_folder_length=120,
    ) -> tuple[int, Path]:
        """
        Starts a new experiment with the given notes and run configuration.
        Creates a new run folder with a timestamp and unique identifier, initializes the database entry,
        and registers a cleanup function to mark the experiment as completed when the program exits.
        Automatically dumps the run configuration to a JSON file in the run folder.

        Raises:
            FileExistsError: If a run folder with the same name already exists.
        """

        id, tmp_folder, folder = self._start(
            run_config,
            name=name,
            notes=notes,
            name_keys=name_keys,
            max_folder_length=max_folder_length,
        )
        self._setup(id, tmp_folder, folder)
        return id, tmp_folder.resolve()

    def _start(
        self,
        run_config: dict,
        name: Optional[str] = None,
        notes: str = "",
        name_keys: Optional[list[str]] = None,
        max_folder_length=120,
    ) -> tuple[int, Path, Path]:
        if name_keys:
            for k in name_keys:
                if k not in run_config:
                    raise ValueError(f"Key '{k}' not found in run_config.")
            filtered_config = {k: run_config[k] for k in name_keys}
        else:
            filtered_config = run_config

        if not name:
            folder_name = config_to_name(filtered_config, max_length=max_folder_length)
            name = inspect.stack()[2].filename.split("/")[-1].split(".")[0]
        else:
            folder_name = f"{name}_{config_to_name(filtered_config, max_length=max_folder_length - len(name))}"

        run_folder = self.exp_dir / folder_name
        if run_folder.exists():
            if self.loglevel >= Theseus.LogLevel.INFO:
                print(
                    f"INFO(Ariadne): Run folder {run_folder} already exists. Beware of overwriting data!"
                )

        db_id = None
        # for atomicity, first create a temp directory and move it to the final location later
        temp_run_folder = self.exp_dir / "staging" / f"{folder_name}"
        if self.loglevel >= Theseus.LogLevel.DEBUG:
            print(
                f"DEBUG(Ariadne): Creating temporary run folder for experiment '{name}' at {temp_run_folder}"
            )
        try:
            os.makedirs(temp_run_folder, exist_ok=True)

            with open(temp_run_folder / "config.json", "w") as f:
                json.dump(run_config, f, indent=2)

            changeset = get_jj_changeset()
            if not changeset:
                if self.loglevel >= Theseus.LogLevel.DEBUG:
                    print("DEBUG(Ariadne): 'jj' not found or not a jj repo, trying git...")
                changeset = get_git_hash()

            if not changeset and self.loglevel >= Theseus.LogLevel.DEBUG:
                print("DEBUG(Ariadne): No version control changeset found.")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                res = cursor.execute(
                    """
                    INSERT INTO experiments (name, timestamp, run_config, path_to_folder, folder, notes, vc_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id
                """,
                    (
                        name,
                        datetime.datetime.now().isoformat(),
                        json.dumps(run_config),
                        str(self.exp_dir),
                        str(folder_name),
                        notes,
                        changeset,
                    ),
                )
                db_id = res.fetchone()[0]

            if self.loglevel >= Theseus.LogLevel.INFO:
                print(
                    f"INFO(Ariadne): Started experiment '{name}' (ID: {db_id}) in folder: {run_folder}"
                )
            return db_id, temp_run_folder, run_folder

        except Exception as e:
            if db_id is not None and run_folder.exists():
                # DB entry was created, but run folder creation failed
                if self.loglevel >= Theseus.LogLevel.INFO:
                    print(
                        f"INFO(Ariadne): Error starting experiment '{name}': {e}. Cleaning up DB entry."
                    )
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("DELETE FROM experiments WHERE id = ?", (db_id,))
                except sqlite3.Error as cleanup_err:
                    print(
                        f"ERROR(Ariadne): Failed to create run folder AND subsequently failed to clean up "
                        f"orphaned database record (ID: {db_id}). Manual intervention may be needed. "
                        f"Cleanup Error: {cleanup_err}. Original Error: {e}"
                    )

            if temp_run_folder.exists():
                shutil.rmtree(temp_run_folder)

            raise e

    def start_test(self, *a, noop=False, **kw) -> tuple[int, Path]:
        """
        Starts a temporary experiment.
        If noop is True, this function is a no-op and returns (-1, Path("/dev/null")).
        Otherwise, creates a new run folder in the users /tmp directory. This run does not update the database entry.

        Raises:
            FileExistsError: If a run folder with the same name already exists.
        """
        if noop:
            if self.loglevel >= Theseus.LogLevel.INFO:
                print("INFO(Ariadne): Starting a no-op test experiment. Returning dummy path.")
            return -1, DummyPath("./")

        now = datetime.datetime.now()
        run_folder = (
            Path(tempfile.gettempdir())
            / f"ariadne_test_{now.strftime('%Y-%m-%d-%H-%M-%S')}_{uuid.uuid4().hex[:4]}"
        ).resolve()

        if self.loglevel >= Theseus.LogLevel.INFO:
            print(f"INFO(Ariadne): Starting temporary experiment in {run_folder}")

        if run_folder.exists():
            raise FileExistsError(f"Run folder {run_folder} already exists.")

        try:
            db_id = -1
            os.makedirs(run_folder)

            self._setup(db_id, run_folder, run_folder)
            return db_id, run_folder.resolve()

        except Exception as e:
            if run_folder.exists():
                # DB entry was created, but run folder creation failed
                shutil.rmtree(run_folder)
            if self.loglevel >= Theseus.LogLevel.INFO:
                print(f"INFO(Ariadne): Error starting temporary experiment: {e}")
            raise e

    def start_batch(
        self,
        run_config: dict,
        total_workers: int,
        name: Optional[str] = None,
        notes="",
        name_keys: Optional[list[str]] = None,
        max_folder_length=120,
    ) -> tuple[int, int, Path]:
        """
        Attaches a worker to a batch experiment.
        The experiment will only be marked as complete when all workers have finished,
        and will be marked as failed if any worker is interrupted.

        returns:
            tuple[int, int, Path]: The experiment ID, worker ID, and run folder path.
        """
        # first worker:
        # sets up the staging batch directory and actually starts the experiment
        # last worker:
        # moves the staging directory to the final location and marks the experiment as complete / failed

        config_hash = hashlib.md5(json.dumps(run_config, sort_keys=True).encode()).hexdigest()

        lock_file_path = self.exp_dir / "staging" / f"batch_{config_hash}.lock"
        with open(lock_file_path, "w") as lock_file:
            if self.loglevel >= Theseus.LogLevel.DEBUG:
                print(
                    f"DEBUG(Ariadne): Acquiring lock for batch experiment with config hash {config_hash}"
                )
            fcntl.flock(lock_file, fcntl.LOCK_EX)

            try:
                batch_metadata_folder = self.exp_dir / "staging" / f"batch_{config_hash}"
                worker_id = uuid.uuid4().int % (10**8)  # type: ignore
                if not batch_metadata_folder.exists():
                    # first worker
                    os.makedirs(batch_metadata_folder, exist_ok=True)

                    exp_id, tmp_folder, run_folder = self._start(
                        run_config,
                        name=name,
                        notes=notes,
                        name_keys=name_keys,
                        max_folder_length=max_folder_length,
                    )
                    with open(batch_metadata_folder / "metadata.json", "w") as f:
                        json.dump(
                            {
                                "expected_total_workers": total_workers,
                                "completed_workers": [],
                                "failed_workers": [],
                                "exp_id": exp_id,
                                "run_folder": str(run_folder),
                                "staging_folder": str(tmp_folder),
                            },
                            f,
                            indent=2,
                        )

                    if self.loglevel >= Theseus.LogLevel.DEBUG:
                        print(
                            f"DEBUG(Ariadne): Batch metadata initialized at {batch_metadata_folder / 'metadata.json'}"
                        )

                else:
                    with open(batch_metadata_folder / "metadata.json", "r") as f:
                        metadata = json.load(f)

                    if self.loglevel >= Theseus.LogLevel.DEBUG:
                        print(
                            f"DEBUG(Ariadne): Joining existing batch experiment with ID {metadata['exp_id']}"
                        )

                    exp_id = metadata["exp_id"]
                    tmp_folder = Path(metadata["staging_folder"])
                    run_folder = Path(metadata["run_folder"])
            except Exception as e:
                raise e
            finally:
                if self.loglevel >= Theseus.LogLevel.DEBUG:
                    print(
                        f"DEBUG(Ariadne): Releasing lock for batch experiment with config hash {config_hash}"
                    )
                fcntl.flock(lock_file, fcntl.LOCK_UN)

        self._setup_batch(exp_id, tmp_folder, run_folder, worker_id, batch_metadata_folder)
        return exp_id, worker_id, tmp_folder.resolve()

    def get(self, name: str) -> list[Spool]:
        """
        Retrieves all experiments with names that partially match the given name.
        """
        out = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            for row in conn.execute(
                """
                SELECT * FROM experiments WHERE name LIKE ?
            """,
                (f"%{name}%",),
            ):
                out.append(self.convert_row(row))
        return out

    def get_by_id(self, id: int) -> Spool:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM experiments WHERE id = ?
            """,
                (id,),
            )
            row = cursor.fetchone()
        cursor.close()

        if row:
            return self.convert_row(row)
        raise ValueError(f"No experiment found with ID {id}.")

    def get_all(self) -> list[Spool]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            out = []
            for row in conn.execute("""
                SELECT * FROM experiments ORDER BY timestamp ASC
            """):
                out.append(self.convert_row(row))

        return out

    def has(self, must_match: dict) -> list[Spool]:
        """
        Returns all experiments whose config matches the given key-value pairs.
        """
        query = f"""
            SELECT * FROM experiments
            WHERE {" AND ".join([f"json_extract(run_config, '$.{k}') = ?" for k in must_match.keys()])}
            ORDER BY timestamp ASC
        """
        # print(query)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()
            cursor.execute(
                query,
                tuple(must_match.values())
            )

            rows = cursor.fetchall()

        out = []
        for row in rows:
            config = json.loads(row["run_config"])
            for field, value in must_match.items():
                if field in config and config[field] == value:
                    out.append(self.convert_row(row))
                    break

        return out

    def peek(self) -> Spool | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM experiments ORDER BY timestamp DESC LIMIT 1
            """)
            row = cursor.fetchone()
        cursor.close()

        if row:
            return self.convert_row(row)
        return None

    def note(self, id: int, text: str, append=True):
        """
        Adds or appends a note to an experiment by its ID.
        Raises:
            ValueError: If no experiment with the given ID is found.
        """
        if append:
            current = self.get_by_id(id)
            if current and current.notes:
                text = current.notes + "\n" + text

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE experiments
                SET notes = ?
                WHERE id = ?
                """,
                (text, id),
            )

    def delete(self, id: int):
        """
        Deletes an experiment by its ID. This will remove the entry from the database and delete the associated run folder.

        Raises:
            ValueError: If no experiment with the given ID is found.
        """
        spool = self.get_by_id(id)
        if not spool:
            raise ValueError(f"No experiment found with ID {id}.")

        # Remove the database entry
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM experiments WHERE id = ?", (id,))

        # Remove the run folder
        if spool.folder.exists():
            shutil.rmtree(spool.folder)

        print(f"Experiment {id} '{spool.name}' deleted successfully.")

    # ------------- Pretty printing -------------------
    def show(self, exps: list[Spool], long=False):
        for spool in exps:
            if long:
                print(str(spool))
            else:
                print(spool.short_print())
            print()

    def convert_row(self, row: sqlite3.Row):
        path_to_folder = Path(row["path_to_folder"])
        # resolve wrt caller directory
        path_to_folder = self.root / path_to_folder
        cwd = Path.cwd().resolve()
        path_to_folder = Path(os.path.relpath(path_to_folder, cwd))

        if row["status"] == ExperimentStatus.INCOMPLETE:
            folder = path_to_folder / "staging" / row["folder"]
        else:
            folder = path_to_folder / row["folder"]
        return Spool(
            id=row["id"],
            name=row["name"],
            timestamp=datetime.datetime.fromisoformat(row["timestamp"]),
            end_timestamp=None
            if row["end_timestamp"] is None
            else datetime.datetime.fromisoformat(row["end_timestamp"]),
            run_config=json.loads(row["run_config"]),
            folder=folder,
            notes=row["notes"],
            vc_hash=row["vc_hash"],
            status=row["status"],
        )


def get_jj_changeset():
    try:
        res = subprocess.run(
            ["jj", "log", "-r", "@", "-T", "'||'++commit_id++'||'"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip().split("||")[1]
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def get_git_hash():
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--pretty=%H"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def config_to_name(config: dict, max_length: int = 120) -> str:
    """
    Convert config into a safe, readable filename string.

    Returns:
        str: Sanitized, human-readable filename.
    """

    def sanitize(s):
        s = str(s)
        s = s.strip().lower()
        # Replace special chars with underscores
        s = re.sub(r"[^\w\-.]+", "_", s)
        # Strip leading/trailing underscores
        return s.strip("_")

    parts = []
    for k, v in config.items():
        key_s = sanitize(k)
        if isinstance(v, bool):
            parts.append(f"{key_s}" if v else f"no-{key_s}")
        else:
            val_s = sanitize(v)
            parts.append(f"{key_s}={val_s}")

    body = "__".join(parts)
    date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    body = f"{date_prefix}__{body}"

    # Truncate if too long (keep a hash to preserve uniqueness)
    if len(body) > max_length:
        body = body[: max_length - 8]  # Leave space for _hash
    digest = hashlib.md5(body.encode()).hexdigest()[:8]
    body = body + f"__{digest}"

    return body


class DummyPath(Path):
    def __new__(cls, *args, **kwargs):
        return Path.__new__(cls, *args, **kwargs)

    def __truediv__(self, key):
        return DummyPath(super().__truediv__(key))

    def exists(self):
        return True

    def mkdir(self, *args, **kwargs):
        pass

    def resolve(self, *args, **kwargs):
        return self

    def is_dir(self):
        return True

    def is_file(self):
        return False

    def open(self, *args, **kwargs):
        return DummyFile()


class DummyFile:
    def write(self, *args, **kwargs):
        pass

    def read(self, *args, **kwargs):
        return ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def cli():
    import argparse

    parser = argparse.ArgumentParser(description="Ariadne CLI")
    parser.add_argument("db", type=str, help="Path to the SQLite database file")

    subparser = parser.add_subparsers(dest="command")

    peek_parser = subparser.add_parser("peek", help="Show the most recent experiment")
    peek_parser.add_argument(
        "--long",
        action="store_true",
        help="Show detailed information for the most recent experiment",
    )

    query_parser = subparser.add_parser(
        "query", help="Get folder of an experiment by id, name, or config"
    )
    query_parser.add_argument("--id", type=int, help="ID to match on")
    query_parser.add_argument("--name", type=str, help="Name of the experiment")
    query_parser.add_argument("--config", type=str, nargs="?", help="Config to match")
    query_parser.add_argument(
        "--long",
        action="store_true",
        help="Show detailed information for each experiment",
    )
    query_parser.add_argument(
        "--include-incomplete",
        action="store_true",
        help="Include incomplete experiments in the listing",
    )

    show_parser = subparser.add_parser("show", help="Show all experiments")
    show_parser.add_argument(
        "--long",
        action="store_true",
        help="Show detailed information for each experiment",
    )
    show_parser.add_argument(
        "--include-incomplete",
        action="store_true",
        help="Include incomplete experiments in the listing",
    )

    note_parser = subparser.add_parser("note", help="Annotate an experiment by ID")
    note_parser.add_argument("id", type=int, help="ID of the experiment")
    note_parser.add_argument("note", type=str, help="Note to add")
    note_parser.add_argument(
        "--append",
        action="store_true",
        help="Append the note instead of replacing existing notes",
    )

    args = parser.parse_args()

    path = Path(args.db)
    if not path.exists():
        print(f"Database file '{path}' does not exist.")
        exit(1)

    theseus = Theseus(db_path=path)
    match args.command:
        case "query":
            # id > name > config
            if args.id is not None:
                exp = theseus.get_by_id(args.id)
                print(exp.short_print())
                exit(0)

            matches = theseus.get_all()
            if args.name is not None:
                matches = theseus.get(args.name)

            if args.config is not None:
                other_matches = theseus.has(json.loads(args.config))
                # merge matches
                matches_ids = set(exp.id for exp in other_matches)
                matches = [m for m in matches if m.id in matches_ids]

            if not args.include_incomplete:
                matches = [m for m in matches if m.status == ExperimentStatus.COMPLETE]

            if len(matches) == 0:
                print("No matching experiments found.")
                exit(1)

            theseus.show(exps=matches, long=args.long)

        case "show":
            exps = theseus.get_all()
            if not args.include_incomplete:
                exps = [m for m in exps if m.status == ExperimentStatus.COMPLETE]
            theseus.show(exps=exps, long=args.long)
        case "peek":
            exp = theseus.peek()
            if exp is None:
                print("No experiments found.")
                exit(1)
            theseus.show(exps=[exp], long=args.long)
        case "note":
            theseus.note(args.id, args.note, append=args.append)
        case _:
            parser.print_help()
            exit(1)


if __name__ == "__main__":
    cli()
