# Running Scrapydweb UI

## Local Environment Setup

0. Source virtual environment, update dependencies, and change working directory to `search_gov_crawler`

1. Start scrapyd

        $ scrapyd

2. Build latest version of scrapy project (if any changes have been made since last run)

        $ scrapyd-deploy local -p search_gov_spiders

3. Start logparser

        $ python -m search_gov_logparser

4. Start scrapydweb

        $ python -m search_gov_scrapydweb

## Deploying with Scrapydweb UI

Due to various design and security decisions, we have never deployed with a UI.  In order to do so the [deploy start script](../cicd-scripts/app_start.sh) would have to be adjusted to accept a value for the SPIDER_RUN_WITH_UI environment variable instead of being hard-coded to `false`.
