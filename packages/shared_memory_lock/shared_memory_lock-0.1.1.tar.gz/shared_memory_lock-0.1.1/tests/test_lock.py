"""Comprehensive tests for SharedMemoryLock."""

import asyncio
import multiprocessing as mp
import pickle
import time
from multiprocessing.context import BaseContext

import pytest

from shared_memory_lock import SharedMemoryLock


@pytest.fixture
def check():
    """pytest-check fixture for soft assertions."""
    import pytest_check
    return pytest_check


@pytest.fixture
def unique_run_id():
    """Generate a unique run_id for each test."""
    return f"test_{time.time()}_{id(object())}"


@pytest.fixture
def lock_name():
    """Standard lock name for tests."""
    return "test_lock"


class TestLockBasics:
    """Basic lock functionality tests."""

    def test_lock_creation(self, check, unique_run_id, lock_name):
        """Test that a lock can be created and cleaned up."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        check.is_not_none(lock)
        check.equal(lock.name, lock_name)
        check.equal(lock.run_id, unique_run_id)

        # Should be able to close without error
        lock.close()
        lock.unlink()

    def test_acquire_release_basic(self, check, unique_run_id, lock_name):
        """Test basic acquire and release operations."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Should be able to acquire
            result = lock.acquire()
            check.is_true(result, "First acquire should succeed")

            # Should be able to release
            lock.release()

            # Should be able to acquire again after release
            result = lock.acquire()
            check.is_true(result, "Second acquire should succeed after release")

            lock.release()
        finally:
            lock.unlink()

    def test_context_manager(self, check, unique_run_id, lock_name):
        """Test lock works correctly as context manager."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Use as context manager
            with lock:
                # Lock should be held here
                # Try non-blocking acquire from same lock instance (should fail)
                result = lock.acquire(blocking=False)
                check.is_false(result, "Should not be able to acquire already-held lock")

            # After context exit, lock should be released
            result = lock.acquire(blocking=False)
            check.is_true(result, "Should be able to acquire after context exit")
            lock.release()

        finally:
            lock.unlink()

    def test_non_blocking_acquire(self, check, unique_run_id, lock_name):
        """Test non-blocking acquire behavior."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Non-blocking acquire on free lock should succeed
            result = lock.acquire(blocking=False)
            check.is_true(result, "Non-blocking acquire on free lock should succeed")

            # Non-blocking acquire on held lock should fail immediately
            start_time = time.time()
            result2 = lock.acquire(blocking=False)
            elapsed = time.time() - start_time

            check.is_false(result2, "Non-blocking acquire on held lock should fail")
            check.less(elapsed, 0.1, "Non-blocking acquire should return quickly")

            # Release and try again
            lock.release()
            result3 = lock.acquire(blocking=False)
            check.is_true(result3, "Non-blocking acquire should succeed after release")

            lock.release()
        finally:
            lock.unlink()

    def test_blocking_acquire_timeout(self, check, unique_run_id, lock_name):
        """Test blocking acquire with timeout."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Acquire lock first
            lock.acquire()

            # Blocking acquire with timeout should fail after timeout
            timeout_duration = 0.2
            start_time = time.time()
            result = lock.acquire(blocking=True, timeout=timeout_duration)
            elapsed = time.time() - start_time

            check.is_false(result, "Timed acquire on held lock should fail")
            check.greater_equal(elapsed, timeout_duration * 0.9, "Should wait at least most of timeout")
            check.less(elapsed, timeout_duration * 2, "Should not wait much longer than timeout")

            lock.release()
        finally:
            lock.unlink()


class TestCrossProcessLocking:
    """Cross-process locking tests."""

    @staticmethod
    def _lock_holder_process(run_id: str, lock_name: str, hold_duration: float, ready_event=None):
        """Process that acquires lock and holds it for specified duration."""
        lock = SharedMemoryLock(name=lock_name, create=False, run_id=run_id)

        with lock:
            # Signal that we've acquired the lock
            if ready_event is not None:
                ready_event.set()
            time.sleep(hold_duration)

    @staticmethod
    def _lock_acquirer_process(run_id: str, lock_name: str, results_dict: dict, wait_event=None):
        """Process that tries to acquire lock and records timing."""
        lock = SharedMemoryLock(name=lock_name, create=False, run_id=run_id)

        # Wait for signal that holder has the lock before starting timing
        if wait_event is not None:
            wait_event.wait(timeout=2.0)

        start_time = time.time()
        success = lock.acquire(blocking=True, timeout=2.0)
        end_time = time.time()

        results_dict['success'] = success
        results_dict['elapsed'] = end_time - start_time

        if success:
            lock.release()

    @pytest.mark.repeat(10)
    def test_cross_process_mutual_exclusion(self, check, unique_run_id, lock_name):
        """Test that lock provides mutual exclusion across processes."""
        ctx = mp.get_context("spawn")

        # Create lock in main process
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            hold_duration = 0.5
            ready_event = ctx.Event()

            # Start process that holds lock
            holder = ctx.Process(
                target=self._lock_holder_process,
                args=(unique_run_id, lock_name, hold_duration, ready_event)
            )
            holder.start()

            # Wait for holder to actually acquire the lock before we try
            check.is_true(ready_event.wait(timeout=2.0), "Holder should acquire lock within timeout")

            # Try to acquire in main process
            start_time = time.time()
            result = lock.acquire(blocking=True, timeout=2.0)
            elapsed = time.time() - start_time

            check.is_true(result, "Should eventually acquire lock after holder releases")
            check.greater_equal(elapsed, hold_duration * 0.8, "Should wait for holder to release")
            check.less(elapsed, hold_duration * 1.5, "Should not wait too much longer")

            lock.release()

            # Clean up
            holder.join(timeout=2)
            check.is_false(holder.is_alive(), "Holder process should have finished")

        finally:
            lock.unlink()

    @pytest.mark.repeat(10)
    def test_multiple_processes_competing(self, check, unique_run_id, lock_name):
        """Test multiple processes competing for the same lock with proper mutual exclusion."""
        ctx = mp.get_context("spawn")
        manager = ctx.Manager()
        results = manager.dict()

        # Create lock in main process
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Test parameters
            hold_duration = 0.3
            ready_event = ctx.Event()

            holder = ctx.Process(
                target=self._lock_holder_process,
                args=(unique_run_id, lock_name, hold_duration, ready_event)
            )

            # Acquirer waits for ready_event before starting its timing
            acquirer = ctx.Process(
                target=self._lock_acquirer_process,
                args=(unique_run_id, lock_name, results, ready_event)
            )

            holder.start()
            acquirer.start()

            # Both should finish successfully
            holder.join(timeout=2)
            acquirer.join(timeout=2)

            check.is_false(holder.is_alive(), "Holder should finish")
            check.is_false(acquirer.is_alive(), "Acquirer should finish")
            check.is_true(results.get('success', False), "Acquirer should eventually get lock")

            # STRICT test: acquirer MUST wait for holder to release the lock
            # This verifies that mutual exclusion actually works
            elapsed = results.get('elapsed', 0)
            expected_minimum_wait = hold_duration * 0.75  # Account for timing variations
            check.greater_equal(elapsed, expected_minimum_wait,
                              f"Acquirer waited {elapsed:.3f}s but should wait at least {expected_minimum_wait:.3f}s - "
                              "this indicates broken mutual exclusion!")
            check.less(elapsed, hold_duration * 1.5, "Acquirer should not wait excessively long")

        finally:
            lock.unlink()


class TestSerialization:
    """Lock serialization and cross-process sharing tests."""

    def test_pickle_roundtrip(self, check, unique_run_id, lock_name):
        """Test that locks can be pickled and unpickled."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Pickle and unpickle
            pickled_data = pickle.dumps(lock)
            lock2 = pickle.loads(pickled_data)

            # Check that unpickled lock has correct attributes
            check.equal(lock2.name, lock_name)
            check.equal(lock2.run_id, unique_run_id)

            # Both should be able to work with same underlying lock
            lock.acquire()

            # Second instance should see lock as held
            result = lock2.acquire(blocking=False)
            check.is_false(result, "Unpickled lock should see lock as held")

            # Release via original
            lock.release()

            # Should be able to acquire via unpickled instance
            result = lock2.acquire(blocking=False)
            check.is_true(result, "Should acquire via unpickled lock after original releases")

            lock2.release()

        finally:
            lock.unlink()

    def test_getstate_setstate(self, check, unique_run_id, lock_name):
        """Test __getstate__ and __setstate__ methods directly."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Get state
            state = lock.__getstate__()

            check.is_instance(state, dict)
            check.equal(state['name'], lock_name)
            check.equal(state['run_id'], unique_run_id)

            # Create new lock and restore state
            lock2 = SharedMemoryLock.__new__(SharedMemoryLock)
            lock2.__setstate__(state)

            check.equal(lock2.name, lock_name)
            check.equal(lock2.run_id, unique_run_id)

            # Should be able to use restored lock
            result = lock2.acquire(blocking=False)
            check.is_true(result, "Restored lock should be functional")

            lock2.release()

        finally:
            lock.unlink()


class TestEdgeCases:
    """Edge cases and error conditions."""

    def test_connect_to_nonexistent_lock(self, check, unique_run_id):
        """Test connecting to non-existent lock raises appropriate error."""
        with check.raises(FileNotFoundError):
            SharedMemoryLock(name="nonexistent", create=False, run_id=unique_run_id)

    def test_empty_run_id(self, check, lock_name):
        """Test lock works with empty run_id."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id="")

        try:
            check.equal(lock.run_id, "")

            result = lock.acquire()
            check.is_true(result, "Lock with empty run_id should work")

            lock.release()
        finally:
            lock.unlink()

    def test_very_long_names(self, check, unique_run_id):
        """Test lock works with long names (within OS limits)."""
        long_name = "a" * 100  # Should be within most OS limits

        lock = SharedMemoryLock(name=long_name, create=True, run_id=unique_run_id)

        try:
            result = lock.acquire()
            check.is_true(result, "Lock with long name should work")
            lock.release()
        finally:
            lock.unlink()

    def test_close_and_unlink_safety(self, check, unique_run_id, lock_name):
        """Test that close() and unlink() can be called multiple times safely."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        # Should not raise errors
        lock.close()
        lock.close()  # Second close should be safe

        lock.unlink()
        lock.unlink()  # Second unlink should be safe

    def test_acquire_after_close(self, check, unique_run_id, lock_name):
        """Test behavior after closing lock."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)
        lock.close()

        # Behavior after close is undefined, but shouldn't crash
        # Most likely will raise an exception
        with check.raises(Exception):
            lock.acquire()

        # Clean up
        try:
            lock.unlink()
        except Exception:
            pass


class TestPerformance:
    """Basic performance characteristics."""

    def test_acquire_release_speed(self, check, unique_run_id, lock_name):
        """Test that acquire/release is reasonably fast."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Time many acquire/release cycles
            iterations = 1000
            start_time = time.time()

            for _ in range(iterations):
                lock.acquire()
                lock.release()

            elapsed = time.time() - start_time
            avg_per_cycle = elapsed / iterations

            # Should be quite fast (less than 1ms per cycle on modern hardware)
            check.less(avg_per_cycle, 0.001, f"Average cycle time {avg_per_cycle:.6f}s seems slow")

        finally:
            lock.unlink()

    def test_non_blocking_acquire_speed(self, check, unique_run_id, lock_name):
        """Test that non-blocking acquire on held lock is fast."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            lock.acquire()

            # Time many failed non-blocking acquires
            iterations = 1000
            start_time = time.time()

            for _ in range(iterations):
                result = lock.acquire(blocking=False)
                check.is_false(result)

            elapsed = time.time() - start_time
            avg_per_attempt = elapsed / iterations

            # Should be very fast since it doesn't wait
            check.less(avg_per_attempt, 0.0001, f"Average failed acquire time {avg_per_attempt:.6f}s seems slow")

            lock.release()
        finally:
            lock.unlink()


class TestAsyncLocking:
    """Async lock functionality tests."""

    @pytest.mark.asyncio
    async def test_async_acquire_release_basic(self, check, unique_run_id, lock_name):
        """Test basic async acquire and release operations."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Should be able to acquire
            result = await lock.acquire_async()
            check.is_true(result, "First async acquire should succeed")

            # Should be able to release
            lock.release()

            # Should be able to acquire again after release
            result = await lock.acquire_async()
            check.is_true(result, "Second async acquire should succeed after release")

            lock.release()
        finally:
            lock.unlink()

    @pytest.mark.asyncio
    async def test_async_context_manager(self, check, unique_run_id, lock_name):
        """Test async lock works correctly as async context manager."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Use as async context manager
            async with lock:
                # Lock should be held here
                # Try non-blocking acquire from same lock instance (should fail)
                result = lock.acquire(blocking=False)
                check.is_false(result, "Should not be able to acquire already-held lock")

            # After context exit, lock should be released
            result = lock.acquire(blocking=False)
            check.is_true(result, "Should be able to acquire after async context exit")
            lock.release()

        finally:
            lock.unlink()

    @pytest.mark.asyncio
    async def test_async_acquire_timeout(self, check, unique_run_id, lock_name):
        """Test async acquire with timeout."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Acquire lock first (synchronously)
            lock.acquire()

            # Async acquire with timeout should fail after timeout
            timeout_duration = 0.2
            start_time = time.time()
            result = await lock.acquire_async(timeout=timeout_duration)
            elapsed = time.time() - start_time

            check.is_false(result, "Timed async acquire on held lock should fail")
            check.greater_equal(elapsed, timeout_duration * 0.9, "Should wait at least most of timeout")
            check.less(elapsed, timeout_duration * 1.5, "Should not wait much longer than timeout")

            lock.release()
        finally:
            lock.unlink()

    @pytest.mark.asyncio
    async def test_async_concurrent_tasks(self, check, unique_run_id, lock_name):
        """Test multiple async tasks competing for the same lock."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            counter = {"value": 0}

            async def increment_with_lock(task_id: int, iterations: int):
                """Task that increments counter with lock protection."""
                for _ in range(iterations):
                    async with lock:
                        # Critical section - increment counter
                        old_value = counter["value"]
                        await asyncio.sleep(0.001)  # Simulate some work
                        counter["value"] = old_value + 1

            # Run multiple tasks concurrently
            num_tasks = 5
            iterations_per_task = 10
            tasks = [
                increment_with_lock(i, iterations_per_task)
                for i in range(num_tasks)
            ]

            await asyncio.gather(*tasks)

            # If lock works correctly, counter should be exactly num_tasks * iterations_per_task
            expected = num_tasks * iterations_per_task
            check.equal(counter["value"], expected,
                       f"Counter should be {expected} if lock provides mutual exclusion")

        finally:
            lock.unlink()

    @pytest.mark.asyncio
    async def test_async_acquire_no_timeout(self, check, unique_run_id, lock_name):
        """Test async acquire without timeout on free lock."""
        lock = SharedMemoryLock(name=lock_name, create=True, run_id=unique_run_id)

        try:
            # Acquire without timeout should succeed immediately on free lock
            start_time = time.time()
            result = await lock.acquire_async(timeout=None)
            elapsed = time.time() - start_time

            check.is_true(result, "Async acquire should succeed on free lock")
            check.less(elapsed, 0.1, "Should acquire very quickly")

            lock.release()
        finally:
            lock.unlink()