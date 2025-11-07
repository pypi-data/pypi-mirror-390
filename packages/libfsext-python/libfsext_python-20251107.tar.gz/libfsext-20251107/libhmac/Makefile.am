if HAVE_LOCAL_LIBHMAC
AM_CPPFLAGS = \
	-I../include -I$(top_srcdir)/include \
	-I../common -I$(top_srcdir)/common \
	@LIBCERROR_CPPFLAGS@ \
	@LIBCRYPTO_CPPFLAGS@ \
	@PTHREAD_CPPFLAGS@ 

noinst_LTLIBRARIES = libhmac.la

libhmac_la_SOURCES = \
	libhmac_byte_stream.h \
	libhmac_definitions.h \
	libhmac_extern.h \
	libhmac_error.c libhmac_error.h \
	libhmac_libcerror.h \
	libhmac_md5.c libhmac_md5.h \
	libhmac_md5_context.c libhmac_md5_context.h \
	libhmac_sha1.c libhmac_sha1.h \
	libhmac_sha1_context.c libhmac_sha1_context.h \
	libhmac_sha224.c libhmac_sha224.h \
	libhmac_sha224_context.c libhmac_sha224_context.h \
	libhmac_sha256.c libhmac_sha256.h \
	libhmac_sha256_context.c libhmac_sha256_context.h \
	libhmac_sha512.c libhmac_sha512.h \
	libhmac_sha512_context.c libhmac_sha512_context.h \
	libhmac_support.c libhmac_support.h \
	libhmac_types.h \
	libhmac_unused.h
endif

DISTCLEANFILES = \
	Makefile \
	Makefile.in

sources-local: $(BUILT_SOURCES)

splint-local:
	@echo "Running splint on libhmac ..."
	-splint -preproc -redef $(DEFS) $(DEFAULT_INCLUDES) $(INCLUDES) $(AM_CPPFLAGS) $(libhmac_la_SOURCES)

