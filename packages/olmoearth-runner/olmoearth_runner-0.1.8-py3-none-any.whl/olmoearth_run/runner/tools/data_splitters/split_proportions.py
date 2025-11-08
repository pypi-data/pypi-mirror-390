"""Shared models for data splitters."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SplitProportions:
    """Container for validated split proportions.

    Attributes:
        train_prop: Proportion of data for training (0.0 to 1.0)
        val_prop: Proportion of data for validation (0.0 to 1.0)
        test_prop: Proportion of data for testing (0.0 to 1.0)
    """

    train_prop: float
    val_prop: float
    test_prop: float

    def __post_init__(self) -> None:
        """Validate split proportions after initialization.

        Raises:
            ValueError: If proportions are negative or don't sum to 1.0
        """
        # Validate proportions
        if self.train_prop < 0 or self.val_prop < 0 or self.test_prop < 0:
            raise ValueError("All proportions must be non-negative")

        total = self.train_prop + self.val_prop + self.test_prop
        if abs(total - 1.0) > 1e-9:  # Allow for small floating point errors
            raise ValueError(f"Proportions must sum to 1.0, got {total}")
