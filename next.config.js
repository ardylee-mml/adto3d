/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Serve static files from temp/output directory
  async rewrites() {
    return [
      {
        source: '/temp/output/:path*',
        destination: '/temp/output/:path*'
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
  },
};

module.exports = nextConfig; 