#!/usr/bin/make -f

patternfly = v3.0.0

all: provokator/static/vendor/patternfly

src/${patternfly}.tar.gz:
	mkdir -p src
	cd src && curl -sLO https://github.com/patternfly/patternfly/archive/${patternfly}.tar.gz

provokator/static/vendor/patternfly: src/${patternfly}.tar.gz
	rm -rf $@
	mkdir -p $@
	cd src && tar -xf ${patternfly}.tar.gz -C ../$@ --strip-components=2 --mode a-X '*/dist'
	chmod 644 $@/*/*.*

clean:
	rm -rf src provokator/static/vendor

# EOF
