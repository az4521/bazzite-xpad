# kmod RPM for the xpad Xbox controller driver with Xbox 360 Chatpad support.
#
# This is a "precompiled" kmod: it builds the module during %build against the
# kernel-devel present in the build environment and installs the resulting
# xpad.ko into the kernel's extra/ directory. depmod searches extra/ before the
# in-tree kernel/ directory, so this module overrides the stock xpad.
#
# It is locked to one kernel version. The build passes:
#   --define "kernel_version <uname -r>"
#   --define "krel <sanitized kernel_version>"   (used in Release for a unique
#                                                  NEVRA per kernel)

%global debug_package %{nil}
%global kmod_name xpad

%{!?kernel_version: %global kernel_version %(uname -r)}
%{!?krel: %global krel %(uname -r | tr '-' '_')}

Name:           xpad-chatpad-kmod
Version:        0.1
Release:        1.%{krel}
Summary:        Xbox controller driver with Xbox 360 Chatpad support (kmod)

License:        GPL-2.0-or-later
URL:            https://github.com/az4521/xpad
Source0:        xpad-src.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  kernel-devel
ExclusiveArch:  x86_64

%description
Out-of-tree build of the xpad Xbox controller driver including Xbox 360
Chatpad keyboard support, packaged for kernel %{kernel_version}.

The module is installed into /usr/lib/modules/%{kernel_version}/extra/, which
takes precedence over the in-tree xpad, so it transparently replaces the stock
driver once depmod has run.

%prep
%setup -q -n xpad-src

%build
make -C /usr/lib/modules/%{kernel_version}/build M="$(pwd)" modules

%install
install -D -m 0644 %{kmod_name}.ko \
    %{buildroot}/usr/lib/modules/%{kernel_version}/extra/%{kmod_name}.ko

%files
/usr/lib/modules/%{kernel_version}/extra/%{kmod_name}.ko

%post
depmod -a %{kernel_version} || :

%postun
depmod -a %{kernel_version} || :
