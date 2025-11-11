# remote/moudels/spammer/spammer.py
"""
Real sending spammer module (asyncio-based, simplified).
- Uses build_final_text() from your project (finaly_text).
- Uses client_manager.get_or_start_client(...) to obtain Pyrogram clients.
- Controls concurrency with Semaphore and per-account locks.
- Handles FloodWait, ChatWriteForbidden, Auth errors, timeouts and backoff.
- WARNING: This version sends real messages. Use only in your safe test group.
"""

import asyncio
import logging
import os
import random
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from pyrogram import errors

# ============================================================
# 📦 Import dependencies
# ============================================================
try:
    from ..text.finaly_text import build_final_text
except Exception:
    def build_final_text(*args, **kwargs):
        return f"[fallback demo message] {datetime.utcnow().isoformat()}"

try:
    from ..account import account_manager
except Exception:
    account_manager = None

try:
    from ..account.client import client_manager
except Exception:
    client_manager = None

# ============================================================
# 🧾 Logger setup
# ============================================================
class NanoFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        ns = int((record.created - int(record.created)) * 1_000_000_000)
        return f"{dt.strftime('%Y-%m-%d %H:%M:%S')}.{ns:09d}"

logger = logging.getLogger("remote.moudels.spammer_real")
logger.setLevel(logging.INFO)
os.makedirs("logs", exist_ok=True)
fh = logging.FileHandler("logs/spammer_real.log", encoding="utf-8")
fh.setFormatter(NanoFormatter("%(asctime)s - %(levelname)s - %(message)s"))
if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith("spammer_real.log") for h in logger.handlers):
    logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setFormatter(NanoFormatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(ch)

_spammer_runner_singleton: Optional["SpammerThreadingRunner"] = None

# ============================================================
# 🎯 Target Normalizer
# ============================================================
def _normalize_target_for_spam(raw: str):
    if raw is None:
        return None, None, None
    s = str(raw).strip()
    original_has_joinchat = "joinchat" in s.lower()
    s = re.sub(r"^(?:https?://)", "", s, flags=re.I)
    s = re.sub(r"^www\.", "", s, flags=re.I)
    if "/" in s:
        s = s.split("/")[-1]
    s = s.split("?")[0].strip().strip("<>\"'")
    if s.startswith("@"):
        s = s[1:].strip()
    if s.startswith("+"):
        return "invite", s.lstrip("+").strip(), False
    if s.lstrip("-").isdigit():
        try:
            return "chat_id", int(s), None
        except Exception:
            pass
    if re.match(r"^[A-Za-z0-9_\-]{8,}$", s):
        if len(s) >= 20:
            return "invite", s, original_has_joinchat
        return "username", s, None
    return "username", s, None

# ============================================================
# 👥 Account List Fetcher
# ============================================================
async def _get_accounts_from_manager(spam_config: Dict[str, Any]) -> List[str]:
    if account_manager is not None:
        try:
            accs = account_manager.accounts()
            if asyncio.iscoroutine(accs):
                accs = await accs
            return list(accs)
        except Exception:
            logger.exception("Failed to get accounts from account_manager; falling back to spam_config['accounts']")
    return list(spam_config.get("accounts", []))

# ============================================================
# 📤 Safe Real Send
# ============================================================
async def safe_send_real(acc_phone: str, spam_config: Dict[str, Any], text: str, remove_client_from_pool: Callable[[str], None]) -> bool:
    """Send real message using Pyrogram with retries and basic backoff."""
    await asyncio.sleep(random.uniform(0.3, 1.2))  # small random delay per account

    try:
        cli = await client_manager.get_or_start_client(acc_phone)
        if not cli:
            logger.warning(f"{acc_phone}: client unavailable from client_manager.")
            return False
    except Exception as e:
        logger.exception(f"{acc_phone}: error while get_or_start_client: {e}")
        try:
            remove_client_from_pool(acc_phone)
        except Exception:
            pass
        return False

    # per-account lock (prevent concurrent sends from same client)
    try:
        locks = getattr(client_manager, "client_locks", None)
    except Exception:
        locks = None
    if locks is None:
        if not hasattr(safe_send_real, "_local_locks"):
            safe_send_real._local_locks = {}
        locks = safe_send_real._local_locks

    if acc_phone not in locks:
        locks[acc_phone] = asyncio.Lock()

    async with locks[acc_phone]:
        try:
            if not getattr(cli, "is_connected", False):
                await cli.start()
                logger.info(f"{acc_phone}: reconnected client before send.")

            target = spam_config.get("spamTarget")
            if not target:
                logger.warning(f"{acc_phone}: no spamTarget specified.")
                return False

            max_attempts = int(spam_config.get("SEND_RETRY_ATTEMPTS", 3))
            attempt = 0
            backoff_initial = float(spam_config.get("SEND_BACKOFF_INITIAL", 1.0))

            while attempt < max_attempts:
                attempt += 1
                try:
                    await cli.send_message(target, text)
                    logger.info(f"{acc_phone}: ✅ Message sent (attempt {attempt}).")
                    return True

                except errors.FloodWait as fw:
                    wait_for = int(getattr(fw, "value", getattr(fw, "x", 5)))
                    logger.warning(f"{acc_phone}: FloodWait {wait_for}s (attempt {attempt}). Sleeping...")
                    await asyncio.sleep(wait_for + 0.5)

                except (errors.RPCError, asyncio.TimeoutError) as e:
                    delay = backoff_initial * (2 ** (attempt - 1)) + random.random()
                    delay = min(delay, 30.0)
                    logger.warning(f"{acc_phone}: transient error {type(e).__name__}: {e} — retrying in {delay:.1f}s.")
                    await asyncio.sleep(delay)

                except errors.AuthKeyUnregistered:
                    logger.error(f"{acc_phone}: AuthKeyUnregistered — removing from pool.")
                    remove_client_from_pool(acc_phone)
                    return False

                except errors.UserDeactivated:
                    logger.error(f"{acc_phone}: UserDeactivated — account disabled.")
                    remove_client_from_pool(acc_phone)
                    return False

                except errors.ChatWriteForbidden:
                    logger.warning(f"{acc_phone}: ChatWriteForbidden — cannot send to {target}.")
                    return False

                except Exception as e:
                    logger.exception(f"{acc_phone}: unexpected error in send (attempt {attempt}): {e}")
                    await asyncio.sleep(min(5 * attempt, 30))

            logger.error(f"{acc_phone}: ❌ all {max_attempts} attempts failed.")
            return False

        except Exception as e:
            logger.exception(f"{acc_phone}: fatal error in safe_send_real: {e}")
            remove_client_from_pool(acc_phone)
            return False

# ============================================================
# 🧠 Main Async Runner
# ============================================================
async def run_spammer(spam_config: Dict[str, Any], remove_client_from_pool: Callable[[str], None]):
    base_delay = float(spam_config.get("TimeSleep", 2.0))
    batch_size = max(1, int(spam_config.get("BATCH_SIZE", 2)))
    concurrency = max(1, int(spam_config.get("CONCURRENCY", 4)))
    total_ok = 0

    logger.info(f"Spammer (real) starting: delay={base_delay}s batch={batch_size} concurrency={concurrency}")
    sem = asyncio.Semaphore(concurrency)

    try:
        while spam_config.get("run", False):
            accounts = await _get_accounts_from_manager(spam_config)
            if not accounts:
                logger.warning("No accounts found; sleeping...")
                await asyncio.sleep(2.0)
                continue

            try:
                text = build_final_text(spam_config)
            except TypeError:
                text = build_final_text()
            except Exception as e:
                logger.warning(f"build_final_text failed: {e}")
                text = "[error building text]"

            if not text.strip():
                logger.warning("Empty text; skipping this round.")
                await asyncio.sleep(base_delay)
                continue

            for i in range(0, len(accounts), batch_size):
                if not spam_config.get("run", False):
                    break
                batch = accounts[i : i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} size={len(batch)}")

                async def _task_for(acc):
                    async with sem:
                        return await safe_send_real(acc, spam_config, text, remove_client_from_pool)

                results = await asyncio.gather(*[_task_for(acc) for acc in batch])
                succ = sum(1 for r in results if r)
                total_ok += succ
                logger.info(f"Batch done: success={succ}/{len(batch)} total_ok={total_ok}")
                await asyncio.sleep(base_delay)

    except asyncio.CancelledError:
        logger.info("run_spammer cancelled.")
        raise
    finally:
        logger.info(f"Spammer stopped. Total sent: {total_ok}")
        if client_manager:
            try:
                await client_manager.stop_all_clients()
            except Exception:
                pass

# ============================================================
# ⚙️ Wrapper Class
# ============================================================
class SpammerThreadingRunner:
    def __init__(self, spam_config: Dict[str, Any], remove_client_from_pool: Callable[[str], None]):
        self.spam_config = spam_config or {}
        self.remove_client_from_pool = remove_client_from_pool
        self._task = None
        self._loop = None

    def start(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            raise RuntimeError("Must be called from async context.")
        self._loop = loop
        self.spam_config["run"] = True
        self._task = loop.create_task(run_spammer(self.spam_config, self.remove_client_from_pool))
        logger.info("SpammerThreadingRunner started (async task created).")

    def stop(self):
        logger.info("Stop requested for SpammerThreadingRunner.")
        self.spam_config["run"] = False
        if self._task and not self._task.done():
            self._task.cancel()

# ============================================================
# 🧩 Singleton Helpers
# ============================================================
def start_spammer_thread(spam_config, remove_client_from_pool):
    global _spammer_runner_singleton
    if _spammer_runner_singleton and _spammer_runner_singleton._task and not _spammer_runner_singleton._task.done():
        logger.info("Spammer already running.")
        return _spammer_runner_singleton
    runner = SpammerThreadingRunner(spam_config, remove_client_from_pool)
    runner.start()
    _spammer_runner_singleton = runner
    return runner

def stop_spammer_thread():
    global _spammer_runner_singleton
    if _spammer_runner_singleton:
        _spammer_runner_singleton.stop()
        _spammer_runner_singleton = None
        logger.info("Spammer stopped (singleton cleared).")
    else:
        logger.info("No running spammer to stop.")
