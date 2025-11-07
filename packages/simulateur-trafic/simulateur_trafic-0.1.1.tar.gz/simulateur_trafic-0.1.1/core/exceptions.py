"""Exception hierarchy for the core traffic simulation package."""

from __future__ import annotations

__all__ = [
    "SimulationError",
    "ConfigurationError",
    "ConfigurationFileNotFoundError",
    "ConfigurationFormatError",
    "InvalidSimulationParameterError",
    "RouteError",
    "RouteNotFoundError",
    "RouteCapacityError",
    "VehicleError",
    "VehicleAlreadyPresentError",
    "InvalidVehicleStateError",
    "AnalysisError",
    "MissingDataError",
    "DivisionByZeroAnalysisError",
]


class SimulationError(Exception):
    """Base exception for all simulation related errors."""


class ConfigurationError(SimulationError):
    """Raised when the simulation configuration data is invalid."""


class ConfigurationFileNotFoundError(FileNotFoundError, ConfigurationError):
    """Configuration file could not be located."""


class ConfigurationFormatError(ConfigurationError, ValueError):
    """Configuration file exists but does not follow the expected schema."""


class InvalidSimulationParameterError(SimulationError, ValueError):
    """Simulation parameters are inconsistent or invalid."""


class RouteError(SimulationError):
    """Base error for route management issues."""


class RouteNotFoundError(RouteError, LookupError):
    """Requested route does not exist within the network."""


class RouteCapacityError(RouteError):
    """Route capacity is exceeded."""


class VehicleError(SimulationError):
    """Base error for vehicle related issues."""


class VehicleAlreadyPresentError(VehicleError):
    """Vehicle already exists on the route or network."""


class InvalidVehicleStateError(VehicleError, ValueError):
    """Vehicle was instantiated or updated with an invalid state."""


class AnalysisError(SimulationError):
    """Base class for analytics/statistics failures."""


class MissingDataError(AnalysisError):
    """Raised when an analysis requires unavailable data."""


class DivisionByZeroAnalysisError(AnalysisError, ZeroDivisionError):
    """Raised when an analysis would perform a division by zero."""
