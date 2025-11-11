import os
import sqlite3
import threading
import time

from uyeia.exceptions import UYEIACacheError
from uyeia.type import Status


def delete_file_db(path):
    if os.path.exists(path):
        # Retry logic for Windows file locking issues
        max_attempts = 20
        for attempt in range(max_attempts):
            try:
                os.remove(path)
                break
            except (PermissionError, OSError):
                if attempt < max_attempts - 1:
                    time.sleep(0.2)  # Wait 100ms before retry
                    continue


class UyeiaCache:
    """
    A simple cache class that uses SQLite to store watcher statuses.
    This class provides methods to set, get, and clear cache entries.
    It is designed to be thread-safe and can be used across multiple threads.
    """

    def __init__(self, db_location: str):
        self.db_location = db_location
        self.__local = threading.local()
        self.__setup()

    def __connect(self):
        """Connect to the SQLite database, recreate if corrupted or missing."""
        # Use thread-local storage for connections
        if not hasattr(self.__local, "connection") or not isinstance(
            self.__local.connection, sqlite3.Connection
        ):
            # Enable WAL mode for better concurrent access on Windows
            connection = sqlite3.connect(self.db_location, timeout=30.0)
            if os.name == "nt":
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute("PRAGMA synchronous=NORMAL")
                connection.execute("PRAGMA cache_size=10000")
                connection.execute("PRAGMA temp_store=MEMORY")
            self.__local.connection = connection
        return self.__local.connection

    def __setup(self, recall: bool = False):
        """Initialise the cache database (tables)."""
        cursor = None
        connection = None
        try:
            connection = self.__connect()
            cursor = connection.cursor()
            # Create the cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    watcher TEXT NOT NULL,
                    status TEXT,
                    message TEXT,
                    solution TEXT,
                    escalation INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(watcher) ON CONFLICT REPLACE
                )
            """)

            # Create the vault table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vault (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(key) ON CONFLICT REPLACE
                )
            """)

            connection.commit()
        except sqlite3.DatabaseError:
            if cursor:
                cursor.close()
            if hasattr(self.__local, "connection") and self.__local.connection:
                self.__local.connection.close()
            if not recall:
                # Corrupted database → delete and rebuild
                if hasattr(self.__local, "connection"):
                    self.__local.connection = None
                delete_file_db(self.db_location)
                # Reconnect and retry once
                self.__setup(recall=True)
            else:
                raise UYEIACacheError("Corrupted database could not be recovered")

    def __query(self, query: str, params: tuple = ()):
        connection = self.__connect()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            command = query.strip().split()[0].upper()

            # If it's a SELECT or similar, fetch results
            if command in ("SELECT", "PRAGMA", "EXPLAIN", "WITH"):
                result = cursor.fetchall()
            else:
                connection.commit()
                # Return useful info for non-SELECTs
                result = {"rowcount": cursor.rowcount, "lastrowid": cursor.lastrowid}
            return result
        except sqlite3.Error as e:
            raise UYEIACacheError(f"Cache query failed: {e}")
        finally:
            cursor.close()

    def exists(self, field: str, value: str) -> bool:
        query = f"SELECT 1 FROM cache WHERE {field} = ? LIMIT 1"
        params = (value,)

        try:
            result = self.__query(query, params)
            return bool(result)
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to check existence in cache: {e}")

    def set(self, watcher: str, status: Status):
        """Set a value in the cache."""
        query = """
            INSERT INTO cache (watcher, status, message, solution, escalation)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            watcher,
            status["status"],
            status["message"],
            status["solution"],
            status["escalation"],
        )

        try:
            self.__query(query, params)
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to set cache: {e}")

    def get_all(self) -> dict[str, dict[str, Status]]:
        data = {}
        query = "SELECT watcher, status, message, solution, escalation FROM cache"
        try:
            result = self.__query(query)
            for row in result:
                data.setdefault(row[1], {}).setdefault(row[0], {}).update(
                    {
                        "watcher": row[0],
                        "status": row[1],
                        "message": row[2],
                        "solution": row[3],
                        "escalation": row[4],
                    }
                )
            return data
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to get all watchers from cache: {e}")

    def remove(self, watcher: str, status: Status):
        """Remove a watcher from the cache."""
        query = "DELETE FROM cache WHERE watcher = ? AND status = ?"
        params = (watcher, status["status"])

        try:
            self.__query(query, params)
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to remove watcher from cache: {e}")

    def get(self, field: str, value: str) -> Status | None:
        query = f"SELECT status, message, solution, escalation FROM cache WHERE {field} = ? LIMIT 1"
        params = (value,)

        try:
            result = self.__query(query, params)
            if result:
                status, message, solution, escalation = result[0]
                return {
                    "status": status,
                    "message": message,
                    "solution": solution,
                    "escalation": escalation,
                }
            return None
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to get watcher from cache: {e}")

    def escalate(self, status: list[str]):
        query = "UPDATE cache SET escalation = COALESCE(escalation, 0) + 1 WHERE status NOT IN (?)"
        params = (",".join(status),)
        try:
            self.__query(query, params)
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to escalate cache: {e}")

    def update_after_escalate(self, max_escalation: int, high_status: str):
        query = "UPDATE cache SET status = ? WHERE escalation >= ?"
        params = (high_status, max_escalation)
        try:
            self.__query(query, params)
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to update cache after escalate: {e}")

    def clear(self):
        """Clear the cache."""
        query = "DELETE FROM cache"
        try:
            self.__query(query)
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to clear cache: {e}")

    def close(self):
        """Close the database connection."""
        if hasattr(self.__local, "connection") and self.__local.connection:
            self.__local.connection.close()
            self.__local.connection = None

    def set_vault(self, key: str, value: str):
        query = "INSERT INTO vault (key, value) VALUES (?, ?)"
        params = (key, value)
        try:
            self.__query(query, params)
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to set vault: {e}")

    def remove_vault(self, key: str):
        query = "DELETE FROM vault WHERE key = ?"
        params = (key,)
        try:
            self.__query(query, params)
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to remove vault: {e}")

    def retrieve_vault(self, key: str) -> str | None:
        query = "SELECT value FROM vault WHERE key = ? LIMIT 1"
        params = (key,)
        try:
            result = self.__query(query, params)
            if result:
                return result[0][0]
            return None
        except UYEIACacheError as e:
            raise UYEIACacheError(f"Failed to retrieve vault: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.close()

    def __del__(self):
        """Close the database connection when the cache is deleted."""
        self.close()
