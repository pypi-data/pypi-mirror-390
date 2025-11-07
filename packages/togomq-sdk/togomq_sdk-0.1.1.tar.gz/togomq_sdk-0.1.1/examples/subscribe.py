"""Example: Subscribing to messages from TogoMQ."""

import signal
from typing import Optional

from togomq import Client, Config, SubscribeOptions


def example_basic_subscribe() -> None:
    """Subscribe to messages from a specific topic."""
    print("\n=== Basic Subscription Example ===\n")

    # Create client
    config = Config(token="your-token-here")
    client = Client(config)

    try:
        # Subscribe to specific topic
        # Topic is required - use "*" to subscribe to all topics
        options = SubscribeOptions("orders")
        msg_gen, err_gen = client.sub(options)

        # Receive messages
        count = 0
        for msg in msg_gen:
            print(f"Received message from {msg.topic}: {msg.body.decode()}")
            print(f"Message UUID: {msg.uuid}")

            # Access variables
            if "priority" in msg.variables:
                print(f"Priority: {msg.variables['priority']}")

            count += 1
            if count >= 10:  # Limit for example
                break

    finally:
        client.close()


def example_subscribe_with_options() -> None:
    """Subscribe with batch size and rate limiting."""
    print("\n=== Advanced Subscription Example ===\n")

    config = Config(token="your-token-here", log_level="info")

    with Client(config) as client:
        # Subscribe with batch size and rate limiting
        # Default values: Batch = 0 (server default 1000), SpeedPerSec = 0 (unlimited)
        options = (
            SubscribeOptions("orders.*")  # Wildcard topic
            .with_batch(10)  # Receive up to 10 messages at once
            .with_speed_per_sec(100)  # Limit to 100 messages per second
        )

        msg_gen, err_gen = client.sub(options)

        # Process messages
        for msg in msg_gen:
            print(f"[{msg.topic}] UUID: {msg.uuid}, Body: {msg.body[:50]}")


def example_subscribe_all_topics() -> None:
    """Subscribe to all topics using wildcard."""
    print("\n=== Subscribe to All Topics Example ===\n")

    config = Config(token="your-token-here")

    with Client(config) as client:
        # Subscribe to all topics using "*" wildcard
        options = SubscribeOptions("*")  # "*" = all topics
        msg_gen, err_gen = client.sub(options)

        for msg in msg_gen:
            print(f"Received from [{msg.topic}]: {msg.body.decode()}")


def example_subscribe_with_pattern() -> None:
    """Subscribe using topic pattern wildcards."""
    print("\n=== Subscribe with Pattern Example ===\n")

    config = Config(token="your-token-here")

    with Client(config) as client:
        # Subscribe to all orders topics (orders.new, orders.updated, etc.)
        options = SubscribeOptions("orders.*")
        msg_gen, err_gen = client.sub(options)

        for msg in msg_gen:
            print(f"Order message from [{msg.topic}]: {msg.body}")

            # Process based on sub-topic
            if msg.topic.endswith(".new"):
                print("  -> Processing new order")
            elif msg.topic.endswith(".updated"):
                print("  -> Processing order update")


def example_graceful_shutdown() -> None:
    """Subscribe with graceful shutdown handling."""
    print("\n=== Graceful Shutdown Example ===\n")

    config = Config(token="your-token-here")
    client: Optional[Client] = None
    running = True

    def signal_handler(sig, frame):  # type: ignore
        """Handle shutdown signal."""
        nonlocal running
        print("\nShutting down gracefully...")
        running = False

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    try:
        client = Client(config)
        options = SubscribeOptions("events")
        msg_gen, err_gen = client.sub(options)

        print("Listening for messages (Press Ctrl+C to stop)...")

        for msg in msg_gen:
            if not running:
                break

            print(f"Received: {msg.uuid} from {msg.topic}")

    finally:
        if client:
            client.close()
        print("Shutdown complete")


def example_error_handling() -> None:
    """Demonstrate subscription error handling."""
    print("\n=== Subscription Error Handling Example ===\n")

    from togomq import ErrorCode, TogoMQError

    config = Config(token="your-token-here")

    try:
        with Client(config) as client:
            # Invalid topic (empty)
            options = SubscribeOptions("")
            msg_gen, err_gen = client.sub(options)

            for msg in msg_gen:
                print(f"Received: {msg}")

    except TogoMQError as e:
        if e.code == ErrorCode.VALIDATION:
            print(f"Validation error: {e}")
        elif e.code == ErrorCode.AUTH:
            print(f"Authentication error: {e}")
        elif e.code == ErrorCode.SUBSCRIBE:
            print(f"Subscription error: {e}")
        else:
            print(f"Error: {e}")


def example_processing_with_variables() -> None:
    """Process messages using their variables."""
    print("\n=== Processing with Variables Example ===\n")

    config = Config(token="your-token-here")

    with Client(config) as client:
        options = SubscribeOptions("orders")
        msg_gen, err_gen = client.sub(options)

        for msg in msg_gen:
            print(f"\nMessage UUID: {msg.uuid}")
            print(f"Topic: {msg.topic}")
            print(f"Body: {msg.body.decode()}")

            # Process based on variables
            if "priority" in msg.variables:
                priority = msg.variables["priority"]
                if priority == "high":
                    print("  -> HIGH PRIORITY: Processing immediately")
                else:
                    print(f"  -> Priority: {priority}")

            if "customer" in msg.variables:
                print(f"  -> Customer: {msg.variables['customer']}")


if __name__ == "__main__":
    print("TogoMQ Subscription Examples")
    print("=" * 50)

    # Note: Replace 'your-token-here' with actual token to run examples

    # Uncomment to run examples:
    # example_basic_subscribe()
    # example_subscribe_with_options()
    # example_subscribe_all_topics()
    # example_subscribe_with_pattern()
    # example_graceful_shutdown()
    # example_error_handling()
    # example_processing_with_variables()

    print("\nTo run examples, replace 'your-token-here' with your actual TogoMQ token")
