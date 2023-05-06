# vim: et:ts=3:sw=3:sts=3
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post %{nil}

%define uid   audiobookshelf
%define gid   audiobookshelf

%define node  18.14.0


Name:          audiobookshelf
Version:       2.2.20
Release:       2%{?dist}
Summary:       A self-hosted audiobook and podcast server.

Group:         Applications/Multimedia
License:       GPL-3.0
URL:           https://audiobookshelf.org
Source0:       https://github.com/advplyr/audiobookshelf/archive/refs/tags/v%{version}.tar.gz
Source1:       https://nodejs.org/dist/v%{node}/node-v%{node}-linux-x64.tar.gz

BuildRequires: tar
BuildRequires: gzip
BuildRequires: nodejs

Requires: ffmpeg >= 4
Requires: tone >= 0.1.3
%if 0%{?el8}
# we include node on el8
%else
Requires: nodejs >= 1:16
%endif

BuildRequires:     systemd
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd


%description
Audiobookshelf is a self-hosted audiobook and podcast server.


%prep
%setup -q
%if 0%{?el8}
tar xf %{SOURCE1}
%endif


%build
# Build client
cd client
npm ci --unsafe-perm=true --allow-root
# Hack to get a node.js version which lets us build the client
curl -O https://nodejs.org/download/release/v16.19.0/node-v16.19.0-linux-x64.tar.gz
tar xf node-v16.19.0-linux-x64.tar.gz
PATH=./node-v16.19.0-linux-x64/bin:$PATH npm run generate
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
%if 0%{?el8}
install -m 0755 node-v*/bin/node %{buildroot}%{_datadir}/%{name}/node
%endif

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

