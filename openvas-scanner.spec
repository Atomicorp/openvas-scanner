%global debug nil

Summary: The Open Vulnerability Assessment (OpenVAS) Server
Name:    openvas-scanner
Version: 20.8.0
Release: RELEASE-AUTO%{?dist}.art
Source0: https://github.com/greenbone/openvas-scanner/archive/v%{version}.tar.gz
#Source1: openvas-initd.sh
Source2: openvassd.conf
Source3: openvas.logrotate
Source4: openvas-scanner.sysconfig
Patch0: greenbone-nvt-update-debug.patch
License: GNU GPLv2
URL: http://www.openvas.org
Vendor: Greenbone https://www.greenbone.net
Packager: https://www.atomicorp.com
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Prefix: %{_prefix}
AutoReqProv: no
AutoReq: 0
Obsoletes: openvas-plugins, openvas-server, openvas-server-devel

Requires: redis

BuildRequires: gvm-libs, gvm-libs-devel
BuildRequires: flex 
BuildRequires: automake  libtool 
BuildRequires:  cmake >= 2.6.0
BuildRequires:  gpgme-devel
BuildRequires: doxygen
BuildRequires: libssh-devel, bison
BuildRequires: libksba-devel


%if  0%{?rhel} == 7

BuildRequires: atomic-libgcrypt, atomic-libgcrypt-devel
BuildRequires: atomic-libgpg-error, atomic-libgpg-error-devel
BuildRequires: atomic-gpgme, atomic-gpgme-devel
BuildRequires: atomic-zlib, atomic-zlib-devel
BuildRequires: atomic-sqlite, atomic-sqlite-devel
BuildRequires: atomic-libksba, atomic-libksba-devel

BuildRequires: cmake3
Requires: atomic-libksba

%else
BuildRequires: libgcrypt-devel
%endif

# Issues with mock on el8
#BuildRequires: redis

%if 0%{?rhel} >= 7 || 0%{?fedora} > 15
BuildRequires:  systemd
BuildRequires:  systemd-units
Requires(post): systemd
Requires(preun):        systemd
Requires(postun):       systemd
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

#Required by the openvas-nvt-sync and greenbone-nvt-sync
Requires:       /usr/bin/md5sum
Requires:       /usr/bin/rsync
Requires:       /usr/bin/wget
Requires:       /usr/bin/curl
Requires: 	which


Requires: gpgme 
Requires: nmap openldap-clients net-snmp-utils
Requires: rsync

%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
%filter_provides_in %{_libdir}/gvm/plugins
%filter_setup
BuildRequires: libuuid libuuid-devel
%else
BuildRequires: e2fsprogs e2fsprogs-devel
%endif

%if 0%{?fedora} >= 15
BuildRequires: libassuan libassuan-devel
%endif

%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
BuildRequires: libuuid libuuid-devel
%else
BuildRequires: e2fsprogs e2fsprogs-devel
%endif


# OV-7
%if  0%{?rhel} == 6
BuildRequires: atomic-gnutls3-gnutls-devel
BuildRequires: atomic-glib2-glib2-devel
BuildRequires: atomic-libxslt-libxslt-devel

BuildConflicts: gnutls gnutls-devel
Requires: atomic-gnutls3-gnutls atomic-glib2-glib2 atomic-libxslt-libxslt
%else
BuildRequires: gnutls-devel
BuildRequires: glib2 >= 2.6.0, glib2-devel >= 2.6.0,
%endif


BuildRequires: libxslt libxslt-devel
BuildRequires: libpcap-devel



 
%description
openvas-scanner is the server component of the Network Vulnerabilty Scanner suite OpenVAS.

%prep
%autosetup -p 1 -n openvas-%{version} -b 0


%build

export CFLAGS="$RPM_OPT_FLAGS -Wno-deprecated-declarations "

%if  0%{?rhel} == 7
        export CC="gcc -Wl,-rpath,/opt/atomicorp/atomic/root/usr/lib64/,-rpath,/opt/atomicorp/atomic/root/usr/lib64/heimdal/"
        export PATH="/opt/atomicorp/atomic/root/usr/bin:$PATH"
        export LDFLAGS="-L/opt/atomicorp/atomic/root/usr/lib64/ -lgcrypt -ldl -lgpg-error"
        export CFLAGS="$CFLAGS -I/opt/atomicorp/atomic/root/usr/include/"
        export PKG_CONFIG_PATH="/opt/atomicorp/atomic/root/usr/lib64/pkgconfig"
        export CMAKE_PREFIX_PATH="/opt/atomicorp/atomic/root/"

%else
        export CFLAGS="$RPM_OPT_FLAGS -Wno-deprecated-declarations -Wno-format-truncation"

%endif



%if 0%{?fedora} >= 30
# disable warnings -> error for stringop-truncation for now
export CFLAGS="%{optflags} -Wno-error=deprecated-declarations -Wno-error=stringop-truncation -Wno-error=format-truncation="
%endif



%if  0%{?rhel} == 7
cmake3 \
%else
%cmake \
%endif
	-DCMAKE_VERBOSE_MAKEFILE=ON \
        -DCMAKE_INSTALL_PREFIX=%{_prefix} \
        -DSYSCONFDIR=%{_sysconfdir} \
        -DLIBDIR=%{_libdir} \
        -DLOCALSTATEDIR=%{_localstatedir} \
	-DOPENVAS_NVT_DIR=/var/lib/gvm/plugins \
	-DOPENVAS_RUN_DIR=/var/run/gvm


# smp flags will sometimes break on el5
%{__make} 


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALL="install -p"
find %{buildroot} -name '*.la' -exec rm -f {} ';'

mkdir -p %{buildroot}/var/lib/gvm/gnupg
mkdir -p %{buildroot}/var/lib/gvm/plugins
mkdir -p %{buildroot}/var/lib/gvm/cert-data
mkdir -p %{buildroot}/var/lib/gvm/scap-data
mkdir -p %{buildroot}/var/run/gvm/

# Make plugin cache directory
mkdir -p %{buildroot}/%{_var}/cache/gvm

# Make the log dir
mkdir -p %{buildroot}/%{_var}/log/gvm

# Make the sysconfig dir
mkdir -p %{buildroot}/%{_sysconfdir}/gvm/
mkdir -p %{buildroot}/%{_sysconfdir}/gvm/gnupg




# Install initial configuration
#install -Dp -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/openvas/
sed -e "s:@@OPENVAS_PLUGINS@@:%{_var}/lib/gvm/plugins:g
        s:@@OPENVAS_CACHE@@:%{_var}/cache/gvm:g
        s:@@OPENVAS_LOGDIR@@:%{_var}/log/gvm:g
        s:@@OPENVAS_SYSCONF@@:%{_sysconfdir}/gvm:g" %{SOURCE2} > openvas.conf
install -Dp -m 644 openvas.conf %{buildroot}/%{_sysconfdir}/openvas/openvas.conf

# install log rotation stuff
install -m 644 -Dp %{SOURCE3} \
        %{buildroot}/%{_sysconfdir}/logrotate.d/openvas-scanner

# Install sysconfig configration
install -Dp -m 644 %{SOURCE4} %{buildroot}/%{_sysconfdir}/sysconfig/openvas-scanner


%pre
if ! id -g gvm > /dev/null 2>&1; then
	groupadd -r gvm
fi

if ! id -g gvm > /dev/null 2>&1; then
	useradd -g gvm -G gvm -d /var/lib/gvm -r -s /bin/bash gvm
fi



%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
#%doc COPYING 
%config(noreplace) /etc/openvas/openvas.conf
%config(noreplace) /etc/openvas/openvas_log.conf
%config(noreplace) %{_sysconfdir}/sysconfig/openvas-scanner
%config(noreplace) %{_sysconfdir}/logrotate.d/openvas-scanner
%{_bindir}/openvas-nasl
%{_bindir}/openvas-nasl-lint
#%{_sbindir}/greenbone-nvt-sync
#%{_sbindir}/openvassd
# el8
#%{_bindir}/greenbone-nvt-sync
#%{_bindir}/openvassd
#%{_sbindir}/openvas
/usr/bin/greenbone-nvt-sync
/usr/sbin/openvas
%dir %{_sysconfdir}/gvm
%dir %{_sysconfdir}/gvm/gnupg
%{_mandir}/man8/greenbone-nvt-sync.8.*
%attr(770,gvm,gvm) %dir %{_var}/log/gvm
%attr(770,gvm,gvm) %dir %{_var}/lib/gvm
%attr(770,gvm,gvm) %dir %{_var}/cache/gvm
%attr(770,gvm,gvm) %dir %{_var}/lib/gvm/plugins
%attr(770,gvm,gvm) %dir /var/lib/gvm/cert-data
%attr(770,gvm,gvm) %dir /var/lib/gvm/scap-data
%attr(770,gvm,gvm) %dir /var/run/gvm/
#%dir %{_var}/lib/openvas/plugins/nvt
#%dir %{_var}/lib/openvas/plugins/gsf
%dir %{_var}/lib/gvm/gnupg
%{_libdir}/libopenvas*
#/usr/share/doc/openvas-scanner/*
# Other el8 changes
/usr/share/man/man1/openvas*
/usr/share/man/man8/openvas.8.gz



%changelog
* Sat Sep 26 2020 Scott R. Shinn <scott@atomicorp.com> - 20.8.0-RELEASE-AUTO
- Fix for GVM issue #31

* Sat Aug 15 2020 Scott R. Shinn <scott@atomicorp.com> - 20.8.0-RELEASE-AUTO
- Update to 20.8.0

* Fri Apr 5 2019 Scott R. Shinn <scott@atomicorp.com> - 6.0.0-RELEASE-AUTO
- Update to 6.0.0

* Tue Sep 13 2016 Scott R. Shinn <scott@atomicorp.com> - 5.0.7-24
- Update to 5.0.7

* Wed Aug 31 2016 Scott R. Shinn <scott@atomicorp.com> - 5.0.6-24
- Update to 5.0.6

* Tue Dec 22 2015 Scott R. Shinn <scott@atomicorp.com> - 5.0.5-23
- Update to 5.0.5

* Mon Jul 13 2015 Scott R. Shinn <scott@atomicorp.com> - 5.0.4-22
- Update to 5.0.4

* Wed Jun 3 2015 Scott R. Shinn <scott@atomicorp.com> - 5.0.3-21
- Add systemd logic

* Sat May 23 2015 Scott R. Shinn <scott@atomicorp.com> - 5.0.3-20
- Update to 5.0.3

* Tue Mar 17 2015 Scott R. Shinn <scott@atomicorp.com> - 4.0.6-19
- Update to 4.0.6

* Mon Dec 15 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.5-18
- Update for Fedora 21

* Thu Nov 27 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.5-17
- Update to 4.0.5

* Mon Nov 17 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.4-16
- Update to 4.0.4

* Tue Sep 9 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.3-15
- Update to 4.0.3

* Fri Aug 1 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.2-14
- Update to 4.0.2

* Wed Jul 30 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.1-13
- Bugfix: Add gnupg directory (Credits: Nelson Estrada)

* Thu Jun 19 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.1-12
- Force rpath settings on EL6

* Mon Jun 16 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.1-11
- Add logic for El6

* Mon Jun 9 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.1-10
- Bugfix #XXX, Update init script 

* Mon May 5 2014 Scott R. Shinn <scott@atomicorp.com> - 4.0.1-9
- Update to 4.0.1

* Fri Feb 28 2014 Scott R. Shinn <scott@atomicorp.com> - 3.4.1-8
- Update to 3.4.1

* Thu Apr 25 2013 Scott R. Shinn <scott@atomicorp.com> - 3.4.0-7
- Bugfix #XXX, create /etc/openvas/gnupg. This fixes credential support

* Thu Apr 18 2013 Scott R. Shinn <scott@atomicorp.com> - 3.4.0-5
- Update to 3.4.0

* Wed Jan 16 2013 Scott R. Shinn <scott@atomicorp.com> - 3.3.1-4
- bugfix #XXX, add PATH to openvas-nvt-sync-cron jobs

* Fri Nov 23 2012 Scott R. Shinn <scott@atomicorp.com> - 3.3.1-3
- bugfix #XXX, add PATH to openvas-nvt-sync jobs

* Thu May 10 2012 Scott R. Shinn <scott@atomicorp.com> - 3.3.1-2
- Update to 3.3.1

* Tue Apr 24 2012 Scott R. Shinn <scott@atomicorp.com> - 3.3.0-1
- Update to 3.3.0

* Fri Nov 4 2011 Scott R. Shinn <scott@atomicorp.com> - 3.2.5-1
- Update to 3.2.5

* Thu Jun 9 2011 Scott R. Shinn <scott@atomicorp.com> - 3.2.4-1
- Update to 3.2.4

* Mon Apr 11 2011 Scott R. Shinn <scott@atomicorp.com> - 3.2.3-1
- Update to 3.2.3

* Wed Feb 23 2011 Scott R. Shinn <scott@atomicorp.com> - 3.2.2-2
- Minor post config updates

* Tue Feb 22 2011 Scott R. Shinn <scott@atomicorp.com> - 3.2.2-1
- Update to 3.2.2

* Thu Feb 17 2011 Scott R. Shinn <scott@atomicorp.com> - 3.2.1-1
- Update to 3.2.1

* Wed Dec 29 2010 Scott R. Shinn <scott@atomicorp.com> - 3.2-0.2
- Update to 3.2 rc1

* Sun Dec 5 2010 Scott R. Shinn <scott@atomicorp.com> - 3.2-0.1
- Update to 3.2 beta1

* Thu Oct 21 2010 Scott R. Shinn <scott@atomicorp.com> - 3.1.0-6
- Added Requires on which
- Removed requires on nikto, amap, hydra, and ike-scan
- Relinked for wmi client libraries

* Mon Aug 30 2010 Scott R. Shinn <scott@atomicorp.com> - 3.1.0-5
- Added OPTIONS support to sysconfig & init scripts
- Minor change to openvas.logrotate to focus on just the openvassd log files

* Tue Jul 27 2010 Scott R. Shinn <scott@atomicorp.com> - 3.1.0-4
- Update to 3.1.0 final

* Thu Jul 1 2010 Scott R. Shinn <scott@atomicorp.com> - 3.1.0-3
- Update to 3.1.0rc3

* Mon Jun 28 2010 Scott R. Shinn <scott@atomicorp.com> - 3.1.0-2
- Update to 3.1.0rc2

* Wed May 19 2010 Scott R. Shinn <scott@atomicorp.com> - 3.1.0-1
- Update to 3.1.0rc1

* Mon Mar 22 2010 Scott R. Shinn <scott@atomicorp.com> - 3.0.2-1
- Update to 3.0.2

* Thu Jan 28 2010 Scott R. Shinn <scott@atomicorp.com> - 3.0.1-1
- Update to 3.0.1

* Wed Jan 13 2010 Scott R. Shinn <scott@atomicorp.com> - 3.0.0-2
- Bugfix #XXX, corrected path in init script to point to the correct openvassd daemon
- Bugfix #XXX, configured system to create the /var/cache/openvas dir by default

* Fri Dec 18 2009 Scott R. Shinn <scott@atomicrocketturtle.com> - 3.0.0-1
- update to 3.0.0

* Wed Aug 19 2009 Scott R. Shinn <scott@atomicrocketturtle.com> - 2.0.3-1
- update to 2.0.3

* Wed Jun 3 2009 Scott R. Shinn <scott@atomicrocketturtle.com> - 2.0.2-1
- update to 2.0.2

* Thu Feb 26 2009 Scott R. Shinn <scott@atomicrocketturtle.com> - 2.0.1-1
- update to 2.0.1 

* Tue Dec 30 2008 Scott R. Shinn <scott@atomicrocketturtle.com> - 2.0.0-2
- Added init scripts and post install routine
- Bugfix #xxx, resolved libopenvas.2 linking issue

* Mon Dec 22 2008 Scott R. Shinn <scott@atomicrocketturtle.com>
- Update to 2.0.0 Final

* Fri Dec 12 2008 Scott R. Shinn <scott@atomicrocketturtle.com>
- Update to 2.0.0.rc1

* Mon Nov 17 2008 Scott R. Shinn <scott@atomicrocketturtle.com>
- Added Requires for port scanners, ovaldi, and ldapclient
- Added Requires for hydra
- Update to beta2

* Fri Nov 7 2008 Scott R. Shinn <scott@atomicrocketturtle.com>
- Update to 2.0.0.beta1
- Import into ART

* Fri Apr 18 2008 Jan-Oliver Wagner <jan-oliver.wagner@intevation.de>
  - Adapated for Fedora 8 (naming)
  - %post and %postrun changed to apply ldconfig directly instead of using
    a (SUSE specific?) scriplet.
* Wed Apr 16 2008 Jan-Oliver Wagner <jan-oliver.wagner@intevation.de>
  Initial OpenSUSE 10.2 spec file, tested for i586
