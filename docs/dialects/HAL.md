# HAL: Hardware Abstraction Layer

Status: draft v0.1.

HAL is the GAL dialect for hardware substrate graphs: devices, buses, drivers,
firmware, interrupts, DMA channels, accelerators, sensors, and portable
capability surfaces.

This HAL dialect is inspired by classic hardware abstraction layers in operating
systems and embedded runtimes. The useful idea is not the low-level driver code
itself; it is the boundary discipline: expose stable capabilities and state while
isolating device-specific registers, buses, firmware quirks, and vendor
behavior behind adapters.

## Research Inspirations

HAL keeps the GAL surface small, but it borrows boundary discipline from mature
hardware abstraction systems:

- Operating-system HALs hide low-level hardware differences from kernels and
  drivers while exposing a stable call surface.
- Embedded common I/O layers let application code use the same API across
  different MCU reference boards and serial peripherals.
- Devicetree-style hardware descriptions treat hardware layout and initial
  configuration as data that can be validated before runtime.
- Layered embedded stacks separate register-level operations, HAL steps, driver
  APIs, and application-facing behavior.
- Hardware error architectures make error sources, handlers, firmware reports,
  and persistent records explicit enough for recovery and audit.

Sources used while refining this dialect:

- Microsoft Learn, Windows kernel-mode HAL library:
  <https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-hal-library>
- AWS FreeRTOS Common I/O:
  <https://docs.aws.amazon.com/freertos/latest/userguide/common-io.html>
- Zephyr Project Devicetree documentation:
  <https://docs.zephyrproject.org/latest/build/dts/index.html>
- Espressif ESP-IDF Hardware Abstraction guide:
  <https://docs.espressif.com/projects/esp-idf/en/release-v4.3/esp32/api-guides/hardware-abstraction.html>
- Apache Mynewt HAL documentation:
  <https://mynewt.apache.org/latest/os/modules/hal/hal.html>
- Microsoft Learn, Windows Hardware Error Architecture components:
  <https://learn.microsoft.com/en-us/windows-hardware/drivers/whea/components-of-the-windows-hardware-error-architecture>

## What GAL Can Recycle

HAL contributes reusable graph patterns that other GAL dialects can borrow:

- Capability discovery: model what the substrate can do before scheduling work.
- Driver/adapter boundaries: separate stable operations from device-specific
  implementation.
- Resource inventory: expose device capacity, topology, and allocation state to
  RAL and TAL.
- Health and fault surfaces: feed OAL and FAL with hardware-level degradation,
  interrupts, resets, and thermal events.
- Firmware and compatibility tracking: connect hardware revision, firmware
  version, and interface compatibility to IAL and VAL.
- Safety gates: require policy, verification, or operator approval before
  privileged device actions.

## Vocabulary

```json
{
  "id": "hal.v0",
  "nodeKinds": ["device", "driver", "bus", "firmware", "accelerator", "sensor", "interrupt", "dma", "register", "capability", "adapter"],
  "relations": ["attached_to", "driven_by", "exposes", "supports", "requires", "maps_to", "interrupts", "streams_to", "compatible_with", "observed_by"],
  "fields": ["health", "capacity", "temperature", "power", "latency", "throughput", "revision", "risk"],
  "signals": ["present", "ready", "faulted", "degraded", "thermal", "reset_required", "capable", "compatible"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["probe", "enumerate", "bind_driver", "check_firmware", "reset_device", "measure_device", "map_capability"],
  "threads": ["tick", "hardware", "probe"]
}
```

## Node Kinds

| kind | purpose |
|---|---|
| `device` | concrete hardware unit |
| `driver` | adapter that exposes stable operations |
| `bus` | attachment or communication fabric |
| `firmware` | firmware version or image metadata |
| `accelerator` | GPU, NPU, FPGA, or domain accelerator |
| `sensor` | measurement source |
| `interrupt` | hardware event source |
| `dma` | direct memory access path |
| `register` | addressable device state, usually diagnostic only |
| `capability` | stable function exposed by hardware or driver |
| `adapter` | portability boundary over device-specific behavior |

## Loader Rules

- `register` nodes must not expose secret material or unsafe write values.
- `reset_device` and `bind_driver` operations must be privileged and explicit.
- `firmware` nodes should preserve version, revision, and compatibility context.
- `capability` nodes should be reusable by CAL, RAL, TAL, IAL, OAL, FAL, and VAL.
- `adapter` nodes should own vendor-specific behavior and expose only stable
  operations to the rest of the graph.
- `interrupt` and `sensor` nodes should preserve event source and sampling
  context so OAL, FAL, and AUDAL can reconstruct what happened.
- `dma` paths should model direction, target fabric, and safety state before
  any loader plans data movement.
- `verify` mode must only inspect; it must not reset, flash, bind, or mutate
  hardware.

## Cross-Dialect Handoffs

HAL should not try to become a full resource, policy, or observability dialect.
Instead, it should hand off explicit graph facts:

- RAL consumes `capability`, `device`, and `bus` capacity for scheduling.
- TAL consumes `attached_to` and `maps_to` topology for placement.
- IAL consumes `compatible_with` and `exposes` relations for interface matching.
- OAL and FAL consume `faulted`, `thermal`, `reset_required`, `interrupt`, and
  `sensor` surfaces for alerting and recovery.
- VAL consumes `check_firmware`, `probe`, and compatibility evidence for gates.

## Example

```gal
@gal netlist.v0
@dialect hal.v0

device_gpu0 "GPU device 0" health(0.94) temperature(68) power(0.62) [kind: device] [vendor: example]
driver_gpu "GPU driver" revision(535) health(0.91) [kind: driver]
bus_pcie0 "PCIe bus 0" capacity(0.80) latency(0.03) [kind: bus]
firmware_gpu0 "GPU firmware 1.2.7" revision(127) risk(0.18) [kind: firmware]
adapter_cuda0 "GPU portability adapter" health(0.90) latency(0.04) [kind: adapter]
cap_tensor "Tensor acceleration capability" throughput(0.86) [kind: capability]
sensor_temp0 "GPU board temperature sensor" temperature(68) [kind: sensor]
interrupt_thermal0 "Thermal interrupt source" risk(0.31) [kind: interrupt]
dma_copy0 "Host to GPU DMA path" throughput(0.78) risk(0.12) [kind: dma]

device_gpu0 attached_to> bus_pcie0(1.0)
device_gpu0 driven_by> driver_gpu(1.0)
device_gpu0 supports> cap_tensor(0.9)
device_gpu0 requires> firmware_gpu0(1.0)
driver_gpu compatible_with> firmware_gpu0(0.9)
adapter_cuda0 exposes> cap_tensor(1.0)
dma_copy0 maps_to> bus_pcie0(1.0)
interrupt_thermal0 streams_to> sensor_temp0(1.0)

net device_ready and2 present compatible
net needs_service or2 faulted thermal
addf probe0 hardware [device: device_gpu0] [interval: 30s]
addf check_firmware0 tick [device: device_gpu0] [policy: compatible]
addf map_capability0 probe [device: device_gpu0] [capability: cap_tensor]
setp probe0.interval 60s
```
