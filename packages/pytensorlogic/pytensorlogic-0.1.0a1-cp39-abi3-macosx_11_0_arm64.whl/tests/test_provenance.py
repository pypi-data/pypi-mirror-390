"""
Tests for provenance tracking functionality.

This module tests the provenance tracking capabilities of pytensorlogic,
including source location tracking, provenance metadata, and RDF integration.
"""

import json
import pytest

# Import will work after maturin develop
try:
    import pytensorlogic as tl
    TENSORLOGIC_AVAILABLE = True
except ImportError:
    TENSORLOGIC_AVAILABLE = False
    pytest.skip("pytensorlogic not installed", allow_module_level=True)


class TestSourceLocation:
    """Tests for SourceLocation class."""

    def test_create_source_location(self):
        """Test creating a source location."""
        loc = tl.SourceLocation("test.tl", 10, 5)
        assert loc.file == "test.tl"
        assert loc.line == 10
        assert loc.column == 5

    def test_source_location_str(self):
        """Test source location string representation."""
        loc = tl.SourceLocation("test.tl", 10, 5)
        assert "test.tl" in str(loc)
        assert "10" in str(loc)

    def test_source_location_repr(self):
        """Test source location repr."""
        loc = tl.SourceLocation("test.tl", 10, 5)
        repr_str = repr(loc)
        assert "SourceLocation" in repr_str
        assert "test.tl" in repr_str


class TestSourceSpan:
    """Tests for SourceSpan class."""

    def test_create_source_span(self):
        """Test creating a source span."""
        start = tl.SourceLocation("test.tl", 10, 1)
        end = tl.SourceLocation("test.tl", 15, 40)
        span = tl.SourceSpan(start, end)

        assert span.start.line == 10
        assert span.end.line == 15

    def test_source_span_same_line(self):
        """Test source span on same line."""
        start = tl.SourceLocation("test.tl", 10, 1)
        end = tl.SourceLocation("test.tl", 10, 20)
        span = tl.SourceSpan(start, end)

        assert span.start.line == span.end.line
        assert span.start.column < span.end.column

    def test_source_span_str(self):
        """Test source span string representation."""
        start = tl.SourceLocation("test.tl", 10, 1)
        end = tl.SourceLocation("test.tl", 15, 40)
        span = tl.SourceSpan(start, end)

        span_str = str(span)
        assert "test.tl" in span_str


class TestProvenance:
    """Tests for Provenance class."""

    def test_create_empty_provenance(self):
        """Test creating empty provenance."""
        prov = tl.Provenance()
        assert prov.rule_id is None
        assert prov.source_file is None
        assert prov.span is None

    def test_set_rule_id(self):
        """Test setting rule ID."""
        prov = tl.Provenance()
        prov.set_rule_id("rule_1")
        assert prov.rule_id == "rule_1"

    def test_set_source_file(self):
        """Test setting source file."""
        prov = tl.Provenance()
        prov.set_source_file("social_rules.tl")
        assert prov.source_file == "social_rules.tl"

    def test_set_span(self):
        """Test setting source span."""
        prov = tl.Provenance()
        start = tl.SourceLocation("test.tl", 10, 1)
        end = tl.SourceLocation("test.tl", 15, 40)
        span = tl.SourceSpan(start, end)

        prov.set_span(span)
        assert prov.span is not None
        assert prov.span.start.line == 10

    def test_add_attribute(self):
        """Test adding custom attributes."""
        prov = tl.Provenance()
        prov.add_attribute("author", "alice")
        prov.add_attribute("version", "1.0")

        assert prov.get_attribute("author") == "alice"
        assert prov.get_attribute("version") == "1.0"

    def test_get_attributes(self):
        """Test getting all attributes."""
        prov = tl.Provenance()
        prov.add_attribute("author", "alice")
        prov.add_attribute("version", "1.0")

        attrs = prov.get_attributes()
        assert isinstance(attrs, dict)
        assert attrs["author"] == "alice"
        assert attrs["version"] == "1.0"

    def test_get_nonexistent_attribute(self):
        """Test getting non-existent attribute."""
        prov = tl.Provenance()
        assert prov.get_attribute("nonexistent") is None

    def test_provenance_repr(self):
        """Test provenance repr."""
        prov = tl.Provenance()
        prov.set_rule_id("rule_1")
        prov.add_attribute("author", "alice")

        repr_str = repr(prov)
        assert "Provenance" in repr_str


class TestProvenanceTracker:
    """Tests for ProvenanceTracker class."""

    def test_create_tracker(self):
        """Test creating provenance tracker."""
        tracker = tl.ProvenanceTracker()
        assert tracker is not None

    def test_create_tracker_with_rdfstar(self):
        """Test creating tracker with RDF* support."""
        tracker = tl.ProvenanceTracker(enable_rdfstar=True)
        assert tracker is not None

    def test_track_entity(self):
        """Test tracking entity to tensor mapping."""
        tracker = tl.ProvenanceTracker()
        tracker.track_entity("http://example.org/alice", 0)
        tracker.track_entity("http://example.org/bob", 1)

        assert tracker.get_entity(0) == "http://example.org/alice"
        assert tracker.get_entity(1) == "http://example.org/bob"

    def test_get_tensor(self):
        """Test getting tensor index for entity."""
        tracker = tl.ProvenanceTracker()
        tracker.track_entity("http://example.org/alice", 42)

        assert tracker.get_tensor("http://example.org/alice") == 42

    def test_get_nonexistent_entity(self):
        """Test getting non-existent entity."""
        tracker = tl.ProvenanceTracker()
        assert tracker.get_entity(999) is None

    def test_get_nonexistent_tensor(self):
        """Test getting non-existent tensor."""
        tracker = tl.ProvenanceTracker()
        assert tracker.get_tensor("http://example.org/nonexistent") is None

    def test_track_shape(self):
        """Test tracking SHACL shape."""
        tracker = tl.ProvenanceTracker()
        tracker.track_shape(
            "http://example.org/PersonShape",
            "Person(x)",
            0
        )

        mappings = tracker.get_shape_mappings()
        assert "http://example.org/PersonShape" in mappings
        assert mappings["http://example.org/PersonShape"] == "Person(x)"

    def test_get_entity_mappings(self):
        """Test getting all entity mappings."""
        tracker = tl.ProvenanceTracker()
        tracker.track_entity("http://example.org/alice", 0)
        tracker.track_entity("http://example.org/bob", 1)

        mappings = tracker.get_entity_mappings()
        assert isinstance(mappings, dict)
        assert len(mappings) == 2
        assert mappings["http://example.org/alice"] == 0
        assert mappings["http://example.org/bob"] == 1

    def test_get_shape_mappings(self):
        """Test getting all shape mappings."""
        tracker = tl.ProvenanceTracker()
        tracker.track_shape("http://example.org/Shape1", "Rule1", 0)
        tracker.track_shape("http://example.org/Shape2", "Rule2", 1)

        mappings = tracker.get_shape_mappings()
        assert isinstance(mappings, dict)
        assert len(mappings) == 2

    def test_track_inferred_triple(self):
        """Test tracking inferred triple."""
        tracker = tl.ProvenanceTracker(enable_rdfstar=True)
        tracker.track_inferred_triple(
            "http://example.org/alice",
            "http://example.org/knows",
            "http://example.org/bob",
            rule_id="rule_42",
            confidence=0.95
        )

        # Should not raise exception
        assert True

    def test_to_rdf_star(self):
        """Test exporting to RDF* statements."""
        tracker = tl.ProvenanceTracker()
        tracker.track_entity("http://example.org/alice", 0)

        statements = tracker.to_rdf_star()
        assert isinstance(statements, list)
        assert len(statements) > 0

    def test_to_rdfstar_turtle(self):
        """Test exporting to RDF* Turtle format."""
        tracker = tl.ProvenanceTracker()
        tracker.track_entity("http://example.org/alice", 0)

        turtle = tracker.to_rdfstar_turtle()
        assert isinstance(turtle, str)
        assert "alice" in turtle
        assert "@prefix" in turtle

    def test_to_json(self):
        """Test exporting to JSON."""
        tracker = tl.ProvenanceTracker()
        tracker.track_entity("http://example.org/alice", 0)

        json_str = tracker.to_json()
        assert isinstance(json_str, str)

        # Verify it's valid JSON
        data = json.loads(json_str)
        assert "entity_to_tensor" in data

    def test_from_json(self):
        """Test importing from JSON."""
        tracker = tl.ProvenanceTracker()
        tracker.track_entity("http://example.org/alice", 0)
        tracker.track_entity("http://example.org/bob", 1)

        json_str = tracker.to_json()
        restored = tl.ProvenanceTracker.from_json(json_str)

        assert restored.get_entity(0) == "http://example.org/alice"
        assert restored.get_entity(1) == "http://example.org/bob"

    def test_get_high_confidence_inferences(self):
        """Test getting high-confidence inferences."""
        tracker = tl.ProvenanceTracker(enable_rdfstar=True)

        # Add some inferences
        tracker.track_inferred_triple(
            "http://example.org/alice",
            "http://example.org/knows",
            "http://example.org/bob",
            confidence=0.95
        )

        tracker.track_inferred_triple(
            "http://example.org/charlie",
            "http://example.org/knows",
            "http://example.org/dave",
            confidence=0.60
        )

        # Get high-confidence inferences (>= 0.8)
        high_conf = tracker.get_high_confidence_inferences(min_confidence=0.8)
        assert isinstance(high_conf, list)
        # At least one should be above threshold
        assert len(high_conf) >= 1

    def test_provenance_tracker_repr(self):
        """Test tracker repr."""
        tracker = tl.ProvenanceTracker()
        tracker.track_entity("http://example.org/alice", 0)

        repr_str = repr(tracker)
        assert "ProvenanceTracker" in repr_str


class TestProvenanceTrackerHelper:
    """Tests for provenance_tracker helper function."""

    def test_create_tracker_via_helper(self):
        """Test creating tracker via helper function."""
        tracker = tl.provenance_tracker()
        assert tracker is not None

    def test_create_tracker_with_rdfstar_via_helper(self):
        """Test creating tracker with RDF* via helper."""
        tracker = tl.provenance_tracker(enable_rdfstar=True)
        assert tracker is not None


class TestGetProvenance:
    """Tests for get_provenance function."""

    def test_get_provenance_from_graph(self):
        """Test getting provenance from compiled graph."""
        # Create an expression with operations (so it has nodes)
        expr = tl.and_(
            tl.pred("knows", [tl.var("x"), tl.var("y")]),
            tl.pred("likes", [tl.var("x"), tl.var("z")])
        )

        # Compile to graph
        graph = tl.compile(expr)

        # Get provenance (will be None for nodes without provenance)
        provenance_list = tl.get_provenance(graph)

        assert isinstance(provenance_list, list)
        # Graph should have at least one node (the AND operation)
        assert len(provenance_list) > 0

    def test_get_provenance_empty_graph(self):
        """Test getting provenance from minimal expression."""
        expr = tl.constant(1.0)
        graph = tl.compile(expr)

        provenance_list = tl.get_provenance(graph)
        assert isinstance(provenance_list, list)


class TestGetMetadata:
    """Tests for get_metadata function."""

    def test_get_metadata_from_graph(self):
        """Test getting metadata from compiled graph."""
        # Use an expression with operations (so it has nodes)
        expr = tl.and_(
            tl.pred("knows", [tl.var("x"), tl.var("y")]),
            tl.pred("likes", [tl.var("x"), tl.var("z")])
        )
        graph = tl.compile(expr)

        metadata_list = tl.get_metadata(graph)

        assert isinstance(metadata_list, list)
        assert len(metadata_list) > 0

    def test_get_metadata_structure(self):
        """Test metadata structure."""
        expr = tl.and_(
            tl.pred("Person", [tl.var("x")]),
            tl.pred("Mortal", [tl.var("x")])
        )
        graph = tl.compile(expr)

        metadata_list = tl.get_metadata(graph)

        for meta in metadata_list:
            if meta is not None:
                assert isinstance(meta, dict)
                # Metadata can have name, span, provenance, attributes
                assert "attributes" in meta


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_provenance_workflow(self):
        """Test full provenance tracking workflow."""
        # Create tracker
        tracker = tl.ProvenanceTracker()

        # Track entities
        tracker.track_entity("http://example.org/alice", 0)
        tracker.track_entity("http://example.org/bob", 1)

        # Track shapes
        tracker.track_shape(
            "http://example.org/PersonShape",
            "Person(x) AND knows(x, y)",
            0
        )

        # Export to JSON
        json_str = tracker.to_json()

        # Import from JSON
        restored = tl.ProvenanceTracker.from_json(json_str)

        # Verify restoration
        assert restored.get_entity(0) == "http://example.org/alice"
        assert restored.get_entity(1) == "http://example.org/bob"

        shape_mappings = restored.get_shape_mappings()
        assert "http://example.org/PersonShape" in shape_mappings

    def test_rdfstar_workflow(self):
        """Test RDF* provenance workflow."""
        tracker = tl.ProvenanceTracker(enable_rdfstar=True)

        # Track inferred triples with metadata
        tracker.track_inferred_triple(
            "http://example.org/alice",
            "http://example.org/knows",
            "http://example.org/bob",
            rule_id="social_network_rule_1",
            confidence=0.95
        )

        tracker.track_inferred_triple(
            "http://example.org/alice",
            "http://example.org/worksAt",
            "http://example.org/Company",
            rule_id="employment_rule_3",
            confidence=0.88
        )

        # Get high-confidence inferences
        high_conf = tracker.get_high_confidence_inferences(min_confidence=0.9)
        assert len(high_conf) >= 1

        # Export to Turtle
        turtle = tracker.to_rdfstar_turtle()
        assert isinstance(turtle, str)
        assert len(turtle) > 0
        assert "alice" in turtle

    def test_expression_with_provenance_tracking(self):
        """Test creating expressions and extracting provenance."""
        # Create complex expression
        person_x = tl.pred("Person", [tl.var("x")])
        person_y = tl.pred("Person", [tl.var("y")])
        knows = tl.pred("knows", [tl.var("x"), tl.var("y")])

        rule = tl.and_(tl.and_(person_x, person_y), knows)

        # Compile
        graph = tl.compile(rule)

        # Get provenance and metadata
        provenance_list = tl.get_provenance(graph)
        metadata_list = tl.get_metadata(graph)

        assert len(provenance_list) > 0
        assert len(metadata_list) > 0
        assert len(provenance_list) == len(metadata_list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
