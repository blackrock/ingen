'use client';

//  InGen Studio — config workspace layout (segment: /configs/[configId])
//
//  Composes the providers (catalog + the config document) around the WorkspaceLayout. Every nested
//  route renders into WorkspaceLayout's content slot and shares this config context. This is the
//  Next App Router equivalent of the old <ConfigWorkspace> react-router element.

import { useParams } from 'next/navigation';

import { CatalogProvider } from '../../../state/CatalogContext.jsx';
import { ConfigProvider } from '../../../state/ConfigContext.jsx';
import WorkspaceLayout from '../../../components/layout/WorkspaceLayout.jsx';

export default function ConfigLayout({ children }) {
  const { configId } = useParams();
  return (
    <CatalogProvider>
      {/* key={configId} remounts the document store on config switch — clean load state per id. */}
      <ConfigProvider key={configId} configId={configId}>
        <WorkspaceLayout configId={configId}>{children}</WorkspaceLayout>
      </ConfigProvider>
    </CatalogProvider>
  );
}
