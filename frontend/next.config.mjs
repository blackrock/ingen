/** @type {import('next').NextConfig} */
const nextConfig = {
  // Mirrors the StrictMode wrapper the Vite entry used to apply.
  reactStrictMode: true,
  eslint: {
    // Keep build and lint separate, as they were under Vite (`vite build` never ran ESLint —
    // `npm run lint` is the dedicated gate). Avoids coupling the production build to pre-existing
    // lint debt in the source tree.
    ignoreDuringBuilds: true,
  },
  // Proxy /api/* to the FastAPI backend so the browser never makes a cross-origin request.
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  // Allow the Windsurf/Cascade browser preview proxy origin.
  allowedDevOrigins: ['127.0.0.1'],
};

export default nextConfig;
