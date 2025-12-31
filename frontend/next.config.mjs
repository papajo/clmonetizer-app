/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable Turbopack to avoid route caching issues
  experimental: {
    turbo: false,
  },
};

export default nextConfig;
