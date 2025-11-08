"""
Test suite for Rule Builder DSL

Tests all DSL components:
- Variable creation with domain bindings
- Predicate builders with arity and domain validation
- Operator overloading (&, |, ~, >>)
- Rule builder context manager
- Symbol table integration
- Compilation and error handling
"""

import pytest
import pytensorlogic as tl


class TestVar:
    """Test Var class for variable creation with domain bindings"""

    def test_var_creation(self):
        """Test basic variable creation"""
        x = tl.Var("x")
        assert x.name == "x"
        assert x.domain is None

    def test_var_with_domain(self):
        """Test variable with domain binding"""
        x = tl.Var("x", domain="Person")
        assert x.name == "x"
        assert x.domain == "Person"

    def test_var_repr(self):
        """Test variable string representations"""
        x = tl.Var("x")
        assert repr(x) == "Var('x')"

        y = tl.Var("y", domain="Person")
        assert "Person" in repr(y)

    def test_var_str(self):
        """Test variable __str__ method"""
        x = tl.Var("x", domain="Person")
        assert str(x) == "x"

    def test_var_to_term(self):
        """Test conversion to PyTerm"""
        x = tl.Var("x")
        term = x.to_term()
        assert term.name() == "x"
        assert term.is_var()

    def test_var_to_expr(self):
        """Test conversion to PyTLExpr"""
        x = tl.Var("x")
        expr = x.to_expr()
        # Should create a nullary predicate with variable name
        assert expr is not None


class TestPredicateBuilder:
    """Test PredicateBuilder for callable predicates"""

    def test_predicate_creation(self):
        """Test basic predicate builder creation"""
        knows = tl.PredicateBuilder("knows")
        assert knows.name == "knows"
        assert knows.arity is None
        assert knows.domains is None

    def test_predicate_with_arity(self):
        """Test predicate with arity specification"""
        knows = tl.PredicateBuilder("knows", arity=2)
        assert knows.name == "knows"
        assert knows.arity == 2

    def test_predicate_with_domains(self):
        """Test predicate with domain specifications"""
        knows = tl.PredicateBuilder(
            "knows", arity=2, domains=["Person", "Person"]
        )
        assert knows.name == "knows"
        assert knows.arity == 2
        assert knows.domains == ["Person", "Person"]

    def test_predicate_call(self):
        """Test calling predicate with variables"""
        knows = tl.PredicateBuilder("knows", arity=2)
        x = tl.Var("x")
        y = tl.Var("y")

        expr = knows(x, y)
        assert expr is not None
        # Check it's a TLExpr
        assert hasattr(expr, 'free_vars')

    def test_predicate_arity_validation(self):
        """Test arity validation when calling predicate"""
        binary = tl.PredicateBuilder("binary", arity=2)
        x = tl.Var("x")
        y = tl.Var("y")
        z = tl.Var("z")

        # Valid call with 2 args
        expr = binary(x, y)
        assert expr is not None

        # Invalid call with 3 args
        with pytest.raises(ValueError, match="expects 2 arguments, got 3"):
            binary(x, y, z)

        # Invalid call with 1 arg
        with pytest.raises(ValueError, match="expects 2 arguments, got 1"):
            binary(x)

    def test_predicate_domain_validation(self):
        """Test domain validation when calling predicate"""
        person_rel = tl.PredicateBuilder(
            "person_rel", arity=2, domains=["Person", "Person"]
        )
        x = tl.Var("x", domain="Person")
        y = tl.Var("y", domain="Animal")

        # Valid call with matching domains
        expr = person_rel(x, x)
        assert expr is not None

        # Invalid call with mismatched domain
        with pytest.raises(TypeError, match="expects domain 'Person', got 'Animal'"):
            person_rel(x, y)

    def test_predicate_with_constants(self):
        """Test calling predicate with string constants"""
        knows = tl.PredicateBuilder("knows", arity=2)
        expr = knows("alice", "bob")
        assert expr is not None

    def test_predicate_repr(self):
        """Test predicate builder string representation"""
        knows = tl.PredicateBuilder("knows", arity=2)
        assert repr(knows) == "PredicateBuilder('knows')"

    def test_predicate_to_info(self):
        """Test conversion to PredicateInfo"""
        knows = tl.PredicateBuilder(
            "knows", arity=2, domains=["Person", "Person"]
        )
        info = knows.to_predicate_info()
        # Should not raise an error
        assert info is not None


class TestOperatorOverloading:
    """Test operator overloading for TLExpr (&, |, ~, >>)"""

    def test_and_operator(self):
        """Test & (AND) operator"""
        knows = tl.PredicateBuilder("knows", arity=2)
        x = tl.Var("x")
        y = tl.Var("y")
        z = tl.Var("z")

        expr1 = knows(x, y)
        expr2 = knows(y, z)
        and_expr = expr1 & expr2

        assert and_expr is not None
        # Should have free variables from both expressions
        free_vars = and_expr.free_vars()
        assert "x" in free_vars
        assert "y" in free_vars
        assert "z" in free_vars

    def test_or_operator(self):
        """Test | (OR) operator"""
        knows = tl.PredicateBuilder("knows", arity=2)
        likes = tl.PredicateBuilder("likes", arity=2)
        x = tl.Var("x")
        y = tl.Var("y")

        or_expr = knows(x, y) | likes(x, y)
        assert or_expr is not None

    def test_not_operator(self):
        """Test ~ (NOT) operator"""
        knows = tl.PredicateBuilder("knows", arity=2)
        x = tl.Var("x")
        y = tl.Var("y")

        not_expr = ~knows(x, y)
        assert not_expr is not None

    def test_imply_operator(self):
        """Test >> (IMPLY) operator"""
        knows = tl.PredicateBuilder("knows", arity=2)
        friend = tl.PredicateBuilder("friend", arity=2)
        x = tl.Var("x")
        y = tl.Var("y")

        imply_expr = knows(x, y) >> friend(x, y)
        assert imply_expr is not None

    def test_complex_expression(self):
        """Test complex expression with multiple operators"""
        knows = tl.PredicateBuilder("knows", arity=2)
        likes = tl.PredicateBuilder("likes", arity=2)
        friend = tl.PredicateBuilder("friend", arity=2)
        x = tl.Var("x")
        y = tl.Var("y")
        z = tl.Var("z")

        # (knows(x,y) & knows(y,z)) >> knows(x,z)
        transitivity = (knows(x, y) & knows(y, z)) >> knows(x, z)
        assert transitivity is not None

        # (knows(x,y) & knows(y,x)) >> friend(x,y) | likes(x,y)
        complex_expr = ((knows(x, y) & knows(y, x)) >> friend(x, y)) | likes(x, y)
        assert complex_expr is not None

    def test_operator_precedence(self):
        """Test operator precedence"""
        p = tl.PredicateBuilder("p", arity=1)
        q = tl.PredicateBuilder("q", arity=1)
        r = tl.PredicateBuilder("r", arity=1)
        x = tl.Var("x")

        # ~ has higher precedence than &
        expr1 = ~p(x) & q(x)
        assert expr1 is not None

        # & has higher precedence than |
        expr2 = p(x) & q(x) | r(x)
        assert expr2 is not None


class TestRuleBuilder:
    """Test RuleBuilder context manager"""

    def test_rule_builder_creation(self):
        """Test basic rule builder creation"""
        rb = tl.RuleBuilder()
        assert len(rb) == 0

    def test_rule_builder_with_config(self):
        """Test rule builder with compilation config"""
        config = tl.CompilationConfig.fuzzy_product()
        rb = tl.RuleBuilder(config=config)
        assert len(rb) == 0

    def test_vars_single(self):
        """Test creating single variable"""
        rb = tl.RuleBuilder()
        x = rb.vars("x", domain="Person")
        assert x.name == "x"
        assert x.domain == "Person"

    def test_vars_multiple(self):
        """Test creating multiple variables"""
        rb = tl.RuleBuilder()
        x, y, z = rb.vars("x", "y", "z", domain="Person")
        assert x.name == "x"
        assert y.name == "y"
        assert z.name == "z"
        assert all(v.domain == "Person" for v in [x, y, z])

    def test_vars_without_domain(self):
        """Test creating variables without domain"""
        rb = tl.RuleBuilder()
        x, y = rb.vars("x", "y")
        assert x.domain is None
        assert y.domain is None

    def test_vars_empty(self):
        """Test that vars() requires at least one name"""
        rb = tl.RuleBuilder()
        with pytest.raises(ValueError, match="At least one variable name required"):
            rb.vars()

    def test_pred(self):
        """Test creating predicate builder"""
        rb = tl.RuleBuilder()
        knows = rb.pred("knows", arity=2, domains=["Person", "Person"])
        assert knows.name == "knows"
        assert knows.arity == 2

    def test_add_domain(self):
        """Test adding domain to symbol table"""
        rb = tl.RuleBuilder()
        rb.add_domain("Person", cardinality=10, description="People")

        st = rb.get_symbol_table()
        domains = st.list_domains()
        assert "Person" in domains

    def test_add_rule(self):
        """Test adding rules to builder"""
        rb = tl.RuleBuilder()
        x, y = rb.vars("x", "y", domain="Person")
        knows = rb.pred("knows", arity=2)

        rb.add_rule(knows(x, y), name="test_rule")
        assert len(rb) == 1

        rules = rb.get_rules()
        assert len(rules) == 1
        assert rules[0][0] == "test_rule"

    def test_add_multiple_rules(self):
        """Test adding multiple rules"""
        rb = tl.RuleBuilder()
        x, y, z = rb.vars("x", "y", "z", domain="Person")
        knows = rb.pred("knows", arity=2)
        friend = rb.pred("friend", arity=2)

        rb.add_rule((knows(x, y) & knows(y, z)) >> knows(x, z), name="transitivity")
        rb.add_rule(knows(x, y) >> knows(y, x), name="symmetry")
        rb.add_rule((knows(x, y) & knows(y, x)) >> friend(x, y), name="friendship")

        assert len(rb) == 3

    def test_get_rules(self):
        """Test getting all rules"""
        rb = tl.RuleBuilder()
        x, y = rb.vars("x", "y")
        p = rb.pred("p", arity=2)

        rb.add_rule(p(x, y), name="rule1")
        rb.add_rule(p(y, x), name="rule2")

        rules = rb.get_rules()
        assert len(rules) == 2
        names = [r[0] for r in rules]
        assert "rule1" in names
        assert "rule2" in names

    def test_get_symbol_table(self):
        """Test getting symbol table"""
        rb = tl.RuleBuilder()
        rb.add_domain("Person", cardinality=10)
        rb.pred("knows", arity=2, domains=["Person", "Person"])

        st = rb.get_symbol_table()
        assert "Person" in st.list_domains()

    def test_clear(self):
        """Test clearing rules and symbol table"""
        rb = tl.RuleBuilder()
        x, y = rb.vars("x", "y", domain="Person")
        knows = rb.pred("knows", arity=2)

        rb.add_rule(knows(x, y), name="test")
        assert len(rb) == 1

        rb.clear()
        assert len(rb) == 0

    def test_context_manager(self):
        """Test rule builder as context manager"""
        with tl.RuleBuilder() as rb:
            x, y = rb.vars("x", "y", domain="Person")
            knows = rb.pred("knows", arity=2)
            rb.add_rule(knows(x, y), name="test")
            assert len(rb) == 1

    def test_compile_empty(self):
        """Test that compiling empty builder raises error"""
        rb = tl.RuleBuilder()
        with pytest.raises(ValueError, match="No rules defined"):
            rb.compile()

    def test_compile_separate_empty(self):
        """Test that compile_separate on empty builder raises error"""
        rb = tl.RuleBuilder()
        with pytest.raises(ValueError, match="No rules defined"):
            rb.compile_separate()

    def test_repr(self):
        """Test rule builder string representation"""
        rb = tl.RuleBuilder()
        x, y = rb.vars("x", "y")
        p = rb.pred("p", arity=2)
        rb.add_rule(p(x, y), name="test")

        repr_str = repr(rb)
        assert "RuleBuilder" in repr_str
        assert "1" in repr_str  # Number of rules


class TestIntegration:
    """Integration tests for complete DSL workflows"""

    def test_social_network_workflow(self):
        """Test complete social network modeling workflow"""
        rb = tl.RuleBuilder()

        # Define domains
        rb.add_domain("Person", cardinality=10, description="People")
        rb.add_domain("Post", cardinality=20, description="Posts")

        # Define predicates
        follows = rb.pred("follows", arity=2, domains=["Person", "Person"])
        likes = rb.pred("likes", arity=2, domains=["Person", "Post"])
        sees = rb.pred("sees", arity=2, domains=["Person", "Post"])
        posted = rb.pred("posted", arity=2, domains=["Person", "Post"])

        # Define variables
        p1, p2, p3 = rb.vars("p1", "p2", "p3", domain="Person")
        post = rb.vars("post", domain="Post")

        # Define rules
        rb.add_rule(
            (follows(p1, p2) & follows(p2, p3)) >> follows(p1, p3),
            name="follow_transitivity"
        )
        rb.add_rule(
            (follows(p1, p2) & posted(p2, post)) >> sees(p1, post),
            name="feed_visibility"
        )

        assert len(rb) == 2

        # Verify symbol table
        st = rb.get_symbol_table()
        assert "Person" in st.list_domains()
        assert "Post" in st.list_domains()

    def test_knowledge_base_workflow(self):
        """Test knowledge base inference workflow"""
        kb = tl.RuleBuilder()

        # Define domains
        kb.add_domain("Concept", cardinality=100)
        kb.add_domain("Property", cardinality=50)

        # Define predicates
        is_a = kb.pred("is_a", arity=2, domains=["Concept", "Concept"])
        has = kb.pred("has", arity=2, domains=["Concept", "Property"])

        # Define variables
        c1, c2, c3 = kb.vars("c1", "c2", "c3", domain="Concept")
        p = kb.vars("p", domain="Property")

        # Transitive subclass
        kb.add_rule(
            (is_a(c1, c2) & is_a(c2, c3)) >> is_a(c1, c3),
            name="transitivity"
        )

        # Property inheritance
        kb.add_rule(
            (is_a(c1, c2) & has(c2, p)) >> has(c1, p),
            name="inheritance"
        )

        assert len(kb) == 2

    def test_complex_rule_construction(self):
        """Test building complex rules with nested operators"""
        rb = tl.RuleBuilder()
        p = rb.pred("p", arity=2)
        q = rb.pred("q", arity=2)
        r = rb.pred("r", arity=2)
        s = rb.pred("s", arity=2)
        x, y, z = rb.vars("x", "y", "z")

        # Build nested rule: ((p & q) | (r & s)) >> result
        complex_rule = ((p(x, y) & q(y, z)) | (r(x, z) & s(z, x))) >> p(x, z)
        rb.add_rule(complex_rule, name="complex")

        assert len(rb) == 1


class TestErrorHandling:
    """Test error handling and validation"""

    def test_invalid_variable_binding(self):
        """Test error when binding variable to non-existent domain"""
        rb = tl.RuleBuilder()
        # This should work but not bind to symbol table (domain doesn't exist yet)
        x = rb.vars("x", domain="NonExistentDomain")
        assert x.domain == "NonExistentDomain"

    def test_add_rule_without_name(self):
        """Test that add_rule generates default name"""
        rb = tl.RuleBuilder()
        x, y = rb.vars("x", "y")
        p = rb.pred("p", arity=2)

        rb.add_rule(p(x, y))  # No name provided
        rb.add_rule(p(y, x))  # No name provided

        rules = rb.get_rules()
        assert len(rules) == 2
        # Should have default names like "rule_0", "rule_1"
        assert rules[0][0] == "rule_0"
        assert rules[1][0] == "rule_1"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
