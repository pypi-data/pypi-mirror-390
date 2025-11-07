# Crieur — A Static Revue Generator.

With sources from Stylo corpora.

## Run

```
uv run --with crieur crieur stylo <stylo-corpus-id-1> <stylo-corpus-id-2> …
uv run --with crieur crieur generate serve --title PHLiT
```

## Help

### Commands

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("crieur --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```

options:
  -h, --help  Show this help message and exit

Available commands:
  
    version   Return the current version.
    generate  Generate a new revue website.
    stylo     Initialize a new revue to current directory from Stylo.
    serve     Serve an HTML book from `repository_path`/public or current
              directory/public.

```
<!-- [[[end]]] -->

### Command: `generate`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("crieur generate --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
                       [--extra-vars EXTRA_VARS] [--target-path TARGET_PATH]
                       [--source-path SOURCE_PATH]
                       [--statics-path STATICS_PATH]
                       [--templates-path TEMPLATES_PATH] [--csl-path CSL_PATH]
                       [--without-statics] [--feed-limit FEED_LIMIT]

options:
  -h, --help            show this help message and exit
  --title, -t TITLE     Title of the website (default: Crieur).
  --base-url BASE_URL   Base URL of the website, ending with / (default: /).
  --extra-vars EXTRA_VARS
                        stringified JSON extra vars passed to the templates.
  --target-path TARGET_PATH
                        Path where site is built (default: /public/).
  --source-path SOURCE_PATH
                        Path where stylo source were downloaded (default:
                        /sources/).
  --statics-path STATICS_PATH
                        Path where statics are located (default:
                        @crieur/statics/).
  --templates-path TEMPLATES_PATH
  --csl-path CSL_PATH   Path to the CSL applied for bibliography (default:
                        @crieur/styles/apa.csl).
  --without-statics     Do not copy statics if True (default: False).
  --feed-limit FEED_LIMIT
                        Number of max items in the feed (default: 10).

```
<!-- [[[end]]] -->





### Command: `serve`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("crieur serve --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```

options:
  -h, --help            show this help message and exit
  --repository-path REPOSITORY_PATH
                        Absolute or relative path to book’s sources (default:
                        current).
  --port, -p PORT       Port to serve the book from (default=8000)

```
<!-- [[[end]]] -->

### Command: `stylo`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("crieur stylo --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
                    [--stylo-export STYLO_EXPORT] [--force-download]
                    [stylo_ids ...]

positional arguments:
  stylo_ids             Corpus ids from Stylo, separated by commas.

options:
  -h, --help            show this help message and exit
  --stylo-instance STYLO_INSTANCE
                        Instance of Stylo (default: stylo.huma-num.fr).
  --stylo-export STYLO_EXPORT
                        Stylo export URL (default: https://export.stylo.huma-
                        num.fr).
  --force-download      Force download of sources from Stylo (default: False).

```
<!-- [[[end]]] -->
