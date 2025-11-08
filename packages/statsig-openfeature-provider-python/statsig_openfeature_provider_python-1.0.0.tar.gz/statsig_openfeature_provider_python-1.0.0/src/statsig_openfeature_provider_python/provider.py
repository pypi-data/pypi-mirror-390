import json
from json import JSONDecodeError
from typing import Any, Callable, Mapping, Optional, Sequence, Union

from openfeature.evaluation_context import EvaluationContext
from openfeature.exception import ProviderFatalError, TypeMismatchError
from openfeature.flag_evaluation import FlagResolutionDetails, FlagValueType, Reason
from openfeature.provider import AbstractProvider, Metadata
from statsig_python_core import Statsig, StatsigOptions, StatsigUser

DEFAULT_TARGETING_KEY = "anonymous-user"


def default_config_value_extractor(config: dict) -> FlagValueType:
    """
    Extracts an embedded value from the config returned as long as there is only one (key, value) pair in the returned
    config. The key is irrelevant for this extractor.

    Args:
        config: the config that the value will be extracted from
    Returns:
        the value extracted from the config
    """
    values = list(config.values())
    if len(values) != 1:
        raise TypeMismatchError(
            "multiple keys found in config which isn't compatible with the default config value extractor, you can "
            "define your own config value extractor function and pass it in on provider initialization using the "
            "config_value_extractor_func kwarg"
        )

    val = values[0]
    if not isinstance(val, bool | int | float | str | Sequence | Mapping):
        raise TypeMismatchError("type of value extracted from statsig config is not a valid FlagValueType")

    return val


class StatsigProvider(AbstractProvider):
    """
    An OpenFeature Provider for the Statsig service. Booleans are resolved by fetching Feature Gates and all other types
    are resolved by fetching Dynamic Configs and extracting a value from the config. The `targeting_key` from the
    `evaluation_context` is used as the `StatsigUser`s ID when fetching Feature Gates and Dynamic Config.

    The way the value is extracted from
    the config depends on the `config_value_extractor_func` used; if one is not provided at initialization then the
    provider will fall back to using the `default_config_value_extractor` which will extract an embedded value from the
    config regardless of the key used, e.g. using the default extractor with a config value like
    `{"foo": {"123": "abc"}}` would result in `{"123": "abc"}` being returned from the extractor.
    """

    def __init__(
        self,
        sdk_key: Optional[str] = None,
        client_options: Optional[StatsigOptions] = None,
        client: Optional[Statsig] = None,
        default_targeting_key: Optional[str] = None,
        config_value_extractor_func: Optional[Callable[[dict], FlagValueType]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            sdk_key: SDK key to pass to Statsig client when initializing, cannot be passed if providing a client
            client_options: options to pass to the Statsig client when initializing, cannot be passed if providing a
                client
            client: an initialized Statsig client, if provided then client_options and sdk_key cannot be provided
            default_targeting_key: the targeting key to use for the StatsigUser used to evaluate the flag when the
                evaluation context doesn't provide one
        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        if client and sdk_key:
            raise ProviderFatalError("either pass in an initialized Statsig client or an API key but not both")
        elif client and client_options:
            raise ProviderFatalError("passing in client_options has no effect if using a pre-initialized client")

        if client:
            self._client = client
        elif sdk_key:
            statsig = Statsig(sdk_key=sdk_key, options=client_options)
            statsig.initialize().wait()
            self._client = statsig
        else:
            raise ProviderFatalError("either an SDK key or an initialized client is needed to initialize the provider")

        self._default_targeting_key = default_targeting_key if default_targeting_key else DEFAULT_TARGETING_KEY

        if config_value_extractor_func:
            self._config_value_extractor = config_value_extractor_func
        else:
            self._config_value_extractor = default_config_value_extractor

    def _get_statsig_user(self, evaluation_context: Optional[EvaluationContext] = None) -> StatsigUser:
        custom = dict(evaluation_context.attributes) if evaluation_context and evaluation_context.attributes else {}

        # TODO(jlc-christie): handle incompatible types between openfeature evaluation context properties and statsig
        #   user custom properties, e.g. datetime, Mapping, etc.
        if evaluation_context and evaluation_context.targeting_key:
            user = StatsigUser(evaluation_context.targeting_key, custom=custom)  # type:ignore[arg-type]
        else:
            user = StatsigUser(self._default_targeting_key, custom=custom)  # type:ignore[arg-type]

        return user

    def _get_embedded_dynamic_config_value(
        self,
        dynamic_config_id: str,
        user: StatsigUser,
    ) -> tuple[FlagValueType | None, Reason]:
        config = self._client.get_dynamic_config(user, dynamic_config_id)

        # no config found with statsig so it returned a default object value
        if not config.rule_id:
            return None, Reason.DEFAULT

        try:
            _ = json.dumps(config.value)
        except JSONDecodeError as e:
            raise TypeMismatchError("statsig returned a dynamic config value that isn't valid json") from e

        val = self._config_value_extractor(config.value)

        return val, Reason.TARGETING_MATCH

    def get_metadata(self) -> Metadata:
        return Metadata(name="StatsigProvider")

    def resolve_boolean_details(
        self,
        flag_key: str,
        default_value: bool,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[bool]:
        user = self._get_statsig_user(evaluation_context)
        resp = self._client.get_feature_gate(user, flag_key)
        reason = Reason.TARGETING_MATCH if resp.rule_id else Reason.DEFAULT

        return FlagResolutionDetails(
            value=resp.value,
            error_code=None,
            error_message=None,
            reason=reason,
            variant=None,
            flag_metadata={},
        )

    def resolve_string_details(
        self,
        flag_key: str,
        default_value: str,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[str]:
        user = self._get_statsig_user(evaluation_context=evaluation_context)
        val, reason = self._get_embedded_dynamic_config_value(dynamic_config_id=flag_key, user=user)

        if reason == Reason.DEFAULT:
            return FlagResolutionDetails(
                value=default_value,
                error_code=None,
                error_message=None,
                reason=reason,
                variant=None,
                flag_metadata={},
            )

        if not isinstance(val, str):
            raise TypeMismatchError("value extracted from dynamic config is not a string")

        return FlagResolutionDetails(
            value=val,
            error_code=None,
            error_message=None,
            reason=reason,
            variant=None,
            flag_metadata={},
        )

    def resolve_integer_details(
        self,
        flag_key: str,
        default_value: int,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[int]:
        user = self._get_statsig_user(evaluation_context=evaluation_context)
        val, reason = self._get_embedded_dynamic_config_value(dynamic_config_id=flag_key, user=user)

        if reason == Reason.DEFAULT:
            return FlagResolutionDetails(
                value=default_value,
                error_code=None,
                error_message=None,
                reason=reason,
                variant=None,
                flag_metadata={},
            )

        if not isinstance(val, int):
            raise TypeMismatchError("value extracted from dynamic config is not an int")

        return FlagResolutionDetails(
            value=val,
            error_code=None,
            error_message=None,
            reason=reason,
            variant=None,
            flag_metadata={},
        )

    def resolve_float_details(
        self,
        flag_key: str,
        default_value: float,
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[float]:
        user = self._get_statsig_user(evaluation_context=evaluation_context)
        val, reason = self._get_embedded_dynamic_config_value(dynamic_config_id=flag_key, user=user)

        if reason == Reason.DEFAULT:
            return FlagResolutionDetails(
                value=default_value,
                error_code=None,
                error_message=None,
                reason=reason,
                variant=None,
                flag_metadata={},
            )

        if not isinstance(val, float):
            raise TypeMismatchError("value extracted from dynamic config is not a float")

        return FlagResolutionDetails(
            value=val,
            error_code=None,
            error_message=None,
            reason=reason,
            variant=None,
            flag_metadata={},
        )

    def resolve_object_details(
        self,
        flag_key: str,
        default_value: Union[Sequence[FlagValueType], Mapping[str, FlagValueType]],
        evaluation_context: Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[Union[Sequence[FlagValueType], Mapping[str, FlagValueType]]]:
        user = self._get_statsig_user(evaluation_context=evaluation_context)
        val, reason = self._get_embedded_dynamic_config_value(dynamic_config_id=flag_key, user=user)

        if reason == Reason.DEFAULT:
            return FlagResolutionDetails(
                value=default_value,
                error_code=None,
                error_message=None,
                reason=reason,
                variant=None,
                flag_metadata={},
            )

        if not isinstance(val, Sequence | Mapping) or isinstance(val, str):
            raise TypeMismatchError("value extracted from dynamic config is not an object")

        return FlagResolutionDetails(
            value=val,
            error_code=None,
            error_message=None,
            reason=reason,
            variant=None,
            flag_metadata={},
        )
