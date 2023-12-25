%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post %{nil}

%define  date      20221226041111
%define  nversion  N-109457-geeb280f351

Name:          ffmpeg
Summary:       Hyper fast MPEG1/MPEG4/H263/RV and AC3/MPEG audio encoder
Version:       6.1
Release:       1%{?dist}
License:       GPLv3+
Group:         System Environment/Libraries

Source:        https://radosgw.public.os.wwu.de/opencast-ffmpeg-static/%{name}-%{version}-amd64-static.tar.xz
URL:           https://ffmpeg.org
BuildRoot:     %{_tmppath}/%{name}-root


%description
FFmpeg is a very fast video and audio converter. It can also grab from a
live audio/video source.
The command line interface is designed to be intuitive, in the sense that
ffmpeg tries to figure out all the parameters, when possible. You have
usually to give only the target bitrate you want. FFmpeg can also convert
from any sample rate to any other, and resize video on the fly with a high
quality polyphase filter.


%prep
%setup -q -n %{name}-%{version}-amd64-static


%build


%install
rm -rf %{buildroot}

install -p -d -m 0755 %{buildroot}%{_bindir}
install -p -d -m 0755 %{buildroot}%{_mandir}
install -p ffmpeg %{buildroot}%{_bindir}
install -p ffprobe %{buildroot}%{_bindir}
install -p qt-faststart %{buildroot}%{_bindir}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc GPLv3.txt
%{_bindir}/*


%changelog
* Fri Nov 24 2023 Lars Kiesow <lkiesow@uos.de> - 6.1-1
- Update to static 6.1

* Wed Dec 14 2022 Lars Kiesow <lkiesow@uos.de> - 5.1.2.git.20221212044324-1
- Update to latest git version

* Tue Jun 14 2022 Lars Kiesow <lkiesow@uos.de> - 5.0.1.git.20220613051048-1
- Update to latest git version

* Mon Jan 17 2022 Lars Kiesow <lkiesow@uos.de> - 5.0.git.20220117045355-1
- Update to latest git version

* Sun Jan 16 2022 Lars Kiesow <lkiesow@uos.de> - 4.4.1.git.20211115053315-1
- Update to latest git version

* Fri May 07 2021 Lars Kiesow <lkiesow@uos.de> - 4.4.git.20210427042125-1
- Update to latest git version

* Thu Dec 17 2020 Lars Kiesow <lkiesow@uos.de> - 4.3.1.git.20201216040124-1
- Update to latest git version

* Tue Jun 16 2020 Lars Kiesow <lkiesow@uos.de> - 4.3.git.20200616044012-1
- Update to latest git version

* Fri Jun 14 2019 Lars Kiesow <lkiesow@uos.de> 4.1.git.20190614175409-1
- now using actual ffmpeg version

* Tue May 14 2019 Lars Kiesow <lkiesow@uos.de> - 4.1.git.20190514042936-1
- initial build
