/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    async rewrites() {
      return [
        {
          source: "/api/:path*",
          destination:
            process.env.NODE_ENV === "development"
              ? "http://127.0.0.1:8000/api/:path*" // local dev fallback
              : "/api/:path*", // deployed fallback
        },
      ];
    },
  };
  
module.exports = nextConfig;
