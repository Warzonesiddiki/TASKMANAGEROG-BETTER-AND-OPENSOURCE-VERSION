# Fetched data (not committed)

`tmog-feedback-issues.json` is produced by `python3 research/fetch_issues.py` and is
deliberately ignored by git:

- it is other people's writing, and it changes hourly;
- it is ~1.8 MB of JSON that would go stale in the repository;
- the durable artefacts are the scripts and the generated report
  (`docs/research/issues-analysis.md`).

To refresh:

```bash
python3 research/fetch_issues.py
python3 research/analyze_issues.py
```

The report states the date window and the counts it was generated from, so a
reader can tell how old a number is.
