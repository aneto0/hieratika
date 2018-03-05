# Minimal makefile for Sphinx documentation
#
export PYTHONPATH=../../server

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = asd
SPHINXAPIDOC  = sphinx-apidoc
SOURCEDIR     = source
BUILDDIR      = build
SOURCEDIR     = source

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	rm $(SOURCEDIR)/hieratika.rst
	rm $(SOURCEDIR)/hieratika.*.rst
	rm $(SOURCEDIR)/test.rst
	rm $(SOURCEDIR)/test.*.rst
	@$(SPHINXAPIDOC) -f -o source/ ../../server/
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
