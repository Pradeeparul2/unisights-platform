import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/unisights.ts"],
  format: ["esm"],
  outDir: "dist",
  minify: true,
  bundle: true,
  clean: true,
  dts: true,
  sourcemap: false,
  noExternal: ["web-vitals"],

  esbuildOptions(options) {
    options.loader = {
      ".wasm": "binary",
    };
  },

  outExtension() {
    return {
      js: ".min.js",
    };
  },
});
