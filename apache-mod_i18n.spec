#Module-Specific definitions
%define mod_name mod_i18n
%define mod_conf B13_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	A Apache module allowing to use gettext as a output filter 
Name:		apache-%{mod_name}
Version:	0
Release:	%mkrel 4
Group:		System/Servers
License:	Apache License
URL:		http://www.heute-morgen.de/modules/mod_i18n/
Source0:	http://www.heute-morgen.de/modules/mod_i18n/mod_i18n.c
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache-mpm-prefork >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
Requires:	apache-mod_xml2
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	apache-mod_xml2-devel
BuildRequires:	libxml2-devel
BuildRequires:	libapreq-devel
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_i18n implements Zopes i18n namespace in an output filter. It thereby allows
gettext based internationalization of arbitray html content delivered by
apache. The i18n attribute that are currently implemented are: translate, name,
domain, target attribute will soon follow.

%prep

%setup -q -c -T -n %{mod_name}

cp %{SOURCE0} mod_i18n.c
cp %{SOURCE1} %{mod_conf}

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%{_sbindir}/apxs -c `xml2-config --cflags` -I%{_includedir}/mod_xml2 mod_i18n.c %{_libdir}/libxml2.la %{_libdir}/libapreq2.la

head -70 mod_i18n.c > README

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -m0755 .libs/%{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
