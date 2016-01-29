# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals

from astropy.tests.helper import pytest
from gammapy.datasets import gammapy_extra
from gammapy.scripts import SpectrumPipe
from gammapy.utils.scripts import read_yaml
from gammapy.utils.testing import requires_dependency, requires_data

try:
    from sherpa.stats import WStat
except ImportError:
    HAS_WSTAT = False
else:
    HAS_WSTAT = True


@requires_dependency('scipy')
@requires_dependency('sherpa')
@pytest.mark.skipif(not HAS_WSTAT, reason="Wstat only in sherpa head version")
@requires_data('gammapy-extra')
def test_spectrum_pipe(tmpdir):
    configfile = gammapy_extra.filename('test_datasets/spectrum/spectrum_pipe_example.yaml')
    config = read_yaml(configfile)
    config['base_config']['general']['outdir'] = str(tmpdir)
    pipe = SpectrumPipe.from_config(config, auto_outdir=False)
    pipe.run()

