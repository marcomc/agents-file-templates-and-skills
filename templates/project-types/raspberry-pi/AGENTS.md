# Raspberry Pi Overlay

## Device Context

- Treat device work as authorized maintenance of owned or managed hardware.
- Distinguish local development validation from validation on real hardware.
- Preserve boot, storage, network, and service startup assumptions unless the
  task explicitly changes them.
- Preserve service lifecycle contracts across primary, standby, failover, and
  recovery roles.

## Operational Safety

- Avoid production device changes unless the user explicitly asks for them.
- When documenting restart behavior, distinguish service restart, host restart,
  and full power-cycle evidence.
- Keep remote deployment guidance generic in docs. Use placeholders such as
  `<USER>@<HOST>`, `<HOSTNAME>`, `<DEVICE_ID>`, and `<LAN_IP>`.
- For backup, restore, failover, and recovery workflows, verify the artifact
  provenance that matters. Reachability alone is not enough proof.
