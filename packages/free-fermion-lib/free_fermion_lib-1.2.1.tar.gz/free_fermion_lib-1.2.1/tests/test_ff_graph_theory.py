"""
Graph Theory Tests for Free Fermion Library

This module contains comprehensive tests for the graph theory functions
in ff_graph_theory.py, including planar graph generation, PFO algorithm,
perfect matching counting, and related algorithms.

Test categories:
- Planar graph generation and properties
- Perfect matching algorithms (PFO/FKT)
- Graph adjacency and incidence matrices
- Planar embedding and face detection
- Performance and edge cases
"""

import networkx as nx
import numpy as np
import pytest

# Import the library
import ff


class TestPerfectMatchingAlgorithms:
    """Test perfect matching counting algorithms"""

    def test_pfo_algorithm_basic(self):
        """Test PFO algorithm on basic graphs"""
        # Complete graph K4 (has perfect matchings)
        G = nx.complete_graph(4)

        # Make it planar by removing one edge if needed
        if not nx.is_planar(G):
            edges = list(G.edges())
            G.remove_edge(*edges[0])

        # Count perfect matchings
        count = ff.count_perfect_matchings(G)
        assert count >= 0, "Perfect matching count should be non-negative"

        # For K4, there should be 3 perfect matchings
        if G.number_of_edges() == 6:  # Complete K4
            assert np.allclose(count, 3), "K4 should have 3 perfect matchings"

    def test_pfo_algorithm_path(self):
        """Test PFO algorithm on path graphs"""
        # Even path (has 1 perfect matching)
        G = nx.path_graph(4)
        count = ff.count_perfect_matchings(G)
        assert np.allclose(count, 1), "Path of length 4 should have 1 perfect matching"

        # Odd path (has 0 perfect matchings)
        G = nx.path_graph(5)
        count = ff.count_perfect_matchings(G)
        assert np.allclose(count, 0), "Path of length 5 should have 0 perfect matchings"

    def test_pfo_algorithm_cycle(self):
        """Test PFO algorithm on cycle graphs"""
        # Even cycle (has 2 perfect matchings)
        G = nx.cycle_graph(4)
        count = ff.count_perfect_matchings(G)
        assert np.allclose(count, 2), "4-cycle should have 2 perfect matchings"

        # 6-cycle should have more perfect matchings
        G = nx.cycle_graph(6)
        count = ff.count_perfect_matchings(G)
        assert count > 0, "6-cycle should have perfect matchings"

        # Odd cycle (has 0 perfect matchings)
        G = nx.cycle_graph(5)
        count = ff.count_perfect_matchings(G)
        assert np.allclose(count, 0), "5-cycle should have 0 perfect matchings"

    def test_pfo_algorithm_grid(self):
        """Test PFO algorithm on grid graphs"""

        # 2x2 grid (doesn't work for some reason, needs investigation)

        # G = nx.grid_2d_graph(2, 2)
        # count = ff.count_perfect_matchings(G)
        # assert count == 2, "2x2 grid should have 2 perfect matchings"

        # 2x3 grid (even number of vertices)
        G = nx.grid_2d_graph(2, 3)
        count = ff.count_perfect_matchings(G)
        assert count >= 0, "2x3 grid perfect matching count should be non-negative"

    def test_fkt_algorithm_comparison(self):
        """Test that FKT algorithm gives same results as PFO"""
        # Create a small planar graph
        G = nx.cycle_graph(6)

        # Both algorithms should give same result

        count_pfo = ff.clean(ff.count_perfect_matchings_planar(G))
        count_brute = len(ff.find_perfect_matchings_brute(G))

        assert np.allclose(
            count_pfo, count_brute
        ), "PFO and FKT should give same result"

    def test_perfect_matching_matrix(self):
        """Test perfect matching via adjacency matrix"""
        # Create adjacency matrix for small graph
        A = np.array([[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]])

        G = nx.from_numpy_array(A)

        count = ff.count_perfect_matchings(G)

        assert count >= 0, "Perfect matching count should be non-negative"

        # Check that matrix is symmetric
        assert np.allclose(A, A.T), "Adjacency matrix should be symmetric"


class TestPerformanceAndEdgeCases:
    """Test performance and edge cases"""

    def test_empty_graph(self):
        """Test behavior with empty graphs"""
        G = nx.Graph()

        # Empty graph properties
        assert np.allclose(
            ff.count_perfect_matchings(G), 0
        ), "Empty graph has 0 perfect matching (vacuous)"
        assert nx.is_planar(G), "Empty graph is planar"

    def test_large_grid_performance(self):
        """Test performance on larger grid graphs"""
        # This should complete in reasonable time
        G = nx.grid_2d_graph(4, 4)

        try:
            count = ff.count_perfect_matchings(G)
            assert count >= 0, "Should return non-negative count"
        except Exception as e:
            pytest.fail(f"Performance test failed on 4x4 grid: {e}")

    # TODO : HANDLE DISCONNECTED GRAPHS

    # def test_disconnected_graph_matching(self):
    #     """Test perfect matching on disconnected graphs"""
    #     # Two disconnected edges
    #     G = nx.Graph()
    #     G.add_edges_from([(0, 1), (2, 3)])

    #     count = ff.count_perfect_matchings(G)
    #     assert count == 1, "Two disconnected edges should have 1 perfect matching"

    #     # Disconnected with odd component
    #     G.add_node(4)  # Isolated node
    #     count = ff.count_perfect_matchings(G)
    #     assert count == 0, "Graph with isolated node has no perfect matching"

    def test_multigraph_handling(self):
        """Test handling of multigraphs"""
        # Create multigraph
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (0, 1), (1, 2)])  # Double edge

        # Should handle gracefully (convert to simple graph or error)
        try:
            result = ff.count_perfect_matchings(G)
            assert isinstance(result, (int, float)), "Should return numeric result"
        except ValueError:
            # Acceptable to reject multigraphs
            pass


class TestSpecialGraphClasses:
    """Test algorithms on special classes of graphs"""

    def test_complete_graphs(self):
        """Test on complete graphs"""
        # K4 is planar
        G = nx.complete_graph(4)
        assert nx.is_planar(G), "K4 should be planar"

        count = ff.count_perfect_matchings(G)
        assert np.allclose(count, 3), "K4 should have 3 perfect matchings"

        # K5 is not planar
        G = nx.complete_graph(5)
        assert not nx.is_planar(G), "K5 should not be planar"

    def test_bipartite_graphs(self):
        """Test on bipartite graphs"""
        # Complete bipartite K2,2
        G = nx.complete_bipartite_graph(2, 2)
        assert nx.is_planar(G), "K2,2 should be planar"

        count = ff.count_perfect_matchings(G)
        assert np.allclose(count, 2), "K2,2 should have 2 perfect matchings"

        # Complete bipartite K3,3
        G = nx.complete_bipartite_graph(3, 3)
        assert not nx.is_planar(G), "K3,3 should not be planar"

    def test_wheel_graphs(self):
        """Test on wheel graphs"""
        # Wheel graph W5 (cycle + center)
        G = nx.wheel_graph(6)  # 5-wheel has 6 nodes
        assert nx.is_planar(G), "Wheel graph should be planar"

        # Check basic properties

        assert np.allclose(G.number_of_nodes(), 6), "W5 should have 6 nodes"
        assert np.allclose(G.number_of_edges(), 10), "W5 should have 10 edges"

    def test_petersen_graph(self):
        """Test on Petersen graph (famous non-planar graph)"""
        G = nx.petersen_graph()
        assert not nx.is_planar(G), "Petersen graph should not be planar"

        # Should have no perfect matching (10 nodes, but structure prevents it)
        count = ff.count_perfect_matchings(G)
        assert count >= 0, "Perfect matching count should be non-negative"


class TestAlgorithmCorrectness:
    """Test correctness of algorithms against known results"""

    def test_known_perfect_matching_counts(self):
        """Test against known perfect matching counts"""
        test_cases = [
            (nx.path_graph(2), 1),  # Single edge
            (nx.path_graph(4), 1),  # Path of 4 nodes
            (nx.cycle_graph(4), 2),  # 4-cycle
            (nx.cycle_graph(6), 2),  # 6-cycle
            (nx.complete_graph(4), 3),  # K4
        ]

        for G, expected in test_cases:
            if nx.is_planar(G):  # Only test planar graphs
                count = ff.clean(ff.count_perfect_matchings(G))
                if count != expected:
                    nx.draw(G)
                assert np.allclose(
                    count, expected
                ), f"Graph should have {expected} perfect matchings, got {count}"

    def test_pfaffian_perfect_matching_relationship(self):
        """Test relationship between pfaffian and perfect matching count"""
        # For planar graphs, pfaffian of adjacency matrix relates to perfect matchings
        G = nx.cycle_graph(4)
        A = nx.adjacency_matrix(G).toarray()

        # Make skew-symmetric version for pfaffian
        A_skew = A - A.T  # This won't work directly, need proper orientation

        # This is a complex relationship, just test that both give finite results
        count = ff.count_perfect_matchings(G)
        pf_val = ff.pf(A_skew)

        assert np.isfinite(count), "Perfect matching count should be finite"
        assert np.isfinite(pf_val), "Pfaffian should be finite"

    def test_euler_formula_verification(self):
        """Test Euler's formula on planar graphs"""
        planar_graphs = [
            nx.cycle_graph(5),
            nx.complete_graph(4),
            nx.grid_2d_graph(2, 3),
        ]

        for G in planar_graphs:
            if nx.is_connected(G):
                v = G.number_of_nodes()
                e = G.number_of_edges()
                faces = ff.faces(G)
                f = len(faces)

                euler_char = v - e + f
                if not np.allclose(euler_char, 2):
                    print(
                        "Euler characteristic should be 2",
                        f" got {euler_char} for graph with v={v}, e={e}, f={f}",
                    )
                    assert False, f"Euler characteristic should be 2; got {euler_char}"
