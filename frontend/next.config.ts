import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    // Disable ESLint during production builds (Docker)
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable type checking during production builds (Docker)
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
