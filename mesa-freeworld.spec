%global srcname mesa
%global _description These drivers contains video acceleration codecs for decoding/encoding H.264 and H.265 \
algorithms and decoding only VC1 algorithm.
%ifnarch s390x
%global with_hardware 1
%global with_vulkan_hw 0
%global with_vdpau 1
%global with_va 1
%if !0%{?rhel}
%global with_nine 0
%global with_omx 0
%global with_opencl 0
%endif
#%%global base_vulkan ,amd
%endif

%ifarch %{ix86} x86_64
%global with_crocus 0
%global with_i915   0
%global with_iris   0
%global with_xa     0
#%%global platform_vulkan ,intel
%endif

%ifarch aarch64
%if !0%{?rhel}
%global with_etnaviv   0
%global with_lima      0
%global with_vc4       0
%global with_v3d       0
%endif
%global with_freedreno 0
%global with_kmsro     0
%global with_panfrost  0
%global with_tegra     0
%global with_xa        0
#%%global platform_vulkan ,broadcom,freedreno,panfrost
%endif

%ifnarch s390x
%if !0%{?rhel}
%global with_r300 1
%global with_r600 1
%endif
%global with_radeonsi 1
%global with_vmware 1
%endif

%ifarch %{valgrind_arches}
%bcond_without valgrind
%else
%bcond_with valgrind
%endif

#%%global vulkan_drivers swrast%%{?base_vulkan}%%{?platform_vulkan}

Name:           %{srcname}-freeworld
Summary:        Mesa graphics libraries
%global ver 22.2.2
Version:        %{lua:ver = string.gsub(rpm.expand("%{ver}"), "-", "~"); print(ver)}
Release:        1%{?dist}
License:        MIT
URL:            http://www.mesa3d.org

Source0:        https://archive.mesa3d.org/%{srcname}-%{ver}.tar.xz
# src/gallium/auxiliary/postprocess/pp_mlaa* have an ... interestingly worded license.
# Source1 contains email correspondence clarifying the license terms.
# Fedora opts to ignore the optional part of clause 2 and treat that code as 2 clause BSD.
Source1:        Mesa-MLAA-License-Clarification-Email.txt
Source2:        org.mesa3d.vaapi.freeworld.metainfo.xml
Source3:        org.mesa3d.vdpau.freeworld.metainfo.xml

# Patches from Karol Herbst to make Tegra work again:
# https://bugzilla.redhat.com/show_bug.cgi?id=1989726#c46
# see also:
# https://gitlab.freedesktop.org/mesa/mesa/-/issues/5399
# Last four revert https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/3724
Patch0005: 0003-Revert-nouveau-Use-format-modifiers-in-buffer-alloca.patch
Patch0006: 0004-Revert-nouveau-no-modifier-the-invalid-modifier.patch
Patch0007: 0005-Revert-nouveau-Use-DRM_FORMAT_MOD_NVIDIA_BLOCK_LINEA.patch
Patch0008: 0006-Revert-nouveau-Stash-supported-sector-layout-in-scre.patch

# Patches from Karol Herbst to fix Nouveau multithreading:
# https://gitlab.freedesktop.org/mesa/mesa/-/merge_requests/10752
Patch0009: nouveau-multithreading-fixes.patch

BuildRequires:  meson >= 0.45
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gettext
%if 0%{?with_hardware}
BuildRequires:  kernel-headers
%endif
# We only check for the minimum version of pkgconfig(libdrm) needed so that the
# SRPMs for each arch still have the same build dependencies. See:
# https://bugzilla.redhat.com/show_bug.cgi?id=1859515
BuildRequires:  pkgconfig(libdrm) >= 2.4.97
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(zlib) >= 1.2.3
BuildRequires:  pkgconfig(libselinux)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.8
BuildRequires:  pkgconfig(wayland-client) >= 1.11
BuildRequires:  pkgconfig(wayland-server) >= 1.11
BuildRequires:  pkgconfig(wayland-egl-backend) >= 3
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
%if 0%{?with_vdpau}
BuildRequires:  pkgconfig(vdpau) >= 1.1
%endif
%if 0%{?with_va}
BuildRequires:  pkgconfig(libva) >= 0.38.0
%endif
%if 0%{?with_omx}
BuildRequires:  pkgconfig(libomxil-bellagio)
%endif
BuildRequires:  pkgconfig(libelf)
BuildRequires:  pkgconfig(libglvnd) >= 1.3.2
BuildRequires:  llvm-devel >= 7.0.0
%if %{with valgrind}
BuildRequires:  pkgconfig(valgrind)
%endif
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3dist(mako)
BuildRequires:  vulkan-headers
BuildRequires:  glslang
%if 0%{?with_vulkan_hw}
BuildRequires:  pkgconfig(vulkan)
%endif

%description
%{_description}

%if 0%{?with_va}
%package        -n %{srcname}-va-drivers-freeworld
Summary:        Mesa-based VA-API drivers
Requires:       %{srcname}-filesystem%{?_isa} >= %{?epoch:%{epoch}:}%{version}
Provides:       %{srcname}-va-drivers = %{?epoch:%{epoch}:}%{version}-%{release}
Enhances:       %{srcname}%{?_isa}

%description    -n %{srcname}-va-drivers-freeworld
%{_description}
%endif

%if 0%{?with_vdpau}
%package        -n %{srcname}-vdpau-drivers-freeworld
Summary:        Mesa-based VDPAU drivers
Requires:       %{srcname}-filesystem%{?_isa} >= %{?epoch:%{epoch}:}%{version}
Provides:       %{srcname}-vdpau-drivers = %{?epoch:%{epoch}:}%{version}-%{release}
Enhances:       %{srcname}%{?_isa}

%description 	-n %{srcname}-vdpau-drivers-freeworld
%{_description}
%endif
%prep
%autosetup -n %{srcname}-%{ver} -p1
cp %{SOURCE1} docs/

%build
# We've gotten a report that enabling LTO for mesa breaks some games. See
# https://bugzilla.redhat.com/show_bug.cgi?id=1862771 for details.
# Disable LTO for now
%define _lto_cflags %{nil}

%meson \
  -Dplatforms=x11,wayland \
  -Ddri3=enabled \
  -Dosmesa=false \
%if 0%{?with_hardware}
  -Dgallium-drivers=swrast,virgl,nouveau%{?with_r300:,r300}%{?with_crocus:,crocus}%{?with_i915:,i915}%{?with_iris:,iris}%{?with_vmware:,svga}%{?with_radeonsi:,radeonsi}%{?with_r600:,r600}%{?with_freedreno:,freedreno}%{?with_etnaviv:,etnaviv}%{?with_tegra:,tegra}%{?with_vc4:,vc4}%{?with_v3d:,v3d}%{?with_kmsro:,kmsro}%{?with_lima:,lima}%{?with_panfrost:,panfrost}%{?with_vulkan_hw:,zink} \
%else
  -Dgallium-drivers=swrast,virgl \
%endif
  -Dgallium-vdpau=%{?with_vdpau:enabled}%{!?with_vdpau:disabled} \
  -Dgallium-xvmc=disabled \
  -Dgallium-omx=%{!?with_omx:bellagio}%{?with_omx:disabled} \
  -Dgallium-va=%{?with_va:enabled}%{!?with_va:disabled} \
  -Dgallium-xa=%{!?with_xa:enabled}%{?with_xa:disabled} \
  -Dgallium-nine=%{!?with_nine:true}%{?with_nine:false} \
  -Dgallium-opencl=%{!?with_opencl:icd}%{?with_opencl:disabled} \
  -Dvideo-codecs=h264dec,h264enc,h265dec,h265enc,vc1dec \
  -Dvulkan-drivers=%{?vulkan_drivers} \
  -Dvulkan-layers=device-select \
  -Dshared-glapi=enabled \
  -Dgles1=disabled \
  -Dgles2=disabled \
  -Dopengl=true \
  -Dgbm=disabled \
  -Dglx=dri \
  -Degl=disabled \
  -Dglvnd=false \
  -Dmicrosoft-clc=disabled \
  -Dllvm=enabled \
  -Dshared-llvm=enabled \
  -Dvalgrind=%{?with_valgrind:enabled}%{!?with_valgrind:disabled} \
  -Dbuild-tests=false \
  -Dselinux=true \
  %{nil}
%meson_build

%install
%meson_install

# install Appdata files
mkdir -p %{buildroot}%{_metainfodir}
install -pm 0644 %{SOURCE2} %{buildroot}%{_metainfodir}
install -pm 0644 %{SOURCE3} %{buildroot}%{_metainfodir}

# libvdpau opens the versioned name, don't bother including the unversioned
rm -vf %{buildroot}%{_libdir}/vdpau/*.so
# likewise glvnd
rm -vf %{buildroot}%{_libdir}/libGLX_mesa.so
rm -vf %{buildroot}%{_libdir}/libEGL_mesa.so
# XXX can we just not build this
rm -vf %{buildroot}%{_libdir}/libGLES*

# glvnd needs a default provider for indirect rendering where it cannot
# determine the vendor
ln -s %{_libdir}/libGLX_mesa.so.0 %{buildroot}%{_libdir}/libGLX_system.so.0

# this keeps breaking, check it early.  note that the exit from eu-ftr is odd.
pushd %{buildroot}%{_libdir}
for i in libOSMesa*.so libGL.so ; do
    eu-findtextrel $i && exit 1
done
popd

# strip unneeded files from va-api and vdpau
rm -rf %{buildroot}%{_datadir}/{drirc.d,glvnd,vulkan}
rm -rf %{buildroot}%{_libdir}/{d3d,EGL,gallium-pipe,libGLX,pkgconfig}
rm -rf %{buildroot}%{_includedir}/{d3dadapter,EGL,GL,KHR}
rm -fr %{buildroot}%{_sysconfdir}/OpenGL
rm -fr %{buildroot}%{_libdir}/libGL.so*
rm -fr %{buildroot}%{_libdir}/libglapi.so*
rm -fr %{buildroot}%{_libdir}/libOSMesa.so*
rm -fr %{buildroot}%{_libdir}/pkgconfig/osmesa.pc
rm -fr %{buildroot}%{_libdir}/libgbm.so*
rm -fr %{buildroot}%{_includedir}/gbm.h
rm -fr %{buildroot}%{_libdir}/libxatracker.so*
rm -fr %{buildroot}%{_includedir}/xa_*.h
rm -fr %{buildroot}%{_libdir}/libMesaOpenCL.so*
rm -fr %{buildroot}%{_libdir}/dri/*_dri.so
rm -fr %{buildroot}%{_libdir}/libvulkan*.so
rm -fr %{buildroot}%{_libdir}/libVkLayer_MESA_device_select.so

%if 0%{?with_va}
%files -n %{srcname}-va-drivers-freeworld
%license docs/license.rst
%{_libdir}/dri/nouveau_drv_video.so
%if 0%{?with_r600}
%{_libdir}/dri/r600_drv_video.so
%endif
%if 0%{?with_radeonsi}
%{_libdir}/dri/radeonsi_drv_video.so
%endif
%{_metainfodir}/org.mesa3d.vaapi.freeworld.metainfo.xml
%endif

%if 0%{?with_vdpau}
%files -n %{srcname}-vdpau-drivers-freeworld
%license docs/license.rst
%{_libdir}/vdpau/libvdpau_nouveau.so.1*
%if 0%{?with_r300}
%{_libdir}/vdpau/libvdpau_r300.so.1*
%endif
%if 0%{?with_r600}
%{_libdir}/vdpau/libvdpau_r600.so.1*
%endif
%if 0%{?with_radeonsi}
%{_libdir}/vdpau/libvdpau_radeonsi.so.1*
%endif
%{_metainfodir}/org.mesa3d.vdpau.freeworld.metainfo.xml
%endif

%changelog
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
