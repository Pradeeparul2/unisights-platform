import * as esbuild from "esbuild";
import * as dotenv from "dotenv";
import { execSync } from "child_process";

dotenv.config();

// Generate type declarations
execSync("tsc --emitDeclarationOnly --declaration --outDir dist", {
  stdio: "inherit",
});

esbuild
  .build({
    entryPoints: ["src/unisights.ts"],
    bundle: true,
    minify: true,
    format: "esm",
    outfile: "dist/unisights.min.js",
    loader: { ".wasm": "binary" },
  })
  .catch(() => process.exit(1));
