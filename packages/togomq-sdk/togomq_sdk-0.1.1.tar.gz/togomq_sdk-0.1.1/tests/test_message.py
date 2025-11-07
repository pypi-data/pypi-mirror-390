"""Unit tests for message module."""

from togomq.message import Message


class TestMessage:
    """Tests for Message class."""

    def test_message_basic(self) -> None:
        """Test basic message creation."""
        msg = Message("test-topic", b"test-body")

        assert msg.topic == "test-topic"
        assert msg.body == b"test-body"
        assert msg.variables == {}
        assert msg.postpone == 0
        assert msg.retention == 0
        assert msg.uuid is None

    def test_message_with_all_fields(self) -> None:
        """Test message with all fields."""
        variables = {"key1": "value1", "key2": "value2"}
        msg = Message(
            topic="test-topic",
            body=b"test-body",
            variables=variables,
            postpone=60,
            retention=3600,
            uuid="test-uuid",
        )

        assert msg.topic == "test-topic"
        assert msg.body == b"test-body"
        assert msg.variables == variables
        assert msg.postpone == 60
        assert msg.retention == 3600
        assert msg.uuid == "test-uuid"

    def test_message_default_body(self) -> None:
        """Test that body defaults to empty bytes."""
        msg = Message("test-topic")
        assert msg.body == b""

    def test_message_with_variables_builder(self) -> None:
        """Test with_variables builder method."""
        variables = {"key": "value"}
        msg = Message("test-topic", b"body").with_variables(variables)

        assert msg.variables == variables
        assert msg.topic == "test-topic"  # Other fields unchanged

    def test_message_with_postpone_builder(self) -> None:
        """Test with_postpone builder method."""
        msg = Message("test-topic", b"body").with_postpone(120)

        assert msg.postpone == 120
        assert msg.topic == "test-topic"  # Other fields unchanged

    def test_message_with_retention_builder(self) -> None:
        """Test with_retention builder method."""
        msg = Message("test-topic", b"body").with_retention(7200)

        assert msg.retention == 7200
        assert msg.topic == "test-topic"  # Other fields unchanged

    def test_message_builder_chaining(self) -> None:
        """Test chaining builder methods."""
        msg = (
            Message("test-topic", b"body")
            .with_variables({"key": "value"})
            .with_postpone(60)
            .with_retention(3600)
        )

        assert msg.variables == {"key": "value"}
        assert msg.postpone == 60
        assert msg.retention == 3600

    def test_message_repr(self) -> None:
        """Test message repr."""
        msg = Message("test-topic", b"test-body", variables={"key": "value"})
        repr_str = repr(msg)

        assert "Message" in repr_str
        assert "test-topic" in repr_str
        assert "key" in repr_str

    def test_message_str(self) -> None:
        """Test message str."""
        msg = Message("test-topic", b"test-body")
        str_repr = str(msg)

        assert "Message" in str_repr
        assert "test-topic" in str_repr

    def test_message_str_truncates_long_body(self) -> None:
        """Test that str truncates long body."""
        long_body = b"x" * 100
        msg = Message("test-topic", long_body)
        str_repr = str(msg)

        # Should be truncated
        assert "..." in str_repr
        assert len(str_repr) < len(long_body)
