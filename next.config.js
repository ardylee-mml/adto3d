/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Serve static files from temp/output directory
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3001/api/:path*'  // Keep API route
      },
      {
        source: '/temp/output/:filename*',
        destination: '/api/files/:filename*'  // File serving route
      }
    ];
  },
  // Configure headers for GLB files
  async headers() {
    return [
      {
        source: '/temp/output/:filename*',
        headers: [
          {
            key: 'Content-Type',
            value: 'model/gltf-binary'
          }
        ],
      }
    ];
  },
  // Remove webpack configuration temporarily
  webpack: (config) => {
    return config;
  }
};

module.exports = nextConfig; 