# Bot Automation Files — Setup Notes

## Before you start
Go to your repo **Settings > Actions > General**, scroll to "Workflow permissions",
select **"Read and write permissions"**, and check
**"Allow GitHub Actions to create and approve pull requests"**.
This lets `github-actions[bot]` push commits (needed for ImgBot).

## Files included
- `.github/dependabot.yml` — dependency update bot. Change `"npm"` to match your
  language (`pip`, `maven`, `cargo`, `gomod`, etc.)
- `renovate.json` — alternate dependency bot, scheduled to run on a different day
  than Dependabot to avoid duplicate PRs
- `.github/workflows/imgbot.yml` — compresses images on PRs
- `.github/workflows/stale.yml` — closes idle issues/PRs after 30 days
- `.github/workflows/auto-merge.yml` — auto-merges PRs opened by the bots above
  once checks pass (requires branch protection to allow it)

## Not included as a standalone file
Codecov is added as a step inside your *existing* test workflow, not a new file.
Add this at the end of your CI job:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }} # optional, recommended for private repos
    directory: ./coverage
    fail_ci_if_error: false
```

## Worth knowing
Installing these bots is straightforward and they're genuinely useful (fresher
dependencies, smaller images, tidier issue tracker). But heads up on the original
goal from our chat — making a repo *look* more active to attract contributors:
GitHub's UI already discounts bot activity in the main contributor graph, and
stacking bots doesn't substitute for what actually gets humans to contribute
(a clear README, labeled "good first issue" tickets, and responsive maintainers).
Worth keeping both tracks going rather than leaning on the bots alone.
