"""
Node_Studio_Visual.py

A Python GUI application for visually designing node-based computational programs 
with a publish-subscribe architecture, inspired by ROS2, but for general Python programs.

ReadMe:
-------
Author: Akhil Shimna Kumar
Release History: v1 -> 12-06-2024
                 v2 -> 05-05-2025
                 v3 -> 18-10-2025
Last Modified: 18-10-2025
Version: 3.6.11
License: CC-BY-NC-ND 4.0 International
Copyright (c) 2025 Akhil Shimna Kumar on behalf of The T&O Synergic Metaverse

Installation (Official Channel):
--------------------------------


Features:
----------
- Create and manage nodes and topics visually.
- Drag-and-drop interface for moving nodes and topics on a canvas.
- Connect nodes and topics via arrows to define publish-subscribe relationships.
- Toggleable "Connect Mode" for creating connections without moving nodes.
- Right-click to delete connections between nodes and topics.
- Randomized placement of new nodes/topics to avoid overlap.
- Export designed node-topic structures as JSON configuration files.
- Import JSON configurations to reconstruct node-topic layouts.
- Export Python code compatible with T&OComputeEngine (or similar middleware).
- Dynamic arrow updates when nodes or topics are moved.

Usage Example:
--------------
from NodeStudio import NodeStudio

# Launch the visual editor
studio = NodeStudio()
studio.mainloop()

# Steps:
# 1. Add nodes and topics via the top toolbar.
# 2. Enable "Connect Mode" to draw publish-subscribe connections.
# 3. Right-click on arrows to remove connections if needed.
# 4. Export your design as JSON or Python code for use with T&OComputeEngine.

Notes:
------
- The editor is fully interactive and allows rapid prototyping of modular programs.
- Exported JSON can be loaded into T&OComputeEngine to automatically create nodes and connections.
- Intended for both educational purposes and rapid application development.
"""

import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import random
import json
from TnOComputeEngine import Node


class NodeBox:
    def __init__(self, canvas, name, x, y):
        self.canvas = canvas
        self.name = name
        self.rect = canvas.create_rectangle(x, y, x + 130, y + 60, fill="#4a90e2", outline="black", width=2)
        self.text = canvas.create_text(x + 65, y + 30, text=name, fill="white", font=("Arial", 11, "bold"))
        self.publish_topics = []
        self.subscribe_topics = []
        self.connections = []
        self._bind_events()

    def _bind_events(self):
        for tag in (self.rect, self.text):
            self.canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.canvas.master.start_action(self, event)
        self._drag_data = (event.x, event.y)

    def on_drag(self, event):
        if not self.canvas.master.connect_mode:
            dx = event.x - self._drag_data[0]
            dy = event.y - self._drag_data[1]
            self.canvas.move(self.rect, dx, dy)
            self.canvas.move(self.text, dx, dy)
            self._drag_data = (event.x, event.y)
            self.canvas.master.update_lines()
        else:
            self.canvas.master.drag_connect(event)

    def on_release(self, event):
        self.canvas.master.end_action(self, event)

    def center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        return ((x1 + x2) / 2, (y1 + y2) / 2)


class TopicCircle:
    def __init__(self, canvas, name, x, y):
        self.canvas = canvas
        self.name = name
        self.circle = canvas.create_oval(x, y, x + 70, y + 70, fill="#f5a623", outline="black", width=2)
        self.text = canvas.create_text(x + 35, y + 35, text=name, fill="white", font=("Arial", 11, "bold"))
        # bookkeeping lists (parallel to NodeBox)
        self.publish_topics = []    # not usually used but kept for symmetry
        self.subscribe_topics = []  # not usually used but kept for symmetry
        self.connections = []
        self._bind_events()


    def _bind_events(self):
        for tag in (self.circle, self.text):
            self.canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.canvas.master.start_action(self, event)
        self._drag_data = (event.x, event.y)

    def on_drag(self, event):
        if not self.canvas.master.connect_mode:
            dx = event.x - self._drag_data[0]
            dy = event.y - self._drag_data[1]
            self.canvas.move(self.circle, dx, dy)
            self.canvas.move(self.text, dx, dy)
            self._drag_data = (event.x, event.y)
            self.canvas.master.update_lines()
        else:
            self.canvas.master.drag_connect(event)

    def on_release(self, event):
        self.canvas.master.end_action(self, event)

    def center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.circle)
        return ((x1 + x2) / 2, (y1 + y2) / 2)


class NodeStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyROS Node Studio")
        self.geometry("1200x700")
        self.configure(bg="#2b2b2b")

        # Canvas
        self.canvas = tk.Canvas(self, bg="#1e1e1e")
        self.canvas.pack(fill="both", expand=True)

        # Toolbar
        toolbar = tk.Frame(self, bg="#333")
        toolbar.place(relx=0, rely=0, relwidth=1, height=40)
        tk.Button(toolbar, text="➕ Add Node", command=self.add_node).pack(side="left", padx=5)
        tk.Button(toolbar, text="🔘 Add Topic", command=self.add_topic).pack(side="left", padx=5)

        self.connect_btn = tk.Button(toolbar, text="🔗 Connect Mode: OFF", bg="#555", fg="white",
                                     command=self.toggle_connect)
        self.connect_btn.pack(side="left", padx=5)

        tk.Button(toolbar, text="💾 Export Code", command=self.export_code).pack(side="left", padx=5)
        tk.Button(toolbar, text="📂 Import Config", command=self.import_config).pack(side="left", padx=5)
        tk.Button(toolbar, text="💾 Export Config", command=self.export_config).pack(side="left", padx=5)
        tk.Button(toolbar, text="🧹 Clear", command=self.clear_all).pack(side="left", padx=5)

        # State
        self.nodes = {}
        self.topics = {}
        self.lines = []  # (line_id, node_obj, topic_obj, mode)
        self.dragging_from = None
        self.temp_line = None
        self.connect_mode = False

    # ---------------------------
    # Connect Mode Toggle
    # ---------------------------
    def toggle_connect(self):
        self.connect_mode = not self.connect_mode
        if self.connect_mode:
            self.connect_btn.config(text="🔗 Connect Mode: ON", bg="#228B22")
        else:
            self.connect_btn.config(text="🔗 Connect Mode: OFF", bg="#555")
        self.dragging_from = None
        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None

    # ---------------------------
    # Node/Topic creation
    # ---------------------------
    def add_node(self):
        name = simpledialog.askstring("Node Name", "Enter node name:")
        if not name:
            return
        x, y = random.randint(50, 900), random.randint(100, 500)
        node = NodeBox(self.canvas, name, x, y)
        self.nodes[name] = node

    def add_topic(self):
        name = simpledialog.askstring("Topic Name", "Enter topic name:")
        if not name:
            return
        x, y = random.randint(200, 1000), random.randint(100, 500)
        topic = TopicCircle(self.canvas, name, x, y)
        self.topics[name] = topic

    # ---------------------------
    # Drag/Connect actions
    # ---------------------------
    def start_action(self, obj, event):
        if self.connect_mode:
            self.dragging_from = obj
            cx, cy = obj.center()
            self.temp_line = self.canvas.create_line(cx, cy, event.x, event.y, fill="#aaa", width=2, dash=(3, 3))
            self.canvas.bind("<Motion>", self.drag_connect)

    def drag_connect(self, event):
        if self.connect_mode and self.temp_line and self.dragging_from:
            cx, cy = self.dragging_from.center()
            self.canvas.coords(self.temp_line, cx, cy, event.x, event.y)

    def end_action(self, obj, event):
        if not self.connect_mode:
            return
        self.canvas.unbind("<Motion>")

        # Find object under mouse
        x, y = event.x, event.y
        overlapping = self.canvas.find_overlapping(x, y, x, y)
        target = None
        for item in overlapping:
            for node in self.nodes.values():
                if item in (node.rect, node.text):
                    target = node
                    break
            for topic in self.topics.values():
                if item in (topic.circle, topic.text):
                    target = topic
                    break
            if target:
                break

        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None

        if self.dragging_from and target and self.dragging_from != target:
            self.create_connection(self.dragging_from, target)
        self.dragging_from = None

    # ---------------------------
    # Connections
    # ---------------------------


    def create_connection(self, src, dst, mode=None):
        """
        Create visual and logical connection between a NodeBox and TopicCircle.
        src/dst may be NodeBox or TopicCircle in either order.
        If mode is None, show the button popup to choose pub/sub.
        """
        # Determine which is node and which is topic
        node_obj = None
        topic_obj = None

        if isinstance(src, NodeBox) and isinstance(dst, TopicCircle):
            node_obj = src
            topic_obj = dst
        elif isinstance(src, TopicCircle) and isinstance(dst, NodeBox):
            node_obj = dst
            topic_obj = src
        else:
            # unsupported types (e.g., node->node or topic->topic)
            return

        # If mode not provided, ask user (UI buttons)
        if not mode:
            mode = self.ask_mode_popup(node_obj.name, topic_obj.name)
            if not mode:
                return  # user cancelled

        color = "#00ff99" if mode == "pub" else "#ff6666"

        # Draw connection line between centers
        nx, ny = node_obj.center()
        tx, ty = topic_obj.center()
        line = self.canvas.create_line(nx, ny, tx, ty, width=2, fill=color, arrow="last")

        # Record connection consistently: line, node, topic, mode
        self.lines.append((line, node_obj, topic_obj, mode))

        # update per-object connection lists
        node_obj.connections.append((line, topic_obj))
        topic_obj.connections.append((line, node_obj))

        # update node's pub/sub lists (node is the logical owner)
        if mode == "pub":
            if topic_obj.name not in node_obj.publish_topics:
                node_obj.publish_topics.append(topic_obj.name)
        else:
            if topic_obj.name not in node_obj.subscribe_topics:
                node_obj.subscribe_topics.append(topic_obj.name)

        # right-click to delete connection
        self.canvas.tag_bind(line, "<Button-3>", lambda e, l=line: self.delete_connection(l))




    def ask_mode_popup(self, node_name, topic_name):
        """Show popup window with Pub/Sub buttons instead of text input."""
        popup = tk.Toplevel(self)
        popup.title("Select Connection Type")
        popup.geometry("300x150")
        popup.configure(bg="#2b2b2b")
        popup.transient(self)
        popup.grab_set()

        tk.Label(
            popup,
            text=f"Connect '{node_name}' with '{topic_name}'",
            bg="#2b2b2b", fg="white",
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        mode = {"choice": None}

        def set_mode(m):
            mode["choice"] = m
            popup.destroy()

        tk.Button(popup, text="Publisher →", bg="#00aa77", fg="white",
                  width=14, command=lambda: set_mode("pub")).pack(pady=5)

        tk.Button(popup, text="← Subscriber", bg="#cc4444", fg="white",
                  width=14, command=lambda: set_mode("sub")).pack(pady=5)

        tk.Button(popup, text="Cancel", bg="#555", fg="white",
                  width=14, command=popup.destroy).pack(pady=5)

        popup.wait_window()
        return mode["choice"]





    def update_lines(self):
        for line_id, node_obj, topic_obj, _ in self.lines:
            nx, ny = node_obj.center()
            tx, ty = topic_obj.center()
            self.canvas.coords(line_id, nx, ny, tx, ty)

    def delete_connection(self, line_id):
        # remove visual
        try:
            self.canvas.delete(line_id)
        except Exception:
            pass

        # remove from lines list
        self.lines = [c for c in self.lines if c[0] != line_id]

        # clean up node/topic connection lists
        for node in self.nodes.values():
            # remove line entries
            node.connections = [c for c in node.connections if c[0] != line_id]
            # rebuild publish/subscribe lists from remaining connections
            pub_set = set()
            sub_set = set()
            for (l, topic_obj) in node.connections:
                # find corresponding mode in self.lines if present
                for ln, nobj, tobj, mode in self.lines:
                    if ln == l and nobj is node and tobj is topic_obj:
                        if mode == "pub":
                            pub_set.add(tobj.name)
                        else:
                            sub_set.add(tobj.name)
            node.publish_topics = list(pub_set)
            node.subscribe_topics = list(sub_set)

        for topic in self.topics.values():
            topic.connections = [c for c in topic.connections if c[0] != line_id]
            # keep topic.publish/subscribe lists in sync (optional)
            # not necessary, but ensure no stale entries
            topic.publish_topics = []
            topic.subscribe_topics = []
            for (l, node_obj) in topic.connections:
                for ln, nobj, tobj, mode in self.lines:
                    if ln == l and nobj is node_obj and tobj is topic:
                        if mode == "pub":
                            topic.publish_topics.append(node_obj.name)
                        else:
                            topic.subscribe_topics.append(node_obj.name)


    # ---------------------------
    # Export Python Code
    # ---------------------------
    def export_code(self):
        code = ["from AkhilShimnaKumar.TnOComputeEngine import Node\n", "import time\n\n"]
        for node_name, node in self.nodes.items():
            code.append(f"# --- Node: {node_name} ---\n")
            code.append(f"{node_name} = Node('{node_name}')\n")
            for t in node.subscribe_topics:
                code.append(f"@{node_name}.subscriber('{t}')\n")
                code.append(f"def on_{node_name}_{t}(msg):\n")
                code.append(f"    print('[{node_name}] received from {t}:', msg)\n\n")
            for t in node.publish_topics:
                code.append(f"{node_name}_{t}_pub = {node_name}.publisher('{t}')\n")
                code.append(f"@{node_name}.timer(1.0)\n")
                code.append(f"def pub_{node_name}_{t}():\n")
                code.append(f"    {node_name}_{t}_pub('Hello from {node_name}!')\n\n")
            code.append(f"{node_name}.spin()\n\n")

        path = filedialog.asksaveasfilename(title="Save Python File", defaultextension=".py",
                                            filetypes=[("Python Files", "*.py")])
        if path:
            with open(path, "w") as f:
                f.write("".join(code))
            messagebox.showinfo("Exported", f"Python code saved to:\n{path}")

    # ---------------------------
    # Export/Import JSON Configuration
    # ---------------------------
    def export_config(self):
        config = {"nodes": {}, "topics": list(self.topics.keys()), "connections": []}
        for node_name, node in self.nodes.items():
            config["nodes"][node_name] = {
                "publish": node.publish_topics,
                "subscribe": node.subscribe_topics
            }
        for line_id, node_obj, topic_obj, mode in self.lines:
            config["connections"].append({
                "from": node_obj.name,
                "to": topic_obj.name,
                "mode": mode
            })
        path = filedialog.asksaveasfilename(title="Save Config", defaultextension=".json",
                                            filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, "w") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Exported", f"Configuration saved to {path}")

    def import_config(self):
        path = filedialog.askopenfilename(title="Open Config",
                                          filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        with open(path, "r") as f:
            config = json.load(f)

        # clear without confirmation (since user chose import)
        self.canvas.delete("all")
        self.nodes.clear()
        self.topics.clear()
        self.lines.clear()

        # recreate nodes
        for node_name, data in config.get("nodes", {}).items():
            x, y = random.randint(50, 900), random.randint(100, 500)
            node = NodeBox(self.canvas, node_name, x, y)
            node.publish_topics = data.get("publish", [])
            node.subscribe_topics = data.get("subscribe", [])
            self.nodes[node_name] = node

        # recreate topics
        for topic_name in config.get("topics", []):
            x, y = random.randint(200, 1000), random.randint(100, 500)
            topic = TopicCircle(self.canvas, topic_name, x, y)
            self.topics[topic_name] = topic

        # recreate connections (mode provided, so no popup)
        for conn in config.get("connections", []):
            node = self.nodes.get(conn["from"])
            topic = self.topics.get(conn["to"])
            mode = conn.get("mode")
            if node and topic and mode:
                self.create_connection(node, topic, mode)
o

    # ---------------------------
    # Clear canvas
    # ---------------------------
    def clear_all(self):
        if messagebox.askyesno("Clear", "Clear all nodes and topics?"):
            self.canvas.delete("all")
            self.nodes.clear()
            self.topics.clear()
            self.lines.clear()


if __name__ == "__main__":
    NodeStudio().mainloop()
