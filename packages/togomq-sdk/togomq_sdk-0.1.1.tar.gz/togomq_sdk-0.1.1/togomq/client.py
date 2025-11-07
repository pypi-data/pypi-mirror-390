"""TogoMQ client implementation."""

from collections.abc import Generator, Iterator
from typing import Optional

import grpc
from mq.v1 import mq_pb2, mq_pb2_grpc

from togomq.config import Config
from togomq.errors import ErrorCode, TogoMQError
from togomq.logger import setup_logger
from togomq.message import Message
from togomq.subscribe_options import SubscribeOptions


class PublishResponse:
    """Response from publish operations."""

    def __init__(self, messages_received: int) -> None:
        """Initialize publish response.

        Args:
            messages_received: Number of messages received by the server.
        """
        self.messages_received = messages_received

    def __repr__(self) -> str:
        """Repr of the response."""
        return f"PublishResponse(messages_received={self.messages_received})"


class Client:
    """TogoMQ client for publishing and subscribing to messages.

    The client maintains a gRPC connection to the TogoMQ server and provides
    methods for publishing and subscribing to messages.

    Example:
        >>> config = Config(token="your-token")
        >>> client = Client(config)
        >>> try:
        >>>     # Use client
        >>>     pass
        >>> finally:
        >>>     client.close()
    """

    def __init__(self, config: Config) -> None:
        """Initialize TogoMQ client.

        Args:
            config: Client configuration.

        Raises:
            TogoMQError: If connection fails.
        """
        self.config = config
        self.logger = setup_logger("togomq.client", config.log_level)
        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[mq_pb2_grpc.MqServiceStub] = None
        self._connect()

    def _connect(self) -> None:
        """Establish connection to TogoMQ server.

        Raises:
            TogoMQError: If connection fails.
        """
        try:
            address = self.config.get_address()
            self.logger.info(f"Connecting to TogoMQ at {address}")

            # Create channel
            if self.config.use_tls:
                credentials = grpc.ssl_channel_credentials()
                self._channel = grpc.secure_channel(address, credentials)
            else:
                self._channel = grpc.insecure_channel(address)

            # Create stub
            self._stub = mq_pb2_grpc.MqServiceStub(self._channel)

            # Test connection with health check
            try:
                metadata = self._get_metadata()
                request = mq_pb2.HealthCheckRequest(message="ping")
                response = self._stub.HealthCheck(request, metadata=metadata, timeout=5.0)
                if response.alive:
                    self.logger.info("Successfully connected to TogoMQ")
                else:
                    raise TogoMQError(
                        code=ErrorCode.CONNECTION,
                        message="Health check failed: server not alive",
                    )
            except grpc.RpcError as e:
                self.logger.error(f"Health check failed: {e}")
                raise TogoMQError(
                    code=ErrorCode.CONNECTION,
                    message="Failed to connect to TogoMQ server",
                    details=str(e),
                ) from e

        except grpc.RpcError as e:
            self.logger.error(f"Connection failed: {e}")
            raise TogoMQError(
                code=ErrorCode.CONNECTION,
                message="Failed to establish connection",
                details=str(e),
            ) from e

    def _get_metadata(self) -> list[tuple[str, str]]:
        """Get gRPC metadata for authentication.

        Returns:
            List of metadata tuples.
        """
        return [("authorization", f"Bearer {self.config.token}")]

    def close(self) -> None:
        """Close the connection to TogoMQ server."""
        if self._channel:
            self.logger.info("Closing connection to TogoMQ")
            self._channel.close()
            self._channel = None
            self._stub = None

    def __enter__(self) -> "Client":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()

    def pub_batch(self, messages: list[Message]) -> PublishResponse:
        """Publish a batch of messages.

        Args:
            messages: List of messages to publish.

        Returns:
            PublishResponse with number of messages received.

        Raises:
            TogoMQError: If publishing fails.
        """
        if not messages:
            raise TogoMQError(
                code=ErrorCode.VALIDATION,
                message="Cannot publish empty message list",
            )

        if self._stub is None:
            raise TogoMQError(
                code=ErrorCode.CONNECTION,
                message="Client not connected",
            )

        try:
            self.logger.debug(f"Publishing batch of {len(messages)} messages")

            # Convert messages to protobuf
            pb_messages = []
            for msg in messages:
                if not msg.topic:
                    raise TogoMQError(
                        code=ErrorCode.VALIDATION,
                        message="Message topic is required",
                    )

                pb_msg = mq_pb2.PubMessageRequest(
                    topic=msg.topic,
                    body=msg.body,
                    postpone=msg.postpone,
                    retention=msg.retention,
                )
                # Add variables
                for key, value in msg.variables.items():
                    pb_msg.variables[key] = value

                pb_messages.append(pb_msg)

            # Create request iterator
            def request_iterator() -> Iterator[mq_pb2.PubMessageRequest]:
                yield from pb_messages

            # Call gRPC
            metadata = self._get_metadata()
            response = self._stub.Pub(request_iterator(), metadata=metadata)

            self.logger.info(f"Published {response.messages_received} messages")
            return PublishResponse(messages_received=response.messages_received)

        except grpc.RpcError as e:
            self.logger.error(f"Publish failed: {e}")
            self._handle_grpc_error(e, ErrorCode.PUBLISH)
            raise  # This line won't be reached, but keeps type checker happy

    def pub(self, messages: Generator[Message, None, None]) -> PublishResponse:
        """Publish messages from a generator (streaming).

        Args:
            messages: Generator yielding messages to publish.

        Returns:
            PublishResponse with number of messages received.

        Raises:
            TogoMQError: If publishing fails.
        """
        if self._stub is None:
            raise TogoMQError(
                code=ErrorCode.CONNECTION,
                message="Client not connected",
            )

        try:
            self.logger.debug("Starting streaming publish")

            # Convert messages to protobuf
            def request_iterator() -> Iterator[mq_pb2.PubMessageRequest]:
                for msg in messages:
                    if not msg.topic:
                        raise TogoMQError(
                            code=ErrorCode.VALIDATION,
                            message="Message topic is required",
                        )

                    pb_msg = mq_pb2.PubMessageRequest(
                        topic=msg.topic,
                        body=msg.body,
                        postpone=msg.postpone,
                        retention=msg.retention,
                    )
                    # Add variables
                    for key, value in msg.variables.items():
                        pb_msg.variables[key] = value

                    yield pb_msg

            # Call gRPC
            metadata = self._get_metadata()
            response = self._stub.Pub(request_iterator(), metadata=metadata)

            self.logger.info(f"Published {response.messages_received} messages")
            return PublishResponse(messages_received=response.messages_received)

        except grpc.RpcError as e:
            self.logger.error(f"Streaming publish failed: {e}")
            self._handle_grpc_error(e, ErrorCode.PUBLISH)
            raise  # This line won't be reached, but keeps type checker happy

    def sub(
        self, options: SubscribeOptions
    ) -> tuple[Generator[Message, None, None], Generator[Exception, None, None]]:
        """Subscribe to messages.

        Args:
            options: Subscription options.

        Returns:
            Tuple of (message_generator, error_generator).

        Raises:
            TogoMQError: If subscription fails to start.
        """
        if not options.topic:
            raise TogoMQError(
                code=ErrorCode.VALIDATION,
                message="Topic is required for subscription",
            )

        if self._stub is None:
            raise TogoMQError(
                code=ErrorCode.CONNECTION,
                message="Client not connected",
            )

        try:
            self.logger.info(f"Subscribing to topic: {options.topic}")

            # Create subscription request
            request = mq_pb2.SubMessageRequest(
                topic=options.topic,
                batch=options.batch,
                speed_per_sec=options.speed_per_sec,
            )

            # Call gRPC
            metadata = self._get_metadata()
            response_stream = self._stub.Sub(request, metadata=metadata)

            # Create message generator
            def message_generator() -> Generator[Message, None, None]:
                try:
                    for pb_msg in response_stream:
                        msg = Message(
                            topic=pb_msg.topic,
                            body=pb_msg.body,
                            uuid=pb_msg.uuid,
                        )
                        # Copy variables
                        msg.variables = dict(pb_msg.variables)
                        self.logger.debug(f"Received message: {msg.uuid}")
                        yield msg
                except grpc.RpcError as e:
                    self.logger.error(f"Subscription stream error: {e}")
                    self._handle_grpc_error(e, ErrorCode.SUBSCRIBE)

            # Create error generator (errors are raised in message generator)
            def error_generator() -> Generator[Exception, None, None]:
                # This is a placeholder - errors are handled in message_generator
                return
                yield  # Make it a generator

            return message_generator(), error_generator()

        except grpc.RpcError as e:
            self.logger.error(f"Subscription failed: {e}")
            self._handle_grpc_error(e, ErrorCode.SUBSCRIBE)
            raise  # This line won't be reached, but keeps type checker happy

    def _handle_grpc_error(self, error: grpc.RpcError, default_code: ErrorCode) -> None:
        """Handle gRPC errors and convert to TogoMQError.

        Args:
            error: The gRPC error.
            default_code: Default error code to use.

        Raises:
            TogoMQError: Always raises.
        """
        status_code = error.code()
        details = error.details() if hasattr(error, "details") else str(error)

        # Map gRPC status codes to TogoMQ error codes
        if status_code == grpc.StatusCode.UNAUTHENTICATED:
            code = ErrorCode.AUTH
            message = "Authentication failed"
        elif status_code == grpc.StatusCode.INVALID_ARGUMENT:
            code = ErrorCode.VALIDATION
            message = "Invalid request"
        elif status_code == grpc.StatusCode.UNAVAILABLE:
            code = ErrorCode.CONNECTION
            message = "Service unavailable"
        elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
            code = ErrorCode.CONNECTION
            message = "Request timeout"
        else:
            code = default_code
            message = f"Operation failed: {status_code.name if status_code else 'unknown'}"

        raise TogoMQError(code=code, message=message, details=details)
