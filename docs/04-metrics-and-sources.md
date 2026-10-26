# 04 — Metrics, semantics and platform sources

*Everything the instrument can show, what it means, and where each OS keeps it. Sources marked **[verify]** are planned and must be confirmed on real hardware before the milestone that needs them ships.*

## 1. Naming

`<domain>.<object>.<measure>_<unit>`

- Domains: `cpu`, `memory`, `storage`, `network`, `gpu`, `thermal`, `power`, `battery`, `system`, `process`, `connection`, `app`.
- Units: `_pct` (0–100), `_bytes`, `_hz`, `_c` (Celsius), `_w` (watt), `_s`, `_count`, `_ratio` (0–1), `_bps` (bytes/s).
- A metric id is a **contract**: it may gain fields, never change meaning. Deprecation is explicit in the schema.

## 2. The reading envelope

Every value the core produces:

```json
{
  "id": "cpu.package.busy_pct",
  "value": 34.2,
  "unit": "pct",
  "state": "ok",
  "provider": "linux.procfs",
  "source": "/proc/stat",
  "sampled_at": "2026-10-26T09:41:02.184Z",
  "window_ms": 1000,
  "generation": 6021,
  "why": null
}
```

`state ∈ {ok, unavailable, unsupported, denied, stale, error}`. `why` is a sentence a user can act on ("powercap energy counters are root-only; see Settings ▸ Provider health"). The UI never renders a value whose state is not `ok` without also rendering the state word.

**Definitions**

| State | Meaning | Example |
| --- | --- | --- |
| `ok` | Measured within the expected window | CPU busy from `/proc/stat` |
| `unavailable` | The source exists but gave nothing this cycle | A sensor that stopped answering |
| `unsupported` | This platform/machine cannot provide it, ever | Per-process network bytes on macOS |
| `denied` | Permission would fix it | RAPL `energy_uj` as a normal user |
| `stale` | Last sample is older than 3 intervals but not missing | A provider skipped two cycles |
| `error` | The provider failed | malformed `/proc/stat` |

## 3. Time, clocks and gaps

- Sampling uses `CLOCK_MONOTONIC` (Linux/macOS `mach_continuous_time`, Windows `QueryPerformanceCounter`).
- Wall time is recorded beside it. **Sleep detection:** when `CLOCK_BOOTTIME − CLOCK_MONOTONIC` grows by more than the sampling interval, the machine slept; emit a `sleep` event with the duration and a gap.
- Clock steps (NTP/manual) never reorder samples: the series is monotonic; the wall-time labels may jump and the graph annotates it.
- History is stored as `(t_mono, value|null)`; `null` is a gap. A gap's cause is one of `sleep`, `paused`, `provider_error`, `dropped`, `startup`.

## 4. CPU

| Metric | Definition | Linux | Windows | macOS |
| --- | --- | --- | --- | --- |
| `cpu.package.busy_pct` | `(Δtotal − Δidle − Δiowait) / Δtotal × 100` | `/proc/stat` first line | `GetSystemTimes` / `NtQuerySystemInformation` | `host_statistics(HOST_CPU_LOAD_INFO)` |
| `cpu.package.kernel_pct` | `(Δsystem + Δirq + Δsoftirq) / Δtotal` | `/proc/stat` | kernel-minus-idle from the same counters | `cpu_ticks[CPU_STATE_SYSTEM]` |
| `cpu.package.user_pct` | `(Δuser + Δnice) / Δtotal` | `/proc/stat` | user time | `CPU_STATE_USER` |
| `cpu.package.iowait_pct` | `Δiowait / Δtotal` (Linux only; `unsupported` elsewhere) | `/proc/stat` | — | — |
| `cpu.package.steal_pct` | `Δsteal / Δtotal` (VMs) | `/proc/stat` | `unsupported` | `unsupported` |
| `cpu.logical.count` | Number of logical processors | `sysconf(_SC_NPROCESSORS_ONLN)` / `/sys/devices/system/cpu/present` | `GetActiveProcessorCount` | `sysctl hw.logicalcpu` |
| `cpu.package.topology.physical_core_count` | Distinct `(package, core)` pairs | `/sys/devices/system/cpu/cpu*/topology/{physical_package_id,core_id}` | `GetLogicalProcessorInformationEx` | `sysctl hw.physicalcpu` |
| `cpu.package.topology.socket_count` | Distinct package ids | `/sys/devices/system/cpu/cpu*/topology/physical_package_id` | same | 1 (or `hw.packages`) |
| `cpu.core.class` | `p` / `e` / `standard` | `/sys/devices/system/cpu/cpu*/topology/core_type` (Intel hybrid); else `cpu_capacity` heuristic; else `standard` **[verify]** | `SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX.EfficiencyClass` | `sysctl hw.perflevel0/1.physicalcpu` + `hw.perflevel{0,1}name` |
| `cpu.core.frequency.reported_hz` | The OS's current clock for a core | `/sys/.../cpufreq/scaling_cur_freq` (kHz) | `CallNtPowerInformation(ProcessorInformation)` | `unsupported` without IOReport/powermetrics **[verify]** |
| `cpu.core.frequency.effective_hz` | Work actually done per second (throttle-aware) | `unsupported` without MSR access (`/dev/cpu/*/msr`, `denied` by default) | `% Processor Performance × base` via PDH | `unsupported` without root |
| `cpu.policy.minimum/maximum_frequency_hz` | Policy bounds | `cpuinfo_min_freq`, `cpuinfo_max_freq` | `PROCESSOR_POWER_INFORMATION` max | `hw.cpufrequency_*` where present |
| `cpu.policy.governor` | Scheduling governor | `/sys/.../cpufreq/scaling_governor` | `unsupported` (use power scheme name) | `unsupported` |
| `cpu.policy.energy_performance_bias` | EPP 0–255 | `/sys/.../cpufreq/energy_performance_preference` | `unsupported` | `unsupported` |
| `cpu.package.power_w` | Package power | RAPL `energy_uj` delta (root-only since 5.10) | PDH power meter / vendor SDK | `powermetrics` (root) **[verify]** |
| `cpu.package.temperature_c` | Package temperature | hwmon selection (below) | vendor SDK / ACPI zone / PDH thermal zone | SMC / IOReport (best-effort) |
| `cpu.package.voltage_v` | Average core voltage | hwmon `in*_input` when exposed | vendor SDK | `unsupported` mostly |
| `cpu.numa.node_count` | NUMA nodes | `/sys/devices/system/node/node*` | `GetNumaHighestNodeNumber` | `unsupported` (Apple silicon unified) |

**Per-process CPU:** `Δ(utime + stime) / Δtotal × logical_count × 100`, so one saturated core reads 100 %. Threads are summed by the process; a tree rollup is a separate computed column.

**Frequency caveat:** "reported" is what the OS claims; "effective" is what the core actually delivered. Conflating them is how monitors lie about throttling. We show both when available and say so when not.

## 5. Memory

| Metric | Definition | Linux | Windows | macOS |
| --- | --- | --- | --- | --- |
| `memory.physical.total_bytes` | Installed RAM usable by the OS | `MemTotal` | `GlobalMemoryStatusEx` | `sysctl hw.memsize` |
| `memory.physical.available_bytes` | What a new allocation can get | `MemAvailable` | `ullAvailPhys` | `free + inactive + speculative + purgeable` |
| `memory.physical.used_bytes` | `total − available` | derived | `total − avail` | derived |
| `memory.physical.utilization_pct` | `used / total` | derived | derived | derived |
| `memory.cached_bytes` | Reclaimable cache | `Buffers + Cached + SReclaimable − Shmem` | `Cache` from `GetPerformanceInfo` | `inactive + purgeable` |
| `memory.pressure_pct` | Stall pressure | `/proc/pressure/memory` `full avg10` (fallback: `some/2`) | hard-fault rate + modified-page pressure (documented heuristic) | `kern.memorystatus_vm_pressure_level` mapped 1/2/3/4 → 0/33/66/100 |
| `memory.swap.total_bytes` / `.used_bytes` | Swap file/partition | `SwapTotal − SwapFree` | `ullTotalPageFile − AvailPageFile` | `vm.swapusage.xsu_total/used` |
| `memory.swap.in/out_bytes_total` | Cumulative swap traffic | `vmstat pswpin/pswpout × page_size` | `Memory\Pages Input/Output/sec` integrated | `vm_stat` swapins/outs |
| `memory.compressed_bytes` | Compressed memory | zram `/sys/block/zram*/mm_stat` (if used) | `Memory\Compressed` **no such counter** → `unsupported` | `compressor_page_count × page` |
| `memory.hardware.speed_mts` / `slots_used` / `form_factor` / `type` | Module facts | SMBIOS DMI table — root-only by default (`denied` + doc link) | WMI `Win32_PhysicalMemory` | `system_profiler SPMemoryDataType` / SMC |
| `memory.arc_bytes` | ZFS ARC (when ZFS is present) | `/proc/spl/kstat/zfs/arcstats` `size`, `c_min` | — | — |

**The used-memory question.** Different tools disagree because they choose different definitions. Ours is published in the UI: *used = total − available*, and the composition bar underneath shows cached, shared, buffers and anonymous so the user can see why "15 GB used" and "12 GB free" describe the same machine.

## 6. Storage

| Metric | Definition | Linux | Windows | macOS |
| --- | --- | --- | --- | --- |
| `storage.activity_pct` | Fraction of wall time the device had I/O in flight | `Δ(io_ticks) / Δt / 10` from `/proc/diskstats` | PDH `% Disk Time` (clamped to 100) | IOKit block-device statistics |
| `storage.read_bytes_total` / `write_bytes_total` | Cumulative | `Δsectors_read/written × 512` | `Disk Read/Write Bytes Total` | IOKit `BytesRead/Written` |
| `storage.read/write_bps` | Rates from the above | derived | derived | derived |
| `storage.iops` / `latency_ms` / `queue_depth` | Depth and service time | `Δ(ios)`, `Δ(ms)/Δ(ios)`, field 9 | PDH queue length, Avg. Disk sec/Transfer | IOKit operations + time |
| `storage.capacity_bytes` / `.used_pct` | Filesystem | `statvfs` per mount; `size × 512` per block device | `GetDiskFreeSpaceEx` | `statfs` |
| `storage.device.model` / `.serial` / `.firmware` | Identity | `/sys/class/block/*/device/{model,serial,rev}` (serial may be `denied`) | `IOCTL_STORAGE_QUERY_PROPERTY` / WMI `MSFT_PhysicalDisk` | IOKit `IOBlockStorageDevice` |
| `storage.health.available_spare_pct` / `.life_used_pct` | Wear and spare | NVMe `smart-log` ioctl or `/sys/class/nvme/*/device/` (**needs a helper**, `denied` by default) | `IOCTL_SMART_RECEIVE_DRIVE_DATA` (admin) | IONVMeController SMART (limited on Apple SSDs) |
| `storage.temperature_c` | Drive temperature | hwmon `temp*_input` named `nvme`/`drivetemp` | SMART attribute 194 / NVMe log | IONVMeController |
| `storage.rotational` | Spinning vs solid | `/sys/class/block/*/queue/rotational` | `MSFT_PhysicalDisk.MediaType` | IOKit |
| `storage.mount.*` | Mount point, fs type, options | `/proc/self/mountinfo` | `GetVolumeInformation` | `getmntinfo` |
| `process.io.read_bytes` / `.write_bytes` | Per-process physical I/O | `/proc/<pid>/io` (own process; others often `denied`) | `GetProcessIoCounters` | `proc_pid_rusage.ri_diskio_bytes*` |

Sector size for `/proc/diskstats` is always 512, regardless of the device's logical block size — a classic source of "my disk is twice as fast as it says".

## 7. Network

| Metric | Definition | Linux | Windows | macOS |
| --- | --- | --- | --- | --- |
| `network.rx/tx_bytes_total` | Cumulative per interface | `/proc/net/dev` | `GetIfTable2` | `sysctl NET_RT_IFLIST2` (`if_data64`) |
| `network.rx/tx_bps` | Rate, with a decaying peak for the meter scale | derived | derived | derived |
| `network.errors/drops_total` | Error counters | `/proc/net/dev` | `GetIfTable2` | `if_data64` |
| `network.link.speed_hz` | Negotiated link speed | `/sys/class/net/*/speed` (may be `unavailable` on Wi-Fi) | `GetIfEntry2.TransmitLinkSpeed` | `if_linkmau` / `IO80211` |
| `network.link.mtu` / `.state` | MTU and operational state | `mtu`, `operstate` | `GetIfEntry2` | `if_data` flags |
| `network.address.*` | IPv4/IPv6, prefix, gateway | `getifaddrs` | `GetAdaptersAddresses` | `getifaddrs` |
| `network.wifi.ssid` | Network name | nl80211 `NL80211_ATTR_SSID` | `WlanQueryInterface` | `CWWiFiClient` (needs location on recent macOS) |
| `process.network.rx/tx_bytes` | Per-process traffic | socket join + counters (kernel ≥ 5.10 `/proc/net/*`, or eBPF which needs privilege) → often `denied` | ETW `Microsoft-Windows-Kernel-Network` (admin) | **`unsupported`** without a Network Extension |
| `connection.*` | Socket table and owner | `/proc/net/{tcp,tcp6,udp,udp6,unix}` + `/proc/<pid>/fd` | `GetExtendedTcpTable/UdpTable(TCP_TABLE_OWNER_PID_ALL)` | `proc_pidfdinfo(PROC_PIDFDSOCKETINFO)` + `sysctl` (**own processes only** without root) |
| `network.retransmits_total` | TCP retransmissions | `/proc/net/snmp` `RetransSegs` | `GetTcpStatisticsEx` | `netstat` sysctl |

**The decaying peak.** Meters need a scale that is stable enough to read but responsive enough to be honest. `peak(t) = max(rate over the window, peak(t−1) × 0.98)`, floored at a per-link minimum. The UI marks the scale as `auto · peak 4.2 MB/s` so nobody mistakes it for a fixed axis.

## 8. GPU and accelerators

| Metric | Linux | Windows | macOS |
| --- | --- | --- | --- |
| `gpu.utilization_pct` | `amdgpu`: `/sys/class/drm/card*/device/gpu_busy_percent`; `i915`/`xe`: fdinfo engine ns or perf **(provider)**; NVIDIA: NVML | PDH `\GPU Engine(*)\Utilization Percentage`; vendor SDKs | IOAccelerator `PerformanceStatistics["Device Utilization %"]` |
| `gpu.memory.used/total_bytes` | `mem_info_vram_used`, `mem_info_gtt_used`; NVML | DXGI `QueryVideoMemoryInfo`; NVML | `In use system memory`; unified memory → total is system RAM |
| `gpu.clock.graphics_hz` / `.memory_hz` | hwmon `freq*_input`, NVML | NVML / ADL / PDH frequency counters | IOAccelerator statistics (**not always available**) |
| `gpu.power.board_w` / `.limit_w` | hwmon `power*_average`, `power*_cap` | NVML / vendor | `unsupported` |
| `gpu.temperature.main_c` / `.hotspot_c` | hwmon `temp*_input` | NVML / vendor | IOAccelerator / SMC |
| `gpu.video.decode/encode.utilization_pct` | NVML, `amdgpu` `mem_info`? | PDH `Video Engine` | `unsupported` mostly |
| `accelerator.memory.*` (VRAM/GTT) | as above | DXGI budget/usage | unified |
| `npu.utilization_pct` | `/sys/class/accel/*/device/` (Intel VPU) **[verify]** | vendor | Apple Neural Engine: `unsupported` publicly |

GPU enumeration is per adapter with a stable key (`vendor:device:pci_slot` or `vendor:index`), because adapter order changes across boots.

## 9. Thermal and power

**Sensor selection precedence (CPU headline):**

1. `hwmon` chip `coretemp` → label `Package id 0` (lowest id for multi-socket).
2. `k10temp` → `Tctl`; then `Tdie`.
3. `zenpower` → `Tdie`/`Tctl`.
4. ARM `cpu_thermal` / `soc_thermal`.
5. Any other CPU-adjacent `hwmon` chip with a labelled package sensor.
6. `acpitz` — and when we use it, the headline is labelled **"ACPI thermal zone (board sensor)"**, exactly because it is not the CPU die.

Drive and GPU sensors are never mixed into the CPU headline; they get their own tiles. This single rule removes the most common "my temperature is wrong" class of complaint in the original's tracker.

**Power:**

- Linux: `RAPL` energy counters, `power = Δenergy_uj / Δt`, with wraparound handled via `max_energy_range_uj`. Root-only since 5.10 → `denied` with the udev recipe.
- Battery: `/sys/class/power_supply/BAT*` (`capacity`, `status`, `power_now` or `current_now × voltage_now`, `cycle_count`, `energy_full`).
- Windows: PDH power meters, `GetSystemPowerStatus`, battery class IOCTL, vendor SDKs.
- macOS: `IOPSCopyPowerSourcesInfo` for battery; `powermetrics` (root) for package power and per-process energy, absent → `denied`.

**Thermal pressure:** Linux `/sys/class/thermal/thermal_zone*/` trip points + PSI; macOS `kern.memorystatus_vm_pressure_level` is memory, so thermal pressure comes from `pmset -g therm` (limited) or IOReport; Windows `CallNtPowerInformation(SystemThermalState)` / `PROCESSOR_THROTTLE` — all marked **[verify]**.

## 10. System, processes, sessions

| Area | Linux | Windows | macOS |
| --- | --- | --- | --- |
| OS + kernel | `/etc/os-release`, `uname` | `RtlGetVersion`, registry `CurrentVersion` | `sw_vers`, `uname` |
| Firmware/board | `/sys/class/dmi/id/*` (serials root-only) | `GetSystemFirmwareTable('RSMB')`, WMI `Win32_Bios` | `IOPlatformExpertDevice` IORegistry |
| CPU model/features | `/proc/cpuinfo`, CPUID | CPUID, registry `CentralProcessor` | `sysctl machdep.cpu.*` / `hw.optional.*` |
| Process enumeration | `/proc/*/stat` (or netlink `CN_PROC`) | `CreateToolhelp32Snapshot` + `NtQuerySystemInformation` | `proc_listallpids` + `proc_pidinfo` |
| Process identity | `pid` + `starttime` (ticks since boot) + `boot_id` | `pid` + creation `FILETIME` | `pid` + `p_starttime` |
| Command line | `/proc/<pid>/cmdline` | `NtQueryInformationProcess` + PEB (or WMI) | `sysctl KERN_PROCARGS2` (own uid) |
| Sessions | utmpx, `org.freedesktop.login1` | `WTSEnumerateSessions` | `SCDynamicStore` / `who` |
| Startup items | XDG `.desktop`, systemd user units | Registry Run/RunOnce, Startup folders | LaunchAgents/Daemons, login items |
| Services | systemd D-Bus | SCM | launchd |
| Installed apps | dpkg/rpm/Flatpak/Snap | Uninstall registry + `PackageManager` | `/Applications`, `pkgutil`, Homebrew |

## 11. Derived metrics and their published formulas

Any number we compute rather than read must be reproducible from its inputs. Those formulas live in the UI's methodology page and in `docs/methodology.md` when the code exists.

| Derived | Formula |
| --- | --- |
| CPU busy % | `(Δtotal − Δidle − Δiowait) / Δtotal × 100` |
| Process CPU % | `Δ(utime + stime) / Δtotal × logical_count × 100` |
| Memory used % | `(total − available) / total × 100` |
| Memory pressure (no PSI) | `min(100, hard_faults_per_s / 2000 × 100)` with the heuristic labelled |
| Disk busy % | `Δio_ticks / Δt_ms × 100 / 10` capped at 100 |
| Disk throughput | `Δsectors × 512 / Δt` |
| Disk latency | `Δ(ms_reading + ms_writing) / Δ(reads + writes)` |
| Network rate | `Δbytes / Δt` |
| Decaying peak | `max(rate, previous × 0.98)`, floor per link |
| Temperature (F) | `C × 9/5 + 32`, computed at render, never stored |
| Energy impact | §9.4 of [the spec](03-product-spec.md#94-energy-impact) |
| Thermal throttle | `effective_hz / max_hz < 0.7 and temp ≥ 0.9 × crit` |

## 12. Correctness programme

1. **Fixture parsers** — every text format has captured samples with expected structured output, including malformed and truncated cases.
2. **Cross-checks against ground truth** — `/proc` derived totals vs `getrusage`/`times` for our own process; disk throughput vs a `dd` of known size on a scratch file; network rate vs a loopback transfer of known size; process CPU vs a known synthetic loop's wall time.
3. **Golden traces** — 10-minute recordings from three machine classes (laptop with hybrid cores and a dGPU, desktop with SMT and multiple disks, VM with no sensors) used as regression inputs for both core and renderer.
4. **Ablation tests** — hide `hwmon`, `powercap`, `DMI`, remove a GPU, run in a container without `/proc/io`: the expected result is the documented availability state, not a crash.
5. **Soak** — 24 hours at 1 Hz asserting RSS growth < 5 %, no gap without a cause, and trace integrity.
6. **Cross-platform replay** — every golden trace must render identically on all three platforms (the renderer is platform-neutral by construction).

## 13. Provider map

| Provider | Platform | Metrics | Privilege | Status |
| --- | --- | --- | --- | --- |
| `linux.procfs` | Linux | CPU, memory, processes, loadavg, uptime | none | M1 |
| `linux.sysfs` | Linux | topology, freq, hwmon, block devices, net devices | none; some files root-only → `denied` | M1 |
| `linux.powercap` | Linux | package/core power | root / udev group | M2 |
| `linux.dmi` | Linux | memory modules, firmware | root / tmpfiles group | M2 |
| `linux.systemd` | Linux | services, sessions | polkit per action | M2 |
| `linux.sockets` | Linux | connections + owner join | own processes; others `denied` | M2 |
| `linux.nvme` | Linux | SMART health | helper (setuid-free) or udev | M3 |
| `vendor.nvml` | Linux/Win | NVIDIA GPU | none | M3 |
| `vendor.amdgpu` | Linux | AMD GPU via sysfs/hwmon | none | M3 |
| `windows.pdh` | Windows | CPU, disk, network, GPU engine, power meters | none | M4 **[verify]** |
| `windows.wmi` | Windows | system, memory modules, battery | none | M4 **[verify]** |
| `windows.etw` | Windows | per-process network/IO | admin | M5 **[verify]** |
| `windows.vendor` | Windows | AMD Ryzen Master SDK, Intel DTT | admin for AMD | M4 **[verify]** |
| `macos.mach` | macOS | CPU, memory, processes | own processes; others partial | M4 **[verify]** |
| `macos.iokit` | macOS | disks, GPU, SMC temps, battery | none to partial | M4 **[verify]** |
| `macos.powermetrics` | macOS | power, per-process energy | root | M5 **[verify]** |
| `plugin.containers` | all | Docker/Podman stats | docker socket | post-1.0 |
| `plugin.nas` | all | SMART/RAID via SSH | user-provided key | post-1.0 |
