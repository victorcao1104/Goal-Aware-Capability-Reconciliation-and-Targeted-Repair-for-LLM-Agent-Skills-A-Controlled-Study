# V6b: corrected adaptive provenance study

This is the measured continuation of v6. The original v6 run stopped before selection or holdout because its parser joined intermediate commentary with the final JSON. V6b freezes a phase-aware response parser and preserves the original samples, prompts, scoring and budgets. Original observations and interruption costs remain in the archive.

Read [measured findings](report/findings.md), the [prospective protocol](../docs/protocol/adaptive-provenance-v6.md), and the [transport amendment](../docs/protocol/adaptive-provenance-v6b-amendment.md).

Install root requirements.lock with Python 3.12, then run offline:

```text
python -m unittest discover -s tests_v6
python -m unittest discover -s tests_v6b
python -m research_v6b.reproduce
python -m scripts.report_v6 --verify
```

No API key or network is needed after dependencies are installed. Use a short Windows checkout path. Replay checks both archives, source hashes, response parsing, all development feedback, selection, held-out trajectories, aggregate metrics and conservative per-model accounting.

Results include all candidates, unsuccessful attacks, model failures and authorized utility. Model aliases and returned identifiers are recorded per request. The comparison covers GPT-4.1 Mini (no reasoning parameter), GPT-6 Luna none and GPT-6 Luna low. Identical logical component inputs are cached; physical requests and logical uses are reported separately. All file operations and transfers are simulated on synthetic data.

The original IEEE manuscript remains the frozen v1 paper; v6b findings are a separate research supplement. A new paid run must have a new output/version and a reconciled cumulative budget; do not overwrite the recorded experiment.
