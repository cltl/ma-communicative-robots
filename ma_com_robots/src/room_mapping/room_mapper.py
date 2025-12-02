import sys
from pathlib import Path

from config import ROOM_SIGNATURES

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
from collections import defaultdict, Counter, deque


class RoomMapper:

    def __init__(self, controller):
        self.controller = controller
        self.room_classifications = {}
        self.data = []
        self.labels = []
        self.room_types = ROOM_SIGNATURES

    def initialize_house_map(self):
        event = self.controller.step(action="GetReachablePositions")
        pos_list = event.metadata["actionReturn"]

        x_vals = [p['x'] for p in pos_list]
        z_vals = [p['z'] for p in pos_list]

        x_min, x_max = min(x_vals), max(x_vals)
        z_min, z_max = min(z_vals), max(z_vals)

        x_range = x_max - x_min
        z_range = z_max - z_min

        print(f"House dimensions: {x_range:.2f}m (x) × {z_range:.2f}m (z)")
        print(f"Area: {x_range * z_range:.2f} m²")

        base_pts = 5
        x_pts = max(3, int(base_pts * (x_range / max(x_range, z_range))))
        z_pts = max(3, int(base_pts * (z_range / max(x_range, z_range))))

        print(f"Creating {x_pts}×{z_pts} grid")

        x_grid = np.linspace(x_min, x_max, x_pts)
        z_grid = np.linspace(z_min, z_max, z_pts)

        grid_pos = []
        for x in x_grid:
            for z in z_grid:
                nearest = self.find_nearest(x, z, pos_list)
                if nearest:
                    grid_pos.append(nearest)

        print(f"Generated {len(grid_pos)} grid positions")

        rotations = [0, 90, 180, 270]

        data = []
        wall_to_label = {}
        wall_counter = 0

        for i, pos in enumerate(grid_pos):
            walls = set()
            objects = []

            for rot in rotations:
                event = self.controller.step(action="Teleport", position=pos, rotation=rot)

                for obj in event.metadata["objects"]:
                    if obj["visible"]:
                        if "wall" in obj["objectId"].lower():
                            walls.add(obj["objectId"])
                        else:
                            objects.append(obj["objectType"])

            wall_labels = []
            for wall_id in walls:
                if wall_id not in wall_to_label:
                    wall_counter += 1
                    wall_to_label[wall_id] = wall_counter
                wall_labels.append(str(wall_to_label[wall_id]))

            wall_str = f"[{', '.join(sorted(wall_labels))}]" if wall_labels else "[]"
            print(
                f"Position {i + 1}/{len(grid_pos)}: ({pos['x']:.2f}, {pos['z']:.2f}) sees {len(walls)} walls {wall_str}")

            data.append({
                'position': pos,
                'walls': walls,
                'objects': objects,
                'x': pos['x'],
                'z': pos['z']
            })

        all_walls = set()
        for d in data:
            all_walls.update(d['walls'])

        all_walls = sorted(list(all_walls))
        print(f"\nTotal unique walls in house: {len(all_walls)}")

        bounds = (min(x_vals), max(x_vals), min(z_vals), max(z_vals))
        segments = self.get_wall_segments()
        rooms, grid_size, origin = self.make_rooms(segments, bounds)
        labels = self.assign_rooms(data, rooms, grid_size, origin)

        print(f"Found {len(rooms)} rooms using spatial wall analysis")

        for i, d in enumerate(data):
            d['cluster'] = labels[i]

        print(f"Found {len(set(labels))} clusters (rooms)")

        self.data = data
        self.labels = labels

        print("\nRoom Type Classification:")
        for cluster_id in sorted(set(labels)):
            cluster_data = [d for d in data if d['cluster'] == cluster_id]
            all_objs = []
            positions = []
            for d in cluster_data:
                all_objs.extend(d['objects'])
                positions.append(d['position'])

            scores = {}
            for room_type, sig in self.room_types.items():
                scores[room_type] = sum(all_objs.count(obj) for obj in sig)

            best = max(scores, key=scores.get) if max(scores.values()) > 0 else 'unknown'
            print(f"Cluster {cluster_id}: {best}")
            print(f"  Objects: {Counter(all_objs).most_common(5)}")

            self.room_classifications[cluster_id] = {
                'type': best,
                'objects': Counter(all_objs),
                'positions': positions
            }

        return True

    def find_nearest(self, target_x, target_z, pos_list):
        min_dist = float('inf')
        nearest = None
        for p in pos_list:
            dist = np.sqrt((p['x'] - target_x) ** 2 + (p['z'] - target_z) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest = p
        return nearest

    def get_wall_segments(self):
        event = self.controller.step(action="Pass")
        segments = []

        for obj in event.metadata["objects"]:
            if "wall" in obj["objectId"].lower():
                parts = obj["objectId"].split("|")
                if len(parts) >= 6:
                    try:
                        x1, z1, x2, z2 = float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])
                        segments.append(((x1, z1), (x2, z2)))
                    except:
                        pass
        return segments

    def make_rooms(self, segments, bounds):
        x_min, x_max, z_min, z_max = bounds
        grid_size = 0.25
        w = int((x_max - x_min) / grid_size) + 1
        h = int((z_max - z_min) / grid_size) + 1

        grid = np.zeros((h, w), dtype=int)

        for (x1, z1), (x2, z2) in segments:
            gx1 = int((x1 - x_min) / grid_size)
            gz1 = int((z1 - z_min) / grid_size)
            gx2 = int((x2 - x_min) / grid_size)
            gz2 = int((z2 - z_min) / grid_size)

            dx = abs(gx2 - gx1)
            dz = abs(gz2 - gz1)
            steps = max(dx, dz)

            if steps > 0:
                for i in range(steps + 1):
                    gx = int(gx1 + (gx2 - gx1) * i / steps)
                    gz = int(gz1 + (gz2 - gz1) * i / steps)
                    if 0 <= gx < w and 0 <= gz < h:
                        grid[gz, gx] = 1

        visited = np.zeros_like(grid, dtype=bool)
        rooms = {}
        room_id = 0

        for gz in range(h):
            for gx in range(w):
                if grid[gz, gx] == 0 and not visited[gz, gx]:
                    room_grid = np.zeros_like(grid, dtype=int)
                    queue = deque([(gx, gz)])
                    visited[gz, gx] = True
                    size = 0

                    while queue:
                        cx, cz = queue.popleft()
                        room_grid[cz, cx] = 1
                        size += 1

                        for dx, dz in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            nx, nz = cx + dx, cz + dz
                            if (0 <= nx < w and 0 <= nz < h and
                                    not visited[nz, nx] and grid[nz, nx] == 0):
                                visited[nz, nx] = True
                                queue.append((nx, nz))

                    if size > 5:
                        rooms[room_id] = room_grid
                        room_id += 1

        return rooms, grid_size, (x_min, z_min)

    def assign_rooms(self, data, rooms, grid_size, origin):
        x_min, z_min = origin
        labels = []

        for d in data:
            x, z = d['x'], d['z']
            gx = int((x - x_min) / grid_size)
            gz = int((z - z_min) / grid_size)

            room = -1
            for rid, room_grid in rooms.items():
                if (0 <= gx < room_grid.shape[1] and 0 <= gz < room_grid.shape[0] and
                        room_grid[gz, gx] == 1):
                    room = rid
                    break

            labels.append(room)

        return np.array(labels)
