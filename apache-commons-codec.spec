%global base_name codec
%global short_name commons-%{base_name}

# enable OSGi automatic dep solving
%global _use_internal_dependency_generator 0
%global __find_provides /usr/lib/rpm/osgideps.pl -p
%global __find_requires /usr/lib/rpm/osgideps.pl -r

Name:          apache-%{short_name}
Version:       1.4
Release:       12
Summary:       Implementations of common encoders and decoders
Group:         Development/Java
License:       ASL 2.0
URL:           http://commons.apache.org/%{base_name}/

Source0:       http://archive.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:     noarch

BuildRequires: java-devel >= 0:1.6.0
BuildRequires: jpackage-utils
BuildRequires: maven2-plugin-antrun
BuildRequires: maven2-plugin-assembly
BuildRequires: maven2-plugin-compiler
BuildRequires: maven2-plugin-idea
BuildRequires: maven2-plugin-install
BuildRequires: maven2-plugin-jar
BuildRequires: maven2-plugin-javadoc
BuildRequires: maven2-plugin-resources
BuildRequires: maven-doxia-sitetools
BuildRequires: maven-plugin-bundle
BuildRequires: maven-surefire-maven-plugin
BuildRequires: maven-surefire-provider-junit
Requires:      java >= 0:1.6.0
Requires:      jpackage-utils
Requires(post):jpackage-utils
Requires(postun):jpackage-utils

Provides:      jakarta-%{short_name} = %{version}-%{release}
Obsoletes:     jakarta-%{short_name} < %{version}-%{release}
# It looks like there are packages in F-13 that BR/R the short name
Provides:      %{short_name} = %{version}-%{release}
Obsoletes:     %{short_name} < %{version}-%{release}

%description
Commons Codec is an attempt to provide definitive implementations of
commonly used encoders and decoders. Examples include Base64, Hex,
Phonetic and URLs.

%package javadoc
Summary:       API documentation for %{name}
Group:         Development/Java
Requires:      jpackage-utils
Obsoletes:     jakarta-%{short_name}-javadoc < %{version}-%{release}

%description javadoc
%{summary}.

%prep
%setup -q -n %{short_name}-%{version}-src

sed -i 's/\r//' RELEASE-NOTES*.txt LICENSE.txt NOTICE.txt

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mvn-jpp \
    -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
    install javadoc:javadoc

%install
rm -rf %{buildroot}

# jars
install -pD -T target/%{short_name}-%{version}.jar \
  %{buildroot}%{_javadir}/%{short_name}.jar
(cd %{buildroot}%{_javadir} && for jar in *; do ln -sf ${jar} `echo $jar| sed "s|%{short_name}|%{name}|g"`; done)

# javadocs
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -pr target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}

# pom
install -pD -T -m 644 pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{short_name}.pom
%add_to_maven_depmap org.apache.commons %{short_name} %{version} JPP %{short_name}

# following line is only for backwards compatibility. New packages
# should use proper groupid org.apache.commons
%add_to_maven_depmap %{short_name} %{short_name} %{version} JPP %{short_name}

%clean
rm -rf %{buildroot}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%pre javadoc
# workaround for rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :

%files
%defattr(-,root,root,-)
%doc LICENSE.txt NOTICE.txt RELEASE-NOTES*
%{_mavendepmapfragdir}/*
%{_mavenpomdir}/*
%{_javadir}/*

%files javadoc
%defattr(-,root,root,-)
%doc LICENSE.txt
%{_javadocdir}/%{name}

