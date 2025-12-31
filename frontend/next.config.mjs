/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable Turbopack to avoid route caching issues
  experimental: {
    turbo: false,
  },
  // Explicitly set port (though package.json script also sets it)
  // This ensures consistency
};

export default nextConfig;
