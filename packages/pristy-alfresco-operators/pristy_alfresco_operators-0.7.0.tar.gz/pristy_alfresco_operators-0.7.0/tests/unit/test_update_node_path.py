# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for update_node_path function.
"""

import pytest
from unittest.mock import patch
from pristy.alfresco_operator.update_node_path import update_node_path


class TestUpdateNodePath:
    """Tests for update_node_path function."""

    def test_default_root_path(self):
        """Test default root path when no variables are set."""
        src_node = {"path": {"name": "/Company Home/Documents/File.pdf"}}
        new_node = {"path": {}}

        with patch("pristy.alfresco_operator.update_node_path.Variable") as mock_var:
            mock_var.get.return_value = None

            update_node_path(src_node, new_node)

            assert new_node["path"]["root"] == "root"
            assert new_node["path"]["short"] == "/Company Home/Documents/File.pdf"

    def test_target_site_injection(self):
        """Test injection into a target site."""
        src_node = {
            "path": {
                "name": "/Company Home/Sites/old-site/documentLibrary/Folder/File.pdf"
            }
        }
        new_node = {"path": {}}

        with patch("pristy.alfresco_operator.update_node_path.Variable") as mock_var:

            def variable_get(key, default_var=None):
                if key == "alfresco_export_target_site":
                    return "new-site"
                return default_var

            mock_var.get.side_effect = variable_get

            update_node_path(src_node, new_node)

            assert new_node["path"]["root"] == "site:new-site"
            assert new_node["path"]["short"] == "/Folder/File.pdf"

    def test_target_site_documentLibrary_root(self):
        """Test documentLibrary at root level."""
        src_node = {"path": {"name": "/Company Home/Sites/test-site/documentLibrary"}}
        new_node = {"path": {}}

        with patch("pristy.alfresco_operator.update_node_path.Variable") as mock_var:

            def variable_get(key, default_var=None):
                if key == "alfresco_export_target_site":
                    return "target-site"
                return default_var

            mock_var.get.side_effect = variable_get

            update_node_path(src_node, new_node)

            assert new_node["path"]["root"] == "site:target-site"
            assert new_node["path"]["short"] == "/"

    def test_target_site_other_container(self):
        """Test other site containers (links, wiki, etc.)."""
        src_node = {"path": {"name": "/Company Home/Sites/old-site/wiki"}}
        new_node = {"path": {}}

        with patch("pristy.alfresco_operator.update_node_path.Variable") as mock_var:

            def variable_get(key, default_var=None):
                if key == "alfresco_export_target_site":
                    return "new-site"
                return default_var

            mock_var.get.side_effect = variable_get

            update_node_path(src_node, new_node)

            assert new_node["path"]["root"] == "site:new-site"
            assert new_node["path"]["short"] == "/wiki"

    def test_target_root_uuid(self):
        """Test injection into specific folder by UUID."""
        src_node = {"path": {"name": "/Company Home/Shared/Documents/File.pdf"}}
        new_node = {"path": {}}

        with patch("pristy.alfresco_operator.update_node_path.Variable") as mock_var:

            def variable_get(key, default_var=None):
                if key == "alfresco_target_root_uuid":
                    return "workspace://SpacesStore/target-folder-uuid"
                return default_var

            mock_var.get.side_effect = variable_get

            update_node_path(src_node, new_node)

            assert (
                new_node["path"]["root"]
                == "node:workspace://SpacesStore/target-folder-uuid"
            )
            assert (
                new_node["path"]["short"] == "/Company Home/Shared/Documents/File.pdf"
            )

    def test_short_path_remove(self):
        """Test custom path prefix removal."""
        src_node = {"path": {"name": "/prefix/to/remove/remaining/path"}}
        new_node = {"path": {}}

        with patch("pristy.alfresco_operator.update_node_path.Variable") as mock_var:

            def variable_get(key, default_var=None):
                if key == "short_path_remove":
                    return "/prefix/to/remove"
                return default_var

            mock_var.get.side_effect = variable_get

            update_node_path(src_node, new_node)

            assert new_node["path"]["short"] == "/remaining/path"

    def test_french_locale_path(self):
        """Test path with French locale (Espace racine instead of Company Home)."""
        src_node = {
            "path": {"name": "/Espace racine/Sites/test-site/documentLibrary/Dossiers"}
        }
        new_node = {"path": {}}

        with patch("pristy.alfresco_operator.update_node_path.Variable") as mock_var:

            def variable_get(key, default_var=None):
                if key == "alfresco_export_target_site":
                    return "target-site"
                return default_var

            mock_var.get.side_effect = variable_get

            update_node_path(src_node, new_node)

            assert new_node["path"]["root"] == "site:target-site"
            assert new_node["path"]["short"] == "/Dossiers"

    def test_priority_target_site_over_uuid(self):
        """Test that target_site takes priority over target_root_uuid."""
        src_node = {
            "path": {"name": "/Company Home/Sites/old-site/documentLibrary/File.pdf"}
        }
        new_node = {"path": {}}

        with patch("pristy.alfresco_operator.update_node_path.Variable") as mock_var:

            def variable_get(key, default_var=None):
                if key == "alfresco_export_target_site":
                    return "new-site"
                if key == "alfresco_target_root_uuid":
                    return "workspace://SpacesStore/uuid"
                return default_var

            mock_var.get.side_effect = variable_get

            update_node_path(src_node, new_node)

            # Should use site, not UUID
            assert new_node["path"]["root"] == "site:new-site"
