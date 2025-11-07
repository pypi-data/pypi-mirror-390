# Pargs

> [!WARNING]
> This is not yet production ready, please wait for the 1.0.0 release

A small python extensible argument system.

## Supported sources

Native supported sources are command arguments, file (json and toml) and
environment variables.
You can glue them together with the `MultiParser` and give them priorities,
to control which arguments may overwrite each other.

## Syntax

Simple example:

```python
params = [
  KwParam.new_simple("hello"),
  KwParam.new_simple("world")
]
config = CliParser().add_params(params).vars()
```

## Roadmap

In the near future, a parsing of a (data)class as a configuration object,
which is then collected via all three native collectors.

## Comparison

Compared to the `argparse` module provided in the standard library,
this provides much fewer features.
This allows for a very small runtime-footprint (>10x faster).
