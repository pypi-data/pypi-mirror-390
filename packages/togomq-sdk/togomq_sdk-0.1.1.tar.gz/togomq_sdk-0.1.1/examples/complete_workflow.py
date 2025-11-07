"""Example: Complete TogoMQ workflow."""

import threading
import time

from togomq import Client, Config, Message, SubscribeOptions


def publisher_thread(client: Client) -> None:
    """Publish messages in a separate thread."""
    print("Publisher: Starting...")

    # Publish some initial messages
    messages = [
        Message("demo.orders", b"order-1").with_variables({"priority": "high"}),
        Message("demo.orders", b"order-2").with_variables({"priority": "low"}),
        Message("demo.events", b"event-1"),
    ]

    response = client.pub_batch(messages)
    print(f"Publisher: Published {response.messages_received} initial messages")

    # Continue publishing periodically
    for i in range(5):
        time.sleep(2)
        msg = Message("demo.orders", f"order-{i+3}".encode())
        client.pub_batch([msg])
        print(f"Publisher: Published message {i+3}")

    print("Publisher: Finished")


def subscriber_thread(client: Client, topic: str) -> None:
    """Subscribe to messages in a separate thread."""
    print(f"Subscriber [{topic}]: Starting...")

    options = SubscribeOptions(topic).with_batch(5)
    msg_gen, err_gen = client.sub(options)

    count = 0
    for msg in msg_gen:
        print(f"Subscriber [{topic}]: Received {msg.uuid} - {msg.body.decode()}")
        count += 1
        if count >= 8:  # Stop after receiving some messages
            break

    print(f"Subscriber [{topic}]: Finished")


def main() -> None:
    """Run complete example with publisher and subscribers."""
    print("\n=== Complete TogoMQ Workflow Example ===\n")

    # Create configuration
    config = Config(token="your-token-here", log_level="info")

    # Create clients (one per thread for thread safety)
    pub_client = Client(config)
    sub1_client = Client(config)
    sub2_client = Client(config)

    try:
        # Start subscriber threads first
        sub1 = threading.Thread(target=subscriber_thread, args=(sub1_client, "demo.orders"))
        sub2 = threading.Thread(target=subscriber_thread, args=(sub2_client, "demo.*"))

        sub1.start()
        sub2.start()

        # Give subscribers time to connect
        time.sleep(1)

        # Start publisher thread
        pub = threading.Thread(target=publisher_thread, args=(pub_client,))
        pub.start()

        # Wait for all threads to complete
        pub.join()
        sub1.join()
        sub2.join()

        print("\n=== Workflow Complete ===")

    finally:
        pub_client.close()
        sub1_client.close()
        sub2_client.close()


if __name__ == "__main__":
    # Note: Replace 'your-token-here' with actual token to run
    # main()
    print("To run this example, replace 'your-token-here' with your actual TogoMQ token")
    print("Then uncomment the main() call above")
