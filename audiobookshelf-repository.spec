Name:      audiobookshelf-repository
Summary:   Audiobookshelf RPM Repository
Version:   1
Release:   1%{?dist}
License:   CC-0
URL:       https://github.com/lkiesow/audiobookshelf-rpm
Source0:   https://raw.githubusercontent.com/lkiesow/audiobookshelf-rpm/main/audiobookshelf.repo
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root


%description
RPM repository for Audiobookshelf on CentOS Stream, Red hat Enterprise Linux
and equivalent distributions.


%prep


%build


%install
install -m 0644 -p -D %{SOURCE0} %{buildroot}%{_sysconfdir}/yum.repos.d/audiobookshelf.repo


%files
%defattr(-,root,root,-)
%config %{_sysconfdir}/yum.repos.d/*


%changelog
* Sat Jan 21 2023 Lars Kiesow <lkiesow@uos.de> - 1-1
- Initial build
