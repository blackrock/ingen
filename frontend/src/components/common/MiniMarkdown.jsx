//  MiniMarkdown — zero-dependency inline markdown renderer for chat bubbles.
//  Supports: **bold**, `code`, [link](url), bullet lists (- / *), numbered lists, and
//  paragraphs separated by blank lines. Intentionally minimal — text is never interpreted as
//  HTML, and link targets are restricted to http/https/mailto (see safeHref).

//  Link hrefs come from assistant-generated replies, so they are untrusted input: a
//  `javascript:` or `data:` URL would otherwise execute on click. Anything not on the allowlist
//  renders as plain text instead of a link.
function safeHref(url) {
  try {
    const { protocol } = new URL(url, 'https://example.invalid');
    return ['http:', 'https:', 'mailto:'].includes(protocol) ? url : null;
  } catch {
    return null;
  }
}

/** Render inline spans: `code`, **bold**, *italic*, [text](url). */
function renderInline(text) {
  // Split on backtick code spans, bold (**), and links.
  const parts = [];
  const re = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[([^\]]+)\]\(([^)]+)\))/g;
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    const token = m[0];
    if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(<code key={m.index} className="mm-code">{token.slice(1, -1)}</code>);
    } else if (token.startsWith('**')) {
      parts.push(<strong key={m.index}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith('*')) {
      parts.push(<em key={m.index}>{token.slice(1, -1)}</em>);
    } else {
      // link — unsafe schemes degrade to the link text, never an anchor
      const href = safeHref(m[3]);
      parts.push(href
        ? <a key={m.index} href={href} target="_blank" rel="noopener noreferrer" className="mm-link">{m[2]}</a>
        : <span key={m.index}>{m[2]}</span>);
    }
    last = m.index + token.length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

/** Parse a block of text into structured nodes. */
function parse(md) {
  const lines = md.split('\n');
  const blocks = [];
  let listType = null; // 'ul' | 'ol' | null
  let listItems = [];

  const flushList = () => {
    if (listItems.length) {
      blocks.push({ type: listType, items: listItems });
      listItems = [];
      listType = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const ulMatch = line.match(/^[-*]\s+(.*)/);
    const olMatch = line.match(/^\d+\.\s+(.*)/);
    const h3Match = line.match(/^###\s+(.*)/);
    const h2Match = line.match(/^##\s+(.*)/);
    const h1Match = line.match(/^#\s+(.*)/);
    const hrMatch = line.match(/^---+$/);

    if (ulMatch) {
      if (listType === 'ol') flushList();
      listType = 'ul';
      listItems.push(ulMatch[1]);
    } else if (olMatch) {
      if (listType === 'ul') flushList();
      listType = 'ol';
      listItems.push(olMatch[1]);
    } else {
      flushList();
      if (h3Match) blocks.push({ type: 'h3', text: h3Match[1] });
      else if (h2Match) blocks.push({ type: 'h2', text: h2Match[1] });
      else if (h1Match) blocks.push({ type: 'h1', text: h1Match[1] });
      else if (hrMatch) blocks.push({ type: 'hr' });
      else if (line.trim() === '') blocks.push({ type: 'br' });
      else blocks.push({ type: 'p', text: line });
    }
  }
  flushList();
  return blocks;
}

export default function MiniMarkdown({ text, className }) {
  if (!text) return null;
  const blocks = parse(text);

  return (
    <div className={`mm${className ? ` ${className}` : ''}`}>
      {blocks.map((b, i) => {
        switch (b.type) {
          case 'h1': return <h1 key={i} className="mm-h1">{renderInline(b.text)}</h1>;
          case 'h2': return <h2 key={i} className="mm-h2">{renderInline(b.text)}</h2>;
          case 'h3': return <h3 key={i} className="mm-h3">{renderInline(b.text)}</h3>;
          case 'hr': return <hr key={i} className="mm-hr" />;
          case 'br': return <div key={i} className="mm-gap" />;
          case 'ul': return (
            <ul key={i} className="mm-ul">
              {b.items.map((it, j) => <li key={j}>{renderInline(it)}</li>)}
            </ul>
          );
          case 'ol': return (
            <ol key={i} className="mm-ol">
              {b.items.map((it, j) => <li key={j}>{renderInline(it)}</li>)}
            </ol>
          );
          case 'p':
          default:
            return <p key={i} className="mm-p">{renderInline(b.text)}</p>;
        }
      })}
    </div>
  );
}
