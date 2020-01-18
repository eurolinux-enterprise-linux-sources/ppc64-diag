Name:           ppc64-diag
Version:        2.6.1
Release:        4%{?dist}
Summary:        PowerLinux Platform Diagnostics
URL:            http://sourceforge.net/projects/linux-diag/files/ppc64-diag/
Group:          System Environment/Base
License:        EPL
ExclusiveArch:  ppc ppc64
BuildRequires:  libservicelog-devel, flex, perl, byacc, librtas-devel
BuildRequires:  libvpd-devel, systemd-units
BuildRequires:  ncurses-devel
Requires:       servicelog, lsvpd
# PRRN RTAS event notification handler depends on below librtas
# and powerpc-utils versions.
Requires:	librtas >= 1.3.8
Requires:	powerpc-utils >= 1.2.16
Source0:        http://downloads.sourceforge.net/project/linux-diag/ppc64-diag/%{version}/%{name}-%{version}.tar.gz
Source1:        rtas_errd.service
Patch0:         ppc64-diag-2.4.2-messagecatalog-location.patch
Patch1:         ppc64-diag-2.4.2-chkconfig.patch
Patch2:         ppc64-diag-2.4.3-scriptlocation.patch
Patch3:         ppc64-diag-unusedvar.patch
Patch4:         ppc64-diag-2.6.1-lpdscriptloc.patch
Patch5:         ppc64-diag-2.6.1-verbose-build.patch
Patch6:         ppc64-diag-2.6.1-mode.patch

%description
This package contains various diagnostic tools for PowerLinux.
These tools captures the diagnostic events from Power Systems
platform firmware, SES enclosures and device drivers, and
write events to servicelog database. It also provides automated
responses to urgent events such as environmental conditions and
predictive failures, if appropriate modifies the FRUs fault
indicator(s) and provides event notification to system
administrators or connected service frameworks.

# BZ#860040:
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}\/usr\/libexec\/ppc64-diag\/servevent_parse.pl

%prep
%setup -q
%patch0 -p1 -b .msg_loc
%patch1 -p1 -b .chkconfig
%patch2 -p1 -b .script_loc
%patch3 -p1 -b .unusevar
%patch4 -p1 -b .lpdscriptloc
%patch5 -p1 -b .verbose
%patch6 -p1 -b .mode

%build
CFLAGS="%{optflags}" CXXFLAGS="%{optflags}" make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
chmod 644 COPYRIGHT
rm -f $RPM_BUILD_ROOT/usr/share/doc/packages/ppc64-diag/COPYRIGHT
mkdir -p $RPM_BUILD_ROOT/%{_libexecdir}/%{name}
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/init.d/rtas_errd $RPM_BUILD_ROOT/%{_libexecdir}/%{name}/
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
install -m644 %{SOURCE1} $RPM_BUILD_ROOT/%{_unitdir}
mkdir $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/ses_pages
ln -sfv %{_sbindir}/usysattn $RPM_BUILD_ROOT/%{_sbindir}/usysfault

%files
%doc COPYRIGHT
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/ses_pages
%{_mandir}/man8/*
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/%{name}/ppc64-diag.config
%attr(744,root,root) %{_sysconfdir}/%{name}/prrn_hotplug
%attr(755,root,root) %{_sbindir}/*
%dir %{_datadir}/%{name}
%dir %attr(755,root,root) %{_datadir}/%{name}/message_catalog/
%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_migrate
%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_mkrsrc
%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_notify
#%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_servagent
%attr(755,root,root) %{_libexecdir}/%{name}/ppc64_diag_setup
%attr(755,root,root) %{_libexecdir}/%{name}/lp_diag_setup
%attr(755,root,root) %{_libexecdir}/%{name}/lp_diag_notify
%attr(644,root,root) %{_libexecdir}/%{name}/servevent_parse.pl
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/cxgb3
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/e1000e
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/exceptions
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/gpfs
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/reporters
%attr(644,root,root) %{_datadir}/%{name}/message_catalog/with_regex/*
%attr(755,root,root) %{_sysconfdir}/rc.powerfail
%attr(755,root,root) %{_libexecdir}/%{name}/rtas_errd
%attr(644,root,root) %{_unitdir}/rtas_errd.service

%post
# Post-install script --------------------------------------------------
%{_libexecdir}/%{name}/lp_diag_setup --register >/dev/null
%{_libexecdir}/%{name}/ppc64_diag_setup --register >/dev/null
if [ "$1" = "1" ]; then # first install
    systemctl -q enable rtas_errd.service
    systemctl start rtas_errd.service
elif [ "$1" = "2" ]; then # upgrade
    systemctl restart rtas_errd.service
fi

%preun
# Pre-uninstall script -------------------------------------------------
if [ "$1" = "0" ]; then # last uninstall
    systemctl stop rtas_errd.service
    systemctl -q disable rtas_errd.service
    %{_libexecdir}/%{name}/ppc64_diag_setup --unregister >/dev/null
    %{_libexecdir}/%{name}/lp_diag_setup --unregister >/dev/null
fi

%triggerin -- librtas
# trigger on librtas upgrades ------------------------------------------
if [ "$2" = "2" ]; then
    systemctl restart rtas_errd.service
fi


%changelog
* Mon Mar 03 2014 Dan Horák <dhorak@redhat.com> - 2.6.1-4
- modernize spec a bit and switch to verbose build in Makefiles
- use system-wide CFLAGS during build (#1070784)
- Resolves: #1070784

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 2.6.1-3
- Mass rebuild 2013-12-27

* Tue May 21 2013 Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.1-2
- Add ncurses-devel as build dependency
- Fix script location issue

* Mon May 20 2013 Vasant Hegde <hegdevasant@linux.vnet.ibm.com> - 2.6.1
- Update to latest upstream 2.6.1

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Sep 26 2012 Karsten Hopp <karsten@redhat.com> 2.4.3-6
- revert permissions fix, filter requirement instead

* Mon Sep 24 2012 karsten Hopp <karsten@redhat.com> 2.4.3-4
- fix permissions of servevent_parse.pl

* Fri Jul 27 2012 Lukáš Nykrýn <lnykryn@redhat.com> - 2.4.3-3
- rename .service file
- auto start rtas_errd (#843471)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri May 04 2012 Karsten Hopp <karsten@redhat.com> 2.4.3-1
- update to 2.4.3

* Wed Feb 15 2012 Karsten Hopp <karsten@redhat.com> 2.4.2-5
- don't strip binaries
- fix some build issues

* Thu Sep 22 2011 Karsten Hopp <karsten@redhat.com> 2.4.2-4
- fix preun and post install scriptlets

* Fri Sep 09 2011 Karsten Hopp <karsten@redhat.com> 2.4.2-3
- add buildrequirement systemd-units for _unitdir rpm macro
- move helper scripts to libexecdir/ppc64-diag

* Wed Sep 07 2011 Karsten Hopp <karsten@redhat.com> 2.4.2-2       
- additional fixes for Fedora package review (bugzilla #736062)

* Wed Aug 17 2011 Karsten Hopp <karsten@redhat.com> 2.4.2-1
- initial Fedora version, based on IBM spec file with rpmlint cleanups
  - move scripts to /usr/share/ppc-diag
  - don't start service automatically after install
