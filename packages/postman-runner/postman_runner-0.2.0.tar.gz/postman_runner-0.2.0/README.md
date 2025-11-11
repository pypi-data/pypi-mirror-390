# Postman Runner (CLI)

This project provides a local-only command line runner for Postman collections. It loads collections exported in JSON format, applies optional environments, and executes the selected request using the `requests` library. Assertions defined in the collection or supplied separately are evaluated and reported in the console output.

## Quick start

```bash
pip install postman-runner
postman-runner --help
```

Export your collection (v2.1 JSON) and, if needed, the related environment file, then run:

```bash
postman-runner --collection collection.json --request-name "Sample request"
```

Additional usage details, including Farsi documentation, are available in `README.fa.md`.
