# Examples

`invoice/Main.xaml` is a deliberately small UiPath-like fixture for parser demonstrations.

Run:

```bash
curl -X POST http://localhost:8000/api/v1/automations/import \
  -H 'Content-Type: application/json' \
  -d @examples/import-uipath.json
```

For a richer end-to-end demo with safe replay behavior, call:

```bash
curl -X POST http://localhost:8000/api/v1/demo/seed
```
