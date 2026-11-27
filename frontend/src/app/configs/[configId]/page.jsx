'use client';

//  Workspace index. New flow: if the first interface has no sources yet, show the source-first
//  Start screen (pick a source → choose inFlow/inChat). Once it has a source, redirect into the
//  interface editor so reloads land where you left off.

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

import { useConfig } from '../../../state/ConfigContext.jsx';
import Start from '../../../components/start/Start.jsx';

export default function ConfigIndex() {
  const { configId } = useParams();
  const router = useRouter();
  const { model, status } = useConfig();

  const first = model?.interfaceOrder?.[0];
  const firstHasSources = first && (model.interfacesByName[first]?.sources?.length ?? 0) > 0;

  useEffect(() => {
    if (firstHasSources) router.replace(`/configs/${configId}/interfaces/${first}`);
  }, [configId, first, firstHasSources, router]);

  if (status === 'loading' || !model) return <div className="placeholder">Loading config…</div>;
  if (firstHasSources) return <div className="placeholder">Opening editor…</div>;
  return <Start configId={configId} />;
}
