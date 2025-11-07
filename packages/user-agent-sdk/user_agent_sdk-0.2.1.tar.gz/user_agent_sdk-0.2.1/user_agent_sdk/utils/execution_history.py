import sqlite3
import threading
from typing import Optional, List, Tuple, Any


class ExecutionHistory:
    def __init__(self, db_path: str = "execution_history.db"):
        self.db_path = db_path
        self._lock = threading.RLock()  # re-entrant lock for nested calls
        self._conn: Optional[sqlite3.Connection] = None
        self._table_ensured = False

    def _create_connection(self) -> sqlite3.Connection:
        """Create a SQLite connection configured for multi-threading."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # allow use across threads
            timeout=10,  # wait up to 10s for database locks
            isolation_level=None  # autocommit mode (we’ll manage transactions)
        )
        conn.execute("PRAGMA journal_mode=WAL;")  # better concurrency
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _ensure_table(self):
        """Ensure the table exists. Only runs once per instance."""
        if not self._table_ensured:
            with self._lock:
                if not self._table_ensured:  # double-check locking
                    conn = self._get_connection()
                    conn.execute("""
                                CREATE TABLE IF NOT EXISTS execution_history (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    task_id TEXT,
                                    agent_id TEXT,
                                    user_agent_id TEXT,
                                    started_at TEXT,
                                    ended_at TEXT,
                                    status TEXT CHECK (
                                        status IN ('success', 'error')
                                    ),
                                    input_data TEXT,
                                    output_data TEXT,
                                    error_message TEXT
                                )
                                 """)
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON execution_history(agent_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_user_agent_id ON execution_history(user_agent_id)")
                    self._table_ensured = True

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create the database connection (lazy initialization)."""
        if self._conn is None:
            with self._lock:
                if self._conn is None:  # double-check locking
                    self._conn = self._create_connection()
        return self._conn

    def _execute(self, query: str, params: Tuple = ()):
        """Thread-safe execute with auto-reconnect and lazy initialization."""
        with self._lock:
            self._ensure_table()  # ensure table on first use
            try:
                cur = self._get_connection().execute(query, params)
                return cur
            except sqlite3.ProgrammingError:
                # connection closed or invalid — recreate
                self._conn = self._create_connection()
                self._table_ensured = False  # re-ensure table with new connection
                self._ensure_table()
                cur = self._conn.execute(query, params)
                return cur

    def record(
            self,
            task_id: str,
            agent_id: str,
            user_agent_id: str,
            started_at: str,
            ended_at: str,
            status: str,
            input_data: str,
            error_message: Optional[str] = None,
            output_data: Optional[str] = None,
    ):
        self._execute("""
                      INSERT INTO execution_history (
                          task_id,
                          agent_id,
                          user_agent_id,
                          started_at,
                          ended_at,
                          status,
                          input_data,
                          output_data,
                          error_message
                      )
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                      """,
                      (
                          task_id,
                          agent_id,
                          user_agent_id,
                          started_at,
                          ended_at,
                          status,
                          input_data,
                          output_data,
                          error_message
                      )
        )

    def get_history(
            self,
            agent_id: Optional[str] = None,
            user_agent_id: Optional[str] = None,
            limit: int = 50
    ) -> List[Tuple[Any, ...]]:
        query = "SELECT * FROM execution_history"
        conditions = []
        params: List[Any] = []

        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        if user_agent_id:
            conditions.append("user_agent_id = ?")
            params.append(user_agent_id)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        return list(self._execute(query, tuple(params)))

    def get_record_by_id(self, record_id: int) -> Optional[Tuple[Any, ...]]:
        """Get a single record by its ID."""
        query = "SELECT * FROM execution_history WHERE id = ?"
        result = list(self._execute(query, (record_id,)))
        return result[0] if result else None

    def close(self):
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None


execution_history = ExecutionHistory()

import atexit


def shutdown():
    execution_history.close()


atexit.register(shutdown)
