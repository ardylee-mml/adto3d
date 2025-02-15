/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3000/api/:path*'
      }
    ]
  },
  webpack: (config, { dev, isServer }) => {
    config.module.rules.push({
      test: /\.(glb|gltf)$/,
      type: 'asset/resource',
    });

    if (dev && !isServer) {
      config.optimization.moduleIds = 'named';
      config.optimization.chunkIds = 'named';
    }

    return config;
  },
  async headers() {
    return [
      {
        source: '/output/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
}

module.exports = nextConfig; 