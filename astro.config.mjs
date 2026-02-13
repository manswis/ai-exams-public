import { defineConfig } from "astro/config";

const repo = process.env.GITHUB_REPOSITORY?.split("/")[1];
const owner = process.env.GITHUB_REPOSITORY?.split("/")[0];
const base = repo ? `/${repo}/` : "/";
const site = repo && owner ? `https://${owner}.github.io/${repo}/` : undefined;

export default defineConfig({
  site,
  base
});
