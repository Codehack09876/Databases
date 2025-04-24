import bisect
import math
from typing import Any, List, Optional, Tuple, Union
from graphviz import Digraph

NodeValue = Union['BPlusTreeNode', Any] # Child node or actual data

class BPlusTreeNode:
    """Represents a node in the B+ Tree (Internal or Leaf)."""
    def __init__(self, order, parent = None, is_leaf = False):
        self.order = order
        self.parent = parent
        self.keys = []
        self.values = [] 
        self.is_leaf = is_leaf
        self.next = None

    def is_full(self):
        return len(self.keys) == self.order - 1

    def has_excess_keys(self, min_keys: int):
        return len(self.keys) > min_keys

    def is_underflow(self, min_keys: int):
        if self.parent is None: return False
        return len(self.keys) < min_keys

class BPlusTree:

    def __init__(self, order = 4):
        if order < 3: 
            raise ValueError("B+ Tree order must be at least 3")
        self.order = order
        self.root = BPlusTreeNode(order, is_leaf=True)
        self._min_keys = self.order // 2

    
    def _find_leaf(self, key: Any):
        
        node = self.root
        while not node.is_leaf:
            assert len(node.values) == len(node.keys) + 1, f"Inv Vio: N {node} K {len(node.keys)} V {len(node.values)}"
            idx = bisect.bisect_right(node.keys, key)
            assert idx < len(node.values), f"Idx Err: idx={idx}, len(V)={len(node.values)} N {node}"
            next_node = node.values[idx]
            assert next_node.parent is node, f"Parent Err: C {next_node} P {next_node.parent}, Exp {node}"
            node = next_node
        return node


    def search(self, key):
        
        leaf = self._find_leaf(key)
        # Find insertion point for key
        idx = bisect.bisect_left(leaf.keys, key)
        # Check if key at that index actually matches
        if idx < len(leaf.keys) and leaf.keys[idx] == key:
            return leaf.values[idx]
        return None

    def insert(self, key, value):
        
        leaf = self._find_leaf(key)
        insert_idx = bisect.bisect_left(leaf.keys, key)
        leaf.keys.insert(insert_idx, key)
        leaf.values.insert(insert_idx, value)
        if len(leaf.keys) == self.order: # Overflow check
            self._split_node(leaf)

    def delete(self, key):
        
        leaf = self._find_leaf(key)
        # Find potential index using bisect_left
        idx = bisect.bisect_left(leaf.keys, key)
        # Verify key exists at that index
        if idx < len(leaf.keys) and leaf.keys[idx] == key:
            leaf.keys.pop(idx)
            leaf.values.pop(idx)
            if leaf.is_underflow(self._min_keys):
                self._handle_underflow(leaf)
            return True 
        return False 

    def update(self, key, new_value):
        
        leaf = self._find_leaf(key)
        idx = bisect.bisect_left(leaf.keys, key)
        if idx < len(leaf.keys) and leaf.keys[idx] == key:
            leaf.values[idx] = new_value
            return True
        return False # Key not found

    # def range_query(self, start_key, end_key):
    #     result = []
    #     leaf = self._find_leaf(start_key)
    #     while leaf is not None:
    #         for i, k in enumerate(leaf.keys):
    #             if k >= start_key:
    #                 if k <= end_key: result.append((k, leaf.values[i]))
    #                 else: return result
    #         if not leaf.keys or leaf.keys[-1] >= end_key: 
    #             break
    #         leaf = leaf.next_leaf
    #     return result
    # def range_query(self, start_key, end_key):
    #     results = []
    #     node = self.root
    #     # Traverse down to the appropriate leaf node
    #     while not node.is_leaf:
    #         i = 0
    #         while i < len(node.keys) and start_key >= node.keys[i]:
    #             i += 1
    #         node = node.next[i]

    #     # Scan leaf nodes starting from the appropriate one
    #     while node:
    #         for i, key in enumerate(node.keys):
    #             if start_key <= key <= end_key:
    #                 results.append((key, node.values[i]))
    #             elif key > end_key:
    #                 return results
    #         node = node.next  # Linked list traversal
    #     return results
    def _split_node(self, node):
        mid = self.order // 2
        new_sibling = BPlusTreeNode(self.order, node.parent, node.is_leaf)
        
        if node.is_leaf:
            key_to_parent = node.keys[mid]
            new_sibling.keys = node.keys[mid:]
            new_sibling.values = node.values[mid:]
            node.keys = node.keys[:mid]
            node.values = node.values[:mid]
            # PROPERLY MAINTAIN LEAF LINKS
            new_sibling.next = node.next
            node.next = new_sibling
        else:
            key_to_parent = node.keys[mid]
            new_sibling.keys = node.keys[mid + 1:]
            new_sibling.values = node.values[mid + 1:]
            node.keys = node.keys[:mid]
            node.values = node.values[:mid + 1]
            for child in new_sibling.values: 
                child.parent = new_sibling
        
        self._insert_in_parent(node, key_to_parent, new_sibling)

    def range_query(self, start_key, end_key):
        results = []
        leaf = self._find_leaf(start_key)
        
        while leaf is not None:
            # Find starting position efficiently
            start_idx = bisect.bisect_left(leaf.keys, start_key)
            
            for i in range(start_idx, len(leaf.keys)):
                key = leaf.keys[i]
                if key > end_key:
                    return results
                results.append((key, leaf.values[i]))
            
            leaf = leaf.next  # Use the properly maintained linked list
        
        return results

    def get_all(self):
        result = []
        node = self.root
        while not node.is_leaf:
             if not node.values: 
                return []
             node = node.values[0] 
        current_leaf = node
        while current_leaf is not None:
            for i, k in enumerate(current_leaf.keys): 
                result.append((k, current_leaf.values[i]))
            current_leaf = current_leaf.next
        return result

    # def _split_node(self, node):
    #     mid = self.order // 2
    #     new_sibling = BPlusTreeNode(self.order, node.parent, node.is_leaf)
    #     if node.is_leaf:
    #         key_to_parent = node.keys[mid]
    #         new_sibling.keys = node.keys[mid:]
    #         new_sibling.values = node.values[mid:]
    #         node.keys = node.keys[:mid]
    #         node.values = node.values[:mid]
    #         new_sibling.next = node.next
    #         node.next = new_sibling
    #     else:
    #         key_to_parent = node.keys[mid]
    #         new_sibling.keys = node.keys[mid + 1:]
    #         new_sibling.values = node.values[mid + 1:]
    #         node.keys = node.keys[:mid]
    #         node.values = node.values[:mid + 1]
    #         for child in new_sibling.values: 
    #             child.parent = new_sibling # type: ignore
    #         assert len(node.values) == len(node.keys) + 1, "Inv fail split orig"
    #         assert len(new_sibling.values) == len(new_sibling.keys) + 1, "Inv fail split sib"
    #     self._insert_in_parent(node, key_to_parent, new_sibling)

    def _insert_in_parent(self, left_child, key, right_child):
        parent = left_child.parent
        if parent is None:
            new_root = BPlusTreeNode(self.order, is_leaf=False)
            new_root.keys = [key]
            new_root.values = [left_child, right_child]
            left_child.parent = new_root
            right_child.parent = new_root
            self.root = new_root
            return
        insert_idx = bisect.bisect_left(parent.keys, key)
        parent.keys.insert(insert_idx, key)
        parent.values.insert(insert_idx + 1, right_child)
        right_child.parent = parent
        assert len(parent.values) == len(parent.keys) + 1, "Inv fail insert parent"
        if len(parent.keys) == self.order: 
            self._split_node(parent)

    def _handle_underflow(self, node):
        if node.parent is None:
            if not node.is_leaf and not node.keys and len(node.values) == 1: 
                self.root = node.values[0] 
                self.root.parent = None # type: ignore
            return
        parent = node.parent
        try: 
            child_index = parent.values.index(node)
        except ValueError:
            raise RuntimeError(f"Consistency Err: N {node} not in P {parent}")
        if child_index > 0: # Try borrow left
            left_sibling = parent.values[child_index - 1]
            if left_sibling.has_excess_keys(self._min_keys): 
                self._borrow_from_left(node, left_sibling, parent, child_index)
                return
        if child_index < len(parent.values) - 1: # Try borrow right
            right_sibling = parent.values[child_index + 1]
            if right_sibling.has_excess_keys(self._min_keys): 
                self._borrow_from_right(node, right_sibling, parent, child_index)
                return
        if child_index > 0: # Merge left
            self._merge_nodes(parent.values[child_index - 1], node, parent, child_index - 1)
        elif child_index < len(parent.values) - 1: # Merge right
             self._merge_nodes(node, parent.values[child_index + 1], parent, child_index)
        else: 
            raise RuntimeError(f"Unexpected state in handle_underflow N {node}")

    def _borrow_from_left(self, node, left_sibling, parent, node_idx):
        sep_idx = node_idx - 1
        if node.is_leaf:
            k = left_sibling.keys.pop()
            v = left_sibling.values.pop()
            node.keys.insert(0, k)
            node.values.insert(0, v)
            parent.keys[sep_idx] = node.keys[0]
        else:
            sep_k = parent.keys[sep_idx]
            node.keys.insert(0, sep_k)
            parent.keys[sep_idx] = left_sibling.keys.pop()
            child = left_sibling.values.pop()
            node.values.insert(0, child)
            child.parent = node # type: ignore

    def _borrow_from_right(self, node, right_sibling, parent, node_idx):
        sep_idx = node_idx
        if node.is_leaf:
            k = right_sibling.keys.pop(0)
            v = right_sibling.values.pop(0)
            node.keys.append(k)
            node.values.append(v)
            parent.keys[sep_idx] = right_sibling.keys[0] if right_sibling.keys else k
        else:
            sep_k = parent.keys[sep_idx]
            node.keys.append(sep_k)
            parent.keys[sep_idx] = right_sibling.keys.pop(0)
            child = right_sibling.values.pop(0)
            node.values.append(child)
            child.parent = node # type: ignore

    def _merge_nodes(self, left_node, right_node, parent, left_idx):
        sep_k = parent.keys.pop(left_idx)
        parent.values.pop(left_idx + 1)
        if not left_node.is_leaf:
            left_node.keys.append(sep_k)
            left_node.keys.extend(right_node.keys)
            moved_children = list(right_node.values)
            left_node.values.extend(moved_children)
            for child in moved_children: 
                child.parent = left_node # type: ignore
        else:
            left_node.keys.extend(right_node.keys)
            left_node.values.extend(right_node.values)
            left_node.next = right_node.next
        assert len(left_node.values) == len(left_node.keys) + (0 if left_node.is_leaf else 1), "Inv fail merge"
        if parent.is_underflow(self._min_keys): 
            self._handle_underflow(parent)

    # --- Visualization (Keep HTML version from previous step) ---

    def visualize_tree(self):
        
        dot = Digraph(comment='B+ Tree', node_attr={'shape': 'box', 'style': 'rounded,filled'})
        
        if not self.root or (self.root.is_leaf and not self.root.keys):
            dot.node('empty', 'Tree is empty')
            return dot

        node_queue = [(self.root, 'node_root')]
        node_id_map = {self.root: 'node_root'}
        id_counter = 0
        processed_nodes = set()
        leaf_nodes = []

        while node_queue:
            current_node, node_id = node_queue.pop(0)
            if current_node in processed_nodes:
                continue
            processed_nodes.add(current_node)

            # Create node label with just keys
            if current_node.keys:
                label = " | ".join(str(k) for k in current_node.keys)
            else:
                label = "[empty]"

            # Style differently for leaves vs internal nodes
            if current_node.is_leaf:
                dot.node(node_id, label, fillcolor='lightblue')
                leaf_nodes.append((current_node, node_id))
            else:
                dot.node(node_id, label, fillcolor='lightgray')

                # Add children to queue
                for i, child in enumerate(current_node.values):
                    if child not in node_id_map:
                        id_counter += 1
                        child_id = f"node_{id_counter}"
                        node_id_map[child] = child_id
                    if child not in processed_nodes:
                        node_queue.append((child, node_id_map[child]))
                    # Simple edge without ports
                    dot.edge(node_id, node_id_map[child])

        # Draw links between leaf nodes
        for i in range(len(leaf_nodes)-1):
            current_node, current_id = leaf_nodes[i]
            next_node, next_id = leaf_nodes[i+1]
            if current_node.next == next_node:
                dot.edge(current_id, next_id, style='dashed', arrowhead='none')

        return dot