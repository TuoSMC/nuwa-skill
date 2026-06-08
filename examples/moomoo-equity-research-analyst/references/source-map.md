# Source And Lens Map

Use this file to keep the skill source-aware without copying whole external repositories into context.

## Primary Operating Stack

| Layer | Use For | Notes |
|---|---|---|
| moomoo API | Structured financials, cash flow, ratios, price, options, market data | Primary data layer. Inspect local wrappers before assuming endpoint names. |
| SEC / IR / earnings calls | Audited numbers, business description, risks, segments, management commentary | Primary source for material facts and filing citations. |
| agent-reach | Web, GitHub, news, social, video, RSS discovery | Search and reading layer; use social as weak evidence unless confirmed. |
| cc-equity-research | Business-model, supply-chain, forensics, reporting-quality, management lenses | Main methodology library. Its data connector is optional; use our moomoo data instead. |
| anthropics/financial-services | 3-statement, DCF, comps, competitive analysis, equity-research workflow standards | Upstream modeling and institutional output standard. |

## GitHub References Evaluated

- `prof-little-bear/cc-equity-research`: best fit as the main equity-research lens library. Especially useful for `business-model`, `supply-chain`, `financial-forensics`, `reporting-quality`, `management`, and Anthropic vendored equity-research workflows.
- `anthropics/financial-services`: official upstream standard. Useful for `equity-research` skills and `financial-analysis` skills such as `3-statement-model`, `dcf-model`, `comps-analysis`, and `competitive-analysis`.
- `cooragent/ClarityFinance`: useful inspiration for multi-agent planning, but heavier than needed as the primary skill.
- `EodHistoricalData/eodhd-claude-skills`: useful data-plugin pattern, but not primary because moomoo is our data layer.
- `QYQSDTC/Financial_Analysis_Agent_Skill`: useful for basic statement-ratio/杜邦 thinking, but too narrow as the main skill.

## Lens Selection

| User Intent | First Lens | Supporting Lens |
|---|---|---|
| "How does this company make money?" | business model | competitive analysis, segment economics |
| "Who benefits upstream/downstream?" | supply chain | value-chain map, customer concentration |
| "Are the earnings clean?" | financial forensics | reporting quality, cash conversion |
| "Is management changing the story?" | management | earnings scorecard, reporting quality |
| "What should we watch next quarter?" | thesis tracker | catalyst calendar, options/event signal |
| "Build valuation/model" | 3-statement / DCF / comps | business model and financial quality first |

## Evidence Rules

- A number needs a source.
- A relationship needs direction and confidence.
- A thesis needs a breaker test.
- A market signal is not a fundamental conclusion.
- A search result is discovery until confirmed by a primary or directly relevant source.

