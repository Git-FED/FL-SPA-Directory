# FED-SPA Prompt Library

Ready-to-use prompts for AI assistants helping with FED-SPA work. Every prompt here encodes the three constraints so you don't have to re-litigate them in a fresh chat:

1. **No backend** — static files only, updated once a year.
2. **No third-party** — no external libraries, SDKs, services, analytics, or tracking, on any surface.
3. **Annual cadence** — the data refresh is a once-a-year human workflow.

Copy a prompt, fill in the bracketed parts, paste it into your assistant of choice.

| Prompt | Use it when |
|---|---|
| [annual-refresh.md](annual-refresh.md) | It's data season and you want step-by-step help running the yearly update. |
| [verify-a-record.md](verify-a-record.md) | You're adding or correcting one establishment record against the MQA portal. |
| [review-a-pr.md](review-a-pr.md) | A pull request is open and you want a constraints-aware review pass. |
| [new-surface.md](new-surface.md) | You want to port FED-SPA to a new platform (a watch, a TV, a car with a different head unit). |
| [release-notes.md](release-notes.md) | The refresh is done and the release announcement needs writing. |

## House rules for using these prompts

- **Never paste subscriber content into any AI chat.** Not the shared code, not decrypted watchlist records. The prompts in this library are written so you never need to.
- **AI output is a draft, not a decision.** Records land in the dataset only after a human has looked at the MQA portal with their own eyes and recorded the check date.
- **If an assistant proposes a library, service, or backend, reject it and point it at the constraints** — they're printed at the top of every prompt for exactly this reason.
