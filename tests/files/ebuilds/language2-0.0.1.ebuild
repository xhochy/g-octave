# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# This ebuild was generated by g-octave

EAPI="3"
G_OCTAVE_CAT="language"

inherit g-octave

DESCRIPTION="This is the Language 2 description"
HOMEPAGE="http://language2.org"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND=">=sci-mathematics/octave-3.2.0
	>sci-mathematics/pkg8-1.0.0
	sci-mathematics/pkg7
	<sci-mathematics/pkg6-1.2.3
	>=sci-mathematics/pkg5-4.3.2"
RDEPEND="${DEPEND}"

PATCHES=(  )
