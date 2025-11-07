"""Unit tests for subscribe options module."""

from togomq.subscribe_options import SubscribeOptions


class TestSubscribeOptions:
    """Tests for SubscribeOptions class."""

    def test_subscribe_options_basic(self) -> None:
        """Test basic subscribe options creation."""
        options = SubscribeOptions("test-topic")

        assert options.topic == "test-topic"
        assert options.batch == 0
        assert options.speed_per_sec == 0

    def test_subscribe_options_with_all_fields(self) -> None:
        """Test subscribe options with all fields."""
        options = SubscribeOptions(
            topic="test-topic",
            batch=10,
            speed_per_sec=100,
        )

        assert options.topic == "test-topic"
        assert options.batch == 10
        assert options.speed_per_sec == 100

    def test_subscribe_options_with_batch_builder(self) -> None:
        """Test with_batch builder method."""
        options = SubscribeOptions("test-topic").with_batch(20)

        assert options.batch == 20
        assert options.topic == "test-topic"  # Other fields unchanged

    def test_subscribe_options_with_speed_builder(self) -> None:
        """Test with_speed_per_sec builder method."""
        options = SubscribeOptions("test-topic").with_speed_per_sec(50)

        assert options.speed_per_sec == 50
        assert options.topic == "test-topic"  # Other fields unchanged

    def test_subscribe_options_builder_chaining(self) -> None:
        """Test chaining builder methods."""
        options = SubscribeOptions("test-topic").with_batch(15).with_speed_per_sec(75)

        assert options.topic == "test-topic"
        assert options.batch == 15
        assert options.speed_per_sec == 75

    def test_subscribe_options_wildcard_topic(self) -> None:
        """Test wildcard topic."""
        options = SubscribeOptions("*")
        assert options.topic == "*"

    def test_subscribe_options_pattern_topic(self) -> None:
        """Test pattern topic."""
        options = SubscribeOptions("orders.*")
        assert options.topic == "orders.*"

    def test_subscribe_options_repr(self) -> None:
        """Test subscribe options repr."""
        options = SubscribeOptions("test-topic", batch=10, speed_per_sec=100)
        repr_str = repr(options)

        assert "SubscribeOptions" in repr_str
        assert "test-topic" in repr_str
        assert "10" in repr_str
        assert "100" in repr_str
