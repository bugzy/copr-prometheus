# Run tests (requires network connectivity)
%global with_check 0

%global provider        github
%global provider_tld    com
%global project         prometheus
%global repo            prometheus
# https://github.com/prometheus/prometheus/
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}

Name:           golang-%{provider}-%{project}-%{repo}
Version:        2.12.0
Release:        1%{?dist}
Summary:        The Prometheus monitoring system and time series database
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/v%{version}.tar.gz
Source1:        prometheus.service

Provides:       prometheus = %{version}-%{release}

%if 0%{?rhel} != 6
BuildRequires:  systemd
%endif

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
Prometheus, a Cloud Native Computing Foundation project, is a systems and service monitoring system.
It collects metrics from configured targets at given intervals, evaluates rule expressions, displays the results, and can trigger alerts if some condition is observed to be true.

Prometheus' main distinguishing features as compared to other monitoring systems are:

* a multi-dimensional data model (timeseries defined by metric name and set of key/value dimensions)
* a flexible query language to leverage this dimensionality
* no dependency on distributed storage; single server nodes are autonomous
* timeseries collection happens via a pull model over HTTP
* pushing timeseries is supported via an intermediary gateway
* targets are discovered via service discovery or static configuration
* multiple modes of graphing and dashboarding support
* support for hierarchical and horizontal federation


%prep
%setup -q -n %{repo}-%{version}

%build
export GO111MODULE=on
cd cmd/prometheus
go build -ldflags=-linkmode=external -mod vendor -o prometheus
cd ../promtool
go build -ldflags=-linkmode=external -mod vendor -o promtool

%install
%if 0%{?rhel} != 6
install -d -p   %{buildroot}%{_unitdir}
%endif

install -Dpm 0644 documentation/examples/prometheus.yml %{buildroot}%{_sysconfdir}/prometheus/prometheus.yml
%if 0%{?rhel} != 6
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_unitdir}/prometheus.service
%endif
install -Dpm 0755 cmd/prometheus/prometheus %{buildroot}%{_sbindir}/prometheus
install -Dpm 0755 cmd/promtool/promtool %{buildroot}%{_bindir}/promtool
install -dm 0750 %{buildroot}%{_sharedstatedir}/prometheus/

%if 0%{?with_check}
%check
export GO111MODULE=on
cd cmd/prometheus
go test -mod vendor
cd ../promtool
go test -mod vendor
%endif


%files
%if 0%{?rhel} != 6
%{_unitdir}/prometheus.service
%endif
%config(noreplace) %{_sysconfdir}/prometheus/prometheus.yml
%license LICENSE
%doc README.md CHANGELOG.md docs/
%dir %{_sharedstatedir}/prometheus/
%{_sbindir}/prometheus
%{_bindir}/promtool

%pre
getent group prometheus > /dev/null || groupadd -r prometheus
getent passwd prometheus > /dev/null || \
    useradd -rg prometheus -d /var/lib/prometheus -s /sbin/nologin \
            -c "Prometheus monitoring system" prometheus
mkdir -p /var/lib/prometheus/tsdb
chgrp prometheus /var/lib/prometheus/tsdm
chmod 771 /var/lib/prometheus/tsdm

%post
%if 0%{?rhel} != 6
%systemd_post prometheus.service
%endif

%preun
%if 0%{?rhel} != 6
%systemd_preun prometheus.service
%endif

%postun
%if 0%{?rhel} != 6
%systemd_postun prometheus.service
%endif

%changelog
