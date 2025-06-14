# IoT Inspector 3

Simply run `./start.bash`. It will take care of all the dependencies.

If the underlying Inspector core library is updated, please run the following first:

```bash
uv cache clean
uv lock --upgrade-package libinspector
uv sync
```
