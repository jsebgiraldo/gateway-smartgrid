# Releases — Gateway SmartGrid

Each row pins every component to an exact commit for that release. Use these
SHAs to reproduce a build end-to-end (`git submodule update --init` at the
matching umbrella tag will check out the listed SHAs).

| Release | Date | firmware-ami-lwm2m | openwrt-morse | flash-tool | mcp-openwrt-ssh |
|---------|------|--------------------|---------------|------------|-----------------|
| _unreleased_ | — | `master` HEAD | `2.9-dev` HEAD | `main` HEAD | `main` HEAD |

## Cutting a release

1. Update each submodule to the desired commit:
   `git -C repos/<name> fetch && git -C repos/<name> checkout <sha>`
2. Commit the umbrella: `git add repos/ && git commit -m "release: gateway vX.Y.Z"`
3. Tag and push: `git tag gateway-vX.Y.Z && git push --tags`
4. Add a row to the table above with the four SHAs.
