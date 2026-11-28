# Source

- Upstream: https://github.com/multica-ai/andrej-karpathy-skills (plugin `andrej-karpathy-skills` v1.0.0, MIT per its plugin.json)
- Commit: 2c606141936f1eeef17fa3043a72095b4765b9c2 (2026-04-20)
- Vendored: `skills/karpathy-guidelines/SKILL.md`, unchanged. The plugin contains only this skill (no hooks, scripts or commands).
- SkillSpector 2026-11-28: CAUTION (8 MEDIUM). All are false positives: the "skill enumeration" hits are install instructions in CURSOR.md, the "autonomous decision" hits are example prose in EXAMPLES.md/README.md. Neither file was vendored.
