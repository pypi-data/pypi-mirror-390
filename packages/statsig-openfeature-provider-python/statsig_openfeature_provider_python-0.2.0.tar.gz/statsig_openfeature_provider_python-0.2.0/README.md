# Statsig OpenFeature Provider Python

Unofficial implementation of an OpenFeature Provider for [Statsig](https://www.statsig.com/) 
compatible with their free tier. This implementation is currently quite rigid in where it pulls data
from and only supports pulling boolean values from Feature Gates and all other types from Dynamic 
Configs.

The OpenFeature Evaluation Context is mapped to a StatsigUser which is then used for Feature 
Gate/Dynamic Config evaluation. The context's `targeting_key` is used as the User's ID and the 
context's `attributes` are passed into the `custom` fields of the user. If a `targeting_key` isn't 
present in the context then a default of `"anonymous-user"` will be used. You can provide an 
alternative fallback ID via the `default_targeting_key` arg of the constructor. 

# Usage

## Initialization
You can initialize the client by either:
1. Passing an `sdk_key` (optionally with some `client_options`)
2. Passing an initialized Statsig client directly

This enables you to remove the direct dependency on statsig in your consuming code if needed.

```python
client = Statsig(sdk_key="sdk-key-here", options=StatsigOptions(...))
client.initialize().wait()
provider = StatsigProvider(
    client=client,
    default_targeting_key="mystery-user",
    config_value_extractor_func=None,  # user default config value extractor 
)
```

## Boolean
The provider will fetch a Feature Gate from Statsig using the `flag_key`, e.g.
```python
from openfeature.api import get_client

if get_client().get_boolean_value("some-feature-gate-id", False):
    print("feature is enabled")
```
will fetch the `some-feature-gate-id` Feature Gate from Statsig if it exists. If it doesn't exist
(i.e. Statsig's returned Feature Gate `rule_id` is `None`) then Statsig provide a default of 
`False` which will be returned from the value and the reason will be `DEFAULT`. 

## String
The provider will fetch a Dynamic Config from Statsig using the `flag_key`, e.g.
```python
from openfeature.api import get_client

if val := get_client().get_string_value("some-dynamic-config-id", "foo"):
    print(f"flag value: {val}")
```
will fetch the `some-dynamic-config-id` Dynamic Config from Statsig if it exists. If it doesn't 
exist (i.e. Statsig's returned Dynamic Config `rule_id` is `None`) then Statsig provide a default of 
`{}` which will result in the default value being returned instead. Since Dynamic Configs are always
an object, we have to extract the inner value from the config - this is done using the 
`config_value_extractor_func`, see the Config Value Extractors section for more info on how this 
works and how to define your own.

## Integer
The provider will fetch a Dynamic Config from Statsig using the `flag_key`, e.g.
```python
from openfeature.api import get_client

if val := get_client().get_integer_value("some-dynamic-config-id", 123):
    print(f"flag value: {val}")
```
will fetch the `some-dynamic-config-id` Dynamic Config from Statsig if it exists. If it doesn't 
exist (i.e. Statsig's returned Dynamic Config `rule_id` is `None`) then Statsig provide a default of 
`{}` which will result in the default value being returned instead. Since Dynamic Configs are always
an object, we have to extract the inner value from the config - this is done using the 
`config_value_extractor_func`, see the Config Value Extractors section for more info on how this 
works and how to define your own.

## Float
The provider will fetch a Dynamic Config from Statsig using the `flag_key`, e.g.
```python
from openfeature.api import get_client

if val := get_client().get_float_value("some-dynamic-config-id", 1.23):
    print(f"flag value: {val}")
```
will fetch the `some-dynamic-config-id` Dynamic Config from Statsig if it exists. If it doesn't 
exist (i.e. Statsig's returned Dynamic Config `rule_id` is `None`) then Statsig provide a default of 
`{}` which will result in the default value being returned instead. Since Dynamic Configs are always
an object, we have to extract the inner value from the config - this is done using the 
`config_value_extractor_func`, see the Config Value Extractors section for more info on how this 
works and how to define your own.

## Object
The provider will fetch a Dynamic Config from Statsig using the `flag_key`, e.g.
```python
from openfeature.api import get_client

if val := get_client().get_object_value("some-dynamic-config-id", []):
    print(f"flag value: {val}")
```
will fetch the `some-dynamic-config-id` Dynamic Config from Statsig if it exists. If it doesn't 
exist (i.e. Statsig's returned Dynamic Config `rule_id` is `None`) then Statsig provide a default of 
`{}` which will result in the default value being returned instead. Since Dynamic Configs are always
an object, we have to extract the inner value from the config - this is done using the 
`config_value_extractor_func`, see the Config Value Extractors section for more info on how this 
works and how to define your own.

> [!WARNING]  
> Even though the response from Statsig when fetching a Dynamic Config _is_ an object, it doesn't
> support the use case for when the value is an array. Because of this, and to keep it consistent 
> with the other methods it still relies on an embedded value existing by default. If you don't want
> this behaviour you can provide your own `config_value_extractor_func`.

# Config Value Extractors
Since we can't return Dynamic Configs directly when evaluating flags for types we need a way of 
mapping the config object we receive into a value that aligns with the type the consumer is trying
to fetch the flag value for. A default is provided with this implementation:
```python
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
```
Which will take any object with a single key and pass the value directly to the caller, which will
then be validated against the type of the flag being requested. e.g. any of the below configs would
return the same value
```json lines
{"foo": "bar"}
{"bar": "bar"}
{"some-other-key": "bar"}
```

If this implementation doesn't work for you, you can pass your own in as long as it has the
`Callable[[dict], FlagValueType]` type. e.g. if you wanted to accept configs with multiple keys but
you always extract from a specific key you could implement a naive solution like:
```python
def static_key_value_extractor(config: dict) -> FlagValueType:
    return config.get("some-static-key", None)
```
