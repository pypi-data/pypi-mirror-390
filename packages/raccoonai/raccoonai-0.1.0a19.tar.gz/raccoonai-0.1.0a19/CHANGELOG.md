# Changelog

## 0.1.0-alpha.19 (2025-11-04)

Full Changelog: [v0.1.0-alpha.18...v0.1.0-alpha.19](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.18...v0.1.0-alpha.19)

### Features

* clean up environment call outs ([64ab1f8](https://github.com/raccoonaihq/raccoonai-python/commit/64ab1f88832be94991c827eac9b1b6fc5937d28f))
* **client:** add support for aiohttp ([f55551a](https://github.com/raccoonaihq/raccoonai-python/commit/f55551aae49ad94af24239e0e26f316698021754))
* **client:** support file upload requests ([124c4c0](https://github.com/raccoonaihq/raccoonai-python/commit/124c4c0cc214e547fa25433053e38cbd7b6338f6))


### Bug Fixes

* **ci:** correct conditional ([4e4eca9](https://github.com/raccoonaihq/raccoonai-python/commit/4e4eca947c064446b95ded935941af2c19ae59b6))
* **ci:** release-doctor — report correct token name ([fcbd5d3](https://github.com/raccoonaihq/raccoonai-python/commit/fcbd5d3abd43ef9ee9d2bd3ba2e8731bb02e42be))
* **client:** don't send Content-Type header on GET requests ([af58369](https://github.com/raccoonaihq/raccoonai-python/commit/af583699fc05b962f33278b1fa0feab3ab495c67))
* **parsing:** correctly handle nested discriminated unions ([661189a](https://github.com/raccoonaihq/raccoonai-python/commit/661189a2a3d503b66ed2c2f499dce0905987ed10))
* **parsing:** ignore empty metadata ([6d4bca8](https://github.com/raccoonaihq/raccoonai-python/commit/6d4bca8de4db86ce82c4addbaf599433f374a646))
* **parsing:** parse extra field types ([3e1aba6](https://github.com/raccoonaihq/raccoonai-python/commit/3e1aba60cb0effd848fbd9412855d568600e7f5c))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([44715e4](https://github.com/raccoonaihq/raccoonai-python/commit/44715e41f17460b45ae2bf5e18dc35ccfa82fc38))


### Chores

* **ci:** change upload type ([3b22540](https://github.com/raccoonaihq/raccoonai-python/commit/3b22540f1c3f6144dc7af703cfec8221f983188e))
* **ci:** only run for pushes and fork pull requests ([c0a2ec3](https://github.com/raccoonaihq/raccoonai-python/commit/c0a2ec355594dd9f609a078b237d44703fd51368))
* **internal:** bump pinned h11 dep ([ddf8719](https://github.com/raccoonaihq/raccoonai-python/commit/ddf871977794ce8b7208b669ed7a0104fd836d6c))
* **internal:** codegen related update ([4f91217](https://github.com/raccoonaihq/raccoonai-python/commit/4f91217e8f0584b4e456c12061ad0016637ff2aa))
* **internal:** codegen related update ([a37625d](https://github.com/raccoonaihq/raccoonai-python/commit/a37625d9889ad5abca5267dcbe11ac38dc79060e))
* **internal:** codegen related update ([92e2b6a](https://github.com/raccoonaihq/raccoonai-python/commit/92e2b6a93faad0e9d5f5a14fbd8f69aa4f47780e))
* **internal:** codegen related update ([6a542a6](https://github.com/raccoonaihq/raccoonai-python/commit/6a542a6f2c23a988acc20c73809960418434c5fc))
* **internal:** codegen related update ([d8e8a73](https://github.com/raccoonaihq/raccoonai-python/commit/d8e8a736f71b694ca9463bce54cce7a1414351b7))
* **internal:** codegen related update ([902ae5e](https://github.com/raccoonaihq/raccoonai-python/commit/902ae5e0f6b083845b85c4bf293a915a63f5b38c))
* **internal:** codegen related update ([609e96d](https://github.com/raccoonaihq/raccoonai-python/commit/609e96de49b1fdc8ac4d8a66530e4292c130ee1c))
* **internal:** fix ruff target version ([cbd2c47](https://github.com/raccoonaihq/raccoonai-python/commit/cbd2c4791e411d3c60afb909a934d641a1aad959))
* **internal:** update comment in script ([ed19702](https://github.com/raccoonaihq/raccoonai-python/commit/ed19702d3c38a2a5c627d401f16a658d87e61f08))
* **package:** mark python 3.13 as supported ([64b34a0](https://github.com/raccoonaihq/raccoonai-python/commit/64b34a04c3344d4d2b6c6c8be258f08480f420fb))
* **project:** add settings file for vscode ([fd70189](https://github.com/raccoonaihq/raccoonai-python/commit/fd70189a623ca46cf2137b6d77e6bde5c21f5cb5))
* **readme:** fix version rendering on pypi ([c06b9e9](https://github.com/raccoonaihq/raccoonai-python/commit/c06b9e905696a5d15f97088c59f20499b91c7926))
* **readme:** update badges ([6152d97](https://github.com/raccoonaihq/raccoonai-python/commit/6152d9729ea7bec51e2fac8c04c74b8312f86d88))
* **tests:** skip some failing tests on the latest python versions ([e508628](https://github.com/raccoonaihq/raccoonai-python/commit/e508628735120437dc1d92e1e5b3f4f34eda2a45))
* update @stainless-api/prism-cli to v5.15.0 ([6ec9c06](https://github.com/raccoonaihq/raccoonai-python/commit/6ec9c06c7133ebdc9bb723cad5d3e92ce95e2da0))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([02eccd7](https://github.com/raccoonaihq/raccoonai-python/commit/02eccd75aa5c06a17d8097112d326fbc2de46d94))

## 0.1.0-alpha.18 (2025-06-17)

Full Changelog: [v0.1.0-alpha.17...v0.1.0-alpha.18](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.17...v0.1.0-alpha.18)

### Features

* **client:** add follow_redirects request option ([ead1aa2](https://github.com/raccoonaihq/raccoonai-python/commit/ead1aa29c13d4f033a0168fdeacee20f85fc487a))


### Bug Fixes

* **client:** correctly parse binary response | stream ([5428452](https://github.com/raccoonaihq/raccoonai-python/commit/5428452fe2a72d1779f18dd5d94f05a790e5d374))
* **docs/api:** remove references to nonexistent types ([c914c59](https://github.com/raccoonaihq/raccoonai-python/commit/c914c596f8f1269d52ac9e733fe6c0687e48934a))
* **package:** support direct resource imports ([f3a27ab](https://github.com/raccoonaihq/raccoonai-python/commit/f3a27ab2bb0a836a24f096588509e295677723e3))


### Chores

* **ci:** enable for pull requests ([b9d4d4a](https://github.com/raccoonaihq/raccoonai-python/commit/b9d4d4ae8d0056704b3a3041d283e65d056709ba))
* **ci:** fix installation instructions ([a8ca3a5](https://github.com/raccoonaihq/raccoonai-python/commit/a8ca3a501421f8ff560aae6544327a17f737a3f2))
* **ci:** upload sdks to package manager ([180aa07](https://github.com/raccoonaihq/raccoonai-python/commit/180aa079b0dbe5d9ad507a90ecc86f300c647a7a))
* **docs:** grammar improvements ([3c7226c](https://github.com/raccoonaihq/raccoonai-python/commit/3c7226cab9643f76ff8478b53ac7e69c05e9a71f))
* **docs:** remove reference to rye shell ([fdf4e0a](https://github.com/raccoonaihq/raccoonai-python/commit/fdf4e0a89c78828f52bfd3a328b76c5c883eb4b9))
* **docs:** remove unnecessary param examples ([1e465a4](https://github.com/raccoonaihq/raccoonai-python/commit/1e465a444fdf34a1a55abd7cdb0558520985f701))
* **internal:** avoid errors for isinstance checks on proxies ([0e03ccf](https://github.com/raccoonaihq/raccoonai-python/commit/0e03ccf60cfcd90fdae07ffb27a83e7acb3455b4))
* **internal:** codegen related update ([8336f4c](https://github.com/raccoonaihq/raccoonai-python/commit/8336f4c7c9217951d908d9d4b201687bc1578a17))
* **internal:** update conftest.py ([07c3955](https://github.com/raccoonaihq/raccoonai-python/commit/07c39557bc235720039aab307764faa6bea099b2))
* **tests:** add tests for httpx client instantiation & proxies ([a9961c3](https://github.com/raccoonaihq/raccoonai-python/commit/a9961c3882797827f7d1b09a2b65f31ce2c7a1e4))
* **tests:** run tests in parallel ([781ba6d](https://github.com/raccoonaihq/raccoonai-python/commit/781ba6d84ce3459e44b7e56e89f091d9f7db53cc))

## 0.1.0-alpha.17 (2025-04-24)

Full Changelog: [v0.1.0-alpha.16...v0.1.0-alpha.17](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.16...v0.1.0-alpha.17)

### Bug Fixes

* **perf:** optimize some hot paths ([5a0becc](https://github.com/raccoonaihq/raccoonai-python/commit/5a0becc2ea338f48ead2c7593e2727e4636c7991))
* **perf:** skip traversing types for NotGiven values ([b710b22](https://github.com/raccoonaihq/raccoonai-python/commit/b710b22dd8918404dbf8b3436b0a0a275cbc2c55))
* **pydantic v1:** more robust ModelField.annotation check ([da858d7](https://github.com/raccoonaihq/raccoonai-python/commit/da858d7536a9b151aa0dbd38e98e30130b1d219e))


### Chores

* broadly detect json family of content-type headers ([90f94bd](https://github.com/raccoonaihq/raccoonai-python/commit/90f94bd047e0522e4956a99da6248259d0619350))
* **ci:** add timeout thresholds for CI jobs ([3256eaa](https://github.com/raccoonaihq/raccoonai-python/commit/3256eaa8373c187a67806366fe5d79e28199fdf9))
* **ci:** only use depot for staging repos ([e50b221](https://github.com/raccoonaihq/raccoonai-python/commit/e50b22110b2bf2b508222589b051b1a94a573a92))
* **client:** minor internal fixes ([3aae4e2](https://github.com/raccoonaihq/raccoonai-python/commit/3aae4e22e2cb6af2281ea4ab9e6d8381eeed86b2))
* **internal:** base client updates ([4f2fd7e](https://github.com/raccoonaihq/raccoonai-python/commit/4f2fd7e046b5ceb9d1d133b066a4d299541151b0))
* **internal:** bump pyright version ([797794a](https://github.com/raccoonaihq/raccoonai-python/commit/797794a5c4d145b64f3f08249e846aa58f95c2de))
* **internal:** codegen related update ([941d8a6](https://github.com/raccoonaihq/raccoonai-python/commit/941d8a6c82ccb521730d9658059936100e4f38e3))
* **internal:** expand CI branch coverage ([b33e54c](https://github.com/raccoonaihq/raccoonai-python/commit/b33e54c4795e36cddc163be5d7f634e0c03048ba))
* **internal:** fix list file params ([795c8f4](https://github.com/raccoonaihq/raccoonai-python/commit/795c8f4980057fe365c08d1e8825e0a94481cf3e))
* **internal:** import reformatting ([1dae4cf](https://github.com/raccoonaihq/raccoonai-python/commit/1dae4cf04bf1aa5f21013e2de72ef0533c43489f))
* **internal:** minor formatting changes ([5d2b343](https://github.com/raccoonaihq/raccoonai-python/commit/5d2b3430c3f6ce32aa5478b161767b34896f04cb))
* **internal:** reduce CI branch coverage ([887e41e](https://github.com/raccoonaihq/raccoonai-python/commit/887e41e985b049f404af0ae9bb9020d2f7231f54))
* **internal:** refactor retries to not use recursion ([e4bd23e](https://github.com/raccoonaihq/raccoonai-python/commit/e4bd23e645ba1a1607cc16f087f2d7636346fa57))
* **internal:** slight transform perf improvement ([#68](https://github.com/raccoonaihq/raccoonai-python/issues/68)) ([d5bf5bd](https://github.com/raccoonaihq/raccoonai-python/commit/d5bf5bdb0cc56ac907aa40e93bd2385c5ef7cf66))
* **internal:** update models test ([0d60312](https://github.com/raccoonaihq/raccoonai-python/commit/0d60312d61e3514827c57e839b60d10fba7d3f39))
* **internal:** update pyright settings ([b059fbe](https://github.com/raccoonaihq/raccoonai-python/commit/b059fbeaeae96b42303b5b12b92a6f77d5120b8d))
* slight wording improvement in README ([#69](https://github.com/raccoonaihq/raccoonai-python/issues/69)) ([a99f7da](https://github.com/raccoonaihq/raccoonai-python/commit/a99f7dac1a402c7afe64bcc22e5726931b65cdf0))

## 0.1.0-alpha.16 (2025-04-05)

Full Changelog: [v0.1.0-alpha.15...v0.1.0-alpha.16](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.15...v0.1.0-alpha.16)

### Chores

* **internal:** remove trailing character ([#65](https://github.com/raccoonaihq/raccoonai-python/issues/65)) ([a82b752](https://github.com/raccoonaihq/raccoonai-python/commit/a82b7527085ac2664785a04f481bcb585716528c))

## 0.1.0-alpha.15 (2025-03-27)

Full Changelog: [v0.1.0-alpha.14...v0.1.0-alpha.15](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.14...v0.1.0-alpha.15)

### Chores

* fix typos ([#62](https://github.com/raccoonaihq/raccoonai-python/issues/62)) ([48b308d](https://github.com/raccoonaihq/raccoonai-python/commit/48b308d54385b04e0d7139b81690a81194499310))

## 0.1.0-alpha.14 (2025-03-18)

Full Changelog: [v0.1.0-alpha.13...v0.1.0-alpha.14](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.13...v0.1.0-alpha.14)

### Features

* **api:** api update ([#59](https://github.com/raccoonaihq/raccoonai-python/issues/59)) ([8c3e83c](https://github.com/raccoonaihq/raccoonai-python/commit/8c3e83cc030af8c2dfe01e79676b9b3f80bd3f8b))
* **api:** update new domain ([#60](https://github.com/raccoonaihq/raccoonai-python/issues/60)) ([89b0074](https://github.com/raccoonaihq/raccoonai-python/commit/89b00747c646dc3ac8dfe84a025ba59aee06bbff))


### Bug Fixes

* **ci:** ensure pip is always available ([#56](https://github.com/raccoonaihq/raccoonai-python/issues/56)) ([1317d91](https://github.com/raccoonaihq/raccoonai-python/commit/1317d91a7551ea5e44d56e2538b1f8498cdc3f0e))
* **ci:** remove publishing patch ([#58](https://github.com/raccoonaihq/raccoonai-python/issues/58)) ([fd0c16a](https://github.com/raccoonaihq/raccoonai-python/commit/fd0c16ab03e82f28591c3fde7b5ed079fe8f0557))

## 0.1.0-alpha.13 (2025-03-15)

Full Changelog: [v0.1.0-alpha.12...v0.1.0-alpha.13](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.12...v0.1.0-alpha.13)

### Bug Fixes

* **types:** handle more discriminated union shapes ([#54](https://github.com/raccoonaihq/raccoonai-python/issues/54)) ([89309c4](https://github.com/raccoonaihq/raccoonai-python/commit/89309c469b5350d7883e9d979ee34af7178ebb11))


### Chores

* **internal:** bump rye to 0.44.0 ([#53](https://github.com/raccoonaihq/raccoonai-python/issues/53)) ([8c6bbb6](https://github.com/raccoonaihq/raccoonai-python/commit/8c6bbb67d288e897cda0d492a6217ae3138e0ba5))
* **internal:** codegen related update ([#51](https://github.com/raccoonaihq/raccoonai-python/issues/51)) ([f1ef956](https://github.com/raccoonaihq/raccoonai-python/commit/f1ef956cfe8fe417214ffc79dff0f233c48a2f82))

## 0.1.0-alpha.12 (2025-03-14)

Full Changelog: [v0.1.0-alpha.11...v0.1.0-alpha.12](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.11...v0.1.0-alpha.12)

### Chores

* **internal:** remove extra empty newlines ([#48](https://github.com/raccoonaihq/raccoonai-python/issues/48)) ([3e29f20](https://github.com/raccoonaihq/raccoonai-python/commit/3e29f20507433c0c7c020d01d7bd1f1a167fcb3c))

## 0.1.0-alpha.11 (2025-03-11)

Full Changelog: [v0.1.0-alpha.10...v0.1.0-alpha.11](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.10...v0.1.0-alpha.11)

### Documentation

* revise readme docs about nested params ([#44](https://github.com/raccoonaihq/raccoonai-python/issues/44)) ([68f152e](https://github.com/raccoonaihq/raccoonai-python/commit/68f152e06a22cae44c28e4f6171df6ee87965866))

## 0.1.0-alpha.10 (2025-03-04)

Full Changelog: [v0.1.0-alpha.9...v0.1.0-alpha.10](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.9...v0.1.0-alpha.10)

### Features

* **api:** add create user and media endpoints + restructure ([#41](https://github.com/raccoonaihq/raccoonai-python/issues/41)) ([9ed4ec5](https://github.com/raccoonaihq/raccoonai-python/commit/9ed4ec5780ebb3ce33e4ba7cd3abb547d3566fa2))

## 0.1.0-alpha.9 (2025-03-04)

Full Changelog: [v0.1.0-alpha.8...v0.1.0-alpha.9](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.8...v0.1.0-alpha.9)

### Chores

* **internal:** remove unused http client options forwarding ([#38](https://github.com/raccoonaihq/raccoonai-python/issues/38)) ([3f63c81](https://github.com/raccoonaihq/raccoonai-python/commit/3f63c811fbd58e6a91beb1e03f26cb9fa084a529))

## 0.1.0-alpha.8 (2025-03-03)

Full Changelog: [v0.1.0-alpha.7...v0.1.0-alpha.8](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.7...v0.1.0-alpha.8)

### Features

* **api:** add tail and extensions resources + update old ones ([#34](https://github.com/raccoonaihq/raccoonai-python/issues/34)) ([46e7bc7](https://github.com/raccoonaihq/raccoonai-python/commit/46e7bc7a131e41a47f05ff3103ad2859997719b9))


### Bug Fixes

* **api:** tail users get path ([#36](https://github.com/raccoonaihq/raccoonai-python/issues/36)) ([00b9303](https://github.com/raccoonaihq/raccoonai-python/commit/00b9303a013a4202f4d4e9c824f8065013d1e236))

## 0.1.0-alpha.7 (2025-03-03)

Full Changelog: [v0.1.0-alpha.6...v0.1.0-alpha.7](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.6...v0.1.0-alpha.7)

### Features

* **api:** api update ([#32](https://github.com/raccoonaihq/raccoonai-python/issues/32)) ([122dfbd](https://github.com/raccoonaihq/raccoonai-python/commit/122dfbdab0b497c7baa5c1e30e8c53d971a99b0c))


### Chores

* **docs:** update client docstring ([#31](https://github.com/raccoonaihq/raccoonai-python/issues/31)) ([7d5b1cb](https://github.com/raccoonaihq/raccoonai-python/commit/7d5b1cbbbc21e7d7daf7860951236ebbfcc3ba70))
* **internal:** fix devcontainers setup ([#27](https://github.com/raccoonaihq/raccoonai-python/issues/27)) ([8b3178e](https://github.com/raccoonaihq/raccoonai-python/commit/8b3178e30fe72e1326eb46c49891b668a15db3ca))
* **internal:** properly set __pydantic_private__ ([#29](https://github.com/raccoonaihq/raccoonai-python/issues/29)) ([f457c28](https://github.com/raccoonaihq/raccoonai-python/commit/f457c28d9b5bbe682cc83156bfad97a0d5216444))


### Documentation

* update URLs from stainlessapi.com to stainless.com ([#30](https://github.com/raccoonaihq/raccoonai-python/issues/30)) ([a90f1af](https://github.com/raccoonaihq/raccoonai-python/commit/a90f1afa15b717ae8b8df892b56ee29c1061d441))

## 0.1.0-alpha.6 (2025-02-21)

Full Changelog: [v0.1.0-alpha.5...v0.1.0-alpha.6](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.5...v0.1.0-alpha.6)

### Features

* **client:** allow passing `NotGiven` for body ([#24](https://github.com/raccoonaihq/raccoonai-python/issues/24)) ([c632aa5](https://github.com/raccoonaihq/raccoonai-python/commit/c632aa57554681c776cb5aad35c673b2c2db65c7))


### Bug Fixes

* **client:** mark some request bodies as optional ([c632aa5](https://github.com/raccoonaihq/raccoonai-python/commit/c632aa57554681c776cb5aad35c673b2c2db65c7))

## 0.1.0-alpha.5 (2025-02-20)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/raccoonaihq/raccoonai-python/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Features

* **api:** manual updates ([#22](https://github.com/raccoonaihq/raccoonai-python/issues/22)) ([cc6e554](https://github.com/raccoonaihq/raccoonai-python/commit/cc6e55441b2f704061e3a83573e4fc74503c8a68))
* **client:** increase initial delay in retries to 1 sec ([#21](https://github.com/raccoonaihq/raccoonai-python/issues/21)) ([7db68d9](https://github.com/raccoonaihq/raccoonai-python/commit/7db68d9a20f316e75c35cefdabb24856435c34cf))
* **client:** set default_timeout to 10 minutes and max_retries to 0 ([#18](https://github.com/raccoonaihq/raccoonai-python/issues/18)) ([51cc5e4](https://github.com/raccoonaihq/raccoonai-python/commit/51cc5e441b12bef5f11d7e942c2ce276f1fe71a0))
* **config:** update github org name ([#19](https://github.com/raccoonaihq/raccoonai-python/issues/19)) ([de5f0e1](https://github.com/raccoonaihq/raccoonai-python/commit/de5f0e128512d004b0e945e0b8a4c280bffe411b))

## 0.1.0-alpha.4 (2025-02-14)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/flyingraccoonai/raccoonai-python/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Bug Fixes

* asyncify on non-asyncio runtimes ([#15](https://github.com/flyingraccoonai/raccoonai-python/issues/15)) ([5a8345e](https://github.com/flyingraccoonai/raccoonai-python/commit/5a8345e71be12864429fa19e8d4d55c9b70a63db))

## 0.1.0-alpha.3 (2025-02-13)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/flyingraccoonai/raccoonai-python/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Features

* **api:** api update ([#13](https://github.com/flyingraccoonai/raccoonai-python/issues/13)) ([72b8d09](https://github.com/flyingraccoonai/raccoonai-python/commit/72b8d0941c8b4e3d4c880815a4bfd4f92ab3f208))
* **client:** send `X-Stainless-Read-Timeout` header ([#9](https://github.com/flyingraccoonai/raccoonai-python/issues/9)) ([8034585](https://github.com/flyingraccoonai/raccoonai-python/commit/80345850aeeb00d8551d467804554b33216866a4))


### Chores

* **internal:** bummp ruff dependency ([#8](https://github.com/flyingraccoonai/raccoonai-python/issues/8)) ([248b017](https://github.com/flyingraccoonai/raccoonai-python/commit/248b017f449a20d44fd9d3f750b61713c2267b08))
* **internal:** change default timeout to an int ([#6](https://github.com/flyingraccoonai/raccoonai-python/issues/6)) ([b889fd3](https://github.com/flyingraccoonai/raccoonai-python/commit/b889fd33d45027dcb9a388be08096e7dc7a1ab9c))
* **internal:** fix type traversing dictionary params ([#10](https://github.com/flyingraccoonai/raccoonai-python/issues/10)) ([4f5365b](https://github.com/flyingraccoonai/raccoonai-python/commit/4f5365bb697819c392bb4e9bc162f7f9f051fdbf))
* **internal:** minor type handling changes ([#11](https://github.com/flyingraccoonai/raccoonai-python/issues/11)) ([9e102a6](https://github.com/flyingraccoonai/raccoonai-python/commit/9e102a69172abf65c913290656137e52b1519d4e))
* **internal:** update client tests ([#12](https://github.com/flyingraccoonai/raccoonai-python/issues/12)) ([13f2190](https://github.com/flyingraccoonai/raccoonai-python/commit/13f2190c2e9fd7d4b6f3159a962d47ef6c2d9316))

## 0.1.0-alpha.2 (2025-01-29)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/flyingraccoonai/raccoonai-python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** api update ([#3](https://github.com/flyingraccoonai/raccoonai-python/issues/3)) ([e251dc3](https://github.com/flyingraccoonai/raccoonai-python/commit/e251dc358ce3cc88ef81c20911125a237cd88d07))

## 0.1.0-alpha.1 (2025-01-24)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/flyingraccoonai/raccoonai-python/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** update via SDK Studio ([b4beda1](https://github.com/flyingraccoonai/raccoonai-python/commit/b4beda18093cfb681ade68610e307b7ce07fa4d2))
