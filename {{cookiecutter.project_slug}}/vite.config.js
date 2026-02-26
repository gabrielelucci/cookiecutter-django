import path from "node:path";

const rootDir = path.resolve(import.meta.dirname);
const staticDir = path.resolve(rootDir, "static");
const isProd = process.env.NODE_ENV === "production";

export default {
	base: "/static/dist/",
	root: staticDir,
	server: {
		host: "0.0.0.0",
		port: 5173,
		strictPort: true,
		origin: "http://localhost:5173",
		cors: true,
	},
	appType: "custom",
	build: {
		rollupOptions: {
			preserveEntrySignatures: "allow-extension",
			input: {
				main: path.resolve(staticDir, "js/main.js"),
			},
			output: {
				dir: path.resolve(staticDir, "dist"),
				entryFileNames: isProd ? "[name]-[hash].js" : "[name].js",
				chunkFileNames: isProd ? "chunks/[name]-[hash].js" : "chunks/[name].js",
				assetFileNames: isProd
					? "assets/[name]-[hash][extname]"
					: "assets/[name][extname]",
			},
		},
		sourcemap: true,
		manifest: "manifest.json",
		minify: "esbuild",
	},
	css: {
		devSourcemap: true,
		preprocessorOptions: {
			scss: {
				silenceDeprecations: [
					"color-functions",
					"global-builtin",
					"import",
					"legacy-js-api",
				],
			},
		},
	},
};
