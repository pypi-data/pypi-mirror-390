"""
Tests for model persistence functionality.

Tests saving and loading models in various formats:
- JSON format (human-readable)
- Binary format (compact)
- Pickle support
- Full model packages with metadata
"""

import os
import pickle
import tempfile
import numpy as np
import pytest

import pytensorlogic as tl


def test_model_package_creation():
    """Test creating an empty model package."""
    package = tl.model_package()
    assert package is not None
    assert isinstance(package, tl.ModelPackage)

    # Check default metadata
    assert "version" in str(package.metadata)
    assert "created_at" in str(package.metadata)


def test_model_package_metadata():
    """Test adding and retrieving metadata."""
    package = tl.model_package()

    # Add metadata
    package.add_metadata("author", "John Doe")
    package.add_metadata("description", "Test model")
    package.add_metadata("version", "1.0.0")

    # Retrieve metadata
    assert package.get_metadata("author") == "John Doe"
    assert package.get_metadata("description") == "Test model"
    assert package.get_metadata("version") == "1.0.0"

    # Non-existent key
    assert package.get_metadata("nonexistent") is None


def test_save_load_model_json():
    """Test saving and loading a model in JSON format."""
    # Create a simple expression and compile
    expr = tl.and_(
        tl.pred("knows", [tl.var("x"), tl.var("y")]),
        tl.pred("likes", [tl.var("y"), tl.var("z")])
    )
    graph = tl.compile(expr)

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        # Save
        tl.save_model(graph, temp_path, format="json")
        assert os.path.exists(temp_path)

        # Load
        loaded_graph = tl.load_model(temp_path, format="json")
        assert loaded_graph is not None
        assert isinstance(loaded_graph, tl.EinsumGraph)

        # Verify the graphs have the same structure
        assert len(loaded_graph.nodes) == len(graph.nodes)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_load_model_binary():
    """Test saving and loading a model in binary format."""
    # Create a simple expression and compile
    expr = tl.or_(
        tl.pred("employee", [tl.var("x")]),
        tl.pred("contractor", [tl.var("x")])
    )
    graph = tl.compile(expr)

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        temp_path = f.name

    try:
        # Save
        tl.save_model(graph, temp_path, format="binary")
        assert os.path.exists(temp_path)

        # Load
        loaded_graph = tl.load_model(temp_path, format="binary")
        assert loaded_graph is not None
        assert isinstance(loaded_graph, tl.EinsumGraph)

        # Verify the graphs have the same structure
        assert len(loaded_graph.nodes) == len(graph.nodes)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_load_model_auto_format():
    """Test automatic format detection from file extension."""
    # Create a simple expression
    expr = tl.not_(tl.pred("inactive", [tl.var("x")]))
    graph = tl.compile(expr)

    # Test JSON auto-detection
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json_path = f.name

    try:
        tl.save_model(graph, json_path, format="json")
        loaded = tl.load_model(json_path)  # No format specified
        assert loaded is not None
    finally:
        if os.path.exists(json_path):
            os.remove(json_path)

    # Test binary auto-detection
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        bin_path = f.name

    try:
        tl.save_model(graph, bin_path, format="binary")
        loaded = tl.load_model(bin_path)  # No format specified
        assert loaded is not None
    finally:
        if os.path.exists(bin_path):
            os.remove(bin_path)


def test_save_full_model_with_symbol_table():
    """Test saving a full model with symbol table."""
    # Create symbol table
    sym_table = tl.symbol_table()
    sym_table.add_domain(tl.domain_info("Person", 10))
    sym_table.add_domain(tl.domain_info("Item", 5))
    sym_table.add_predicate(tl.predicate_info("owns", ["Person", "Item"]))

    # Create expression
    expr = tl.pred("owns", [tl.var("x"), tl.var("y")])
    graph = tl.compile(expr)

    # Save with symbol table
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        tl.save_full_model(
            graph,
            temp_path,
            symbol_table=sym_table,
            metadata={"description": "Ownership model", "version": "1.0"},
            format="json"
        )
        assert os.path.exists(temp_path)

        # Load
        model = tl.load_full_model(temp_path)
        assert "graph" in model
        assert "symbol_table" in model
        assert "metadata" in model

        # Verify symbol table
        loaded_st = model["symbol_table"]
        assert len(loaded_st.list_domains()) == 2
        assert len(loaded_st.list_predicates()) == 1

        # Verify metadata
        metadata = model["metadata"]
        assert metadata["description"] == "Ownership model"
        assert metadata["version"] == "1.0"

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_save_full_model_binary():
    """Test saving a full model in binary format."""
    # Create symbol table first (needed for quantifiers)
    sym_table = tl.symbol_table()
    sym_table.add_domain(tl.domain_info("User", 100))
    sym_table.add_predicate(tl.predicate_info("active", ["User"]))

    # Create expression and compile with context
    ctx = tl.compiler_context()
    ctx.add_domain("User", 100)
    expr = tl.exists("x", "User", tl.pred("active", [tl.var("x")]))
    graph = tl.compile_with_context(expr, ctx)

    # Save in binary format
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        temp_path = f.name

    try:
        tl.save_full_model(
            graph,
            temp_path,
            symbol_table=sym_table,
            format="binary"
        )
        assert os.path.exists(temp_path)

        # Load
        model = tl.load_full_model(temp_path, format="binary")
        assert "graph" in model
        assert "symbol_table" in model

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_model_package_json_serialization():
    """Test ModelPackage to_json and from_json methods."""
    package = tl.model_package()
    package.add_metadata("author", "Alice")
    package.add_metadata("project", "TensorLogic")

    # Serialize to JSON
    json_str = package.to_json()
    assert isinstance(json_str, str)
    assert "Alice" in json_str
    assert "TensorLogic" in json_str

    # Deserialize from JSON
    loaded_package = tl.ModelPackage.from_json(json_str)
    assert loaded_package.get_metadata("author") == "Alice"
    assert loaded_package.get_metadata("project") == "TensorLogic"


def test_model_package_pickle_support():
    """Test pickling and unpickling ModelPackage."""
    package = tl.model_package()
    package.add_metadata("test_key", "test_value")
    package.add_metadata("number", "42")

    # Pickle
    pickled = pickle.dumps(package)
    assert isinstance(pickled, bytes)

    # Unpickle
    unpickled = pickle.loads(pickled)
    assert isinstance(unpickled, tl.ModelPackage)
    assert unpickled.get_metadata("test_key") == "test_value"
    assert unpickled.get_metadata("number") == "42"


def test_model_package_save_load_json():
    """Test ModelPackage save_json and load_json methods."""
    package = tl.model_package()
    package.add_metadata("format", "json")
    package.add_metadata("compression", "none")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        # Save
        package.save_json(temp_path)
        assert os.path.exists(temp_path)

        # Load
        loaded = tl.ModelPackage.load_json(temp_path)
        assert loaded.get_metadata("format") == "json"
        assert loaded.get_metadata("compression") == "none"

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_model_package_save_load_binary():
    """Test ModelPackage save_binary and load_binary methods."""
    package = tl.model_package()
    package.add_metadata("format", "binary")
    package.add_metadata("compressed", "true")

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        temp_path = f.name

    try:
        # Save
        package.save_binary(temp_path)
        assert os.path.exists(temp_path)

        # Load
        loaded = tl.ModelPackage.load_binary(temp_path)
        assert loaded.get_metadata("format") == "binary"
        assert loaded.get_metadata("compressed") == "true"

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_complex_model_persistence():
    """Test saving and loading a complex model with multiple operations."""
    # Build a complex expression
    x, y, z = tl.var("x"), tl.var("y"), tl.var("z")

    # Transitive closure: knows(x,y) AND knows(y,z) => knows(x,z)
    expr = tl.imply(
        tl.and_(
            tl.pred("knows", [x, y]),
            tl.pred("knows", [y, z])
        ),
        tl.pred("knows", [x, z])
    )

    graph = tl.compile(expr)

    # Create symbol table
    sym_table = tl.symbol_table()
    sym_table.add_domain(tl.domain_info("Person", 20))
    sym_table.add_predicate(tl.predicate_info("knows", ["Person", "Person"]))
    sym_table.bind_variable("x", "Person")
    sym_table.bind_variable("y", "Person")
    sym_table.bind_variable("z", "Person")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        # Save
        tl.save_full_model(
            graph,
            temp_path,
            symbol_table=sym_table,
            metadata={
                "model": "transitive_closure",
                "domains": "social_network",
                "author": "TensorLogic Team"
            }
        )

        # Load
        model = tl.load_full_model(temp_path)

        # Verify all components
        assert "graph" in model
        assert "symbol_table" in model
        assert "metadata" in model

        loaded_st = model["symbol_table"]
        assert "Person" in loaded_st.list_domains()
        assert "knows" in loaded_st.list_predicates()

        metadata = model["metadata"]
        assert metadata["model"] == "transitive_closure"
        assert metadata["author"] == "TensorLogic Team"

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_repr_and_str():
    """Test __repr__ and __str__ methods of ModelPackage."""
    package = tl.model_package()
    package.add_metadata("key1", "value1")
    package.add_metadata("key2", "value2")

    # Test __repr__
    repr_str = repr(package)
    assert "ModelPackage" in repr_str
    assert "graph=" in repr_str
    assert "config=" in repr_str

    # Test __str__
    str_str = str(package)
    assert "ModelPackage" in str_str
    assert "metadata entries" in str_str


def test_invalid_format_error():
    """Test that invalid format raises an error."""
    expr = tl.pred("test", [tl.var("x")])
    graph = tl.compile(expr)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        temp_path = f.name

    try:
        # Try to save with invalid format
        with pytest.raises(ValueError, match="Unknown format"):
            tl.save_model(graph, temp_path, format="invalid_format")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_load_nonexistent_file():
    """Test loading from nonexistent file raises error."""
    nonexistent_path = "/tmp/tensorlogic_nonexistent_model_12345.json"

    with pytest.raises(IOError):
        tl.load_model(nonexistent_path)


def test_model_package_bytes_conversion():
    """Test ModelPackage to_bytes and from_bytes methods."""
    package = tl.model_package()
    package.add_metadata("test", "bytes_conversion")

    # Convert to bytes
    # Note: to_bytes requires Python context, so we test indirectly via pickle
    pickled = pickle.dumps(package)
    assert isinstance(pickled, bytes)
    assert len(pickled) > 0

    # Convert back
    unpickled = pickle.loads(pickled)
    assert unpickled.get_metadata("test") == "bytes_conversion"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
