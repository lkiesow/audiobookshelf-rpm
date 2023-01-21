%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post %{nil}

Name:           tone
Version:        0.1.3
Release:        1%{?dist}
Summary:        Modify audio metadata

License:        Apache-2.0
URL:            https://github.com/sandreas/tone

Source0:        https://github.com/sandreas/tone/releases/download/v%{version}/%{name}-%{version}-linux-x64.tar.gz
Source1:        https://raw.githubusercontent.com/sandreas/%{name}/v%{version}/README.md
Source2:        https://raw.githubusercontent.com/sandreas/%{name}/v%{version}/LICENSE

BuildRequires:  tar
BuildRequires:  gzip


%description
tone is a cross platform utility to dump and modify audio metadata for a wide
variety of formats.


%prep
%setup -q -n %{name}-%{version}-linux-x64


%build
# nothing to do


%install
install -p -D -m 0755 tone %{buildroot}%{_bindir}/%{name}
cp %{SOURCE1} .
cp %{SOURCE2} .


%files
%{_bindir}/%{name}
%doc README.md
%license LICENSE



%changelog
* Fri Jan 20 2023 Lars Kiesow <lkiesow@uos.de> - 0.1.3-1
- Initial build
