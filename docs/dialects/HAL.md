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

## What GAL Can Recycle

HAL contributes reusable graph patterns that other GAL dialects can borrow:

- Capability discovery: model what the substrate can do before scheduling work.
- Driver/adaptor boundaries: separate stable operations from device-specific
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
- `verify` mode must only inspect; it must not reset, flash, bind, or mutate
  hardware.

## Example

```gal
@gal netlist.v0
@dialect hal.v0

device_gpu0 "GPU device 0" health(0.94) temperature(68) power(0.62) [kind: device] [vendor: example]
driver_gpu "GPU driver" revision(535) health(0.91) [kind: driver]
bus_pcie0 "PCIe bus 0" capacity(0.80) latency(0.03) [kind: bus]
firmware_gpu0 "GPU firmware 1.2.7" revision(127) risk(0.18) [kind: firmware]
cap_tensor "Tensor acceleration capability" throughput(0.86) [kind: capability]

device_gpu0 attached_to> bus_pcie0(1.0)
device_gpu0 driven_by> driver_gpu(1.0)
device_gpu0 supports> cap_tensor(0.9)
device_gpu0 requires> firmware_gpu0(1.0)

net device_ready and2 present compatible
net needs_service or2 faulted thermal
addf probe0 hardware [device: device_gpu0] [interval: 30s]
addf check_firmware0 tick [device: device_gpu0] [policy: compatible]
setp probe0.interval 60s
```
