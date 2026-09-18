/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const api = process.env.BACKEND_URL || "http://localhost:8000";
    return [
      { source: "/api/:path*", destination: `${api}/api/:path*` },
      { source: "/media/:path*", destination: `${api}/media/:path*` },
    ];
  },
};

export default nextConfig;
