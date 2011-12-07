##############################################################################
#
# Copyright (C) 2006-2008 Red Hat, Inc. All rights reserved.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License version 2.
#
###############################################################################


%define PEGASUS_PROVIDERS_DIR %{_libdir}/Pegasus/providers


############ SRPM ###################


Name: clustermon
Version: 0.16.2
Release: 10%{?dist}
License: GPLv2
URL: http://sources.redhat.com/cluster/conga

Group: System Environment/Base
Summary: Monitoring and management of Red Hat Cluster Suite

Source0: http://people.redhat.com/rmccabe/conga/fedora/src/clustermon-0.16.2.tar.gz
Patch0: bz581661.patch
Patch1: bz588520.patch
Patch2: bz553382-Fix-initscript-return-code.patch
Patch3: bz612752.patch
Patch4: bz603913.patch

# Patch 100..199 are for SNMP subsystem
Patch101: bz561413-01-Fix-REDHAT-MIB-smilint-issues.patch
Patch102: bz561413-02-Update-REDHAT-CLUSTER-MIB.patch
Patch103: bz561413-03-Add-rhcClusterConfigurationVersion-hand.patch
Patch104: bz561413-04-Fix-XML-comparison.patch
Patch105: bz561413-05-Fix-missing-definition.patch
Patch106: bz561413-06-Fix-config_version-presentation.patch
Patch107: bz561413-07-Add-node-ID-to-snmp-output.patch
Patch108: bz561413-08-Update-MIBs.patch
Patch109: bz561413-09-Add-cache-to-ClusterMonitor-objects.patch
Patch110: bz561413-10-Add-trap-support-to-SNMP-agent.patch
Patch111: bz561413-11-Fix-snmpd-README.patch
Patch112: bz561413-12-Put-OIDs-in-one-place.patch
Patch113: bz561413-13-Convert-traps-to-C.patch
Patch114: bz561413-14-Send-quorum-state-change-trap.patch
Patch115: bz561413-15-Cache-quorum-and-vote-states.patch
Patch116: bz561413-16-Add-SNMP-traps-for-services-node-events.patch
Patch117: bz561413-17-Clean-up-MIB-add-missing-notification.patch


Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: clusterlib-devel
BuildRequires: libxml2-devel openssl-devel dbus-devel pam-devel pkgconfig
BuildRequires: net-snmp-devel tog-pegasus-devel

ExclusiveArch: i686 x86_64

%description
This package contains Red Hat Cluster Suite SNMP/CIM module/agent/provider.

%prep
%setup -q
%patch0 -p1 -b .bz581661
%patch1 -p1 -b .bz588520
%patch2 -p1 -b .bz553382
%patch3 -p1 -b .bz612752
%patch4 -p1 -b .bz603913

# BZ561413 - SNMP traps
%patch101 -p1 -b .bz561413
%patch102 -p1 -b .bz561413
%patch103 -p1 -b .bz561413
%patch104 -p1 -b .bz561413
%patch105 -p1 -b .bz561413
%patch106 -p1 -b .bz561413
%patch107 -p1 -b .bz561413
%patch108 -p1 -b .bz561413
%patch109 -p1 -b .bz561413
%patch110 -p1 -b .bz561413
%patch111 -p1 -b .bz561413
%patch112 -p1 -b .bz561413
%patch113 -p1 -b .bz561413
%patch114 -p1 -b .bz561413
%patch115 -p1 -b .bz561413
%patch116 -p1 -b .bz561413
%patch117 -p1 -b .bz561413

%build
%configure		--arch=%{_arch} \
		--docdir=%{_docdir} \
		--pegasus_providers_dir=%{PEGASUS_PROVIDERS_DIR} \
		--include_zope_and_plone=no

make %{?_smp_mflags} clustermon

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install_clustermon

%clean
rm -rf %{buildroot}

### cluster module ###

%package -n modcluster
Group: System Environment/Base
Summary: Red Hat Cluster Suite - remote management

Requires: oddjob dbus
Requires(post): chkconfig initscripts
Requires(preun): chkconfig initscripts
Requires(postun): initscripts

%description -n modcluster
Management module for Red Hat Cluster Suite.

%files -n modcluster
%defattr(-,root,root)
%config(noreplace)	%{_sysconfdir}/oddjobd.conf.d/modcluster.oddjob.conf
%config(noreplace)	%{_sysconfdir}/dbus-1/system.d/modcluster.systembus.conf
			%{_sysconfdir}/rc.d/init.d/modclusterd
			%{_libexecdir}/modcluster
			%{_sbindir}/modclusterd
			%{_docdir}/modcluster-%{version}/


%post -n modcluster
/sbin/chkconfig --add modclusterd
DBUS_PID=`cat /var/run/messagebus.pid 2>/dev/null`
/bin/kill -s SIGHUP $DBUS_PID >&/dev/null
# It's ok if this fails (it will fail when oddjob is not running).
/sbin/service oddjobd reload >&/dev/null
exit 0

%preun -n modcluster
if [ "$1" == "0" ]; then
	/sbin/service modclusterd stop >&/dev/null
	/sbin/chkconfig --del modclusterd
fi
exit 0

%postun -n modcluster
if [ "$1" == "0" ]; then
	DBUS_PID=`cat /var/run/messagebus.pid 2> /dev/null`
	/bin/kill -s SIGHUP $DBUS_PID >&/dev/null
	/sbin/service oddjobd reload >&/dev/null
fi
if [ "$1" == "1" ]; then
	/sbin/service modclusterd condrestart >&/dev/null
fi
exit 0


### cluster-snmp ###

%package -n cluster-snmp
Group: System Environment/Base
Summary: Red Hat Enterprise Linux Cluster Suite - SNMP agent

Requires: modcluster = %{version}-%{release}
Requires: net-snmp oddjob
Requires(post): initscripts
Requires(postun): initscripts

%description -n cluster-snmp
SNMP agent for Red Hat Cluster Suite.

%files -n cluster-snmp
%defattr(-,root,root)
			%{_libdir}/cluster-snmp/
			%{_datadir}/snmp/mibs/REDHAT-MIB
			%{_datadir}/snmp/mibs/REDHAT-CLUSTER-MIB
			%{_docdir}/cluster-snmp-%{version}/

%post -n cluster-snmp
/sbin/service snmpd condrestart >&/dev/null
exit 0

%postun -n cluster-snmp
# don't restart snmpd twice on upgrades
if [ "$1" == "0" ]; then
	/sbin/service snmpd condrestart >&/dev/null
fi
exit 0



### cluster-cim ###

%package -n cluster-cim
Group: System Environment/Base
Summary: Red Hat Cluster Suite - CIM provider

Requires: modcluster = %{version}-%{release}
Requires: tog-pegasus oddjob
Requires(post): initscripts
Requires(postun): initscripts

%description -n cluster-cim
CIM provider for Red Hat Enterprise Linux Cluster Suite.

%files -n cluster-cim
%defattr(-,root,root)
			%{PEGASUS_PROVIDERS_DIR}/libRedHatClusterProvider.so
			%{_docdir}/cluster-cim-%{version}/

%post -n cluster-cim
# pegasus might not be running, don't fail
/sbin/service tog-pegasus condrestart >&/dev/null
exit 0

%postun -n cluster-cim
# don't restart pegasus twice on upgrades
if [ "$1" == "0" ]; then
	/sbin/service tog-pegasus condrestart >&/dev/null
fi
# pegasus might not be running, don't fail
exit 0


%changelog
* Tue Aug 03 2010 Ryan McCabe <rmccabe@redhat.com> - 0.16.2-10
- Fix cluster status passing among nodes via modclusterd
- Resolves: rhbz#603913

* Fri Jul 09 2010 Chris Feist <cfeist@redhat.com> - 0.16.2-9
- Modclusterd will now start even if IPv6 is disabled
- Resolves: rhbz#612752

* Tue May 18 2010 Lon Hohberger <lhh@redhat.com> - 0.16.2-7
- Add missing SNMP notifications to MIB and clean MIB up
- Fix initscript return code when an invalid operation was
  specified
- Resolves: rhbz#553382 rhbz#561413

* Mon May 17 2010 Lon Hohberger <lhh@redhat.com> - 0.16.2-6
- Fix Changelog
- Add SNMP traps for service state changes, node state changes,
  quorum changes, and configuration updates
- Resolves: rhbz#561413

* Wed May 12 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0-16.2-5
- Do not build on ppc and ppc64.
  Resolves: rhbz#590982

* Mon May 03 2010 Chris Feist <cfeist@redhat.cmo> - 0.16.2-4
- Clustermon will now properly shutdown services on version 6
  clusters.
- Resolves: rhbz#588520

* Fri Apr 16 2010 Chris Feist <cfeist@redhat.cmo> - 0.16.2-3
- Adding additional logging of cluster actions through ricci
- Resolves: rhbz#581661

* Thu Feb 25 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.16.2-2
- Resolves: rhbz#568000
- Do not build clustermon on s390 and s390x

* Thu Jan 14 2010 Ryan McCabe <rmccabe@redhat.com> - 0.16.2-1
- Make the modclusterd init script exit with status 2 when invalid
  arguments are provided

* Mon Aug 31 2009 Ryan McCabe <rmccabe@redhat.com> - 0.16.1-2
- Forward port from F11.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Apr 16 2009 Ryan McCabe <rmccabe@redhat.com> 0.16.1-1
- Fix memory corruption bug.
- Cleanup stale code paths.

* Mon Mar 30 2009 Ryan McCabe <rmccabe@redhat.com> 0.16.0-1
- Remove legacy RHEL4 and RHEL5-specific code.
- Fix build issues uncovered by g++ 4.4
- Apply patch provided for bz480151

* Tue Feb 03 2009 Fabio M. Di Nitto <fdinitto@redhat.com> 0.15.0-8
- Merge sparc support patch from F10 branch.
- BuildRequires clusterlib-devel instead of cmanlib-devel.

* Thu Jan 15 2009 Tomas Mraz <tmraz@redhat.com> 0.15.0-7
- rebuild with new openssl

* Wed Oct 15 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-6
- Don't make failing to update the cluster version a fatal error when trying to set a new configuration file.

* Mon Oct 06 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-5
- Update the cman configuration version when propagating a new cluster.conf
  via "ccs_sync"

* Fri Sep 26 2008 Fabio M. Di Nitto <fdinitto@redhat.com> 0.15.0-3
 - Change BuildRequires from cman-devel to cmanlib-devel

* Thu Sep 25 2008 Fabio M. Di Nitto <fdinitto@redhat.com> 0.15.0-2
 - Add versioned BR on cman-devel

* Tue Sep 09 2008 Ryan McCabe <rmccabe@redhat.com> 0.15.0-1
 - Restore missing XVM.cpp file for modcluster

* Fri Jun 06 2008 Ryan McCabe <rmccabe@redhat.com> 0.13.0-4
 - Recognize F9 by name (Sulphur).

* Tue May 20 2008 Ryan McCabe <rmccabe@redhat.com> 0.13.0-3
- Initial build.
