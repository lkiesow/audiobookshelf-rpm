# vim: et:ts=3:sw=3:sts=3
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post %{nil}

%define uid   audiobookshelf
%define gid   audiobookshelf

%define node  20.11.1


Name:          audiobookshelf
Version:       2.18.1
Release:       2%{?dist}
Summary:       A self-hosted audiobook and podcast server.

Group:         Applications/Multimedia
License:       GPL-3.0
URL:           https://audiobookshelf.org
Source0:       https://github.com/advplyr/audiobookshelf/archive/refs/tags/v%{version}.tar.gz
Source1:       https://nodejs.org/download/release/v%{node}/node-v%{node}-linux-x64.tar.gz

BuildRequires: tar
BuildRequires: gzip
BuildRequires: nodejs

Requires: ffmpeg >= 4
Requires: tone >= 0.1.3
# we need node 20
#Requires: nodejs >= 1:20

BuildRequires:     systemd
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd


%description
Audiobookshelf is a self-hosted audiobook and podcast server.


%prep
%setup -q
tar xf %{SOURCE1}


%build
# Set npm path
npmpath="$(readlink -f node-v20.11.1-linux-x64/bin)"
export PATH=${npmpath}:${PATH}

# Build client
cd client
npm ci --unsafe-perm=true --allow-root
npm run generate
cd ..

# Build server
npm ci --only=production --unsafe-perm=true --allow-root

# Update systemd unit
sed -i 's#^WorkingDirectory=.*$#WorkingDirectory=%{_sharedstatedir}/%{name}#' build/debian/lib/systemd/system/audiobookshelf.service
sed -i 's#^ExecStart=.*$#ExecStart=%{_bindir}/%{name} --source=rpm#' build/debian/lib/systemd/system/audiobookshelf.service

# Build configuration
echo METADATA_PATH=%{_sharedstatedir}/%{name}/metadata  > etc-default-audiobookshelf
echo CONFIG_PATH=%{_sharedstatedir}/%{name}/config     >> etc-default-audiobookshelf
echo PORT=13378                                        >> etc-default-audiobookshelf
echo HOST=127.0.0.1                                    >> etc-default-audiobookshelf

echo '#!/bin/sh'                > bin-%{name}
echo 'cd %{_datadir}/%{name}/' >> bin-%{name}
echo 'export PATH=.:$PATH'     >> bin-%{name}
echo 'node prod.js $@'         >> bin-%{name}


%install
rm -rf %{buildroot}

# Create directories
mkdir -m 755 -p %{buildroot}%{_sharedstatedir}/%{name}/metadata
mkdir -m 755 -p %{buildroot}%{_sharedstatedir}/%{name}/config
mkdir -m 755 -p %{buildroot}%{_datadir}/%{name}/client

# Add node
install -m 0755 node-v*/bin/node %{buildroot}%{_datadir}/%{name}/node

# Add Audiobookshelf
mv client/dist/ %{buildroot}%{_datadir}/%{name}/client/
mv node_modules/ package.json package-lock.json prod.js server/ %{buildroot}%{_datadir}/%{name}/

# Install systemd unit file
install -p -D -m 0644 \
   build/debian/lib/systemd/system/audiobookshelf.service \
   %{buildroot}%{_unitdir}/%{name}.service

# Install configuration
install -p -D -m 0644 etc-default-audiobookshelf %{buildroot}%{_sysconfdir}/default/%{name}

# Install binary
install -p -D -m 0755 bin-%{name} %{buildroot}%{_bindir}/%{name}


%pre
# Create user and group if nonexistent
if [ ! $(getent group %{gid}) ]; then
   groupadd -r %{gid} > /dev/null 2>&1 || :
fi
if [ ! $(getent passwd %{uid}) ]; then
   useradd -M -r -d /srv/opencast -g %{gid} %{uid} > /dev/null 2>&1 || :
fi


%post
%systemd_post audiobookshelf.service

# (SELinux) Allow httpd to serve client directly
semanage fcontext -a -t httpd_sys_content_t "%{_datadir}/%{name}/client/dist(/.*)?" || :
restorecon -R -v "%{_datadir}/%{name}/client/dist/" || :


%preun
%systemd_preun audiobookshelf.service


%postun
%systemd_postun_with_restart audiobookshelf.service


%files
%config(noreplace) %{_sysconfdir}/default/%{name}
%{_unitdir}/%{name}.service
%{_bindir}/%{name}
%{_datadir}/%{name}
%attr(755,%{uid},%{gid}) %{_sharedstatedir}/%{name}


%changelog
* Tue Jan 21 2025 Lars Kiesow <lkiesow@uos.de> - 2.18.1-1
- Update to 2.18.1

* Mon Jan 20 2025 Lars Kiesow <lkiesow@uos.de> - 2.18.0-1
- Update to 2.18.0

* Thu Jan 02 2025 Lars Kiesow <lkiesow@uos.de> - 2.17.7-1
- Update to 2.17.7

* Mon Dec 30 2024 Lars Kiesow <lkiesow@uos.de> - 2.17.6-1
- Update to 2.17.6

* Mon Dec 09 2024 Lars Kiesow <lkiesow@uos.de> - 2.17.5-1
- Update to 2.17.5

* Fri Dec 06 2024 Lars Kiesow <lkiesow@uos.de> - 2.17.4-1
- Update to 2.17.4

* Sun Dec 01 2024 Lars Kiesow <lkiesow@uos.de> - 2.17.3-1
- Update to 2.17.3

* Fri Nov 22 2024 Lars Kiesow <lkiesow@uos.de> - 2.17.2-1
- Update to 2.17.2

* Mon Nov 18 2024 Lars Kiesow <lkiesow@uos.de> - 2.17.1-1
- Update to 2.17.1

* Mon Nov 18 2024 Lars Kiesow <lkiesow@uos.de> - 2.17.0-1
- Update to 2.17.0

* Wed Oct 30 2024 Lars Kiesow <lkiesow@uos.de> - 2.16.2-1
- Update to 2.16.2

* Tue Oct 29 2024 Lars Kiesow <lkiesow@uos.de> - 2.16.1-1
- Update to 2.16.1

* Mon Oct 28 2024 Lars Kiesow <lkiesow@uos.de> - 2.16.0-1
- Update to 2.16.0

* Sat Oct 19 2024 Lars Kiesow <lkiesow@uos.de> - 2.15.1-1
- Update to 2.15.1

* Sun Oct 13 2024 Lars Kiesow <lkiesow@uos.de> - 2.15.0-1
- Update to 2.15.0

* Sun Oct 06 2024 Lars Kiesow <lkiesow@uos.de> - 2.14.0-1
- Update to 2.14.0

* Tue Sep 10 2024 Lars Kiesow <lkiesow@uos.de> - 2.13.4-1
- Update to 2.13.4

* Tue Sep 03 2024 Lars Kiesow <lkiesow@uos.de> - 2.13.3-1
- Update to 2.13.3

* Mon Sep 02 2024 Lars Kiesow <lkiesow@uos.de> - 2.13.2-1
- Update to 2.13.2

* Sun Sep 01 2024 Lars Kiesow <lkiesow@uos.de> - 2.13.0-1
- Update to 2.13.0

* Sat Aug 10 2024 Lars Kiesow <lkiesow@uos.de> - 2.12.3-1
- Update to 2.12.3

* Fri Aug 09 2024 Lars Kiesow <lkiesow@uos.de> - 2.12.2-1
- Update to 2.12.2

* Tue Aug 06 2024 Lars Kiesow <lkiesow@uos.de> - 2.12.1-1
- Update to 2.12.1

* Mon Aug 05 2024 Lars Kiesow <lkiesow@uos.de> - 2.12.0-1
- Update to 2.12.0

* Mon Jul 08 2024 Lars Kiesow <lkiesow@uos.de> - 2.11.0-1
- Update to 2.11.0

* Tue May 28 2024 Lars Kiesow <lkiesow@uos.de> - 2.10.1-1
- Update to 2.10.1

* Mon May 27 2024 Lars Kiesow <lkiesow@uos.de> - 2.10.0-1
- Update to 2.10.0

* Mon Apr 22 2024 Lars Kiesow <lkiesow@uos.de> - 2.9.0-1
- Update to 2.9.0

* Sun Mar 17 2024 Lars Kiesow <lkiesow@uos.de> - 2.8.1-1
- Update to 2.8.1

* Tue Feb 27 2024 Lars Kiesow <lkiesow@uos.de> - 2.8.0-2
- Use Node.js 20.x

* Tue Feb 20 2024 Lars Kiesow <lkiesow@uos.de> - 2.8.0-1
- Update to 2.8.0

* Wed Jan 17 2024 Lars Kiesow <lkiesow@uos.de> - 2.7.2-1
- Update to 2.7.2

* Mon Jan 01 2024 Lars Kiesow <lkiesow@uos.de> - 2.7.1-1
- Update to 2.7.1

* Sun Dec 24 2023 Lars Kiesow <lkiesow@uos.de> - 2.7.0-1
- Update to 2.7.0

* Tue Nov 28 2023 Lars Kiesow <lkiesow@uos.de> - 2.6.0-1
- Update to 2.6.0

* Mon Oct 30 2023 Lars Kiesow <lkiesow@uos.de> - 2.5.0-1
- Update to 2.5.0

* Sun Oct 01 2023 Lars Kiesow <lkiesow@uos.de> - 2.4.4-1
- Update to 2.4.4

* Mon Sep 18 2023 Lars Kiesow <lkiesow@uos.de> - 2.4.3-1
- Update to 2.4.3

* Thu Sep 14 2023 Lars Kiesow <lkiesow@uos.de> - 2.4.2-1
- Update to 2.4.2

* Sun Sep 10 2023 Lars Kiesow <lkiesow@uos.de> - 2.4.1-1
- Update to 2.4.1

* Sat Sep 09 2023 Lars Kiesow <lkiesow@uos.de> - 2.4.0-1
- Update to 2.4.0

* Thu Jul 20 2023 Lars Kiesow <lkiesow@uos.de> - 2.3.3-1
- Update to 2.3.3

* Tue Jul 18 2023 Lars Kiesow <lkiesow@uos.de> - 2.3.2-1
- Update to 2.3.2

* Sun Jul 16 2023 Lars Kiesow <lkiesow@uos.de> - 2.3.1-1
- Update to 2.3.1

* Sun Jul 16 2023 Lars Kiesow <lkiesow@uos.de> - 2.3.0-1
- Update to 2.3.0

* Sun Jun 11 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.23-1
- Update to 2.2.23

* Wed May 31 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.22-1
- Update to 2.2.22

* Sun May 28 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.21-1
- Update to 2.2.21

* Sat May 06 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.20-1
- Update to 2.2.20

* Mon Apr 17 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.19-1
- Update to 2.2.19

* Mon Apr 03 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.18-1
- Update to 2.2.18

* Wed Mar 29 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.17-1
- Update to 2.2.17

* Tue Mar 28 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.16-1
- Update to 2.2.16

* Sun Mar 19 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.17-1
- Update to 2.2.17

* Mon Mar 06 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.16-1
- Update to 2.2.16

* Sun Feb 12 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.15-1
- Update to 2.2.15

* Thu Feb 02 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.14-2
- Package built without pkg
- Include node binary on el8 only
- Allow httpd to deliver client )SELinux label=

* Thu Feb 02 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.14-1
- Update to 2.2.14

* Wed Feb 01 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.13-1
- Update to 2.2.13

* Fri Jan 20 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.12-1
- Initial build

