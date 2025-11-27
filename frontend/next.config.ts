/** @type {import('next').NextConfig} */

const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  transpilePackages: ["clsx", "tailwind-merge"],
  typescript: {
    ignoreBuildErrors: true,
  }
};

module.exports = nextConfig;
