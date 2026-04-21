from unittest import TestCase
from unittest.mock import patch

import models.activation as activation_module
import models.asset as asset_module
from data.db import Base, make_engine, make_session_factory


class RepositoryTestCase(TestCase):
    """Create an isolated in-memory database for ORM repository tests."""

    def setUp(self) -> None:
        """Create an isolated database and bind all repositories to it."""
        self.engine = make_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_factory = make_session_factory(self.engine)

        self.activation_session_patch = patch.object(
            activation_module,
            "SessionLocal",
            new=self.session_factory,
        )
        self.asset_session_patch = patch.object(
            asset_module,
            "SessionLocal",
            new=self.session_factory,
        )
        self.activation_session_patch.start()
        self.asset_session_patch.start()

    def tearDown(self) -> None:
        """Stop repository patches and dispose of the test database."""
        self.asset_session_patch.stop()
        self.activation_session_patch.stop()
        self.engine.dispose()
