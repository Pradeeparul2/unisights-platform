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
    loader: {
      ".wasm": "file",
    },
    define: {
      "process.env.INSIGHTS_ENDPOINT": JSON.stringify(
        process.env.INSIGHTS_ENDPOINT,
      ),
      "process.env.INSIGHTS_SECRET": JSON.stringify(
        process.env.INSIGHTS_SECRET,
      ),
      "process.env.INSIGHTS_SALT": JSON.stringify(process.env.INSIGHTS_SALT),
      "process.env.INSIGHTS_DEBUG": JSON.stringify(process.env.INSIGHTS_DEBUG),
    },
  })
  .catch(() => process.exit(1));
