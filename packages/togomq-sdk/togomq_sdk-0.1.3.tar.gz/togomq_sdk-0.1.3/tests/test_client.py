"""Unit tests for client module."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import grpc
import pytest
from mq.v1 import mq_pb2

from togomq.client import Client, PublishResponse
from togomq.config import Config
from togomq.errors import ErrorCode, TogoMQError
from togomq.message import Message
from togomq.subscribe_options import SubscribeOptions


# Create a concrete RpcError for testing
class MockRpcError(grpc.RpcError):
    """Mock RpcError for testing."""

    def __init__(self, code=None, details=""):
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


@pytest.fixture
def mock_channel():
    """Create a mock gRPC channel."""
    with patch("togomq.client.grpc.secure_channel") as mock:
        channel = MagicMock()
        mock.return_value = channel
        yield channel


@pytest.fixture
def mock_stub():
    """Create a mock gRPC stub."""
    stub = MagicMock()

    # Mock health check to succeed
    health_response = mq_pb2.HealthCheckResponse(alive=True)
    stub.HealthCheck.return_value = health_response

    return stub


@pytest.fixture
def client(mock_channel, mock_stub):
    """Create a client with mocked dependencies."""
    with patch("togomq.client.mq_pb2_grpc.MqServiceStub", return_value=mock_stub):
        config = Config(token="test-token")
        client = Client(config)
        yield client
        client.close()


class TestPublishResponse:
    """Tests for PublishResponse class."""

    def test_publish_response_creation(self) -> None:
        """Test creating a publish response."""
        response = PublishResponse(messages_received=5)
        assert response.messages_received == 5

    def test_publish_response_repr(self) -> None:
        """Test publish response repr."""
        response = PublishResponse(messages_received=10)
        repr_str = repr(response)

        assert "PublishResponse" in repr_str
        assert "10" in repr_str


class TestClient:
    """Tests for Client class."""

    def test_client_creation(self, mock_channel, mock_stub) -> None:
        """Test client creation and connection."""
        with patch("togomq.client.mq_pb2_grpc.MqServiceStub", return_value=mock_stub):
            config = Config(token="test-token")
            client = Client(config)

            assert client.config == config
            assert client._channel is not None
            assert client._stub is not None

            client.close()

    def test_client_creation_insecure(self, mock_stub) -> None:
        """Test client creation without TLS."""
        with patch("togomq.client.grpc.insecure_channel") as mock_channel:
            with patch("togomq.client.mq_pb2_grpc.MqServiceStub", return_value=mock_stub):
                config = Config(token="test-token", use_tls=False)
                client = Client(config)

                mock_channel.assert_called_once()
                client.close()

    def test_client_connection_failure(self, mock_channel) -> None:
        """Test client connection failure."""
        stub = MagicMock()
        stub.HealthCheck.side_effect = grpc.RpcError()

        with patch("togomq.client.mq_pb2_grpc.MqServiceStub", return_value=stub):
            with pytest.raises(TogoMQError) as exc_info:
                config = Config(token="test-token")
                Client(config)

            assert exc_info.value.code == ErrorCode.CONNECTION

    def test_client_context_manager(self, mock_channel, mock_stub) -> None:
        """Test client as context manager."""
        with patch("togomq.client.mq_pb2_grpc.MqServiceStub", return_value=mock_stub):
            config = Config(token="test-token")

            with Client(config) as client:
                assert client._channel is not None
                channel = client._channel

            # Channel should be closed after context
            channel.close.assert_called_once()
            assert client._channel is None

    def test_client_close(self, client) -> None:
        """Test client close method."""
        assert client._channel is not None
        channel = client._channel

        client.close()

        channel.close.assert_called_once()
        assert client._channel is None
        assert client._stub is None

    def test_pub_batch_success(self, client, mock_stub) -> None:
        """Test successful batch publishing."""
        # Mock successful publish
        pub_response = mq_pb2.PubMessageResponse(messages_received=2)
        mock_stub.Pub.return_value = pub_response

        messages = [
            Message("topic1", b"body1"),
            Message("topic2", b"body2"),
        ]

        response = client.pub_batch(messages)

        assert response.messages_received == 2
        mock_stub.Pub.assert_called_once()

    def test_pub_batch_empty_list(self, client) -> None:
        """Test publishing empty message list raises error."""
        with pytest.raises(TogoMQError) as exc_info:
            client.pub_batch([])

        assert exc_info.value.code == ErrorCode.VALIDATION

    def test_pub_batch_missing_topic(self, client) -> None:
        """Test publishing message without topic raises error."""
        messages = [Message("", b"body")]

        with pytest.raises(TogoMQError) as exc_info:
            client.pub_batch(messages)

        assert exc_info.value.code == ErrorCode.VALIDATION

    def test_pub_batch_grpc_error(self, client, mock_stub) -> None:
        """Test handling gRPC error in pub_batch."""
        error = MockRpcError(code=grpc.StatusCode.UNAVAILABLE, details="Service unavailable")
        mock_stub.Pub.side_effect = error

        messages = [Message("topic", b"body")]

        with pytest.raises(TogoMQError) as exc_info:
            client.pub_batch(messages)

        assert exc_info.value.code == ErrorCode.CONNECTION

    def test_pub_streaming_success(self, client, mock_stub) -> None:
        """Test successful streaming publishing."""
        pub_response = mq_pb2.PubMessageResponse(messages_received=3)
        mock_stub.Pub.return_value = pub_response

        def message_gen() -> Generator[Message, None, None]:
            for i in range(3):
                yield Message(f"topic-{i}", f"body-{i}".encode())

        response = client.pub(message_gen())

        assert response.messages_received == 3
        mock_stub.Pub.assert_called_once()

    def test_sub_success(self, client, mock_stub) -> None:
        """Test successful subscription."""
        # Mock subscription stream
        pb_messages = [
            mq_pb2.SubMessageResponse(topic="topic1", uuid="uuid1", body=b"body1"),
            mq_pb2.SubMessageResponse(topic="topic2", uuid="uuid2", body=b"body2"),
        ]
        mock_stub.Sub.return_value = iter(pb_messages)

        options = SubscribeOptions("test-topic")
        msg_gen, err_gen = client.sub(options)

        messages = list(msg_gen)

        assert len(messages) == 2
        assert messages[0].topic == "topic1"
        assert messages[0].uuid == "uuid1"
        assert messages[0].body == b"body1"

    def test_sub_missing_topic(self, client) -> None:
        """Test subscription without topic raises error."""
        options = SubscribeOptions("")

        with pytest.raises(TogoMQError) as exc_info:
            client.sub(options)

        assert exc_info.value.code == ErrorCode.VALIDATION

    def test_get_metadata(self, client) -> None:
        """Test metadata generation for authentication."""
        metadata = client._get_metadata()

        assert len(metadata) == 1
        assert metadata[0][0] == "authorization"
        assert metadata[0][1] == "Bearer test-token"

    def test_handle_grpc_error_unauthenticated(self, client) -> None:
        """Test handling unauthenticated error."""
        error = MagicMock()
        error.code.return_value = grpc.StatusCode.UNAUTHENTICATED
        error.details.return_value = "Invalid token"

        with pytest.raises(TogoMQError) as exc_info:
            client._handle_grpc_error(error, ErrorCode.PUBLISH)

        assert exc_info.value.code == ErrorCode.AUTH

    def test_handle_grpc_error_invalid_argument(self, client) -> None:
        """Test handling invalid argument error."""
        error = MagicMock()
        error.code.return_value = grpc.StatusCode.INVALID_ARGUMENT
        error.details.return_value = "Invalid request"

        with pytest.raises(TogoMQError) as exc_info:
            client._handle_grpc_error(error, ErrorCode.PUBLISH)

        assert exc_info.value.code == ErrorCode.VALIDATION

    def test_handle_grpc_error_unavailable(self, client) -> None:
        """Test handling unavailable error."""
        error = MagicMock()
        error.code.return_value = grpc.StatusCode.UNAVAILABLE
        error.details.return_value = "Service unavailable"

        with pytest.raises(TogoMQError) as exc_info:
            client._handle_grpc_error(error, ErrorCode.PUBLISH)

        assert exc_info.value.code == ErrorCode.CONNECTION
