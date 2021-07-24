BUILDDIR = build
JS_NOTEST = build/fish.js build/stack.js build/stack_op.js build/codebox_op.js build/sanity.js

all : $(BUILDDIR)/lib.js $(BUILDDIR)/test.js
	cat $^ | sed 's/import.*//g' | sed 's/export//g' > $(BUILDDIR)/hoho.js

build/lib.js : $(JS_NOTEST)
	cat $^ | sed 's/import.*//g' | sed 's/export//g' > $@

build/%.js : %.ts
	tsc $< --target esnext --lib esnext,dom --outDir $(BUILDDIR)

clean :
	rm -f $(BUILDDIR)/*.js
