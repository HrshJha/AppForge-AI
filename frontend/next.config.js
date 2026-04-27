/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  // Increase proxy timeout for long-running pipeline requests
  experimental: {
    proxyTimeout: 120000, // 2 minutes
  },
};

module.exports = nextConfig;
