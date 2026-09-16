'use client';

//  useSourceActions — the "what should happen to this source?" dialog behaviour.
//
//  When a source is picked from the registry the user is asked whether to start a NEW interface
//  from it or MERGE it into the current one. Three surfaces offer that choice (the sources tab,
//  the graph canvas and the nav rail), so the state and both handlers live here rather than being
//  copied into each.

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useConfig } from '../state/ConfigContext.jsx';
import { upsertInterface, createEmptyInterface } from '../models/configModel.js';

/**
 * @param {string} interfaceName  interface the merge action applies to
 * @param {{ onMerged?: () => void }} [opts]  onMerged fires after a successful merge (e.g. so the
 *        graph can recompute its layout)
 */
export function useSourceActions(interfaceName, { onMerged } = {}) {
  const { model, updateModel, updateInterface } = useConfig();
  const router = useRouter();
  const { configId } = useParams() || {};
  const [pendingSourceAction, setPendingSourceAction] = useState(null); // { sid } | null

  const handleNewInterface = () => {
    if (!pendingSourceAction) return;
    const { sid } = pendingSourceAction;
    const newName = `${sid}_pipeline`;
    const finalName = model.interfacesByName[newName] ? `${newName}_${Date.now()}` : newName;
    updateModel((m) =>
      upsertInterface(m, finalName, { ...createEmptyInterface(), sources: [sid] }),
    );
    setPendingSourceAction(null);
    if (configId) {
      router.push(`/configs/${configId}/interfaces/${encodeURIComponent(finalName)}`);
    }
  };

  const handleMergeSource = () => {
    if (!pendingSourceAction) return;
    const { sid } = pendingSourceAction;
    updateInterface(interfaceName, (it) => {
      const cur = it.sources ?? [];
      return {
        ...it,
        sources: cur.includes(sid) ? cur : [...cur, sid],
        pre_processing: [
          ...(it.pre_processing ?? []),
          { type: 'merge', source: sid, merge_type: 'inner', left_key: '', right_key: '' },
        ],
      };
    });
    onMerged?.();
    setPendingSourceAction(null);
  };

  return { pendingSourceAction, setPendingSourceAction, handleNewInterface, handleMergeSource };
}
