import itertools
from typing import Generator
from unittest.mock import create_autospec

import pytest
import statsig_python_core
from openfeature.evaluation_context import EvaluationContext
from openfeature.exception import TypeMismatchError
from openfeature.flag_evaluation import Reason

import statsig_openfeature_provider_python
from statsig_openfeature_provider_python import StatsigProvider
from statsig_openfeature_provider_python.provider import DEFAULT_TARGETING_KEY


@pytest.fixture(autouse=True)
def mock_statsig_client() -> Generator[statsig_python_core.Statsig, None, None]:
    yield create_autospec(statsig_python_core.Statsig, instance=True)


@pytest.fixture
def mock_statsig_feature_gate() -> Generator[statsig_python_core.FeatureGate, None, None]:
    yield create_autospec(statsig_python_core.FeatureGate, instance=True)


@pytest.fixture
def mock_statsig_dynamic_config() -> Generator[statsig_python_core.DynamicConfig, None, None]:
    yield create_autospec(statsig_python_core.DynamicConfig, instance=True)


class TestStatsigProvider:
    def test_get_metadata(self, mock_statsig_client):
        provider = StatsigProvider(client=mock_statsig_client)
        assert provider.get_metadata().name == "StatsigProvider"

    @pytest.mark.parametrize(
        "targeting_key,attributes",
        list(itertools.product(["some-targeting-key", None], [{"foo": "bar", "baz": "bux"}, None])),
    )
    def test__get_statsig_user(self, mock_statsig_client, targeting_key, attributes):
        provider = StatsigProvider(client=mock_statsig_client)
        context = EvaluationContext(
            targeting_key=targeting_key,
            attributes=attributes,
        )
        user = provider._get_statsig_user(evaluation_context=context)
        assert user.user_id == (targeting_key if targeting_key else DEFAULT_TARGETING_KEY)
        assert user.custom == (attributes if attributes else {})

    def test__get_statsig_user_without_evaluation_context(self, mock_statsig_client):
        provider = StatsigProvider(client=mock_statsig_client)
        user = provider._get_statsig_user()
        assert user.user_id == statsig_openfeature_provider_python.provider.DEFAULT_TARGETING_KEY

    @pytest.mark.parametrize(
        "statsig_rule_id,statsig_value",
        [
            ("some-rule-id", True),  # gate exists and returned True for user
            ("some-rule-id", False),  # gate exists and returned False for user
            (None, False),  # gate doesn't exist and returned False default
        ],
    )
    def test_resolve_boolean_details(
        self, mock_statsig_client, mock_statsig_feature_gate, statsig_rule_id, statsig_value
    ):
        mock_statsig_feature_gate.rule_id = statsig_rule_id
        mock_statsig_feature_gate.value = statsig_value
        mock_statsig_client.get_feature_gate.return_value = mock_statsig_feature_gate
        provider = StatsigProvider(client=mock_statsig_client)
        resp = provider.resolve_boolean_details("some-rule-id", False, None)

        assert resp.value == statsig_value
        assert resp.reason == (Reason.TARGETING_MATCH if statsig_rule_id else Reason.DEFAULT)

    @pytest.mark.parametrize(
        "statsig_config_id,statsig_config_value,expected_value",
        [
            # config exists and returned valid array obj for user
            ("some-config-id", {"foo": ["bar", "baz"]}, ["bar", "baz"]),
            # config exists and returned valid dict obj for user
            ("some-config-id", {"foo": {"bar": "baz"}}, {"bar": "baz"}),
            # config exists and returned invalid obj for user
            ("some-config-id", {"foo": "bar"}, None),
            # config doesn't exist and returned default empty obj for user
            (None, {}, None),
        ],
    )
    def test_resolve_object_details(
        self,
        mock_statsig_client,
        mock_statsig_dynamic_config,
        statsig_config_id,
        statsig_config_value,
        expected_value,
    ):
        mock_statsig_dynamic_config.config_id = statsig_config_id
        mock_statsig_dynamic_config.value = statsig_config_value
        mock_statsig_client.get_dynamic_config.return_value = mock_statsig_dynamic_config
        provider = StatsigProvider(client=mock_statsig_client)

        if expected_value:
            resp = provider.resolve_object_details("some-config-id", [], None)
            assert resp.value == expected_value
            assert resp.reason == (Reason.TARGETING_MATCH if statsig_config_id else Reason.DEFAULT)
        else:
            with pytest.raises(TypeMismatchError) as e:
                _ = provider.resolve_object_details("some-config-id", [], None)

            if statsig_config_id:
                assert str(e.value) == "value extracted from dynamic config is not an object"
            else:
                assert (
                    str(e.value)
                    == "multiple keys found in config which isn't compatible with the default config value extractor, "
                    "you can define your own config value extractor function and pass it in on provider "
                    "initialization using the config_value_extractor_func kwarg"
                )

    @pytest.mark.parametrize(
        "statsig_config_id,statsig_config_value,expected_value",
        [
            # config exists and returned invalid array obj for user
            ("some-config-id", {"foo": ["bar", "baz"]}, None),
            # config exists and returned invalid dict obj for user
            ("some-config-id", {"foo": {"bar": "baz"}}, None),
            # config exists and returned valid string for user
            ("some-config-id", {"foo": "bar"}, "bar"),
            # config doesn't exist and returned default empty obj for user
            (None, {}, None),
        ],
    )
    def test_resolve_string_details(
        self,
        mock_statsig_client,
        mock_statsig_dynamic_config,
        statsig_config_id,
        statsig_config_value,
        expected_value,
    ):
        mock_statsig_dynamic_config.config_id = statsig_config_id
        mock_statsig_dynamic_config.value = statsig_config_value
        mock_statsig_client.get_dynamic_config.return_value = mock_statsig_dynamic_config
        provider = StatsigProvider(client=mock_statsig_client)

        if expected_value:
            resp = provider.resolve_string_details("some-config-id", "foo", None)
            assert resp.value == expected_value
            assert resp.reason == (Reason.TARGETING_MATCH if statsig_config_id else Reason.DEFAULT)
        else:
            with pytest.raises(TypeMismatchError) as e:
                _ = provider.resolve_string_details("some-config-id", "foo", None)

            if statsig_config_id:
                assert str(e.value) == "value extracted from dynamic config is not a string"
            else:
                assert (
                    str(e.value)
                    == "multiple keys found in config which isn't compatible with the default config value extractor, "
                    "you can define your own config value extractor function and pass it in on provider "
                    "initialization using the config_value_extractor_func kwarg"
                )

    @pytest.mark.parametrize(
        "statsig_config_id,statsig_config_value,expected_value",
        [
            # config exists and returned invalid array obj for user
            ("some-config-id", {"foo": ["bar", "baz"]}, None),
            # config exists and returned invalid dict obj for user
            ("some-config-id", {"foo": {"bar": "baz"}}, None),
            # config exists and returned valid int for user
            ("some-config-id", {"foo": 345}, 345),
            # config doesn't exist and returned default empty obj for user
            (None, {}, None),
        ],
    )
    def test_resolve_integer_details(
        self,
        mock_statsig_client,
        mock_statsig_dynamic_config,
        statsig_config_id,
        statsig_config_value,
        expected_value,
    ):
        mock_statsig_dynamic_config.config_id = statsig_config_id
        mock_statsig_dynamic_config.value = statsig_config_value
        mock_statsig_client.get_dynamic_config.return_value = mock_statsig_dynamic_config
        provider = StatsigProvider(client=mock_statsig_client)

        if expected_value:
            resp = provider.resolve_integer_details("some-config-id", 123, None)
            assert resp.value == expected_value
            assert resp.reason == (Reason.TARGETING_MATCH if statsig_config_id else Reason.DEFAULT)
        else:
            with pytest.raises(TypeMismatchError) as e:
                _ = provider.resolve_integer_details("some-config-id", 123, None)

            if statsig_config_id:
                assert str(e.value) == "value extracted from dynamic config is not an int"
            else:
                assert (
                    str(e.value)
                    == "multiple keys found in config which isn't compatible with the default config value extractor, "
                    "you can define your own config value extractor function and pass it in on provider "
                    "initialization using the config_value_extractor_func kwarg"
                )

    @pytest.mark.parametrize(
        "statsig_config_id,statsig_config_value,expected_value",
        [
            # config exists and returned invalid array obj for user
            ("some-config-id", {"foo": ["bar", "baz"]}, None),
            # config exists and returned invalid dict obj for user
            ("some-config-id", {"foo": {"bar": "baz"}}, None),
            # config exists and returned valid float for user
            ("some-config-id", {"foo": 3.45}, 3.45),
            # config doesn't exist and returned default empty obj for user
            (None, {}, None),
        ],
    )
    def test_resolve_float_details(
        self,
        mock_statsig_client,
        mock_statsig_dynamic_config,
        statsig_config_id,
        statsig_config_value,
        expected_value,
    ):
        mock_statsig_dynamic_config.config_id = statsig_config_id
        mock_statsig_dynamic_config.value = statsig_config_value
        mock_statsig_client.get_dynamic_config.return_value = mock_statsig_dynamic_config
        provider = StatsigProvider(client=mock_statsig_client)

        if expected_value:
            resp = provider.resolve_float_details("some-config-id", 1.23, None)
            assert resp.value == expected_value
            assert resp.reason == (Reason.TARGETING_MATCH if statsig_config_id else Reason.DEFAULT)
        else:
            with pytest.raises(TypeMismatchError) as e:
                _ = provider.resolve_float_details("some-config-id", 1.23, None)

            if statsig_config_id:
                assert str(e.value) == "value extracted from dynamic config is not a float"
            else:
                assert (
                    str(e.value)
                    == "multiple keys found in config which isn't compatible with the default config value extractor, "
                    "you can define your own config value extractor function and pass it in on provider "
                    "initialization using the config_value_extractor_func kwarg"
                )
