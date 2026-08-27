import assert from "node:assert/strict";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";
import { ContentRenderer } from "../src/components/content/ContentRenderer";

const fixture = `# H1

## H2

### H3

**bold** and \`inline code\`

- unordered

1. ordered

\`\`\`python
x = 10
print(x)
\`\`\`

> quoted text

| A | B |
| - | - |
| 1 | 2 |

<script>alert("xss")</script>`;

test("ContentRenderer renders Markdown structure and never renders raw HTML", () => {
  const html = renderToStaticMarkup(<ContentRenderer content={fixture} />);

  assert.match(html, /<h1[^>]*>H1<\/h1>/);
  assert.match(html, /<strong>bold<\/strong>/);
  assert.match(html, /<pre[^>]*>/);
  assert.match(html, /language-python/);
  assert.match(html, /print/);
  assert.match(html, /<blockquote[^>]*>/);
  assert.match(html, /<table[^>]*>/);
  assert.doesNotMatch(html, /<script>/);
  assert.doesNotMatch(html, /```/);
});
