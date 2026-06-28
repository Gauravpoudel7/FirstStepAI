# Graph Report - web\src  (2026-06-26)

## Corpus Check
- 41 files · ~11,814 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 154 nodes · 429 edges · 12 communities (10 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a6896645`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 11|Community 11]]

## God Nodes (most connected - your core abstractions)
1. `useAuthStore` - 25 edges
2. `cn()` - 23 edges
3. `api` - 15 edges
4. `CardContent()` - 14 edges
5. `Card` - 13 edges
6. `CardHeader()` - 13 edges
7. `CardTitle()` - 13 edges
8. `CardDescription()` - 13 edges
9. `Button` - 12 edges
10. `Input` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Badge()` --calls--> `cn()`  [EXTRACTED]
  components/ui/badge.tsx → lib/utils.ts
- `RoleBadge()` --calls--> `cn()`  [EXTRACTED]
  components/layout/RoleBadge.tsx → lib/utils.ts
- `CardHeader()` --calls--> `cn()`  [EXTRACTED]
  components/ui/card.tsx → lib/utils.ts
- `CardTitle()` --calls--> `cn()`  [EXTRACTED]
  components/ui/card.tsx → lib/utils.ts
- `CardDescription()` --calls--> `cn()`  [EXTRACTED]
  components/ui/card.tsx → lib/utils.ts

## Import Cycles
- None detected.

## Communities (12 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (17): ChatMessage, ChatPage(), Role, SUGGESTIONS, DashboardPage(), ChatStreamSource, ChatStreamState, useChatStream() (+9 more)

### Community 1 - "Community 1"
Cohesion: 0.19
Nodes (16): LoginPage(), useLogin(), useLogout(), useMe(), useMounted(), useTheme(), ITEMS, NavItem (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.26
Nodes (10): ROLES, api, pendingQueue, DocumentOut, LANGS, Button, ButtonProps, buttonVariants (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (15): cn(), STATUS_COLORS, CardFooter(), Dialog(), DialogContent(), DialogContentProps, DialogDescription(), DialogDescriptionProps (+7 more)

### Community 4 - "Community 4"
Cohesion: 0.33
Nodes (9): ACTION_COLORS, ROLE_LABEL, TYPE_LABEL, Props, Card, CardContent(), CardDescription(), CardHeader() (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (11): AdminPage(), AnalyticsPage(), App(), DocumentsPage(), ChatHistoryPage(), KnowledgeBasePage(), AppShell(), queryClient (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (12): ActivityLogEntry, ActivityLogSummary, AdminUserOut, BrandingOut, ConversationOut, DashboardSummaryOut, DemoAccountRow, MessageOut (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.29
Nodes (4): Toast, ToastContext, ToastContextValue, ToastVariant

### Community 8 - "Community 8"
Cohesion: 0.40
Nodes (4): ChatMessage, ChatState, Conversation, useChatStore

## Knowledge Gaps
- **47 isolated node(s):** `Props`, `RoleBadgeProps`, `COLOR`, `NavItem`, `ITEMS` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `useAuthStore` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `cn()` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 4`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `CardContent()` connect `Community 4` to `Community 0`, `Community 2`, `Community 3`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `Props`, `RoleBadgeProps`, `COLOR` to the rest of the system?**
  _47 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09359605911330049 - nodes in this community are weakly interconnected._