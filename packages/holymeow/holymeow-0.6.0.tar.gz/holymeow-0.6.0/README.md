# Steps

```shell
>> uv version --bump minor 
>> rm -rf dist/* && uv build 
>> uv publish
>> uv run --with holymeow --no-project -- python -c "import holymeow"
>> uv run python

>> uv run src/holymeow/main.py 
```
