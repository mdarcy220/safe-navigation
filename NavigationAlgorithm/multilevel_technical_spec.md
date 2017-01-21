# Multi-level Navigation Algorithm Description and Explanation

This document describes a multi-level navigation planner, using both a
high-level global planner and a local planner. The local planner can be any
algorithm that works over short distances.


## The Algorithm
Initialize the graph with one vertex at the starting location of the robot.
Optionally, additional information about static obstacles could also be encoded
if available. For example, if the environment has a known map, it could be used
to generate a roadmap of vertices and edges.

1. Make a list of to-be-checked (TBC) points

      1.a. Include all pre-existing points within a certain distance of the
	   current point.

      1.b. Until the point cap is reached, generate new points (which could be
	   generated randomly or according to some other generation algorithm).
	   These are marked as "unvisited points" (which hereinafter may also
	   be referred to as "unexplored states" or "unexplored nodes").

2. For each TBC point, use the local planner to check if a path can be found
   *directly* from the current point to the point in question. If so, add a
   finite-cost edge between the two points, where the cost could be uniform for
   all edges or determined based on some traversability metric (which could
   include safety, so less-safe edges would be considered as having higher
   cost).  If not, add an infinite-cost edge between the two points (note:
   maybe it would be better to set to "unknown" instead of infinite, since it
   could be blocked by a dynamic obstacle that will move away later?).

3. Select the next unexplored node to visit. To do this, start by attempting
   to do an AStar search from the current point to the goal. Nodes that are not
   marked as unexplored can be expanded normally, but when the search attempts
   to expand an unexplored node, the search algorithm is immediately halted
   and the unexplored node that was to be expanded becomes the next node to
   visit.

4. Plan a high-level path to the next unexplored node to visit ("high-level"
   meaning it plans a series of waypoints in the graph, rather than planning
   every detail of the sequence of actions to take; this allows the local
   planner to have some flexibility in the next step). (Optimization note: This
   might be possible to speed up by reusing the path generated while running
   the AStar in Step 3.)

5. Follow the path from Step 4, using the local planner to go from waypoint to
   waypoint safely.

      5.a. Depending on processing power constraints is may be desirable to go
	   back to Step 1 each time a waypoint is reached, to update the edge
	   weights (a previously blocked path may now be accessible, or a
	   previously accessable path may now be blocked) and re-select a more
	   appropriate next node to visit if the weights have changed.

      5.b. It is possible that the local planner may have to make a significant
	   detour for safety reasons. In this case, either the planner could
	   continue to head towards the selected waypoint, or the high-level
	   planner could change the route to account for the unexpected factor.
	   One option is to add a new vertex to the graph any time the robot
	   wanders too far off course, and then go back to Step 1, starting at
	   the new node.


6. When the next node to visit is eventually reached, check if it is the goal
   node. If so, stop. If not, go back to Step 1.


## Notes
- Because a cap is set on the number of connections from a point, and
  connections are first searched for with nearby points, new points
  will not be generated in areas where there are already many points
  nearby. This, combined with the fact that the robot only seeks out
  unexplored nodes, means that the robot will not needlessly wander
  around the same area for a long period of time.

- The cap on the number of connections from each point makes it
  possible that the graph will reach saturation; that is, there will be
  no unexplored points left. In this case, the point cap could be
  raised incrementally over time. Alternatively, it might be better to
  use a more intelligent method of generating new points, such that
  there will always be some that are outside the convex hull of the
  graph. This would be more difficult to design an implement, but would
  have the advantage of ensuring the graph expands outwards, increasing
  exploration and minimizing the chances of saturation.

- There would have to be some kind of termination condition for the
  case that a path doesn't exist. For now, we will assume a simple cap
  on the maximum number of steps the robot is allowed to take.
