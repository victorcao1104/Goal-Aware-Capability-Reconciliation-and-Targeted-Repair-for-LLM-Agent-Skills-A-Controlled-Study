# Updated literature claim map

All referenced papers were acquired from primary arXiv sources and checked against their text. Bibliographic metadata are in literature/verified-references.bib and paper/references.bib. Prior coursework review is retained locally as a starting reference; its broad claim that no task-derived runtime policy exists is not carried forward.

| Source/version | Sections inspected | Supported use in this paper | Important boundary |
|---|---|---|---|
| Skill-Inject 2602.20156v3 | §4–5, limitations | Skill body/script attacks, warning/legitimizing policies | Native scaffolds and tasks differ from our transfer fixtures |
| SkillScope 2605.05868v3 | §3–4, §5, limitations | Unified graph, task validation, control-flow constraining | Our conservative approximation is not its implementation; revised count 6,590 |
| SkillGuard 2606.03024v2 | Threat models, design principles | Permission-bearing Skills, context/action governance | Updated title and 1,260-Skill evaluation; implementation not recovered |
| IntentCap 2609.14631v1 | §1–3 | Source-specific capability fields and monotonic narrowing | Checker/replay evidence, not full end-to-end agent ASR replication |
| Semia 2605.00314v1 | §3.3–4.1 | Representation synthesis, structural risk | Documented gate is not runtime enforcement proof |
| SCR-Bench 2606.15242v1 | Abstract, benchmark overview | Composition requires path/state observations | Our study is single-bundle, not its multi-Skill setting |
| SEFZ 2605.13044v1 | Threat model, overview, oracle limitations | Benign-input specification violations | Its Skill specification authority differs from current-user authority here |
| VIGIL 2606.26524v1 | §3.3–4.2 | Finite trace policy checking and value flow | Trusted collector cannot observe opaque non-tool effects |
| Aletheia 2609.39678v1 | §1–2 | Independent tests and permission-dispensability witnesses | No globally minimal permission claim |
| AgentDojo 2406.13352v3 | §3.1, §4, limitations | Stateful tools; separate utility and security | Authored fixtures here lack its manual quality review |
| ASB 2410.02644v4 | §3–4, setup | Broader agent attack taxonomy | No numerical comparison across incompatible tasks |
| Progent 2504.11703v3 | Current abstract, downloaded paper | Task-derived symbolic policy, deterministic mediation and controlled updates | Directly narrows novelty claim; not a reproduced baseline |
| CaMeL 2503.18813v2 | Current abstract, downloaded paper | Trusted control/data separation and capabilities | Our closed handle taint is not its complete architecture |

Additional PDFs acquired by primary agent after the resource subagent completed:

- Progent: https://arxiv.org/pdf/2504.11703v3 — SHA256 6b96e0a25ddd5df8aafc368e8f8f3798bf911caf40db23945617cc5d1f2f36f26
- CaMeL: https://arxiv.org/pdf/2503.18813v2 — SHA256 c3719f6ce73eecf45e3764debef8a3d8ff8c9233b37d128c558b694ec3790cc7

No claims of publication venue are inferred from an arXiv identifier. This paper cites the inspected preprint versions explicitly. Original authors retain rights; downloaded PDFs are not included in the public-ready package.
