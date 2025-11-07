"""Example: Publishing messages to TogoMQ."""

import time
from collections.abc import Generator

from togomq import Client, Config, Message


def example_batch_publish() -> None:
    """Publish a batch of messages."""
    print("\n=== Batch Publishing Example ===\n")

    # Create client
    config = Config(token="your-token-here")
    client = Client(config)

    try:
        # Create messages - topic is required for each message
        messages = [
            Message("orders", b"order-1"),
            Message("orders", b"order-2").with_variables({"priority": "high", "customer": "12345"}),
            Message("orders", b"order-3")
            .with_postpone(60)  # Delay 60 seconds
            .with_retention(3600),  # Keep for 1 hour
        ]

        # Publish
        response = client.pub_batch(messages)
        print(f"Published {response.messages_received} messages")

    finally:
        client.close()


def example_streaming_publish() -> None:
    """Publish messages via streaming."""
    print("\n=== Streaming Publishing Example ===\n")

    # Create client
    config = Config(token="your-token-here", log_level="debug")

    with Client(config) as client:
        # Create a generator for messages
        def message_generator() -> Generator[Message, None, None]:
            for i in range(100):
                msg = Message("events", f"event-{i}".encode())
                yield msg
                time.sleep(0.01)  # Simulate some work

        # Publish
        response = client.pub(message_generator())
        print(f"Published {response.messages_received} messages")


def example_custom_config() -> None:
    """Publish with custom configuration."""
    print("\n=== Custom Configuration Example ===\n")

    # Create client with custom config
    config = Config(
        token="your-token-here",
        host="custom.togomq.io",
        port=9000,
        log_level="info",
    )

    with Client(config) as client:
        messages = [
            Message("notifications", b"notification-1"),
            Message("notifications", b"notification-2"),
        ]

        response = client.pub_batch(messages)
        print(f"Published {response.messages_received} messages")


def example_error_handling() -> None:
    """Demonstrate error handling."""
    print("\n=== Error Handling Example ===\n")

    from togomq import ErrorCode, TogoMQError

    try:
        # Invalid config (empty token)
        config = Config(token="")
    except TogoMQError as e:
        print(f"Configuration error: {e}")
        print(f"Error code: {e.code}")

    try:
        config = Config(token="your-token-here")
        client = Client(config)

        # Invalid message (no topic)
        messages = [Message("", b"invalid")]
        client.pub_batch(messages)

    except TogoMQError as e:
        if e.code == ErrorCode.VALIDATION:
            print(f"Validation error: {e}")
        elif e.code == ErrorCode.AUTH:
            print(f"Authentication error: {e}")
        elif e.code == ErrorCode.CONNECTION:
            print(f"Connection error: {e}")
        else:
            print(f"Error: {e}")
    finally:
        if "client" in locals():
            client.close()


def example_with_metadata() -> None:
    """Publish messages with metadata."""
    print("\n=== Messages with Metadata Example ===\n")

    config = Config(token="your-token-here")

    with Client(config) as client:
        # Create message with variables
        message = Message("orders", b'{"order_id": 123, "amount": 99.99}')
        message.with_variables(
            {
                "priority": "high",
                "customer_id": "CUST-12345",
                "region": "US-WEST",
                "source": "web-app",
            }
        )

        response = client.pub_batch([message])
        print(f"Published {response.messages_received} messages with metadata")


if __name__ == "__main__":
    print("TogoMQ Publishing Examples")
    print("=" * 50)

    # Note: Replace 'your-token-here' with actual token to run examples

    # Uncomment to run examples:
    # example_batch_publish()
    # example_streaming_publish()
    # example_custom_config()
    # example_error_handling()
    # example_with_metadata()

    print("\nTo run examples, replace 'your-token-here' with your actual TogoMQ token")
