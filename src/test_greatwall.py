from greatwall.resources.greatwall import GreatWall

def test_navigation_history():

    greatwall = GreatWall()
    greatwall.set_depth(4)
    greatwall.set_arity(3)

    assert(greatwall.saved_path == [])
    assert(greatwall.saved_states == {})

    greatwall.time_intensive_derivation()

    step_done = greatwall.history_step_next(0)
    assert(step_done)
    assert(greatwall.saved_path == [0])

    greatwall.time_intensive_derivation()

    step_done = greatwall.history_step_next(0)
    assert(step_done)
    assert(greatwall.saved_path == [0, 0])

    greatwall.time_intensive_derivation()

    step_done = greatwall.history_step_next(0)
    assert(step_done)
    assert(greatwall.saved_path == [0, 0, 0])

    greatwall.time_intensive_derivation()

    step_done = greatwall.history_step_next(0)
    assert(step_done)
    assert(greatwall.saved_path == [0, 0, 0, 0])

    greatwall.time_intensive_derivation()

    step_done = greatwall.history_step_next(0)
    assert(not step_done)
    assert(greatwall.saved_path == [0, 0, 0, 0])

    greatwall.history_step_back()
    assert(greatwall.saved_path == [0, 0, 0])

    greatwall.history_step_back()
    assert(greatwall.saved_path == [0, 0])

    greatwall.history_step_back()
    assert(greatwall.saved_path == [0])

    greatwall.history_step_back()
    assert(greatwall.saved_path == [])

    greatwall.history_step_back()
    assert(greatwall.saved_path == [])

def test_history_reset():

    greatwall = GreatWall()
    greatwall.set_depth(5)
    greatwall.set_arity(2)

    assert(greatwall.saved_path == [])
    assert(greatwall.saved_states == {})

    greatwall.time_intensive_derivation()

    step_done = greatwall.history_step_next(0)
    assert(step_done)
    assert(greatwall.saved_path == [0])

    greatwall.time_intensive_derivation()

    step_done = greatwall.history_step_next(1)
    assert(step_done)
    assert(greatwall.saved_path == [0, 1])

    greatwall.time_intensive_derivation()

    step_done = greatwall.history_step_next(0)
    assert(step_done)
    assert(greatwall.saved_path == [0, 1, 0])

    greatwall.history_reset()
    assert(greatwall.saved_path == [])
    assert(greatwall.saved_states == {})

def test_history_path_to_index():

    greatwall = GreatWall()

    # the path [] maps to the index 0, for any tree
    index = greatwall.history_path_to_index([])
    assert(index == 0)

    # the path [1, 2] maps to the index 23, for a tree of arity 3 and depth 4
    greatwall.set_arity(3)
    greatwall.set_depth(4)
    index = greatwall.history_path_to_index([1, 2])
    assert(index == 23)

    # the path [0, 1, 1] maps to the index 13, for a tree of arity 2 and depth 5
    greatwall.set_arity(2)
    greatwall.set_depth(5)
    index = greatwall.history_path_to_index([0, 1, 1])
    assert(index == 13)

