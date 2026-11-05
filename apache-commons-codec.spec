%global base_name codec
%global short_name commons-%{base_name}
%bcond_with javadoc

Name:          apache-%{short_name}
Version:       1.23.0
Release:       1
Group:         Development/Java
Summary:       Implementations of common encoders and decoders
License:       ASL 2.0
URL:           https://commons.apache.org/%{base_name}/
BuildArch:     noarch
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{short_name} --link %{name} --alias %{short_name}:%{short_name}

Source0:       https://archive.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
# Data in DoubleMetaphoneTest.java originally has an inadmissible license.
# The author gives MIT in e-mail communication.
Source1:       aspell-mail.txt

BuildRequires: mvn(org.apache.commons:commons-parent:pom::)

# It looks like there are packages in F-18 that BR/R the short name
Provides: %{short_name} = %{version}-%{release}
Obsoletes: %{short_name} < %{version}-%{release}
# Provide and obsolete jakarta-commons-codec to support installing this
# package on RHEL 6, which still uses the old jakarta-commons-* package
# naming scheme.
Provides: jakarta-%{short_name} = %{version}-%{release}
Obsoletes: jakarta-%{short_name} < %{version}-%{release}

%description
Commons Codec is an attempt to provide definitive implementations of
commonly used encoders and decoders. Examples include Base64, Hex,
Phonetic and URLs.

%if %{with javadoc}
%package javadoc
Summary:       API documentation for %{name}
Provides: jakarta-%{short_name}-javadoc = %{version}-%{release}
Obsoletes: jakarta-%{short_name}-javadoc < %{version}-%{release}

%endif
%if %{with javadoc}
%description javadoc
%{summary}.

%endif
%prep
%setup -q -n commons-codec-%{version}-src
cp %{SOURCE1} aspell-mail.txt
sed -i 's/\r//' RELEASE-NOTES*.txt LICENSE.txt NOTICE.txt


%files -f .mfiles
%doc LICENSE.txt NOTICE.txt RELEASE-NOTES* aspell-mail.txt

%if %{with javadoc}
%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt aspell-mail.txt

%endif
