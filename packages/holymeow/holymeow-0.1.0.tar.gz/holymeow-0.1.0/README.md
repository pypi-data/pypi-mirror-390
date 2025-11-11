# Steps

```shell
>> uv version --bump minor 
>> rm -rf dist/* && uv build 
>> uv publish
>> uv run --with hello_uv_42353 --no-project -- python -c "import hello_uv"
>> uv run python
```
