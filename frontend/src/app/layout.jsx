//  InGen Studio — root layout
//
//  Server component that owns the document shell. Global styles (which also pull in the Inter
//  webfont via @import) are imported here. BootGate seeds localStorage on the client; AppShell is
//  the persistent brand-bar frame that used to be the top-level react-router layout route.

import '../index.css';
import BootGate from './BootGate.jsx';
import AppShell from '../components/layout/AppShell.jsx';

export const metadata = {
  title: 'InGen Data Transformation',
  description: 'YAML interface authoring for the InGen data transformation pipeline.',
  icons: { icon: '/favicon.svg' },
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <BootGate>
          <AppShell>{children}</AppShell>
        </BootGate>
      </body>
    </html>
  );
}
