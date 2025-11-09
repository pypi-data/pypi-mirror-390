# Async AllDebrid API

Lightweight async API to interact with AllDebrid.
This version uses `pydantic` to parse and manipulate the responses.

Start with `alldebrid.Client("<apikey>")` to create an API client.

## Changelog

v0.2.0 uses `pydantic` instead of `attrs`+`cattrs` to parse the responses.