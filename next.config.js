/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  api: {
    bodyParser: false,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://40.81.21.27:3000/api/:path*'  // Replace YOUR_VM_IP with your VM's public IP
      },
      {
        source: '/output/:path*',
        destination: '/temp/output/:path*'
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