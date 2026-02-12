%global srcname mesa
%global _description These drivers contains video acceleration codecs for decoding/encoding H.264 and H.265 \
algorithms and decoding only VC1 algorithm.
%ifnarch s390x
%global with_hardware 1
%global with_kmsro 0
%global with_radeonsi 1
%global with_spirv_tools 1
%global with_vmware 1
%global with_vulkan_hw 1
%if !0%{?rhel}
%global with_r300 1
%global with_r600 1
%global with_opencl 0
%global with_va 1
%endif
%if !0%{?rhel} || 0%{?rhel} >= 9
%global with_nvk %{with_vulkan_hw}
%endif
%global base_vulkan %{?with_vulkan_hw:,amd}%{!?with_vulkan_hw:%{nil}}
%endif

%ifnarch %{ix86}
%if !0%{?rhel}
%global with_teflon 0
%endif
%endif

%ifarch %{ix86} x86_64
%global with_crocus 0
%global with_iris   1
%global intel_platform_vulkan %{?with_vulkan_hw:,intel,intel_hasvk}%{!?with_vulkan_hw:%{nil}}
%if !0%{?rhel}
%global with_i915   1
%endif
%endif
%ifarch x86_64
%if 0%{?with_vulkan_hw}
%global with_intel_vk_rt 1
%endif
%endif

%ifarch aarch64 x86_64 %{ix86}
%if !0%{?rhel}
%global with_asahi     1
%global with_d3d12     1
%global with_etnaviv   0
%global with_lima      0
%global with_tegra     0
%global with_vc4       0
%global with_v3d       0
%endif
%global with_freedreno 0
%global with_panfrost  0
%if 0%{?with_asahi}
%global asahi_platform_vulkan %{?with_vulkan_hw:,asahi}%{!?with_vulkan_hw:%{nil}}
%endif
%global extra_platform_vulkan %{?with_vulkan_hw:,broadcom,freedreno,panfrost,imagination}%{!?with_vulkan_hw:%{nil}}
%endif

%if !0%{?rhel}
%global with_libunwind 1
%global with_lmsensors 1
%global with_virtio    1
%endif

%ifarch %{valgrind_arches}
%bcond_without valgrind
%else
%bcond_with valgrind
%endif

%global vulkan_drivers swrast%{?base_vulkan}%{?intel_platform_vulkan}%{?asahi_platform_vulkan}%{?extra_platform_vulkan}%{?with_nvk:,nouveau}%{?with_virtio:,virtio}%{?with_d3d12:,microsoft-experimental}

%if 0%{?with_nvk} && 0%{?rhel}
%global vendor_nvk_crates 1
%endif

# We've gotten a report that enabling LTO for mesa breaks some games. See
# https://bugzilla.redhat.com/show_bug.cgi?id=1862771 for details.
# Disable LTO for now
%global _lto_cflags %nil

Name:           %{srcname}-freeworld
Summary:        Mesa graphics libraries
Version:        26.0.0
Release:        1%{?dist}
License:        MIT AND BSD-3-Clause AND SGI-B-2.0
URL:            https://mesa3d.org

# The "Version" field for release candidates has the format: A.B.C~rcX
# However, the tarball has the format: A.B.C-rcX.
# The "ver" variable contains the version in the second format.
%global ver %{gsub %version ~ -}

Source0:        https://archive.mesa3d.org/%{srcname}-%{ver}.tar.xz
# src/gallium/auxiliary/postprocess/pp_mlaa* have an ... interestingly worded license.
# Source1 contains email correspondence clarifying the license terms.
# Fedora opts to ignore the optional part of clause 2 and treat that code as 2 clause BSD.
Source1:        Mesa-MLAA-License-Clarification-Email.txt
Source2:        org.mesa3d.vaapi.freeworld.metainfo.xml

%if 0%{?vendor_nvk_crates}
# In CentOS/RHEL, Rust crates required to build NVK are vendored.
# The minimum target versions are obtained from the .wrap files
# https://gitlab.freedesktop.org/mesa/mesa/-/tree/main/subprojects
# but we generally want the latest compatible versions
%global rust_paste_ver 1.0.15
%global rust_proc_macro2_ver 1.0.101
%global rust_quote_ver 1.0.40
%global rust_syn_ver 2.0.106
%global rust_unicode_ident_ver 1.0.18
%global rustc_hash_ver 2.1.1
Source10:       https://crates.io/api/v1/crates/paste/%{rust_paste_ver}/download#/paste-%{rust_paste_ver}.tar.gz
Source11:       https://crates.io/api/v1/crates/proc-macro2/%{rust_proc_macro2_ver}/download#/proc-macro2-%{rust_proc_macro2_ver}.tar.gz
Source12:       https://crates.io/api/v1/crates/quote/%{rust_quote_ver}/download#/quote-%{rust_quote_ver}.tar.gz
Source13:       https://crates.io/api/v1/crates/syn/%{rust_syn_ver}/download#/syn-%{rust_syn_ver}.tar.gz
Source14:       https://crates.io/api/v1/crates/unicode-ident/%{rust_unicode_ident_ver}/download#/unicode-ident-%{rust_unicode_ident_ver}.tar.gz
Source15:       https://crates.io/api/v1/crates/rustc-hash/%{rustc_hash_ver}/download#/rustc-hash-%{rustc_hash_ver}.tar.gz
%endif


BuildRequires:  meson >= 1.3.0
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gettext
%if 0%{?with_hardware}
BuildRequires:  kernel-headers
BuildRequires:  systemd-devel
%endif
# We only check for the minimum version of pkgconfig(libdrm) needed so that the
# SRPMs for each arch still have the same build dependencies. See:
# https://bugzilla.redhat.com/show_bug.cgi?id=1859515
BuildRequires:  pkgconfig(libdrm) >= 2.4.122
%if 0%{?with_libunwind}
BuildRequires:  pkgconfig(libunwind)
%endif
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(zlib) >= 1.2.3
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.34
BuildRequires:  pkgconfig(wayland-client) >= 1.11
BuildRequires:  pkgconfig(wayland-server) >= 1.11
BuildRequires:  pkgconfig(wayland-egl-backend) >= 3
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xdamage) >= 1.1
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xcb-glx) >= 1.8.1
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xcb-dri2) >= 1.8
BuildRequires:  pkgconfig(xcb-dri3)
BuildRequires:  pkgconfig(xcb-present)
BuildRequires:  pkgconfig(xcb-sync)
BuildRequires:  pkgconfig(xshmfence) >= 1.1
BuildRequires:  pkgconfig(dri2proto) >= 2.8
BuildRequires:  pkgconfig(glproto) >= 1.4.14
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcb-randr)
BuildRequires:  pkgconfig(xrandr) >= 1.3
BuildRequires:  bison
BuildRequires:  flex
%if 0%{?with_lmsensors}
BuildRequires:  lm_sensors-devel
%endif
%if 0%{?with_va}
BuildRequires:  pkgconfig(libva) >= 0.38.0
%endif
BuildRequires:  pkgconfig(libelf)
BuildRequires:  pkgconfig(libglvnd) >= 1.3.2
BuildRequires:  llvm-devel >= 7.0.0
%if 0%{?with_teflon}
BuildRequires:  flatbuffers-devel
BuildRequires:  flatbuffers-compiler
BuildRequires:  xtensor-devel
%endif
%if 0%{?with_opencl} || 0%{?with_nvk} || 0%{?with_asahi} || 0%{?with_panfrost}
BuildRequires:  clang-devel
BuildRequires:  pkgconfig(libclc)
BuildRequires:  pkgconfig(SPIRV-Tools)
BuildRequires:  pkgconfig(LLVMSPIRVLib)
%endif
%if 0%{?with_opencl} || 0%{?with_nvk}
BuildRequires:  bindgen
%if 0%{?rhel}
BuildRequires:  rust-toolset
%else
BuildRequires:  cargo-rpm-macros
%endif
%endif
%if 0%{?with_nvk}
BuildRequires:  cbindgen
%endif
%if %{with valgrind}
BuildRequires:  pkgconfig(valgrind)
%endif
BuildRequires:  python3-devel
BuildRequires:  python3-mako
BuildRequires:  python3-pycparser
BuildRequires:  python3-pyyaml
BuildRequires:  vulkan-headers
BuildRequires:  glslang
%if 0%{?with_vulkan_hw}
BuildRequires:  pkgconfig(vulkan)
%endif
%if 0%{?with_d3d12}
BuildRequires:  pkgconfig(DirectX-Headers) >= 1.618.1
%endif

%description
%{_description}

%if 0%{?with_va}
%package        -n %{srcname}-va-drivers-freeworld
Summary:        Mesa-based VA-API drivers
Requires:       %{srcname}-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}
Provides:       %{srcname}-va-drivers = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       %{srcname}-va-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      %{srcname}-vdpau-drivers-freeworld < %{?epoch:%{epoch}:}%{version}-%{release}

%description    -n %{srcname}-va-drivers-freeworld
%{_description}
%endif

%package -n %{srcname}-vulkan-drivers-freeworld
Summary:        Mesa Vulkan drivers
Requires:       vulkan%{_isa}
Requires:       %{srcname}-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}
Provides:       %{srcname}-vulkan-drivers = %{?epoch:%{epoch}:}%{version}
Provides:       %{srcname}-vulkan-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}
Obsoletes:      mesa-vulkan-devel < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      VK_hdr_layer < 1
# the following conflict is needed until we can find a way to install freeworld
# drivers in parallel to Fedora's; for ideas how to realize this see:
# * https://github.com/KhronosGroup/Vulkan-Loader/issues/1647 and its backstory: 
#   https://lists.freedesktop.org/archives/mesa-dev/2025-February/226460.html
# * https://gitlab.freedesktop.org/mesa/mesa/-/issues/12606
Conflicts:      %{srcname}-vulkan-drivers%{?_isa}

%description -n %{srcname}-vulkan-drivers-freeworld
The drivers with support for the Vulkan API with support for accelerating
decoding and encoding of various video codecs, including H.264 and H.265.

%prep
%autosetup -n %{srcname}-%{ver} -p1
cp %{SOURCE1} docs/

# Extract Rust crates meson cache directory
%if 0%{?vendor_nvk_crates}
mkdir subprojects/packagecache/
tar -xvf %{SOURCE10} -C subprojects/packagecache/
tar -xvf %{SOURCE11} -C subprojects/packagecache/
tar -xvf %{SOURCE12} -C subprojects/packagecache/
tar -xvf %{SOURCE13} -C subprojects/packagecache/
tar -xvf %{SOURCE14} -C subprojects/packagecache/
tar -xvf %{SOURCE15} -C subprojects/packagecache/
for d in subprojects/packagecache/*-*; do
    echo '{"files":{}}' > $d/.cargo-checksum.json
done
%endif

%if 0%{?with_nvk}
cat > Cargo.toml <<_EOF
[package]
name = "mesa"
version = "%{ver}"
edition = "2021"

[lib]
path = "src/nouveau/nil/lib.rs"

# only direct dependencies need to be listed here
[dependencies]
paste = "$(grep ^directory subprojects/paste*.wrap | sed 's|.*-||')"
syn = { version = "$(grep ^directory subprojects/syn*.wrap | sed 's|.*-||')", features = ["clone-impls"] }
rustc-hash = "$(grep ^directory subprojects/rustc-hash*.wrap | sed 's|.*-||')"
_EOF
%if 0%{?vendor_nvk_crates}
%cargo_prep -v subprojects/packagecache
%else
%cargo_prep

%generate_buildrequires
%cargo_generate_buildrequires
%endif
%endif


%build
# ensure standard Rust compiler flags are set
export RUSTFLAGS="%build_rustflags"

%if 0%{?with_nvk}
# So... Meson can't actually find them without tweaks
%if !0%{?vendor_nvk_crates}
export MESON_PACKAGE_CACHE_DIR="%{cargo_registry}/"
%endif

# This function rewrites a mesa .wrap file:
# - Removes the lines that start with "source"
# - Replaces the "directory =" with the MESON_PACKAGE_CACHE_DIR
#
# Example: An upstream .wrap file like this (proc-macro2-1-rs.wrap):
#
# [wrap-file]
# directory = proc-macro2-1.0.86
# source_url = https://crates.io/api/v1/crates/proc-macro2/1.0.86/download
# source_filename = proc-macro2-1.0.86.tar.gz
# source_hash = 5e719e8df665df0d1c8fbfd238015744736151d4445ec0836b8e628aae103b77
# patch_directory = proc-macro2-1-rs
#
# Will be transformed to:
#
# [wrap-file]
# directory = meson-package-cache-dir
# patch_directory = proc-macro2-1-rs
rewrite_wrap_file() {
  sed -e "/source.*/d" -e "s/^directory = ${1}-.*/directory = $(basename ${MESON_PACKAGE_CACHE_DIR:-subprojects/packagecache}/${1}-*)/" -i subprojects/${1}*.wrap
}

rewrite_wrap_file proc-macro2
rewrite_wrap_file quote
rewrite_wrap_file syn
rewrite_wrap_file unicode-ident
rewrite_wrap_file paste
rewrite_wrap_file rustc-hash
%endif

%meson \
  --libdir=%{_libdir}/dri-freeworld \
  -Ddri-drivers-path=%{_libdir}/dri-freeworld \
  -Dva-libs-path=%{_libdir}/dri-freeworld \
  -Dplatforms=x11,wayland \
%if 0%{?with_hardware}
  -Dgallium-drivers=llvmpipe,virgl,nouveau%{?with_r300:,r300}%{?with_crocus:,crocus}%{?with_i915:,i915}%{?with_iris:,iris}%{?with_vmware:,svga}%{?with_radeonsi:,radeonsi}%{?with_r600:,r600}%{?with_asahi:,asahi}%{?with_freedreno:,freedreno}%{?with_etnaviv:,etnaviv}%{?with_tegra:,tegra}%{?with_vc4:,vc4}%{?with_v3d:,v3d}%{?with_lima:,lima}%{?with_panfrost:,panfrost}%{?with_vulkan_hw:,zink}%{?with_d3d12:,d3d12} \
%else
  -Dgallium-drivers=llvmpipe,virgl \
%endif
  -Dgallium-va=%{?with_va:enabled}%{!?with_va:disabled} \
  -Dgallium-mediafoundation=disabled \
  -Dteflon=false \
%if 0%{?with_opencl}
  -Dgallium-rusticl=true \
%endif
  -Dvideo-codecs=h264dec,h264enc,h265dec,h265enc,vc1dec,av1dec,av1enc,vp9dec \
  -Dvulkan-drivers=%{?vulkan_drivers} \
  -Dvulkan-layers=device-select \
  -Dshared-glapi=enabled \
  -Dgles1=enabled \
  -Dgles2=enabled \
  -Dopengl=true \
  -Dgbm=disabled \
  -Dglx=dri \
  -Degl=disabled \
  -Dglvnd=false \
  -Dintel-rt=%{?with_intel_vk_rt:enabled}%{!?with_intel_vk_rt:disabled} \
  -Dmicrosoft-clc=disabled \
  -Dllvm=enabled \
  -Dshared-llvm=enabled \
  -Dvalgrind=%{?with_valgrind:enabled}%{!?with_valgrind:disabled} \
  -Dbuild-tests=false \
%if !0%{?with_libunwind}
  -Dlibunwind=disabled \
%endif
%if !0%{?with_lmsensors}
  -Dlmsensors=disabled \
%endif
  -Dandroid-libbacktrace=disabled \
%ifarch %{ix86}
  -Dglx-read-only-text=true \
%endif
  -Dspirv-tools=%{?with_spirv_tools:enabled}%{!?with_spirv_tools:disabled} \
  %{nil}
%meson_build

%if 0%{?with_nvk}
%cargo_license_summary
%{cargo_license} > LICENSE.dependencies
%if 0%{?vendor_nvk_crates}
%cargo_vendor_manifest
%endif
%endif

%install
%meson_install

# install Appdata files
mkdir -p %{buildroot}%{_metainfodir}
install -pm 0644 %{SOURCE2} %{buildroot}%{_metainfodir}

# glvnd opens the versioned name, don't bother including the unversioned
rm -vf %{buildroot}%{_libdir}/libGLX_mesa.so
rm -vf %{buildroot}%{_libdir}/libEGL_mesa.so
# XXX can we just not build this
rm -vf %{buildroot}%{_libdir}/libGLES*

%if ! 0%{?with_asahi}
# This symlink is unconditionally created when any kmsro driver is enabled
# We don't want this one so delete it
rm -vf %{buildroot}%{_libdir}/dri/apple_dri.so
%endif

# glvnd needs a default provider for indirect rendering where it cannot
# determine the vendor
ln -s %{_libdir}/libGLX_mesa.so.0 %{buildroot}%{_libdir}/libGLX_system.so.0

# strip unneeded files from va-api
rm -rf %{buildroot}%{_datadir}/{drirc.d/00-mesa-defaults.conf,glvnd}
rm -rf %{buildroot}%{_libdir}{,/dri-freeworld}/{d3d,EGL,gallium-pipe,libGLX,pkgconfig}
rm -rf %{buildroot}%{_includedir}/{d3dadapter,EGL,GL,KHR}
rm -fr %{buildroot}%{_sysconfdir}/OpenGL
rm -fr %{buildroot}%{_libdir}{,/dri-freeworld}/libGL.so*
rm -fr %{buildroot}%{_libdir}/libgallium-*.so
rm -fr %{buildroot}%{_libdir}{,/dri-freeworld}/libglapi.so*
rm -fr %{buildroot}%{_libdir}/libOSMesa.so*
rm -fr %{buildroot}%{_libdir}/pkgconfig/osmesa.pc
rm -fr %{buildroot}%{_libdir}/libgbm.so*
rm -fr %{buildroot}%{_includedir}/gbm.h %{buildroot}%{_includedir}/gbm_backend_abi.h
rm -fr %{buildroot}%{_libdir}{,/dri-freeworld}/libxatracker.so*
rm -fr %{buildroot}%{_includedir}/xa_*.h
rm -fr %{buildroot}%{_libdir}/libMesaOpenCL.so*
rm -fr %{buildroot}%{_libdir}/dri/*_dri.so
rm -fr %{buildroot}%{_includedir}/GLES*
rm -fr %{buildroot}%{_libdir}/dri-freeworld/libGLES*
rm -fr %{buildroot}%{_prefix}/lib%{_libdir}/dri-freeworld/libGLES*
rm -fr %{buildroot}%{_bindir}/spirv2dxil
rm -fr %{buildroot}%{_libdir}/dri-freeworld/libspirv_to_dxil.*

# ld.so.conf.d file
install -m 0755 -d  %{buildroot}%{_sysconfdir}/ld.so.conf.d/
echo -e "%{_libdir}/dri-freeworld/ \n" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}-%{_lib}.conf

%if 0%{?with_va}
%post -n %{srcname}-va-drivers-freeworld -p /sbin/ldconfig
%postun -n %{srcname}-va-drivers-freeworld -p /sbin/ldconfig
%files -n %{srcname}-va-drivers-freeworld
%config %{_sysconfdir}/ld.so.conf.d/%{name}-%{_lib}.conf
%{_libdir}/dri-freeworld/libgallium-%{ver}.so
%{_libdir}/dri-freeworld/nouveau_drv_video.so
%if 0%{?with_r600}
%{_libdir}/dri-freeworld/r600_drv_video.so
%endif
%if 0%{?with_radeonsi}
%{_libdir}/dri-freeworld/radeonsi_drv_video.so
%endif
%if 0%{?with_d3d12}
%{_libdir}/dri-freeworld/d3d12_drv_video.so
%endif
%{_libdir}/dri-freeworld/virtio_gpu_drv_video.so
%{_metainfodir}/org.mesa3d.vaapi.freeworld.metainfo.xml
%license docs/license.rst
%endif

%files -n %{srcname}-vulkan-drivers-freeworld
%if 0%{?with_nvk}
%license LICENSE.dependencies
%if 0%{?vendor_nvk_crates}
%license cargo-vendor.txt
%endif
%endif
%{_libdir}/dri-freeworld/libvulkan_lvp.so
%{_datadir}/vulkan/icd.d/lvp_icd.*.json
%{_libdir}/dri-freeworld/libVkLayer_MESA_device_select.so
%{_datadir}/vulkan/implicit_layer.d/VkLayer_MESA_device_select.json
%if 0%{?with_virtio}
%{_libdir}/dri-freeworld/libvulkan_virtio.so
%{_datadir}/vulkan/icd.d/virtio_icd.*.json
%endif
%if 0%{?with_vulkan_hw}
%{_libdir}/dri-freeworld/libvulkan_radeon.so
%{_datadir}/drirc.d/00-radv-defaults.conf
%{_datadir}/vulkan/icd.d/radeon_icd.*.json
%if 0%{?with_nvk}
%{_libdir}/dri-freeworld/libvulkan_nouveau.so
%{_datadir}/vulkan/icd.d/nouveau_icd.*.json
%endif
%if 0%{?with_d3d12}
%{_libdir}/dri-freeworld/libvulkan_dzn.so
%{_datadir}/vulkan/icd.d/dzn_icd.*.json
%endif
%ifarch %{ix86} x86_64
%{_libdir}/dri-freeworld/libvulkan_intel.so
%{_datadir}/vulkan/icd.d/intel_icd.*.json
%{_libdir}/dri-freeworld/libvulkan_intel_hasvk.so
%{_datadir}/vulkan/icd.d/intel_hasvk_icd.*.json
%endif
%ifarch aarch64 x86_64 %{ix86}
%if 0%{?with_asahi}
%{_libdir}/dri-freeworld/libvulkan_asahi.so
%{_datadir}/vulkan/icd.d/asahi_icd.*.json
%endif
%{_libdir}/dri-freeworld/libvulkan_broadcom.so
%{_datadir}/vulkan/icd.d/broadcom_icd.*.json
%{_libdir}/dri-freeworld/libvulkan_freedreno.so
%{_datadir}/vulkan/icd.d/freedreno_icd.*.json
%{_libdir}/dri-freeworld/libvulkan_panfrost.so
%{_datadir}/vulkan/icd.d/panfrost_icd.*.json
%{_libdir}/dri-freeworld/libvulkan_powervr_mesa.so
%{_datadir}/vulkan/icd.d/powervr_mesa_icd.*.json
%endif
%endif

%changelog
* Thu Feb 12 2026 Thorsten Leemhuis <fedora@leemhuis.info> - 26.0.0-1
- Update to 26.0.0
- sync various bits with recent Fedora changes

* Mon Feb 09 2026 Thorsten Leemhuis <fedora@leemhuis.info> - 26.0.0~rc3-1
- Update to 26.0.0~rc3

* Mon Feb 09 2026 Thorsten Leemhuis <fedora@leemhuis.info> - 25.3.5-1
- Update to 25.3.5
- sync various bits with recent Fedora changes

* Tue Jan 27 2026 Thorsten Leemhuis <fedora@leemhuis.info> - 25.3.4-3
- Update to 25.3.4
- sync various bits with recent Fedora changes

* Wed Jan 07 2026 Thorsten Leemhuis <fedora@leemhuis.info> - 25.3.3-3
- Update to 25.3.3

* Fri Dec 05 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.3.1-1
- Update to 25.3.1
- Fix DirectX-Headers minimal required version for 25.3.0

* Fri Nov 28 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.3.0-2
- Update vulkan device select layer patches
- Disable LTO globally

* Mon Nov 17 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.3.0-1
- Update to 25.3.0
- sync various bits with recent Fedora changes

* Fri Nov 7 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.2.6-1
- Update to 25.2.5
- sync various bits with recent Fedora changes

* Thu Oct 16 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.2.5-1
- Update to 25.2.5
- Follow Fedora and drop VDPAU support

* Fri Oct 3 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.2.4-1
- Update to 25.2.4

* Mon Sep 22 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.2.3-1
- Update to 25.2.3

* Thu Sep 4 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.2.2-1
- Update to 25.2.2

* Thu Aug 28 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.2.1-1
- Update to 25.2.1
- sync many bits with recent Fedora changes

* Sun Jul 27 2025 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 25.1.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Fri Jun 20 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.1.4-2
- Endable D3D12

* Thu Jun 19 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.1.4-1
- Update to 25.1.4
- sync a few minor bits with Fedora
- improve description of mesa-vulkan-drivers-freeworld

* Mon Jun 9 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.1.3-1
- Update to 25.1.3
- sync a few minor bits with Fedora

* Fri May 30 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.1.1-1
- Update to 25.1.1
- add provides mesa-va-drivers to mesa-va-drivers-freeworld (#7231)
- sync a few minor bits with Fedora

* Thu May 8 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.1.0-1
- Update to 25.1.0
- Sync new bits with Fedora

* Fri Apr 25 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.1.0~rc2-1
- Update to 25.1.0~rc2
- Sync new bits with Fedora, which includes enabling of the asahi driver

* Tue Apr 22 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.4-1
- Update to 25.0.4
- Sync a few bits with Fedora

* Thu Apr 3 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.3-1
- Update to 25.0.3

* Thu Mar 27 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.2-2
- pick up backport and fixes from Fedora for clover/llvm20 and
  vulkan/wsi: implement the Wayland color management protocol

* Thu Mar 20 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.2-1
- Update to 25.0.2

* Thu Mar 06 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.1-1
- Update to 25.0.1
- drop 0001-vulkan-wsi-x11-fix-use-of-uninitialised-xfixes-regio.patch

* Thu Feb 20 2025 Björn Esser <besser82@fedoraproject.org> - 25.0.0-4
- Add archless provides for mesa-vulkan-drivers

* Thu Feb 20 2025 Björn Esser <besser82@fedoraproject.org> - 25.0.0-3
- Fix mesa-filesystem requires in mesa-vulkan-drivers-freeworld

* Thu Feb 20 2025 Björn Esser <besser82@fedoraproject.org> - 25.0.0-2
- Fix general installability of mesa-vulkan-drivers-freeworld

* Wed Feb 19 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.0-1
- Update to 25.0.0
- add 0001-vulkan-wsi-x11-fix-use-of-uninitialised-xfixes-regio.patch

* Thu Feb 13 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.0~rc3-1
- Update to 25.0.0~rc3

* Tue Feb 11 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.0~rc2-2
- create mesa-vulkan-drivers-freeworld, conflicting with mesa-vulkan-drivers

* Thu Feb 06 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 25.0.0~rc2-1
- Update to 25.0.0~rc2
- drop upstreamed patch

* Tue Jan 28 2025 Björn Esser <besser82@fedoraproject.org> - 24.3.4-8
- Add patch for radeonsi to disallow compute queues on Raven/Raven2
  due to hangs

* Mon Jan 27 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.4-7
- Drop conflicts with mesa-va-drivers, as its files do not conclict
  anymore with the ones in mesa-va-drivers-freeworld
- Drop now unneeded BR on a specific LLVM version

* Fri Jan 24 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.4-6
- Rebuild due to mishap with the release number

* Fri Jan 24 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.4-2
- Reapply ldconfig changes from Leigh
- Enable GLES stuff and exclude some of the files now getting build

* Fri Jan 24 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.4-1
- Update to 24.3.4

* Fri Jan 17 2025 Leigh Scott <leigh123linux@gmail.com> - 24.3.3-5
- Remove ldconfig as it breaks some apps

* Sat Jan 11 2025 Leigh Scott <leigh123linux@gmail.com> - 24.3.3-4
- Fix ldconfig scriptlets

* Sat Jan 11 2025 Leigh Scott <leigh123linux@gmail.com> - 24.3.3-3
- Add ldconfig scriptlets

* Fri Jan 10 2025 Leigh Scott <leigh123linux@gmail.com> - 24.3.3-2
- Fix tearing due to fedora libgallium

* Fri Jan 10 2025 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.3-1
- Update to 24.3.3

* Fri Dec 20 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.2-1
- Update to 24.3.2

* Thu Dec 05 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.1-1
- Update to 24.3.1

* Fri Nov 22 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.0-1
- Update to 24.3.0

* Thu Nov 14 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.0~rc2-1
- Update to 24.3.0-rc2

* Tue Nov 12 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.3.0~rc1-1
- Update to 24.3.0-rc1
- Drop unneeded omx support

* Thu Oct 31 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.6-1
- Update to 24.2.6

* Mon Oct 28 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.5-1
- Update to 24.2.5

* Fri Oct 04 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.4-1
- Update to 24.2.4
- drop 0001-gallium-Don-t-pass-avx512er-and-avx512pf-features-on.patch

* Sun Sep 29 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.3-5
- rebuild for -Ehuman-not-enough-tee-error

* Sun Sep 29 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.3-4
- add 0001-gallium-Don-t-pass-avx512er-and-avx512pf-features-on.patch

* Wed Sep 25 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.3-3
- temporarily require llvm 19 for Fedora 41 and up

* Fri Sep 20 2024 Nicolas Chauvet <kwizart@gmail.com> - 24.2.3-2
- Attempt to complement Fedora

* Thu Sep 19 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.3-1
- Update to 24.2.3
- Sync a few bits with mesa.spec from fedora

* Fri Sep 6 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.2-1
- Update to 24.2.2
- Sync a few bits with mesa.spec from fedora

* Thu Aug 29 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.1-1
- Update to 24.2.1
- Sync a few bits with mesa.spec from fedora

* Mon Aug 19 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.0-1
- Update to 24.2.0

* Thu Aug 8 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.0~rc4-1
- Update to 24.2.0-rc4

* Fri Aug 02 2024 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 24.2.0~rc3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Thu Aug 1 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.2.0~rc3-1
- Update to 24.2.0-rc3
- Drop upstreamed patch

* Fri Jul 19 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.4-2
- add revert-6746d4df-to-fix-av1-slice_data_offset.patch

* Thu Jul 18 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.4-1
- Update to 24.1.4
- Drop upstreamed patch

* Mon Jul 01 2024 Leigh Scott <leigh123linux@gmail.com> - 24.1.2-2
- Fix mutter crash when calling eglQueryDmaBufModifiersEXT
- Fix GNOME and KDE crash with some AMD GPUs

* Thu Jun 20 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.2-1
- Update to 24.1.2

* Thu Jun 06 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.1-1
- Update to 24.1.1

* Thu May 23 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.0-1
- Update to 24.1.0

* Fri May 17 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.0~rc4-2
- disable teflon on ix86, too

* Thu May 16 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.0~rc4-1
- Update to 24.1.0-rc4
- Sync a few more bits with mesa.spec from fedora

* Thu May 9 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.0~rc3-1
- Update to 24.1.0-rc3
- Sync with_intel_vk_rt bits with mesa.spec from fedora
- Unconditionally BR clang-devel, bindgen, libclc, SPIRV-Tools, and
  LLVMSPIRVLib which are needed now

* Tue May 7 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.1.0~rc2-1
- Update to 24.1.0-rc2

* Thu Apr 25 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.6-1
- Update to 24.0.6

* Thu Apr 11 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.5-1
- Update to 24.0.5

* Mon Apr 1 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.4-1
- Update to 24.0.4

* Thu Mar 14 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.3-1
- Update to 24.0.3

* Wed Mar 6 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.2-3
- Disable nvk explicitly to avoid BR on rust-packaging

* Wed Mar 6 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.2-2
- Update to 24.0.2

* Thu Feb 22 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.0-2
- enable vp9, av1 codecs due to new meson build flag (#6873)

* Fri Feb 02 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.0-1
- Update to 24.0.0

* Fri Jan 19 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 24.0.0~rc2-1
- Update to 24.0.0-rc2

* Thu Jan 11 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 23.3.3-1
- Update to 23.3.3

* Wed Jan 3 2024 Thorsten Leemhuis <fedora@leemhuis.info> - 23.3.2-1
- Update to 23.3.2

* Mon Dec 18 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.3.1-1
- Update to 23.3.1

* Fri Dec 15 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.3.0-2
- sync a few bit with fedora's mesa.spec

* Fri Dec 1 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.3.0-1
- Update to 23.3.0

* Thu Nov 30 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.3.0~rc5-1
- Update to 23.3.0-rc5

* Thu Nov 2 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.3.0~rc2-1
- Update to 23.3.0-rc2

* Thu Oct 26 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.3.0~rc1-1
- Update to 23.3.0-rc1

* Tue Oct 10 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.2.1-2
- follow Fedora: backport MR #24045 to fix Iris crashes (RHBZ#2238711)
- temporarily hard require llvm16, as that's what's used by fedora

* Sat Sep 30 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.2.1-1
- Update to 23.2.1

* Wed Sep 6 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.2.0~rc3.1
- Update to 23.2.0-rc3
- sync a few spec file bits with Fedora's mesa package

* Fri Aug 11 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.2.0~rc1.1
- Update to 23.2.0-rc2

* Thu Aug 3 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.1.5-1
- Update to 23.1.5

* Sun Jul 23 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.1.4-1
- Update to 23.1.4

* Fri Jun 23 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.1.3-1
- Update to 23.1.3

* Mon Jun 12 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.1.2-1
- Update to 23.1.2
- sync a few spec file bits with Fedora's mesa package

* Fri May 26 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.1.1-1
- Update to 23.1.1

* Tue May 23 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.1.0-1
- Update to 23.1.0
- sync a few spec file bits with Fedora's mesa package

* Tue Apr 25 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.0.3-1
- Update to 23.0.3

* Thu Apr 20 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.0.2-1.1
- Re-introduce Conflicts (rfbz#6612, kwizart)
- Enforces version to avoid miss-match with fedora (rfbz#6613, kwizart)

* Thu Apr 13 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.0.2-1
- Update to 23.0.2

* Tue Apr 11 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.0.1-2
- Rebuild for LLVM 16

* Sat Mar 25 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.0.1-1
- Update to 23.0.1

* Thu Feb 23 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.0.0-1
- Update to 23.0.0

* Thu Feb 16 2023 Luya Tshimbalanga <luya@fedoraproject.org> - 23.0.0~rc4-2
- Remove trailed .1 in release tag

* Thu Feb 2 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.0.0~rc4-1
- Update to 23.0.0-rc4

* Mon Jan 30 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 23.0.0~rc3-1
- Update to 23.0.0-rc3

* Wed Jan 18 2023 Luya Tshimbalanga <luya@fedoraproject.org> - 22.3.3-2.1
- Drop conflicts with provides

* Tue Jan 17 2023 Luya Tshimbalanga <luya@fedoraproject.org> - 22.3.3-2
- Fix dependencies issues between Fedora and RPM Fusion

* Thu Jan 12 2023 Thorsten Leemhuis <fedora@leemhuis.info> - 22.3.3-1
- Update to 22.3.3

* Wed Jan 4 2023 Luya Tshimbalanga <luya@fedoraproject.org> - 22.3.2-3
- fix typo on conflict condition for vdpau sub-package

* Sun Jan 1 2023 Luya Tshimbalanga <luya@fedoraproject.org> - 22.3.2-2
- Add conflicts to resolve dependencies from Fedora repo on update

* Sat Dec 31 2022 Thorsten Leemhuis <fedora@leemhuis.info> - 22.3.2-1
- Update to 22.3.2

* Mon Dec 19 2022 Thorsten Leemhuis <fedora@leemhuis.info> - 22.3.1-1
- adjust placement of a few files entries to stay in sync with Fedora; while at it
  make it more obvious that the license files are specific to rpmfusion

* Mon Dec 19 2022 Thorsten Leemhuis <fedora@leemhuis.info> - 22.3.1-1
- Update to 22.3.1
- sync a few bits with Fedora's mesa.spec

* Sun Nov 13 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 22.3.0~rc2-2
- Updated to version 22.3.0-rc2.

* Sun Nov 13 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 22.2.3-1
- Updated to version 22.2.3.

* Sun Nov 6 2022 Luya Tshimbalanga <luya@fedoraproject.org> - 22.2.2-1
- Update to 22.2.2

* Thu Oct 13 2022 Luya Tshimbalanga <luya@fedoraproject.org> - 22.2.1-1
- Update to 22.2.1
- Add appdata files for each subpackage

* Wed Oct 5 2022 Luya Tshimbalanga <luya@fedoraproject.org> - 22.2.0-4
- Drop unneeded omx support
- Add missing license for each files

* Sun Oct 2 2022 Luya Tshimbalanga <luya@fedoraproject.org> - 22.2.0-3
- Rename vaapi to va
- Broaden description
- Add Enhancement line
- Clean up spec file

* Sat Oct 1 2022 Luya Tshimbalanga <luya@fedoraproject.org> - 22.2.0-2
- Drop unsupported autospec in rpmfusion infra
- Enable h264, h265 and vc1 codecs
- Re-enable vdpau and omx (OpenMax) support

* Sat Oct 1 2022 Luya Tshimbalanga <luya@fedoraproject.org> - 22.2.0-1
- Initial release
