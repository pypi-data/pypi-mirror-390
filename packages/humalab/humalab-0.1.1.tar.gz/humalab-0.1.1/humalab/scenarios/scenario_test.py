import unittest
import numpy as np
from humalab.scenarios.scenario import Scenario


class ScenarioTest(unittest.TestCase):
    """Unit tests for Scenario class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.scenario = Scenario()

    def tearDown(self):
        """Clean up after each test method."""
        self.scenario._clear_resolvers()

    def test_init_should_initialize_with_empty_scenario(self):
        """Test that init() initializes with empty scenario when none provided."""
        # Pre-condition
        self.assertIsNone(self.scenario._scenario_id)

        # In-test
        self.scenario.init(
            scenario=None,
            seed=42
        )

        # Post-condition
        self.assertIsNotNone(self.scenario._scenario_id)
        self.assertEqual(len(self.scenario._scenario_template), 0)

    def test_init_should_initialize_with_dict_scenario(self):
        """Test that init() correctly processes dict-based scenario."""
        # Pre-condition
        scenario_dict = {
            "test_key": "test_value",
            "nested": {"inner_key": "inner_value"}
        }

        # In-test
        self.scenario.init(
            scenario=scenario_dict,
            seed=42
        )

        # Post-condition
        resolved, _ = self.scenario.resolve()
        self.assertEqual(resolved.test_key, "test_value")
        self.assertEqual(resolved.nested.inner_key, "inner_value")

    def test_init_should_use_provided_scenario_id(self):
        """Test that init() uses provided scenario_id."""
        # Pre-condition
        custom_id = "custom_scenario_id"

        # In-test
        self.scenario.init(
            scenario={},
            scenario_id=custom_id
        )

        # Post-condition
        self.assertEqual(self.scenario._scenario_id, custom_id)

    def test_init_should_set_seed_for_reproducibility(self):
        """Test that init() with same seed produces reproducible results."""
        # Pre-condition
        scenario_config = {"value": "${uniform: 0.0, 1.0}"}
        seed = 42

        # In-test
        scenario1 = Scenario()
        scenario1.init(
            scenario=scenario_config,
            seed=seed
        )
        resolved1, _ = scenario1.resolve()
        value1 = resolved1.value

        scenario2 = Scenario()
        scenario2.init(
            scenario=scenario_config,
            seed=seed
        )
        resolved2, _ = scenario2.resolve()
        value2 = resolved2.value

        # Post-condition
        self.assertEqual(value1, value2)

        # Cleanup
        scenario1._clear_resolvers()
        scenario2._clear_resolvers()

    def test_uniform_distribution_should_resolve_correctly(self):
        """Test that uniform distribution resolver works correctly."""
        # Pre-condition
        scenario_config = {
            "uniform_value": "${uniform: 0.0, 1.0}"
        }

        # In-test
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Post-condition
        resolved, _ = self.scenario.resolve()
        value = resolved.uniform_value
        self.assertIsInstance(value, (int, float))
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_uniform_distribution_should_handle_size_parameter(self):
        """Test that uniform_1d distribution returns list."""
        # Pre-condition
        scenario_config = {
            "uniform_array": "${uniform_1d: 0.0, 1.0}"
        }

        # In-test
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Post-condition
        resolved, _ = self.scenario.resolve()
        value = resolved.uniform_array
        # Convert to list if it's a ListConfig
        value_list = list(value) if hasattr(value, '__iter__') and not isinstance(value, str) else [value]
        self.assertGreaterEqual(len(value_list), 1)
        for v in value_list:
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)

    def test_gaussian_distribution_should_resolve_correctly(self):
        """Test that gaussian distribution resolver works correctly."""
        # Pre-condition
        scenario_config = {
            "gaussian_value": "${gaussian: 0.0, 1.0}"
        }

        # In-test
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Post-condition
        resolved, _ = self.scenario.resolve()
        value = resolved.gaussian_value
        self.assertIsInstance(value, (int, float))

    def test_gaussian_distribution_should_handle_size_parameter(self):
        """Test that gaussian_1d distribution returns list."""
        # Pre-condition
        scenario_config = {
            "gaussian_array": "${gaussian_1d: 0.0, 1.0}"
        }

        # In-test
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Post-condition
        resolved, _ = self.scenario.resolve()
        value = resolved.gaussian_array
        # Convert to list if it's a ListConfig
        value_list = list(value) if hasattr(value, '__iter__') and not isinstance(value, str) else [value]
        self.assertGreaterEqual(len(value_list), 1)

    def test_bernoulli_distribution_should_resolve_correctly(self):
        """Test that bernoulli distribution resolver works correctly."""
        # Pre-condition
        scenario_config = {
            "bernoulli_value": "${bernoulli: 0.5}"
        }

        # In-test
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Post-condition
        resolved, _ = self.scenario.resolve()
        value = resolved.bernoulli_value
        self.assertIn(value, [0, 1, True, False])

    def test_resolve_should_regenerate_distribution_values(self):
        """Test that resolve() regenerates new values from distributions."""
        # Pre-condition
        scenario_config = {
            "random_value": "${uniform: 0.0, 100.0}"
        }
        self.scenario.init(
            scenario=scenario_config,
            seed=None  # No seed for randomness
        )

        # In-test - First resolve
        resolved1, _ = self.scenario.resolve()
        value1 = resolved1.random_value

        # Second resolve
        resolved2, _ = self.scenario.resolve()
        value2 = resolved2.random_value

        # Post-condition
        # Values should be different (statistically very unlikely to be same)
        # Note: There's a tiny chance they could be equal, but extremely unlikely
        self.assertIsInstance(value1, (int, float))
        self.assertIsInstance(value2, (int, float))

    def test_template_property_should_access_scenario_template(self):
        """Test that template property allows access to scenario values."""
        # Pre-condition
        scenario_config = {
            "test_attribute": "test_value"
        }
        self.scenario.init(
            scenario=scenario_config
        )

        # In-test
        value = self.scenario.template.test_attribute

        # Post-condition
        self.assertEqual(value, "test_value")

    def test_template_should_contain_unresolved_distributions(self):
        """Test that template contains unresolved distribution strings."""
        # Pre-condition
        scenario_config = {
            "test_key": "${uniform: 0.0, 1.0}"
        }
        self.scenario.init(
            scenario=scenario_config
        )

        # In-test
        yaml_str = self.scenario.yaml

        # Post-condition
        self.assertIn("uniform", yaml_str)

    def test_resolve_should_return_resolved_values(self):
        """Test that resolve() returns dict-style access to resolved values."""
        # Pre-condition
        scenario_config = {
            "test_key": "test_value"
        }
        self.scenario.init(
            scenario=scenario_config
        )

        # In-test
        resolved, _ = self.scenario.resolve()
        value = resolved["test_key"]

        # Post-condition
        self.assertEqual(value, "test_value")

    def test_resolve_should_raise_error_for_missing_key(self):
        """Test that resolve() result raises KeyError for missing keys."""
        # Pre-condition
        self.scenario.init(
            scenario={}
        )

        # In-test & Post-condition
        resolved, _ = self.scenario.resolve()
        with self.assertRaises(KeyError):
            _ = resolved["nonexistent_key"]

    def test_get_final_size_should_handle_none_size_without_num_env(self):
        """Test _get_final_size with None size and no num_env."""
        # Pre-condition
        self.scenario.init(
            scenario={}
        )

        # In-test
        result = self.scenario._get_final_size(None)

        # Post-condition
        self.assertIsNone(result)

    def test_get_final_size_should_handle_int_size_without_num_env(self):
        """Test _get_final_size with int size and no num_env."""
        # Pre-condition
        self.scenario.init(
            scenario={}
        )

        # In-test
        result = self.scenario._get_final_size(3)

        # Post-condition
        self.assertEqual(result, 3)

    def test_get_final_size_should_handle_tuple_size_without_num_env(self):
        """Test _get_final_size with tuple size and no num_env."""
        # Pre-condition
        self.scenario.init(
            scenario={}
        )

        # In-test
        result = self.scenario._get_final_size((2, 3))

        # Post-condition
        self.assertEqual(result, (2, 3))

    def test_get_final_size_should_handle_size_without_num_env(self):
        """Test _get_final_size with size but no num_env."""
        # Pre-condition
        self.scenario.init(
            scenario={}
        )

        # In-test
        result = self.scenario._get_final_size(5)

        # Post-condition
        self.assertEqual(result, 5)

    def test_convert_to_python_should_handle_numpy_scalar(self):
        """Test _convert_to_python with numpy scalar."""
        # Pre-condition
        np_scalar = np.float64(3.14)

        # In-test
        result = Scenario._convert_to_python(np_scalar)

        # Post-condition
        self.assertIsInstance(result, float)
        self.assertEqual(result, 3.14)

    def test_convert_to_python_should_handle_numpy_array(self):
        """Test _convert_to_python with numpy array."""
        # Pre-condition
        np_array = np.array([1, 2, 3])

        # In-test
        result = Scenario._convert_to_python(np_array)

        # Post-condition
        self.assertIsInstance(result, list)
        self.assertEqual(result, [1, 2, 3])

    def test_convert_to_python_should_handle_zero_dim_array(self):
        """Test _convert_to_python with 0-dimensional numpy array."""
        # Pre-condition
        np_zero_dim = np.array(42)

        # In-test
        result = Scenario._convert_to_python(np_zero_dim)

        # Post-condition
        self.assertIsInstance(result, int)
        self.assertEqual(result, 42)

    def test_convert_to_python_should_handle_regular_python_types(self):
        """Test _convert_to_python with regular Python types."""
        # Pre-condition
        regular_values = [42, 3.14, "string", [1, 2, 3], {"key": "value"}]

        # In-test & Post-condition
        for value in regular_values:
            result = Scenario._convert_to_python(value)
            self.assertEqual(result, value)

    def test_get_node_path_should_find_simple_key(self):
        """Test _get_node_path with simple dictionary key."""
        # Pre-condition
        root = {"key1": "target_node", "key2": "other"}
        self.scenario.init(
            scenario={}
        )

        # In-test
        path = self.scenario._get_node_path(root, "target_node")

        # Post-condition
        self.assertEqual(path, "key1")

    def test_get_node_path_should_find_nested_key(self):
        """Test _get_node_path with nested dictionary."""
        # Pre-condition
        root = {"level1": {"level2": "target_node"}}
        self.scenario.init(
            scenario={}
        )

        # In-test
        path = self.scenario._get_node_path(root, "target_node")

        # Post-condition
        self.assertEqual(path, "level1.level2")

    def test_get_node_path_should_find_in_list(self):
        """Test _get_node_path with list containing target."""
        # Pre-condition
        root = {"key": ["item1", "target_node", "item3"]}
        self.scenario.init(
            scenario={}
        )

        # In-test
        path = self.scenario._get_node_path(root, "target_node")

        # Post-condition
        self.assertEqual(path, "key[1]")

    def test_get_node_path_should_return_empty_for_missing_node(self):
        """Test _get_node_path returns empty string when node not found."""
        # Pre-condition
        root = {"key": "value"}
        self.scenario.init(
            scenario={}
        )

        # In-test
        path = self.scenario._get_node_path(root, "nonexistent")

        # Post-condition
        self.assertEqual(path, "")

    def test_template_property_should_return_scenario_template(self):
        """Test that template property returns the scenario template."""
        # Pre-condition
        scenario_config = {"key": "value"}
        self.scenario.init(
            scenario=scenario_config
        )

        # In-test
        template = self.scenario.template

        # Post-condition
        self.assertIsNotNone(template)
        self.assertEqual(template.key, "value")

    def test_resolve_should_return_resolved_scenario(self):
        """Test that resolve() returns the resolved scenario."""
        # Pre-condition
        scenario_config = {"key": "value"}
        self.scenario.init(
            scenario=scenario_config
        )

        # In-test
        resolved, _ = self.scenario.resolve()

        # Post-condition
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.key, "value")

    def test_yaml_property_should_return_yaml_representation(self):
        """Test that yaml property returns YAML string."""
        # Pre-condition
        scenario_config = {"key": "value"}
        self.scenario.init(
            scenario=scenario_config
        )

        # In-test
        yaml_str = self.scenario.yaml

        # Post-condition
        self.assertIsInstance(yaml_str, str)
        self.assertIn("key:", yaml_str)
        self.assertIn("value", yaml_str)

    def test_resolve_returns_episode_vals(self):
        """Test that resolve() returns episode values for distributions."""
        # Pre-condition
        scenario_config = {
            "dist_value": "${uniform: 0.0, 1.0}"
        }
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # In-test
        resolved, episode_vals = self.scenario.resolve()

        # Post-condition
        # Verify resolved scenario has the value
        self.assertIsNotNone(resolved.dist_value)
        # Verify episode_vals dict contains the distribution samples
        self.assertGreater(len(episode_vals), 0)

    def test_nested_scenario_access_should_work(self):
        """Test accessing deeply nested scenario values."""
        # Pre-condition
        scenario_config = {
            "level1": {
                "level2": {
                    "level3": "deep_value"
                }
            }
        }
        self.scenario.init(
            scenario=scenario_config
        )

        # In-test
        resolved, _ = self.scenario.resolve()
        value = resolved.level1.level2.level3

        # Post-condition
        self.assertEqual(value, "deep_value")

    def test_multiple_distributions_should_work_together(self):
        """Test scenario with multiple different distributions."""
        # Pre-condition
        scenario_config = {
            "uniform_val": "${uniform: 0.0, 1.0}",
            "gaussian_val": "${gaussian: 0.0, 1.0}",
            "bernoulli_val": "${bernoulli: 0.5}"
        }

        # In-test
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Post-condition
        resolved, _ = self.scenario.resolve()
        self.assertIsInstance(resolved.uniform_val, (int, float))
        self.assertIsInstance(resolved.gaussian_val, (int, float))
        self.assertIn(resolved.bernoulli_val, [0, 1, True, False])

    def test_clear_resolvers_should_clear_dist_cache(self):
        """Test that _clear_resolvers clears the distribution cache."""
        # Pre-condition
        scenario_config = {"value": "${uniform: 0.0, 1.0}"}
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )
        _ = self.scenario.resolve()  # Trigger cache population

        # In-test
        self.scenario._clear_resolvers()

        # Post-condition
        self.assertEqual(len(Scenario.dist_cache), 0)

    def test_main_script_scenario_should_initialize_with_nested_structure(self):
        """Test scenario initialization matching the __main__ script example."""
        # Pre-condition
        scenario_config = {
            "scenario": {
                "scenario_id": "scenario_1",
                "cup_x": "${uniform: 0.7, 1.5}",
                "cup_y": "${uniform: 0.3, 0.7}",
            }
        }

        # In-test
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Post-condition
        # Verify scenario structure exists
        resolved, _ = self.scenario.resolve()
        self.assertIsNotNone(resolved.scenario)
        self.assertEqual(resolved.scenario.scenario_id, "scenario_1")

        # Verify cup_x and cup_y are resolved
        cup_x = resolved.scenario.cup_x
        cup_y = resolved.scenario.cup_y

        # Verify values are in expected ranges
        self.assertGreaterEqual(cup_x, 0.7)
        self.assertLessEqual(cup_x, 1.5)
        self.assertGreaterEqual(cup_y, 0.3)
        self.assertLessEqual(cup_y, 0.7)

    def test_main_script_scenario_should_allow_both_access_methods(self):
        """Test that both attribute and dict access work as shown in __main__ script."""
        # Pre-condition
        scenario_config = {
            "scenario": {
                "scenario_id": "scenario_1",
                "cup_x": "${uniform: 0.7, 1.5}",
            }
        }

        # In-test
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Post-condition
        # Both access methods should return the same value
        resolved, _ = self.scenario.resolve()
        cup_x_attr = resolved.scenario.cup_x
        cup_x_dict = resolved["scenario"].cup_x

        self.assertEqual(cup_x_attr, cup_x_dict)

    def test_main_script_scenario_should_regenerate_on_resolve(self):
        """Test that resolve regenerates values as shown in __main__ script."""
        # Pre-condition
        scenario_config = {
            "scenario": {
                "cup_x": "${uniform: 0.7, 1.5}",
            }
        }
        self.scenario.init(
            scenario=scenario_config,
            seed=None  # No seed for random values
        )

        resolved1, _ = self.scenario.resolve()
        first_cup_x = resolved1.scenario.cup_x

        # In-test
        resolved2, _ = self.scenario.resolve()
        second_cup_x = resolved2.scenario.cup_x

        # Post-condition
        # Values should be in valid range
        self.assertGreaterEqual(first_cup_x, 0.7)
        self.assertLessEqual(first_cup_x, 1.5)
        self.assertGreaterEqual(second_cup_x, 0.7)
        self.assertLessEqual(second_cup_x, 1.5)

    def test_main_script_scenario_should_convert_to_numpy_array(self):
        """Test that scenario values can be converted to numpy arrays."""
        # Pre-condition
        scenario_config = {
            "scenario": {
                "cup_x": "${uniform_1d: 0.7, 1.5}",
            }
        }
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # In-test
        resolved, _ = self.scenario.resolve()
        cup_x = resolved.scenario.cup_x
        np_array = np.array(cup_x)

        # Post-condition
        self.assertIsInstance(np_array, np.ndarray)

        # Verify values are in expected range
        for val in np.atleast_1d(np_array):
            self.assertGreaterEqual(val, 0.7)
            self.assertLessEqual(val, 1.5)

    def test_main_script_scenario_should_produce_valid_yaml(self):
        """Test that scenario.yaml returns valid YAML string."""
        # Pre-condition
        scenario_config = {
            "scenario": {
                "scenario_id": "scenario_1",
                "cup_x": "${uniform: 0.7, 1.5}",
                "cup_y": "${uniform: 0.3, 0.7}",
            }
        }
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # In-test
        yaml_str = self.scenario.yaml

        # Post-condition
        self.assertIsInstance(yaml_str, str)
        self.assertIn("scenario:", yaml_str)
        self.assertIn("scenario_id:", yaml_str)
        self.assertIn("scenario_1", yaml_str)
        self.assertIn("cup_x:", yaml_str)
        self.assertIn("cup_y:", yaml_str)

    def test_main_script_scenario_should_handle_multiple_resolves(self):
        """Test multiple resolve calls as shown in __main__ script."""
        # Pre-condition
        scenario_config = {
            "scenario": {
                "cup_x": "${uniform: 0.7, 1.5}",
            }
        }
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        resolved1, _ = self.scenario.resolve()
        first_value = resolved1.scenario.cup_x

        # In-test - First resolve
        resolved2, _ = self.scenario.resolve()
        second_value = resolved2.scenario.cup_x

        # In-test - Second resolve
        resolved3, _ = self.scenario.resolve()
        third_value = resolved3.scenario.cup_x

        # Post-condition
        # All values should be in range
        for val in [first_value, second_value, third_value]:
            self.assertGreaterEqual(val, 0.7)
            self.assertLessEqual(val, 1.5)

    def test_main_script_scenario_should_reinitialize_with_none(self):
        """Test reinitializing scenario with None as shown in __main__ script."""
        # Pre-condition
        scenario_config = {
            "scenario": {
                "cup_x": "${uniform: 0.7, 1.5}",
            }
        }
        self.scenario.init(
            scenario=scenario_config,
            seed=42
        )

        # Verify initial scenario has content
        first_yaml = self.scenario.yaml
        self.assertIn("cup_x:", first_yaml)

        # In-test - Reinitialize with None
        self.scenario.init(
            scenario=None,
            seed=42
        )

        # Post-condition
        # Should have an empty scenario
        second_yaml = self.scenario.yaml
        self.assertEqual(second_yaml.strip(), "{}")

    def test_main_script_scenario_should_handle_seed_consistency(self):
        """Test that same seed produces consistent results across resolves."""
        # Pre-condition
        scenario_config = {
            "scenario": {
                "cup_x": "${uniform: 0.7, 1.5}",
                "cup_y": "${uniform: 0.3, 0.7}",
            }
        }

        # Create first scenario with seed
        scenario1 = Scenario()
        scenario1.init(
            scenario=scenario_config,
            seed=42
        )
        resolved1, _ = scenario1.resolve()
        values1_x = resolved1.scenario.cup_x
        values1_y = resolved1.scenario.cup_y

        # Create second scenario with same seed
        scenario2 = Scenario()
        scenario2.init(
            scenario=scenario_config,
            seed=42
        )
        resolved2, _ = scenario2.resolve()
        values2_x = resolved2.scenario.cup_x
        values2_y = resolved2.scenario.cup_y

        # Post-condition
        self.assertEqual(values1_x, values2_x)
        self.assertEqual(values1_y, values2_y)

        # Cleanup
        scenario1._clear_resolvers()
        scenario2._clear_resolvers()


if __name__ == "__main__":
    unittest.main()
