# Metripy
A multilanguage, multi project code metrics analysis tool. 

# Languages
Supported languages
- Python (with radon)
- Php (experimental)
- Typescript (experimental)
- TBD

# Analysis types

## Code analysis
Analyses code with cyclomatic complexity, maintainability index, halstead metrics.

## Git analysis
Analyses git stats of the past months

## Dependeny analysis
Analyzses composer, npm or pip dependencies

More dependencies TBD

# Report formats

## Html
Generates an easy to read dashboard

TODO: as this application generates multi project reports, add central dashboard to have project specific insights at first glance

## Csv
Coming soon...

## Json
Coming soon...

## Cli
Coming soon...

# Configuration
Configuration is for the moment only possible with the `--config=<file>.json` option. More TBD

Sample configuraiton:
```json
{
    "configs": {
        "metripy": {
            "base_path": "./", // base path to look at
            "includes": [
                "metripy/" // paths to include from the base path on
            ],
            "excludes": [
                "__pycache__" // exclude patterns of paths / files
            ],
            "extensions": [
                "py" // file extensions to look at
            ],
            "git": { // if git is set, analyzes git history
                "branch": "main" // git branch to look at
            },
            "composer": true, // looks for base_path/composer.json and analyzes dependencies - for php projects
            "npm": true, // looks for base_path/package.json and analyzes dependencies - for ts/js projects
            "pip": true,
            // looks for base_path/requirements.txt or base_path/pyproject.toml and analyzes dependencies - for python projects
            "reports": {
                "html": "./build/report/metripy", // report should be put into this directory
                "json-git": "./build/json-report/metripy-git.json" // file where to put git json report
                // more types of reports TBA
            }
        },
        // next project name: { next config... } 
    }
}
```

## Configuration for only git stats
```json
{
    "configs": {
        "metripy-git": {
            "base_path": "./",
            "git": {
                "branch": "main"
            },
            "reports": {
                "json-git": "./build/json-report/metripy-git.json"
            }
        }
    }
}
```
