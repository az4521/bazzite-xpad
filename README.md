# bazzite-xpad

A layered **kmod RPM** of the [`az4521/xpad`](https://github.com/az4521/xpad)
driver (Xbox controllers + **Xbox 360 Chatpad** support) for immutable
[Bazzite](https://bazzite.gg/) / Universal Blue systems.

Instead of rebuilding the whole OS image, this packages `xpad.ko` as an RPM you
add with `rpm-ostree install`. The module installs into
`/usr/lib/modules/<kernel>/extra/`, which `depmod` searches before the in-tree
`kernel/` directory — so it transparently replaces the stock `xpad` and loads
normally at boot via udev (no boot-time unload/reload, no `/var`, no SELinux
relabeling, no Secure Boot signing needed when Secure Boot is off).

Target image: `ghcr.io/ublue-os/bazzite-deck:testing`.

## Install

1. Grab the RPM that matches your running kernel from the
   [latest release](../../releases/tag/latest) (or the Actions run's artifact).
   Make sure your kernel matches — check with `uname -r` and compare to the
   RPM's `Release` field.

   ```bash
   curl -L -O https://github.com/az4521/bazzite-xpad/releases/download/latest/<the rpm>
   ```

2. Layer it and reboot:

   ```bash
   sudo rpm-ostree install ./xpad-chatpad-kmod-*.rpm
   systemctl reboot
   ```

3. Verify after reboot:

   ```bash
   modinfo -F filename xpad        # -> /usr/lib/modules/<kver>/extra/xpad.ko
   modinfo xpad | grep -i chatpad  # the chatpad module parameter is present
   ```

Plug in a controller with the Chatpad attached — it shows up as a second
keyboard input device ("`<controller> Chatpad`").

## Kernel updates (the one caveat)

The RPM is locked to the kernel it was built against. When `rpm-ostree upgrade`
bumps the Bazzite kernel, this module no longer matches and **silently stops
loading** — your controllers keep working via the stock in-tree `xpad`, just
without the Chatpad symbol layers. There is intentionally no hard kernel
dependency, so updates are never blocked.

To restore Chatpad support after a kernel bump:

```bash
# rebuild for the new kernel: run the GitHub Action (Actions tab ->
# "Build xpad-chatpad kmod RPM" -> Run workflow), or wait for the weekly run,
# then:
sudo rpm-ostree uninstall xpad-chatpad-kmod          # optional, removes the old one
curl -L -O https://github.com/az4521/bazzite-xpad/releases/download/latest/<new rpm>
sudo rpm-ostree install ./xpad-chatpad-kmod-*.rpm
systemctl reboot
```

## How it's built

- [`xpad-chatpad.spec`](xpad-chatpad.spec) — builds `xpad.ko` from
  `az4521/xpad@chatpad-support` and packages it into the kernel's `extra/` dir,
  with `depmod` in `%post`/`%postun`.
- [`Containerfile.build`](Containerfile.build) — a builder stage `FROM` the
  Bazzite image (so it has the exact matching `kernel-devel`) that runs
  `rpmbuild`; the final `scratch` stage exports just the RPM.
- [`.github/workflows/build.yml`](.github/workflows/build.yml) — builds the RPM
  weekly + on demand and publishes it to the rolling `latest` release.

Build locally instead of via CI:

```bash
docker buildx build --target export -o type=local,dest=out -f Containerfile.build .
ls out/
```

## Configuration

If you run a different image or want a different driver branch, edit `BASE_IMAGE`
and `XPAD_REF` in [`.github/workflows/build.yml`](.github/workflows/build.yml)
(or pass `--build-arg` when building locally).
