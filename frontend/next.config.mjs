/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8001/api/:path*",
      },
    ];
  },
  async redirects() {
    return [
      {
        source: "/partners/assignment",
        destination: "/partners/assignments",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;