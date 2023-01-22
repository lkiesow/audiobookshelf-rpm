# vim: et:ts=3:sw=3:sts=3
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post %{nil}

%define uid   audiobookshelf
%define gid   audiobookshelf


Name:          audiobookshelf
Version:       2.2.12
Release:       1%{?dist}
Summary:       A self-hosted audiobook and podcast server.

Group:         Applications/Multimedia
License:       GPL-3.0
URL:           https://audiobookshelf.org
Source0:       https://github.com/advplyr/audiobookshelf/archive/refs/tags/v%{version}.tar.gz

BuildRequires: tar
BuildRequires: gzip

# Using Node.js 18.x will fail
# For now, we get an old version in the build step
BuildRequires: nodejs >= 16

# We need https://github.com/vercel/pkg
# But we just cheat and expect it to be installed already.
# Install via:  npm install -g pkg
#BuildRequires: nodejs-pkg

Requires: ffmpeg >= 4
Requires: tone >= 0.1.3

BuildRequires:     systemd
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd


%description
Audiobookshelf is a self-hosted audiobook and podcast server.


%prep
%setup -q


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
pkg -t node18-linux-x64 -o %{name} .

# Update systemd unit
sed -i 's#^WorkingDirectory=.*$#WorkingDirectory=%{_sharedstatedir}/%{name}#' build/debian/lib/systemd/system/audiobookshelf.service
sed -i 's#^ExecStart=.*$#ExecStart=%{_bindir}/%{name} --source=rpm#' build/debian/lib/systemd/system/audiobookshelf.service

# Build configuration
echo METADATA_PATH=%{_sharedstatedir}/%{name}/metadata  > etc-default-audiobookshelf
echo CONFIG_PATH=%{_sharedstatedir}/%{name}/config     >> etc-default-audiobookshelf
echo PORT=13378                                        >> etc-default-audiobookshelf
echo HOST=127.0.0.1                                    >> etc-default-audiobookshelf



%install
rm -rf %{buildroot}

# Create directories
mkdir -m 755 -p %{buildroot}%{_sharedstatedir}/%{name}/metadata
mkdir -m 755 -p %{buildroot}%{_sharedstatedir}/%{name}/config

# Install systemd unit file
install -p -D -m 0644 \
   build/debian/lib/systemd/system/audiobookshelf.service \
   %{buildroot}%{_unitdir}/%{name}.service

# Install configuration
install -p -D -m 0644 etc-default-audiobookshelf %{buildroot}%{_sysconfdir}/default/%{name}

# Install binary
install -p -D -m 0755 %{name} %{buildroot}%{_bindir}/%{name}


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


%preun
%systemd_preun audiobookshelf.service


%postun
%systemd_postun_with_restart audiobookshelf.service


%files
%config(noreplace) %{_sysconfdir}/default/%{name}
%{_unitdir}/%{name}.service
%{_bindir}/%{name}
%attr(755,%{uid},%{gid}) %{_sharedstatedir}/%{name}


%changelog
* Fri Jan 20 2023 Lars Kiesow <lkiesow@uos.de> - 2.2.12-1
- Initial build

