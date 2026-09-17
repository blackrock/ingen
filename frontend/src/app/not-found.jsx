import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="placeholder">
      <p>Page not found.</p>
      <Link href="/">Back to editor</Link>
    </div>
  );
}
