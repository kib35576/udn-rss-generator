name: Generate RSS
on:
  schedule:
    - cron: '0 */4 * * *'
  workflow_dispatch:
permissions:
  contents: write
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install requests
      - run: python generate_rss.py
      - run: |
          git config user.name 'GitHub Action'
          git config user.email 'action@github.com'
          git add feed.xml
          git diff --cached --quiet || (git commit -m "Update RSS $(date)" && git push)
