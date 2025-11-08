class BiasVarBOError(Exception):
    """Base class for all package-specific exceptions."""

class ConfigError(BiasVarBOError):
    """Invalid or inconsistent configuration supplied by the user."""

class SpaceError(BiasVarBOError):
    """Search space definition or transformation error."""

class SurrogateError(BiasVarBOError):
    """Surrogate model failed to fit/predict or encountered invalid inputs."""

class AcquisitionError(BiasVarBOError):
    """Acquisition function evaluation/optimization failed."""

class SchedulerError(BiasVarBOError):
    """Batch/asynchronous suggestion scheduling failed."""

class RiskComputationError(BiasVarBOError):
    """Risk estimator (CV/SURE/PAC-Bayes) encountered an error."""
