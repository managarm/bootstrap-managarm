
c := cross/autoconf-v2.64

.PHONY: all-$c
all-$c: $(TREEPATH)/$c/build.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $(TREEPATH)/$c/*.tag
	
$(TREEPATH)/$c/build.tag: c := $c
$(TREEPATH)/$c/build.tag: $(TREEPATH)/$c/configure.tag
	cd $(TREEPATH)/$c/build && make && make install
	touch $@

$(TREEPATH)/$c/init.tag: c := $c
$(TREEPATH)/$c/init.tag:
	git submodule update --init $c/src
	touch $@

$(TREEPATH)/$c/configure.tag: c := $c
$(TREEPATH)/$c/configure.tag: $(TREEPATH)/$c/init.tag
	rm -rf $(TREEPATH)/$c/build
	rm -rf $(TREEPATH)/host-roots/autoconf-v2.64
	mkdir -p $(TREEPATH)/$c/build
	mkdir -p $(TREEPATH)/host-roots/autoconf-v2.64
	cd $(TREEPATH)/$c/build && ../src/configure --prefix=$(TREEPATH)/host-roots/autoconf-v2.64
	touch $@

