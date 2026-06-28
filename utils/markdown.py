"""Code block highlighting helper — wraps fenced blocks for CSS styling.

We deliberately avoid server-side Pygments to keep deployment simple; CSS
token colors give a respectable look for Python / JS / Bash / JSON / YAML.
"""
from __future__ import annotations

import re
import html as _html

FENCE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)


def highlight_code_blocks(text: str) -> str:
    """Escape HTML and wrap fenced code blocks in <pre><code> for CSS styling."""
    escaped = _html.escape(text)
    # The fence language tags are preserved in a data-lang attr for CSS hooks.
    def _wrap(m: re.Match) -> str:
        lang = m.group(1) or "text"
        body = m.group(2)
        return f'<pre class="code-block" data-lang="{lang}"><code class="language-{lang}">{body}</code></pre>'

    return FENCE_RE.sub(_wrap, escaped)
