"""
Barge-in Feature Demonstration Script

This script demonstrates the barge-in functionality without requiring
a full NOVA setup. It shows how the interrupt mechanisms work.
"""

import queue
import threading
import time


class MockTTS:
    """Mock TTS class demonstrating interrupt functionality."""

    def __init__(self):
        self.tts_queue = queue.Queue()
        self.is_playing = False
        self.interrupt_flag = threading.Event()
        self.interrupt_callback = None

    def set_interrupt_callback(self, callback):
        """Set callback for interrupt events."""
        self.interrupt_callback = callback

    def interrupt(self):
        """Interrupt current playback."""
        print("🛑 [TTS] Interrupt triggered!")
        self.interrupt_flag.set()

        # Clear queues
        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
            except queue.Empty:
                break

    def reset_interrupt(self):
        """Reset interrupt flag."""
        self.interrupt_flag.clear()

    def speak(self, text):
        """Simulate speaking text."""
        self.tts_queue.put(text)
        if not self.is_playing:
            threading.Thread(target=self._playback_loop, daemon=True).start()

    def _playback_loop(self):
        """Simulate playback with interrupt checking."""
        self.is_playing = True
        try:
            while not self.tts_queue.empty():
                if self.interrupt_flag.is_set():
                    print("🔴 [TTS] Playback interrupted!")
                    if self.interrupt_callback:
                        self.interrupt_callback()
                    break

                try:
                    text = self.tts_queue.get(timeout=0.1)
                    print(f"🔊 [TTS] Speaking: {text}")

                    # Simulate speaking (check for interrupt every 0.5s)
                    words = text.split()
                    for i, word in enumerate(words):
                        if self.interrupt_flag.is_set():
                            print(f"🔴 [TTS] Interrupted mid-sentence! (after '{word}')")
                            break
                        print(f"     {word}", end=" ", flush=True)
                        time.sleep(0.5)
                    print()  # Newline
                except queue.Empty:
                    continue
        finally:
            self.is_playing = False
            print("✅ [TTS] Playback finished")


class MockVAD:
    """Mock Voice Activity Detection."""

    def __init__(self):
        self.monitoring = False
        self.callback = None
        self.stop_event = threading.Event()

    def start_monitoring(self, callback):
        """Start monitoring for speech."""
        self.callback = callback
        self.stop_event.clear()
        self.monitoring = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        print("👂 [VAD] Monitoring started")

    def stop_monitoring(self):
        """Stop monitoring."""
        if not self.monitoring:
            return
        self.stop_event.set()
        self.monitoring = False
        print("🔇 [VAD] Monitoring stopped")

    def _monitor_loop(self):
        """Simulate monitoring for speech."""
        frames_detected = 0
        threshold = 3  # Detect 3 "frames" of speech

        while not self.stop_event.is_set():
            time.sleep(0.3)  # Simulate frame processing

            # Simulate random speech detection (20% chance per frame)
            import random

            if random.random() < 0.2:
                frames_detected += 1
                print(f"   🎤 [VAD] Speech frame detected ({frames_detected}/{threshold})")

                if frames_detected >= threshold:
                    print("🗣️  [VAD] SPEECH DETECTED! Triggering interrupt...")
                    if self.callback:
                        self.callback()
                    break
            else:
                frames_detected = max(0, frames_detected - 1)


def demo_basic_interrupt():
    """Demonstrate basic interrupt functionality."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Interrupt")
    print("=" * 60)

    tts = MockTTS()

    # Simulate speaking multiple sentences
    tts.speak("This is the first sentence that NOVA is speaking.")
    tts.speak("This is the second sentence that will be interrupted.")
    tts.speak("This is the third sentence that won't be heard.")

    # Wait a bit, then interrupt
    time.sleep(3)
    print("\n👤 [USER] *starts speaking*")
    tts.interrupt()

    time.sleep(2)


def demo_barge_in_with_vad():
    """Demonstrate barge-in with voice activity detection."""
    print("\n" + "=" * 60)
    print("DEMO 2: Barge-in with Voice Activity Detection")
    print("=" * 60)

    tts = MockTTS()
    vad = MockVAD()

    # Set up interrupt handler
    def handle_interrupt():
        print("⚡ [HANDLER] Interrupt handler called")
        tts.interrupt()
        vad.stop_monitoring()

    tts.set_interrupt_callback(handle_interrupt)

    # Start speaking and monitoring simultaneously
    print("\n🤖 [NOVA] Starting to speak...")
    tts.speak("This is NOVA speaking a long sentence that demonstrates the barge-in feature.")
    tts.speak("If you start speaking, I will stop immediately and listen to you.")
    tts.speak("This makes our conversation much more natural and human-like.")

    # Start VAD monitoring
    vad.start_monitoring(handle_interrupt)

    # Wait for completion or interrupt
    time.sleep(10)

    # Clean up
    vad.stop_monitoring()
    tts.reset_interrupt()


def demo_workflow():
    """Demonstrate complete workflow with interrupt and recovery."""
    print("\n" + "=" * 60)
    print("DEMO 3: Complete Workflow with Recovery")
    print("=" * 60)

    tts = MockTTS()
    vad = MockVAD()

    def handle_interrupt():
        print("⚡ [HANDLER] User interrupted - stopping and cleaning up")
        tts.interrupt()
        vad.stop_monitoring()

    tts.set_interrupt_callback(handle_interrupt)

    # Round 1: Normal completion
    print("\n📍 Round 1: Normal completion (no interrupt)")
    tts.speak("Hello! I am NOVA, your AI assistant.")
    vad.start_monitoring(handle_interrupt)
    time.sleep(3)
    vad.stop_monitoring()
    tts.reset_interrupt()

    time.sleep(1)

    # Round 2: With interrupt
    print("\n📍 Round 2: With interrupt")
    tts.speak("Now I'm going to speak a longer sentence that will be interrupted by the user.")
    tts.speak("You won't hear this part because the interrupt will happen first.")
    vad.start_monitoring(handle_interrupt)
    time.sleep(2)  # Interrupt will likely happen during playback

    # Wait for interrupt
    time.sleep(3)

    # Round 3: Recovery after interrupt
    print("\n📍 Round 3: Recovery after interrupt")
    tts.reset_interrupt()
    tts.speak("Great! I've recovered from the interrupt and can speak again.")
    time.sleep(3)


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("BARGE-IN FUNCTIONALITY DEMONSTRATION")
    print("=" * 60)
    print("\nThis demo shows how barge-in works in NOVA:")
    print("- TTS playback can be interrupted")
    print("- Voice Activity Detection triggers interrupts")
    print("- System recovers and continues after interrupts")
    print("\n(Note: Speech detection is simulated randomly)")

    try:
        demo_basic_interrupt()
        demo_barge_in_with_vad()
        demo_workflow()

        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE ✅")
        print("=" * 60)
        print("\nKey takeaways:")
        print("- Barge-in allows natural conversation flow")
        print("- Interrupts are handled gracefully")
        print("- System recovers automatically after interrupts")
        print("- Works seamlessly with existing NOVA components")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")


if __name__ == "__main__":
    main()
