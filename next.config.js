/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Serve static files from temp/output directory
  async rewrites() {
    return [
      {
        source: '/temp/output/:path*',
        destination: '/temp/output/:path*'
      },
      {
        source: '/api/files/uploads/:path*',
        destination: '/api/files/uploads/:path*',
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
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
        port: '',
        pathname: '/processors-bucket.masterpiecex.com/**',
      },
    ],
    domains: [
      'storage.googleapis.com',
      process.env.NEXT_PUBLIC_VERCEL_URL || 'localhost',
    ],
  },
};

module.exports = nextConfig; 