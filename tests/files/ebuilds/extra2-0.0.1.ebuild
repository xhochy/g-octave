# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# This ebuild was generated by g-octave

EAPI="3"

G_OCTAVE_CAT="extra"

inherit g-octave

DESCRIPTION="This is the Extra 2 description"
HOMEPAGE="http://extra2.org"

LICENSE="|| ( GPL-2 GPL-3 LGPL BSD GFDL )"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND=">sci-mathematics/pkg8-1.0.0
	sci-mathematics/pkg7
	<sci-mathematics/pkg6-1.2.3
	>=sci-mathematics/pkg5-4.3.2"
RDEPEND="${DEPEND}
	>=sci-mathematics/octave-3.2.0"
