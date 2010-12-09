# -*- coding: utf-8 -*-

"""
    overlay.py
    ~~~~~~~~~~
    
    This module implements a function to create an overlay to host the
    ebuilds generated by g-octave.
    
    :copyright: (c) 2009-2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from __future__ import absolute_import

__all__ = ['create_overlay']

import os
import sys
import shutil
import portage.output

from .config import Config, ConfigException
from .compat import open

out = portage.output.EOutput()

def create_overlay(force=False, conf=None, quiet=False):
    
    # the function parameter conf is used by the tests
    if conf is None:
        conf = Config()
    
    if force and os.path.exists(conf.overlay):
        shutil.rmtree(conf.overlay)
    
    if not os.path.exists(os.path.join(conf.overlay, 'profiles', 'repo_name')):
        
        if not quiet:
            out.ebegin('Creating overlay: %s' % conf.overlay)
        
        try:
            # creating dirs
            for _dir in ['profiles', 'eclass']:
                dir = os.path.join(conf.overlay, _dir)
                if not os.path.exists(dir) or force:
                    os.makedirs(dir, 0o755)
            
            # creating files
            files = {
                os.path.join(conf.overlay, 'profiles', 'repo_name'): 'g-octave',
                os.path.join(conf.overlay, 'profiles', 'categories'): 'g-octave',
            }
            
            # symlinking g-octave eclass
            local_eclass = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'share', 'g-octave.eclass'
            )
            global_eclass = os.path.join(sys.prefix, 'share', 'g-octave', 'g-octave.eclass')
            overlay_eclass = os.path.join(conf.overlay, 'eclass', 'g-octave.eclass')
            if os.path.exists(local_eclass):
                os.symlink(local_eclass, overlay_eclass)
            elif os.path.exists(global_eclass):
                os.symlink(global_eclass, overlay_eclass)
            else:
                if not quiet:
                    out.eend(1)
                sys.exit(1)
            for _file in files:
                if not os.path.exists(_file) or force:
                    with open(_file, 'w') as fp:
                        content = files[_file]
                        if hasattr(content, 'name'):
                            content = content.read()
                        fp.write(content)
        except Exception as error:
            if not quiet:
                out.eend(1)
            sys.exit(1)
        else:
            if not quiet:
                out.eend(0)
