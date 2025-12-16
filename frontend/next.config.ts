import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,

  /* Docker Configuration */
  output: "standalone",
};

export default nextConfig;
