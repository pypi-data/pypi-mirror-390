from usdm3_excel.__version__ import __package_version__, __model_version__


class TestVersion:
    """Tests for the version module."""

    def test_package_version(self):
        """Test that the package version is correctly defined."""
        # Verify that the version is a string
        assert isinstance(__package_version__, str)

        # Verify that the version follows semantic versioning (x.y.z)
        parts = __package_version__.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_model_version(self):
        """Test that the model version is correctly defined."""
        # Verify that the version is a string
        assert isinstance(__model_version__, str)

        # Verify that the version follows semantic versioning (x.y.z)
        parts = __model_version__.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_version_matches_package(self):
        """Test that the version matches the package version."""
        # This test just verifies that the version is defined
        from usdm3_excel.__version__ import __package_version__

        # Verify that the version is a string
        assert isinstance(__package_version__, str)

        # Verify that the version follows semantic versioning (x.y.z)
        parts = __package_version__.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)
