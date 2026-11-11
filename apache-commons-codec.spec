%global base_name codec
%global short_name commons-%{base_name}
%bcond_with javadoc

Name:          apache-%{short_name}
Version:       1.23.0
Release:       2
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
# Gradle 9.9.1 strictly pins commons-codec:commons-codec 1.18.0.
Source2:       https://archive.apache.org/dist/commons/codec/source/commons-codec-1.18.0-src.tar.gz

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
Phonetic and URLs. 1.23.0 stays the default jar. Gradle 9.9.1 strictly
pins 1.18.0, so that jar is installed beside it.

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
%setup -q -T -D -a 2 -n commons-codec-%{version}-src
cp %{SOURCE1} aspell-mail.txt
sed -i 's/\r//' RELEASE-NOTES*.txt LICENSE.txt NOTICE.txt
find . -name '*.jar' -delete

%build -a
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
mkdir -p codec118/classes
find commons-codec-1.18.0-src/src/main/java -name '*.java' > codec118/sources.list
test -s codec118/sources.list
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-d codec118/classes @codec118/sources.list
"$JAVA_HOME/bin/jar" cf codec118/commons-codec.jar -C codec118/classes .
cat > codec118/commons-codec.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>commons-codec</groupId>
  <artifactId>commons-codec</artifactId>
  <version>1.18.0</version>
  <name>Apache Commons Codec</name>
  <description>Implementations of common encoders and decoders.</description>
  <url>https://commons.apache.org/proper/commons-codec/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
</project>
EOF

%install -p
sysjar install --buildroot %{buildroot} \
	--artifact codec118/commons-codec.pom:codec118/commons-codec.jar \
	--file-name commons-codec-1.18.0 \
	--filelist .mfiles118
# 1.23.0 owns commons-codec.sysjar. 1.18.0 keeps a second index file.
/bin/mv %{buildroot}/usr/share/sysjar/index/commons-codec/commons-codec.sysjar \
	%{buildroot}/usr/share/sysjar/index/commons-codec/commons-codec-1.18.0.sysjar
sed -i 's|/usr/share/sysjar/index/commons-codec/commons-codec\.sysjar|/usr/share/sysjar/index/commons-codec/commons-codec-1.18.0.sysjar|' .mfiles118

%install -a
while IFS= read -r line; do
	grep -qxF -- "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
done < .mfiles118

%check -a
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
cat > CodecSmoke.java << 'EOF'
import org.apache.commons.codec.binary.Hex;
public class CodecSmoke {
	public static void main(String[] args) {
		String hex = Hex.encodeHexString(new byte[]{0x2a});
		if (!"2a".equals(hex)) {
			throw new AssertionError(hex);
		}
		System.out.println(args[0] + " " + hex);
	}
}
EOF
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{buildroot}%{_javadir}/commons-codec.jar CodecSmoke.java
"$JAVA_HOME/bin/java" -cp "%{buildroot}%{_javadir}/commons-codec.jar:." CodecSmoke codec123_ok | tee check123.log
grep -F -q 'codec123_ok 2a' check123.log
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{buildroot}%{_javadir}/commons-codec-1.18.0.jar CodecSmoke.java
"$JAVA_HOME/bin/java" -cp "%{buildroot}%{_javadir}/commons-codec-1.18.0.jar:." CodecSmoke codec118_ok | tee check118.log
grep -F -q 'codec118_ok 2a' check118.log

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt RELEASE-NOTES* aspell-mail.txt

%if %{with javadoc}
%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt aspell-mail.txt

%endif
