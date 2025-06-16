#  (2025-06-16)


### Bug Fixes

* 🧹 resolve flake8 and mypy issues ([e01b3cd](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e01b3cd5f509bb072833f2bde7cbed59e205d33a))
* 🩹 consolidate task cancellation ([3f1e15e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/3f1e15e5f50c74b485016b9cd84cb7608a44bb52))
* **changelog:** 📝 restore full history ([1762a0e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/1762a0e5d9e9dd5032955daf829b6aa82d6c4903))
* **changelog:** 📝 restore full history ([956b290](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/956b2903f9ea73e37366a6428b67cd1a7d2daa1b))
* **changelog:** 🛠️ append new release notes ([e989861](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e9898613b9519002906bdf1236ec3a3302da1321))
* **deps:** 🔧 Fix MCP compatibility and enhance dependency management ([2fdd40c](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/2fdd40c9d2ee2b3b1d9ce6b597cb480deffcf4c8))
* **docsets:** 🐛 Fix Dash docset discovery and database schema handling ([7fbb1ea](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7fbb1ea561991d74e2c707adfed90153a2152524))
* **scripts:** 🛠️ Resolve script stalling issues in Codex environments ([0a97842](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/0a9784220eae11d4176896228bc99c8feb8da8f1))
* **search:** 🐛 cast limit param to int ([e70b568](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e70b568f98e4420f8569ed58768c6a12441b2c87))
* **search:** 🛡️ validate limit inputs\n\nAdd tests for invalid limit values and document the behavior. ([530de36](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/530de36cb74dff32b05ca8bf4c8247f55c33f8a5))
* **server:** 🐛 run using StdioClient ([93aaff0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/93aaff05ff784c468d0adcf4aced73c09625aa28))
* **server:** 🚮 re-raise KeyboardInterrupt ([91c26b2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/91c26b2c67dfb278dfe5a912409b2ba0aa8773ef))
* **server:** 🛑 handle KeyboardInterrupt cleanly ([5ba6459](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/5ba6459dadee3e36e58f66f547c03b5cf13aa22d))
* **startup:** 🐛 create initialization options ([e9cb087](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e9cb08758c4a50fa6be24403aebce8cebb2c84dc))
* **symlink:** 🛠️ improve docset symlink handling ([da23af6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/da23af6a509eb331f11d5a11e9611ca279c8c7b0))
* **tests:** ✅ make stdio_server check robust ([48dd505](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/48dd505d794f58ebb0dd5246c931c0190302562a))


### Features

* 🎉 automate changelog ([b661b06](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/b661b063d2d3b162d17ddfd5766c527e1778b688))
* 📝 bump to 1.1.3 and update docs ([7ffc5ac](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7ffc5ac5b3750f0a0f9c6ee38c580e98f960f06f))
* 🛠️ use stdio_server for server I/O\n\n* replace removed StdioClient import\n* adjust main execution flow\n* bump version to 1.1.2 and update docs\n* update tests and changelog ([2efa38e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/2efa38e8b3378476431e494f12022ce02ba877ee))
* Allow nested docset directories ([43d44dd](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/43d44dd93ccf653bcfb7f887af1173886a0a72de))
* **ci:** 🎉 add release workflow and changelog links ([957aa45](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/957aa45a6ed03952249ad7e11475858df26cdbc0))
* **docsets:** 🗂️ support nested docset folders ([55417e0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/55417e0a97811003c9be17044610e48b38598c54))
* **docsets:** 🧭 auto-adjust docset path ([f37a2b8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f37a2b8419316d966519a2817229c7e531815425))
* **docsets:** 🚀 Expand docset discovery to entire Dash directory tree ([7f7c4df](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7f7c4dff3c85e73a5adedd6229deba108a8e3b36))
* **enhanced-dash-mcp:** 🚀 Complete MCP server implementation with Warp integration ([4755ac8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/4755ac817b84fb566e9871d4965faf96e5e6b7b0))
* Initial commit ([f4bfea4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f4bfea4dcff04ec063a2abd5ab1c82df803c6b8f))
* **logging:** ✨ log docset path and document symlink support ([fb5ac07](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/fb5ac07ad01868a69bfd7454ca6517bc857c038d))
* **logging:** 🎉 add startup logging ([f072579](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f072579b89d6d0466d0c130315a6b0ae08415164))
* **logging:** 🎉 add structured logging ([248d36f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/248d36f75f150557d7a025feb969d080bb422d0f))
* **logging:** 📝 improve server event logging ([8849a8f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/8849a8f966aa0ce5113d939bff45b17d9b99d2d2))
* **server:** ✨ handle cancellation without hang ([48f5ec6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/48f5ec62ece95fd8625bbeee28e688e696ce6d4e))
* **server:** 🛑 unify cancellation handling ([b1d9693](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/b1d96934a14c25059dac61fc72febd5bf33423c9))
* **server:** 🛠️ ensure Server.run receives streams ([a993850](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/a993850b6a707ce3500337850a95aae4e0a7a5c1))
* **structure:** 📁 reorganize project files ([4bc2243](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/4bc2243269c5ab335e3b5585580b687cd4620e55))



#  (2025-06-16)


### Bug Fixes

* 🧹 resolve flake8 and mypy issues ([e01b3cd](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e01b3cd5f509bb072833f2bde7cbed59e205d33a))
* 🩹 consolidate task cancellation ([3f1e15e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/3f1e15e5f50c74b485016b9cd84cb7608a44bb52))
* **changelog:** 📝 restore full history ([1762a0e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/1762a0e5d9e9dd5032955daf829b6aa82d6c4903))
* **changelog:** 📝 restore full history ([956b290](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/956b2903f9ea73e37366a6428b67cd1a7d2daa1b))
* **changelog:** 🛠️ append new release notes ([e989861](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e9898613b9519002906bdf1236ec3a3302da1321))
* **deps:** 🔧 Fix MCP compatibility and enhance dependency management ([2fdd40c](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/2fdd40c9d2ee2b3b1d9ce6b597cb480deffcf4c8))
* **docsets:** 🐛 Fix Dash docset discovery and database schema handling ([7fbb1ea](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7fbb1ea561991d74e2c707adfed90153a2152524))
* **scripts:** 🛠️ Resolve script stalling issues in Codex environments ([0a97842](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/0a9784220eae11d4176896228bc99c8feb8da8f1))
* **search:** 🐛 cast limit param to int ([e70b568](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e70b568f98e4420f8569ed58768c6a12441b2c87))
* **search:** 🛡️ validate limit inputs\n\nAdd tests for invalid limit values and document the behavior. ([530de36](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/530de36cb74dff32b05ca8bf4c8247f55c33f8a5))
* **server:** 🐛 run using StdioClient ([93aaff0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/93aaff05ff784c468d0adcf4aced73c09625aa28))
* **server:** 🚮 re-raise KeyboardInterrupt ([91c26b2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/91c26b2c67dfb278dfe5a912409b2ba0aa8773ef))
* **server:** 🛑 handle KeyboardInterrupt cleanly ([5ba6459](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/5ba6459dadee3e36e58f66f547c03b5cf13aa22d))
* **startup:** 🐛 create initialization options ([e9cb087](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e9cb08758c4a50fa6be24403aebce8cebb2c84dc))
* **symlink:** 🛠️ improve docset symlink handling ([da23af6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/da23af6a509eb331f11d5a11e9611ca279c8c7b0))
* **tests:** ✅ make stdio_server check robust ([48dd505](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/48dd505d794f58ebb0dd5246c931c0190302562a))


### Features

* 🎉 automate changelog ([b661b06](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/b661b063d2d3b162d17ddfd5766c527e1778b688))
* 📝 bump to 1.1.3 and update docs ([7ffc5ac](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7ffc5ac5b3750f0a0f9c6ee38c580e98f960f06f))
* 🛠️ use stdio_server for server I/O\n\n* replace removed StdioClient import\n* adjust main execution flow\n* bump version to 1.1.2 and update docs\n* update tests and changelog ([2efa38e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/2efa38e8b3378476431e494f12022ce02ba877ee))
* Allow nested docset directories ([43d44dd](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/43d44dd93ccf653bcfb7f887af1173886a0a72de))
* **ci:** 🎉 add release workflow and changelog links ([957aa45](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/957aa45a6ed03952249ad7e11475858df26cdbc0))
* **docsets:** 🗂️ support nested docset folders ([55417e0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/55417e0a97811003c9be17044610e48b38598c54))
* **docsets:** 🧭 auto-adjust docset path ([f37a2b8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f37a2b8419316d966519a2817229c7e531815425))
* **enhanced-dash-mcp:** 🚀 Complete MCP server implementation with Warp integration ([4755ac8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/4755ac817b84fb566e9871d4965faf96e5e6b7b0))
* Initial commit ([f4bfea4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f4bfea4dcff04ec063a2abd5ab1c82df803c6b8f))
* **logging:** ✨ log docset path and document symlink support ([fb5ac07](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/fb5ac07ad01868a69bfd7454ca6517bc857c038d))
* **logging:** 🎉 add startup logging ([f072579](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f072579b89d6d0466d0c130315a6b0ae08415164))
* **logging:** 🎉 add structured logging ([248d36f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/248d36f75f150557d7a025feb969d080bb422d0f))
* **logging:** 📝 improve server event logging ([8849a8f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/8849a8f966aa0ce5113d939bff45b17d9b99d2d2))
* **server:** ✨ handle cancellation without hang ([48f5ec6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/48f5ec62ece95fd8625bbeee28e688e696ce6d4e))
* **server:** 🛑 unify cancellation handling ([b1d9693](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/b1d96934a14c25059dac61fc72febd5bf33423c9))
* **server:** 🛠️ ensure Server.run receives streams ([a993850](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/a993850b6a707ce3500337850a95aae4e0a7a5c1))
* **structure:** 📁 reorganize project files ([4bc2243](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/4bc2243269c5ab335e3b5585580b687cd4620e55))



#  (2025-06-11)


### Bug Fixes

* 🧹 resolve flake8 and mypy issues ([e01b3cd](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e01b3cd5f509bb072833f2bde7cbed59e205d33a))
* 🩹 consolidate task cancellation ([3f1e15e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/3f1e15e5f50c74b485016b9cd84cb7608a44bb52))
* **changelog:** 📝 restore full history ([1762a0e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/1762a0e5d9e9dd5032955daf829b6aa82d6c4903))
* **changelog:** 📝 restore full history ([956b290](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/956b2903f9ea73e37366a6428b67cd1a7d2daa1b))
* **changelog:** 🛠️ append new release notes ([e989861](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e9898613b9519002906bdf1236ec3a3302da1321))
* **deps:** 🔧 Fix MCP compatibility and enhance dependency management ([2fdd40c](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/2fdd40c9d2ee2b3b1d9ce6b597cb480deffcf4c8))
* **docsets:** 🐛 Fix Dash docset discovery and database schema handling ([7fbb1ea](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7fbb1ea561991d74e2c707adfed90153a2152524))
* **search:** 🐛 cast limit param to int ([e70b568](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e70b568f98e4420f8569ed58768c6a12441b2c87))
* **search:** 🛡️ validate limit inputs\n\nAdd tests for invalid limit values and document the behavior. ([530de36](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/530de36cb74dff32b05ca8bf4c8247f55c33f8a5))
* **server:** 🐛 run using StdioClient ([93aaff0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/93aaff05ff784c468d0adcf4aced73c09625aa28))
* **server:** 🚮 re-raise KeyboardInterrupt ([91c26b2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/91c26b2c67dfb278dfe5a912409b2ba0aa8773ef))
* **server:** 🛑 handle KeyboardInterrupt cleanly ([5ba6459](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/5ba6459dadee3e36e58f66f547c03b5cf13aa22d))
* **startup:** 🐛 create initialization options ([e9cb087](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e9cb08758c4a50fa6be24403aebce8cebb2c84dc))
* **symlink:** 🛠️ improve docset symlink handling ([da23af6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/da23af6a509eb331f11d5a11e9611ca279c8c7b0))
* **tests:** ✅ make stdio_server check robust ([48dd505](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/48dd505d794f58ebb0dd5246c931c0190302562a))


### Features

* 🎉 automate changelog ([b661b06](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/b661b063d2d3b162d17ddfd5766c527e1778b688))
* 📝 bump to 1.1.3 and update docs ([7ffc5ac](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7ffc5ac5b3750f0a0f9c6ee38c580e98f960f06f))
* 🛠️ use stdio_server for server I/O\n\n* replace removed StdioClient import\n* adjust main execution flow\n* bump version to 1.1.2 and update docs\n* update tests and changelog ([2efa38e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/2efa38e8b3378476431e494f12022ce02ba877ee))
* Allow nested docset directories ([43d44dd](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/43d44dd93ccf653bcfb7f887af1173886a0a72de))
* **ci:** 🎉 add release workflow and changelog links ([957aa45](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/957aa45a6ed03952249ad7e11475858df26cdbc0))
* **docsets:** 🗂️ support nested docset folders ([55417e0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/55417e0a97811003c9be17044610e48b38598c54))
* **docsets:** 🧭 auto-adjust docset path ([f37a2b8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f37a2b8419316d966519a2817229c7e531815425))
* **enhanced-dash-mcp:** 🚀 Complete MCP server implementation with Warp integration ([4755ac8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/4755ac817b84fb566e9871d4965faf96e5e6b7b0))
* Initial commit ([f4bfea4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f4bfea4dcff04ec063a2abd5ab1c82df803c6b8f))
* **logging:** ✨ log docset path and document symlink support ([fb5ac07](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/fb5ac07ad01868a69bfd7454ca6517bc857c038d))
* **logging:** 🎉 add startup logging ([f072579](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f072579b89d6d0466d0c130315a6b0ae08415164))
* **logging:** 🎉 add structured logging ([248d36f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/248d36f75f150557d7a025feb969d080bb422d0f))
* **logging:** 📝 improve server event logging ([8849a8f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/8849a8f966aa0ce5113d939bff45b17d9b99d2d2))
* **server:** ✨ handle cancellation without hang ([48f5ec6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/48f5ec62ece95fd8625bbeee28e688e696ce6d4e))
* **server:** 🛑 unify cancellation handling ([b1d9693](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/b1d96934a14c25059dac61fc72febd5bf33423c9))
* **server:** 🛠️ ensure Server.run receives streams ([a993850](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/a993850b6a707ce3500337850a95aae4e0a7a5c1))
* **structure:** 📁 reorganize project files ([4bc2243](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/4bc2243269c5ab335e3b5585580b687cd4620e55))



# Changelog
## [1.2.12](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.12) - 2025-06-11
- merge upstream changes with local docset fixes
- add comprehensive `.gitignore` and remove debug script
- improved project structure and documentation


## [1.2.11](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.11) - 2025-06-10
- feat: recursively search for `.docset` directories to support nested docsets

## [1.2.10](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.10) - 2025-06-10
- docs: clarify symlink placement instructions in README

## [1.2.9](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.9) - 2025-06-08
- fix: preserve full history when generating changelog via GitHub Actions

## [1.2.8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.8) - 2025-06-08
- fix: handle symlinked DocSets paths more robustly
- test: add coverage for symlinked DocSets environment variable

## [1.2.7](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.7) - 2025-06-08
- feat: automatically adjust docset path when DASH_DOCSETS_PATH points to Dash directory or symlink

## [1.2.6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.6) - 2025-06-08
- feat: log docset directory on startup and resolve symlinks

## [1.2.5](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.5) - 2025-06-08
- feat: docset directory can be configured via `DASH_DOCSETS_PATH`

## [1.2.4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.4) - 2025-06-08
- fix: cast limit argument to int to prevent slice index errors

## [1.2.3](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.3) - 2025-06-08
- fix: generate initialization options correctly to avoid AttributeError during startup

## [1.2.2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.2) - 2025-06-08
- startup and shutdown log messages
- error logging for unexpected exceptions

## [1.2.1](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.1) - 2025-06-08
- startup log message to confirm server launch

## [1.2.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.0) - 2025-06-08
- configurable structured logging with file rotation

## [1.1.11](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.11) - 2025-06-08
- cancel helper suppresses `KeyboardInterrupt` so shutdown completes cleanly

## [1.1.10](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.10) - 2025-06-08
- ensure `main` returns after task cancellation so startup never hangs

## [1.1.9](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.9) - 2025-06-08
- suppress KeyboardInterrupt traceback to prevent hanging

## [1.1.8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.8) - 2025-06-08
- extracted cancellation logic into a helper to avoid duplication

## [1.1.7](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.7) - 2025-06-08
- re-raise KeyboardInterrupt after cleanup for proper exit status

## [1.1.6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.6) - 2025-06-08
- cancel server task on Ctrl+C so startup no longer hangs

## [1.1.5](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.5) - 2025-06-08
- graceful shutdown on Ctrl+C without stack trace

## [1.1.4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.4) - 2025-06-08
- added `.flake8` and `mypy.ini` to resolve linter and type checker errors

## [1.1.3](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.3) - 2025-06-08
- documented `stdio_server` usage in help docs and bumped version constant

## [1.1.2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.2) - 2025-06-08
- use `stdio_server` from MCP library instead of removed `StdioClient`

## [1.1.1](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.1) - 2025-06-08
- run server using `StdioClient` and update documentation

## [1.1.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.0) - 2025-06-08
- Automatic changelog generation via GitHub Actions
- Version constant in `enhanced_dash_server.py`
- Help documentation for CI and changelog

## [1.0.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.0.0) - 2025-06-07
- Initial release
