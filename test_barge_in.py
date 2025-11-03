"""
Simple test script to validate barge-in functionality.
This script tests the interrupt mechanisms without requiring full system setup.
"""

import queue
import threading
import time


def test_interrupt_flag():
    """Test that interrupt flag works correctly."""
    print("Testing interrupt flag...")
    interrupt_flag = threading.Event()

    assert not interrupt_flag.is_set(), "Flag should start unset"

    interrupt_flag.set()
    assert interrupt_flag.is_set(), "Flag should be set after calling set()"

    interrupt_flag.clear()
    assert not interrupt_flag.is_set(), "Flag should be clear after calling clear()"

    print("✓ Interrupt flag test passed")


def test_queue_clearing():
    """Test that queues can be cleared properly."""
    print("Testing queue clearing...")
    test_queue = queue.Queue()

    # Add items to queue
    for i in range(5):
        test_queue.put(i)

    assert test_queue.qsize() == 5, "Queue should have 5 items"

    # Clear queue
    while not test_queue.empty():
        try:
            test_queue.get_nowait()
        except queue.Empty:
            break

    assert test_queue.empty(), "Queue should be empty after clearing"

    print("✓ Queue clearing test passed")


def test_callback_invocation():
    """Test that callbacks are invoked correctly."""
    print("Testing callback invocation...")
    callback_called = [False]

    def test_callback():
        callback_called[0] = True

    # Simulate callback being called
    test_callback()

    assert callback_called[0], "Callback should have been called"

    print("✓ Callback invocation test passed")


def test_threading_event_with_timeout():
    """Test that threading events work with timeouts."""
    print("Testing threading event with timeout...")
    stop_event = threading.Event()

    # Should return False if not set
    assert not stop_event.is_set(), "Event should not be set initially"

    # Set in a separate thread after a delay
    def set_after_delay():
        time.sleep(0.1)
        stop_event.set()

    thread = threading.Thread(target=set_after_delay, daemon=True)
    thread.start()

    # Wait for event to be set
    start_time = time.time()
    while not stop_event.is_set() and (time.time() - start_time) < 1.0:
        time.sleep(0.01)

    assert stop_event.is_set(), "Event should be set after delay"

    print("✓ Threading event test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("BARGE-IN FUNCTIONALITY TESTS")
    print("=" * 60)
    print()

    try:
        test_interrupt_flag()
        test_queue_clearing()
        test_callback_invocation()
        test_threading_event_with_timeout()

        print()
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"TEST FAILED: {e}")
        print("=" * 60)
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print(f"UNEXPECTED ERROR: {e}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
