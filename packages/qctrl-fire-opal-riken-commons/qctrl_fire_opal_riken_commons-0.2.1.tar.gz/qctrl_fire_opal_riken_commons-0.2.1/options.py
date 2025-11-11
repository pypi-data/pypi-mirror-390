"""Custom types to be shared between Fire Opal client and server implementations."""

from pydantic import BaseModel
from qiskit_ibm_runtime.options import SamplerOptions
from qiskit_ibm_runtime.options.utils import Unset


class FireOpalSamplerOptions(BaseModel):
    """
    Custom set of supported `SamplerOptions` for the Fire Opal Sampler.

    Parameters
    ----------
    default_shots : int, optional
        The default number of shots to use if none are specified in the PUBs
        or in the run method. If not provided, will default to 4096.
        Defaults to None.
    """

    default_shots: int | None = None

    @classmethod
    def from_sampler_options(cls, options: SamplerOptions) -> "FireOpalSamplerOptions":
        """
        Create a `FireOpalSamplerOptions` instance from a `SamplerOptions` instance.

        Parameters
        ----------
        options : SamplerOptions
            The `SamplerOptions` instance to convert.

        Returns
        -------
        FireOpalSamplerOptions
            The corresponding `FireOpalSamplerOptions` instance.
        """
        return FireOpalSamplerOptions(
            default_shots=options.default_shots
            if options.default_shots is not Unset
            else None
        )
