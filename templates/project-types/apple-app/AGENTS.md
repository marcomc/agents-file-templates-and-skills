# Apple Application Overlay

## Xcode and Swift Application Work

- Identify the supported platforms, schemes, build configurations, destinations,
  and project-approved wrappers before changing an app or shared package. Use
  the configured toolchain and regenerate generated projects when source or
  target membership changes.
- Keep shared behavior common across platforms. Isolate platform-specific UI,
  capabilities, and lifecycle handling at their existing boundaries; verify API
  availability against every affected deployment target.

## Build and Test Evidence

- For opt-in XCTest fixtures, verify the effective generated test configuration
  and environment before execution, then inspect expected pass and skip counts.
- Build successfully before testing and reuse artifacts or evidence only while their relevant source, generated inputs, dependencies, environment and requirement coverage remain valid.
- Prefer bounded compatible batches when setup is costly, keeping results per case and all required platform and configuration checks; isolate incompatible state without removing sequences needed to reproduce a defect, and measure savings rather than inferring them from fewer commands.
- Verify required test identifiers, parameter combinations, assertion results, failures and skips in terminal framework results. Count test cases, process iterations and produced outputs separately; a successful command or helper return does not establish coverage or assertion success, and XCTest assertions can fail without throwing.
- Preserve the first relevant failing evidence before fixture cleanup; retain failures and timeouts when a retry passes and distinguish isolated passes from one passing suite or clean-install coverage.

## Platform Acceptance

- Validate each affected supported platform and configuration. State whether
  evidence comes from a local Mac, Catalyst, an iOS/iPadOS simulator, or a physical
  device; compilation and simulator passes do not establish physical behavior.
- For UI changes, inspect the rendered app at affected layouts and text sizes. Scope queries and gestures to the owning pane or presented container. When acceptance requires readability, verify complete label or row containment in the unobscured viewport; existence and hittability alone do not prove it.
- For rotation acceptance, wait for the expected window geometry with a bounded observable condition and inspect a full-display capture. When an app-scoped capture is cropped or contradicts layout geometry, retain and compare both scopes before changing product UI; functional test success and visual verification remain separate evidence.
- Before pixel assertions, honor image orientation and normalize to a known raster size and coordinate space. Compare image dimensions, orientation and element bounds before attributing a pixel mismatch to the product.
- On macOS, verify changed sandbox, Keychain, helper, and signing capabilities in
  the actual app runtime. On iOS/iPadOS, verify the selected device, readiness,
  and provisioning for both the app and any separately installed test runner.

## User Data and Distribution

- Preserve app containers, archives, preferences, and credentials during tests
  or app replacement. Use isolated fixtures, verify required idle/backup guards,
  and restore temporary settings and the normal app when the workflow requires
  it. Keep secrets out of logs, screenshots, and exported diagnostics.
- Keep build, signature, installation, runtime, SDK distribution support, and
  Store approval as separate results. Use the user's existing authorization for
  local preparation; submission, publication, and irreversible external actions
  retain their explicit authorization boundaries.
