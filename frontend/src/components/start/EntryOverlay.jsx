//  EntryOverlay — after a source is described, choose how to build: inFlow (visual board) or
//  inChat (assistant). Non-binding — both edit the same config and you can switch anytime.

import { GitBranch, MessageSquare } from 'lucide-react';

export default function EntryOverlay({ onChoose, onBack }) {
  return (
    <div className="entry">
      <div className="entry__head">
        <h2 className="entry__title">How do you want to build it?</h2>
        <p className="entry__sub">Both edit the same pipeline — switch anytime from the top bar.</p>
      </div>
      <div className="entry__choices">
        <button type="button" className="entrychoice entrychoice--flow" onClick={() => onChoose('graph')}>
          <span className="entrychoice__icon"><GitBranch size={26} /></span>
          <span className="entrychoice__name">inFlow</span>
          <span className="entrychoice__desc">Drag sources and transforms on a visual board. See the whole pipeline at a glance.</span>
        </button>
        <button type="button" className="entrychoice entrychoice--chat" onClick={() => onChoose('chat')}>
          <span className="entrychoice__icon"><MessageSquare size={26} /></span>
          <span className="entrychoice__name">inChat</span>
          <span className="entrychoice__desc">Describe what you want in plain language. The assistant wires it up for you.</span>
        </button>
      </div>
      {onBack && <button type="button" className="btn btn--ghost entry__back" onClick={onBack}>← Back to source</button>}
    </div>
  );
}
