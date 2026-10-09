# Publish to a personal GitHub repository
The connected account was verified as `karansoni15-create`. At build time the connector exposed only Hardhat team repositories; no suitable personal repository was available. No team repository was modified.

Create a repository named `assureledger-grc` under your personal account and make it accessible to the GitHub connection in ChatGPT. A private repository is a reasonable default while reviewing the portfolio. Then share its exact URL so this prepared project can be pushed and CI verified. Never paste a GitHub token into chat.

For local publication with Git already authenticated, run from the extracted project folder (replace the remote only if your repository URL differs):

```sh
git init -b main
git add .
git commit -m "Build AssureLedger GRC portfolio MVP"
git remote add origin https://github.com/karansoni15-create/assureledger-grc.git
git push -u origin main
```

Use an empty remote for these commands. If it already contains files, fetch and inspect before combining history; do not force-push. Check the Actions tab after publication. The included workflow is prepared but has not run on GitHub yet.
