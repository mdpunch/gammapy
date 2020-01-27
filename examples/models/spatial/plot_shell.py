r"""
.. _shell-spatial-model:

Shell Spatial Model
===================

The shell spatial model is defined by the following equations:

.. math::
    \phi(lon, lat) = \frac{3}{2 \pi (r_{out}^3 - r_{in}^3)} \cdot
            \begin{cases}
                \sqrt{r_{out}^2 - \theta^2} - \sqrt{r_{in}^2 - \theta^2} &
                             \text{for } \theta \lt r_{in} \\
                \sqrt{r_{out}^2 - \theta^2} &
                             \text{for } r_{in} \leq \theta \lt r_{out} \\
                0 & \text{for } \theta > r_{out}
            \end{cases}

where :math:`\theta` is the sky separation and :math:`r_{\text{out}} = r_{\text{in}}` + width

Note that the normalization is a small angle approximation,
although that approximation is still very good even for 10 deg radius shells.

"""

# %%
# Example plot
# ------------
# Here is an example plot of the model:

from gammapy.modeling.models import (
    ShellSpatialModel,
    SkyModel,
    Models,
    PowerLawSpectralModel,
)

model = ShellSpatialModel(
    lon_0="10 deg", lat_0="20 deg", radius="2 deg", width="0.5 deg", frame="galactic",
)

ax = model.plot()

# %%
# YAML representation
# -------------------
# Here is an example YAML file using the model:

pwl = PowerLawSpectralModel()
shell = ShellSpatialModel()

model = SkyModel(spectral_model=pwl, spatial_model=shell)
models = Models([model])

print(models.to_yaml())
