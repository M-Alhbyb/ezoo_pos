/** @type {import('next').NextConfig} */
const isExport = process.env.NEXT_OUTPUT === "export";

const nextConfig = {
  ...(isExport
    ? {
        output: "export",
        trailingSlash: true,
        images: { unoptimized: true },
      }
    : {
        async rewrites() {
          return [
            {
              source: "/api/:path*",
              destination: `http://127.0.0.1:${process.env.DEV_API_PORT ?? 8001}/api/:path*`,
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
      }),
};

export default nextConfig;