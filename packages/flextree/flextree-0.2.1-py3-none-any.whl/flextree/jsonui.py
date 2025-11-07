"""
FlexTree JSON UI - A graphical interface for viewing and exploring tree structures.

This module provides a GUI application with a tree viewer panel on the left
and an information viewer panel on the right, allowing interactive exploration
of tree data structures.
"""
import json
import copy
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import Optional, Dict, Any, List, Tuple
from flextree import TreeNode, Tree


class ActionMemorySystem:
    """
    A system to remember and manage undo/redo operations for tree actions.
    
    This class maintains a history of actions performed on the tree, storing
    the action type, the tree state before the action, selected node, and
    tree expansion state. It supports up to 20 steps of history.
    """
    
    def __init__(self, max_steps: int = 20):
        """
        Initialize the action memory system.
        
        Args:
            max_steps: Maximum number of action steps to remember
        """
        self.max_steps = max_steps
        self.action_history: List[Dict[str, Any]] = []
        self.current_index = -1  # -1 means no actions yet
        
    def record_action(self, action_type: str, tree_state_before: Tree, 
                     selected_node_name: Optional[str], expansion_state: Dict[str, Any],
                     action_data: Optional[Dict[str, Any]] = None):
        """
        Record an action in the history.
        
        Args:
            action_type: Type of action performed (e.g., 'cut', 'copy', 'paste', 'delete', 'insert', 'rename', 'content_edit')
            tree_state_before: Deep copy of the tree state before the action
            selected_node_name: Name of the selected node when action was performed
            expansion_state: Current expansion state and selection
            action_data: Additional data specific to the action type
        """
        # Remove any actions after current index (when we're in the middle of history)
        if self.current_index >= 0:
            self.action_history = self.action_history[:self.current_index + 1]
        
        # Create action record
        action_record = {
            'action_type': action_type,
            'tree_state_before': tree_state_before,
            'selected_node_name': selected_node_name,
            'expansion_state': expansion_state,
            'action_data': action_data or {},
            'tree_state_after': None,  # Will be set by complete_action
            'expansion_state_after': None,
            'selected_node_name_after': None,
            'timestamp': None  # Could add timestamp if needed
        }
        
        # Add to history
        self.action_history.append(action_record)
        
        # Maintain max steps limit
        if len(self.action_history) > self.max_steps:
            self.action_history.pop(0)
            if self.current_index >= 0:
                self.current_index = min(self.current_index, len(self.action_history) - 1)
        
        # Update current index
        self.current_index = len(self.action_history) - 1
    
    def complete_action(self, tree_state_after: Tree, selected_node_name_after: Optional[str], 
                       expansion_state_after: Dict[str, Any]):
        """
        Complete the last recorded action by adding the 'after' state.
        
        Args:
            tree_state_after: Tree state after the action was performed
            selected_node_name_after: Selected node name after the action
            expansion_state_after: Expansion state after the action
        """
        if self.action_history and self.current_index >= 0:
            current_action = self.action_history[self.current_index]
            current_action['tree_state_after'] = tree_state_after
            current_action['selected_node_name_after'] = selected_node_name_after
            current_action['expansion_state_after'] = expansion_state_after
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.current_index < len(self.action_history) - 1
    
    def get_undo_action(self) -> Optional[Dict[str, Any]]:
        """Get the action to undo."""
        if not self.can_undo():
            return None
        
        action = self.action_history[self.current_index]
        self.current_index -= 1
        return action
    
    def get_redo_action(self) -> Optional[Dict[str, Any]]:
        """Get the action to redo."""
        if not self.can_redo():
            return None
        
        self.current_index += 1
        return self.action_history[self.current_index]
    
    def clear_history(self):
        """Clear all action history."""
        self.action_history = []
        self.current_index = -1
    
    def get_current_action_description(self) -> str:
        """Get description of the current action for status display."""
        if not self.can_undo():
            return "No actions to undo"
        
        action = self.action_history[self.current_index]
        action_type = action['action_type']
        
        descriptions = {
            'cut': 'Cut node',
            'copy': 'Copy node', 
            'paste': 'Paste node',
            'delete': 'Delete node',
            'insert': 'Insert new node',
            'rename': 'Rename node',
            'content_edit': 'Edit node content'
        }
        
        return descriptions.get(action_type, f'Unknown action: {action_type}')


class TreeViewerPanel(ttk.Frame):
    """
    Left panel that displays the tree structure in a hierarchical view.
    
    This panel shows the tree nodes in an expandable/collapsible tree view
    and handles node selection events.
    """
    
    def __init__(self, parent, on_node_select=None, clipboard_callbacks=None):
        """
        Initialize the tree viewer panel.
        
        Args:
            parent: The parent widget
            on_node_select: Callback function called when a node is selected
            clipboard_callbacks: Dictionary with 'cut', 'copy', 'paste' callback functions
        """
        super().__init__(parent)
        self.on_node_select = on_node_select
        self.clipboard_callbacks = clipboard_callbacks or {}
        self.tree = None
        self.node_map = {}  # Maps treeview item IDs to TreeNode objects
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Create title label
        title_label = ttk.Label(self, text="Tree Structure", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(5, 10))
        
        # Create buttons frame at the top
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Configure buttons to take roughly 50% width each with margins
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        # Measure typical scrollbar width so we can add extra right margin to buttons
        try:
            temp_sb = ttk.Scrollbar(self)
            # ensure requested size is calculated
            self.update_idletasks()
            scrollbar_width = temp_sb.winfo_reqwidth() or 16
            temp_sb.destroy()
        except Exception:
            scrollbar_width = 16

        # Expand all button
        expand_btn = ttk.Button(buttons_frame, text="Expand All", command=self._expand_all)
        expand_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        # Collapse all button - give a larger right margin to account for the vertical scrollbar
        collapse_btn = ttk.Button(buttons_frame, text="Collapse All", command=self._collapse_all)
        collapse_btn.grid(row=0, column=1, sticky="ew", padx=(2, scrollbar_width))
        
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview with scrollbars
        self.treeview = ttk.Treeview(tree_frame)
        self.treeview.heading('#0', text='Nodes', anchor='w')
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=v_scrollbar.set)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.treeview.xview)
        self.treeview.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and treeview
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.treeview.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.treeview.bind('<<TreeviewSelect>>', self._on_select)
        
        # Bind right-click for context menu
        self.treeview.bind('<Button-3>', self._show_context_menu)
    
    def load_tree(self, tree: Tree, preserve_expansion=False):
        """
        Load a Tree object into the viewer.
        
        Args:
            tree: The Tree object to display
            preserve_expansion: Whether to preserve current expansion state
        """
        self.tree = tree
        if preserve_expansion:
            self._populate_treeview_with_state()
        else:
            self._populate_treeview()
    
    def _populate_treeview(self):
        """Populate the treeview with tree data."""
        # Clear existing items
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        self.node_map.clear()
        
        if self.tree:
            self._add_node_to_treeview('', self.tree.root)
            # Automatically select the root node
            self._select_root_node()
    
    def _select_root_node(self):
        """Select the root node in the treeview."""
        # Get the first (root) item in the treeview
        root_items = self.treeview.get_children()
        if root_items:
            root_item_id = root_items[0]
            # Select and focus on the root node
            self.treeview.selection_set(root_item_id)
            self.treeview.focus(root_item_id)
            self.treeview.see(root_item_id)
            
            # Trigger the selection event to update info panel
            if self.on_node_select and root_item_id in self.node_map:
                self.on_node_select(self.node_map[root_item_id])
    
    def _add_node_to_treeview(self, parent_id: str, node: TreeNode):
        """
        Recursively add a node and its children to the treeview.
        
        Args:
            parent_id: The parent item ID in the treeview
            node: The TreeNode to add
        """
        # Display only the node name (no content preview)
        display_text = node.name
        
        # Insert the node into treeview
        item_id = self.treeview.insert(parent_id, tk.END, text=display_text)
        self.node_map[item_id] = node
        
        # Add children
        for child in node.children:
            self._add_node_to_treeview(item_id, child)
    
    def _on_select(self, event):
        """Handle treeview selection event."""
        selection = self.treeview.selection()
        if selection and self.on_node_select:
            item_id = selection[0]
            node = self.node_map.get(item_id)
            if node:
                self.on_node_select(node)
    
    def _expand_all(self):
        """Expand all nodes in the treeview."""
        def expand_item(item):
            self.treeview.item(item, open=True)
            for child in self.treeview.get_children(item):
                expand_item(child)
        
        for item in self.treeview.get_children():
            expand_item(item)
    
    def _collapse_all(self):
        """Collapse all nodes in the treeview."""
        def collapse_item(item):
            self.treeview.item(item, open=False)
            for child in self.treeview.get_children(item):
                collapse_item(child)
        
        for item in self.treeview.get_children():
            collapse_item(item)
    
    def _capture_expansion_state(self) -> Dict[str, Any]:
        """
        Capture the current expansion state and selection of all nodes by their names.
        
        Returns:
            Dict with expansion state and selected node name
        """
        expansion_state = {}
        selected_node_name = None
        
        # Capture selected node
        selection = self.treeview.selection()
        if selection:
            selected_node = self.node_map.get(selection[0])
            if selected_node:
                selected_node_name = selected_node.name
        
        def capture_item_state(item_id):
            node = self.node_map.get(item_id)
            if node:
                is_open = self.treeview.item(item_id, 'open')
                expansion_state[node.name] = is_open
                
                # Recursively capture children
                for child_id in self.treeview.get_children(item_id):
                    capture_item_state(child_id)
        
        # Capture state for all top-level items
        for item_id in self.treeview.get_children():
            capture_item_state(item_id)
            
        return {
            'expansion': expansion_state,
            'selection': selected_node_name
        }
    
    def _restore_expansion_state(self, state_info: Dict[str, Any]):
        """
        Restore expansion state and selection of nodes based on their names.
        
        Args:
            state_info: Dict with expansion state and selected node name
        """
        expansion_state = state_info.get('expansion', {})
        selected_node_name = state_info.get('selection')
        
        def restore_item_state(item_id):
            node = self.node_map.get(item_id)
            if node:
                # Restore expansion state
                if node.name in expansion_state:
                    should_expand = expansion_state[node.name]
                    self.treeview.item(item_id, open=should_expand)
                
                # Restore selection if this is the selected node
                if selected_node_name and node.name == selected_node_name:
                    self.treeview.selection_set(item_id)
                    self.treeview.focus(item_id)
                    self.treeview.see(item_id)
                
            # Recursively restore children
            for child_id in self.treeview.get_children(item_id):
                restore_item_state(child_id)
        
        # Restore state for all top-level items
        for item_id in self.treeview.get_children():
            restore_item_state(item_id)
    
    def _populate_treeview_with_state(self):
        """Populate treeview while preserving expansion and selection state."""
        # Capture current state before clearing
        state_info = self._capture_expansion_state()
        
        # Clear and repopulate
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        self.node_map.clear()
        
        if self.tree:
            self._add_node_to_treeview('', self.tree.root)
            # Restore expansion and selection state after population
            self._restore_expansion_state(state_info)
    
    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select the item under the cursor
        item = self.treeview.identify_row(event.y)
        if item:
            self.treeview.selection_set(item)
            
            # Get selected node to determine menu options
            node = self.node_map.get(item)
            
            # Create context menu
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(label="Cut", accelerator="Ctrl+X", command=self._context_cut)
            context_menu.add_command(label="Copy", accelerator="Ctrl+C", command=self._context_copy)
            context_menu.add_separator()
            context_menu.add_command(label="Paste", accelerator="Ctrl+V", command=self._context_paste)
            context_menu.add_command(label="Insert New Node", accelerator="Ctrl+I", command=self._context_insert)
            
            # Add delete option (except for root node)
            if node and node.parent:  # Don't allow deleting root node
                context_menu.add_separator()
                context_menu.add_command(label="Delete", accelerator="Del", command=self._context_delete)
            
            # Add expand/collapse if node has children
            if node and node.children:
                context_menu.add_separator()
                context_menu.add_command(label="Expand All Below", 
                                       command=lambda: self._expand_subtree(item))
                context_menu.add_command(label="Collapse All Below", 
                                       command=lambda: self._collapse_subtree(item))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def _context_cut(self):
        """Handle cut from context menu."""
        if 'cut' in self.clipboard_callbacks:
            self.clipboard_callbacks['cut']()
    
    def _context_copy(self):
        """Handle copy from context menu."""
        if 'copy' in self.clipboard_callbacks:
            self.clipboard_callbacks['copy']()
    
    def _context_paste(self):
        """Handle paste from context menu."""
        if 'paste' in self.clipboard_callbacks:
            self.clipboard_callbacks['paste']()
    
    def _context_delete(self):
        """Handle delete from context menu."""
        if 'delete' in self.clipboard_callbacks:
            self.clipboard_callbacks['delete']()
    
    def _context_insert(self):
        """Handle insert new node from context menu."""
        if 'insert' in self.clipboard_callbacks:
            self.clipboard_callbacks['insert']()
    
    def _expand_subtree(self, item):
        """Expand a subtree starting from the given item."""
        def expand_item(current_item):
            self.treeview.item(current_item, open=True)
            for child in self.treeview.get_children(current_item):
                expand_item(child)
        
        expand_item(item)
    
    def _collapse_subtree(self, item):
        """Collapse a subtree starting from the given item."""
        def collapse_item(current_item):
            for child in self.treeview.get_children(current_item):
                collapse_item(child)
            self.treeview.item(current_item, open=False)
        
        collapse_item(item)


class InfoViewerPanel(ttk.Frame):
    """
    Right panel that displays detailed information about the selected tree node.
    
    This panel shows comprehensive details about the selected node including
    its properties, content, and statistics.
    """
    
    def __init__(self, parent):
        """
        Initialize the info viewer panel.
        
        Args:
            parent: The parent widget
        """
        super().__init__(parent)
        self.current_node = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Create title label
        title_label = ttk.Label(self, text="Node Information", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(5, 10))
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_overview_tab()
        self._create_content_tab()
        self._create_children_tab()
        
        # Setup tab switching with Ctrl+Tab
        self._setup_tab_bindings()
    
    def _setup_tab_bindings(self):
        """Setup keyboard bindings for tab navigation with Ctrl+Tab."""
        def _switch_tab_forward(event=None):
            # Get current tab index
            current_tab = self.notebook.index(self.notebook.select())
            # Get total number of tabs
            total_tabs = self.notebook.index("end")
            # Calculate next tab (cycle to beginning if at end)
            next_tab = (current_tab + 1) % total_tabs
            # Switch to next tab
            self.notebook.select(next_tab)
            return "break"  # Prevent default behavior
        
        def _switch_tab_backward(event=None):
            # Get current tab index
            current_tab = self.notebook.index(self.notebook.select())
            # Get total number of tabs
            total_tabs = self.notebook.index("end")
            # Calculate previous tab (cycle to end if at beginning)
            prev_tab = (current_tab - 1) % total_tabs
            # Switch to previous tab
            self.notebook.select(prev_tab)
            return "break"  # Prevent default behavior
        
        # Bind Ctrl+Tab for forward navigation and Ctrl+Shift+Tab for backward
        try:
            self.bind_all('<Control-Tab>', _switch_tab_forward)
            self.bind_all('<Control-Shift-Tab>', _switch_tab_backward)
        except Exception:
            # If binding isn't available for some reason, ignore silently
            pass
    
    def _create_overview_tab(self):
        """Create the overview tab."""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Create treeview for tabular display
        self.overview_table = ttk.Treeview(overview_frame, columns=('Value',), show='tree headings')
        self.overview_table.heading('#0', text='Property', anchor='w')
        self.overview_table.heading('Value', text='Value', anchor='w')
        self.overview_table.column('#0', width=200, minwidth=150)
        self.overview_table.column('Value', width=300, minwidth=200)
        
        # Bind double-click for editing node name
        self.overview_table.bind('<Double-1>', self._on_overview_double_click)
        
        # Add scrollbar for overview table
        overview_scrollbar = ttk.Scrollbar(overview_frame, orient=tk.VERTICAL, command=self.overview_table.yview)
        self.overview_table.configure(yscrollcommand=overview_scrollbar.set)
        
        # Pack overview components
        overview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.overview_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_content_tab(self):
        """Create the content tab."""
        content_frame = ttk.Frame(self.notebook)
        self.notebook.add(content_frame, text="Content")
        
        # Create toolbar for edit controls
        self.content_toolbar = ttk.Frame(content_frame)
        self.content_toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Edit mode toggle
        self.edit_mode_var = tk.BooleanVar()
        self.edit_toggle_btn = ttk.Checkbutton(
            self.content_toolbar, 
            text="Edit Mode", 
            variable=self.edit_mode_var,
            command=self._toggle_edit_mode
        )
        self.edit_toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add/Remove buttons (initially hidden)
        self.add_btn = ttk.Button(self.content_toolbar, text="Add", command=self._add_item)
        self.remove_btn = ttk.Button(self.content_toolbar, text="Remove", command=self._remove_item)
        self.clear_btn = ttk.Button(self.content_toolbar, text="Clear", command=self._clear_content)
        self.create_new_btn = ttk.Button(self.content_toolbar, text="Create New", command=self._create_new_content)
        self.save_btn = ttk.Button(self.content_toolbar, text="Save Changes", command=self._save_changes)
        self.cancel_btn = ttk.Button(self.content_toolbar, text="Cancel", command=self._cancel_changes)
        
        # Create a frame that will contain either table or text
        self.content_container = ttk.Frame(content_frame)
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize with text widget (will be recreated as needed)
        self._create_content_text_widget()
        
        # Keep track of current display mode and edit state
        self.content_display_mode = "text"
        self.is_editing = False
        self.original_content = None  # Store original content for cancel functionality

        # Note: Ctrl+E binding is now handled globally by the main UI

    def _toggle_edit_mode(self):
        """Toggle edit mode on/off."""
        self.is_editing = self.edit_mode_var.get()
        # Switch to Content tab when entering edit mode
        self.notebook.select(1)  # Index 1 is the Content tab (Overview=0, Content=1, Children=2)
            
        if self.is_editing:
            # Record action for undo/redo before making changes
            if hasattr(self, 'record_action'):
                action_data = {'node_name': self.current_node.name, 'old_content': copy.deepcopy(self.original_content)}
                self.record_action('content_edit', action_data)
            
            # Store original content for cancel functionality
            self.original_content = self._deep_copy_content(self.current_node.content)            

            # Show edit buttons
            self.add_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.remove_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.clear_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.create_new_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
            self.cancel_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Enable text editing if in text mode
            if self.content_display_mode == "text" and hasattr(self, 'content_text'):
                self.content_text.config(state=tk.NORMAL)
        else:
            # Hide edit buttons
            self.add_btn.pack_forget()
            self.remove_btn.pack_forget()
            self.clear_btn.pack_forget()
            self.create_new_btn.pack_forget()
            self.save_btn.pack_forget()
            self.cancel_btn.pack_forget()
            
            # Disable text editing if in text mode
            if self.content_display_mode == "text" and hasattr(self, 'content_text'):
                self.content_text.config(state=tk.DISABLED)
            
            # Update overview to reflect any unsaved changes when exiting edit mode
            self._update_overview()

            messagebox.showinfo("Success", "Content updated successfully!")
            # Complete the action recording (if callback is available)
            if hasattr(self, 'complete_action'):
                self.complete_action()
    
    def _deep_copy_content(self, content):
        """Create a deep copy of content for backup."""
        if isinstance(content, dict):
            return {k: self._deep_copy_content(v) for k, v in content.items()}
        elif isinstance(content, list):
            return [self._deep_copy_content(item) for item in content]
        elif isinstance(content, tuple):
            return tuple(self._deep_copy_content(item) for item in content)
        else:
            return content
    
    def _save_changes(self):
        """Save changes to the node content."""
        if not self.current_node or not self.is_editing:
            return
        
        try:
            if self.content_display_mode == "text":
                # Parse text content
                text_content = self.content_text.get(1.0, tk.END).strip()
                if text_content == "No content":
                    new_content = None
                else:
                    try:
                        # Try to parse as JSON
                        new_content = json.loads(text_content)
                    except json.JSONDecodeError:
                        # If not valid JSON, store as string
                        new_content = text_content
            else:
                # For table mode, content is already updated in place
                new_content = self.current_node.content
            
            # Update the node content
            self.current_node.set_content(new_content)
            
            # Update original content to reflect saved state
            self.original_content = self._deep_copy_content(new_content)
            
            # Turn off edit mode
            self.edit_mode_var.set(False)
            self._toggle_edit_mode()
            
            # Refresh all displays to reflect changes
            self._update_content()
            self._update_overview()  # Update overview tab to reflect content changes
            self._update_children()  # Update children tab in case structure changed
            
            # Notify that content has changed
            if hasattr(self, 'content_changed_callback') and self.content_changed_callback:
                self.content_changed_callback()
            
            # Complete the action recording (if callback is available)
            if hasattr(self, 'complete_action'):
                self.complete_action()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes:\n{str(e)}")
            # Don't turn off edit mode if save failed
    
    def _cancel_changes(self):
        """Cancel changes and restore original content."""
        if not self.current_node or not self.is_editing:
            return
        
        self._revert_to_original()
        
        # Turn off edit mode
        self.edit_mode_var.set(False)
        self._toggle_edit_mode()
        
        # Refresh all displays to reflect reverted state
        self._update_content()
        self._update_overview()  # Update overview tab to reflect reverted content
        self._update_children()  # Update children tab in case structure changed
    
    def _revert_to_original(self):
        """Revert current node content to original state."""
        if self.current_node and self.original_content is not None:
            self.current_node.set_content(self._deep_copy_content(self.original_content))
    
    def _has_unsaved_changes(self):
        """Check if there are unsaved changes in the current node.

        New behavior: if edit mode is active for a node, consider that there
        are unsaved changes (regardless of content comparison).
        """
        # If currently editing, treat as having unsaved changes
        if self.is_editing:
            return True

        # Not editing -> no unsaved changes
        return False
    
    def _content_equals(self, content1, content2):
        """Deep comparison of two content objects."""
        if type(content1) != type(content2):
            return False
        
        if isinstance(content1, dict):
            if set(content1.keys()) != set(content2.keys()):
                return False
            return all(self._content_equals(content1[k], content2[k]) for k in content1.keys())
        elif isinstance(content1, (list, tuple)):
            if len(content1) != len(content2):
                return False
            return all(self._content_equals(a, b) for a, b in zip(content1, content2))
        else:
            return content1 == content2
    
    def _on_overview_double_click(self, event):
        """Handle double-click on overview table for editing."""
        item = self.overview_table.identify('item', event.x, event.y)
        column = self.overview_table.identify('column', event.x, event.y)
        
        if not item:
            return
        
        property_name = self.overview_table.item(item, 'text')
        
        # Only allow editing the Node Name and only in the Value column
        if property_name == "Node Name" and column == '#1':
            self._edit_node_name(item)
    
    def _edit_node_name(self, item_id):
        """Edit the node name with validation."""
        if not self.current_node:
            return
        
        current_name = self.current_node.name
        dialog = EditNodeNameDialog(self.overview_table, current_name)
        
        if dialog.result and dialog.result != current_name:
            new_name = dialog.result.strip()
            
            # Validate the new name
            if not new_name:
                messagebox.showerror("Error", "Node name cannot be empty.")
                return
            
            # Check if name is unique in the tree
            if self._is_name_unique_in_tree(new_name):
                try:
                    # Record action for undo/redo
                    if hasattr(self, 'record_action'):
                        action_data = {'old_name': self.current_node.name, 'new_name': new_name}
                        self.record_action('rename', action_data)
                    
                    # Update the node name
                    old_name = self.current_node.name
                    self.current_node.name = new_name
                    
                    # Update the overview display
                    self.overview_table.set(item_id, 'Value', new_name)
                    
                    # Notify parent UI to refresh tree view
                    self._notify_node_renamed(old_name, new_name)
                    
                    # Complete the action recording (if callback is available)
                    if hasattr(self, 'complete_action'):
                        self.complete_action()
                    
                    messagebox.showinfo("Success", f"Node renamed from '{old_name}' to '{new_name}'")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to rename node:\n{str(e)}")
            else:
                messagebox.showerror("Error", f"Name '{new_name}' already exists in the tree. Please choose a unique name.")
    
    def _is_name_unique_in_tree(self, name):
        """Check if the given name is unique in the entire tree."""
        if not self.current_node:
            return True
        
        # Find the root of the tree
        root = self.current_node
        while root.parent:
            root = root.parent
        
        # Check if name exists anywhere in the tree (except current node)
        return not self._name_exists_in_subtree(root, name, self.current_node)
    
    def _name_exists_in_subtree(self, node, name, exclude_node):
        """Recursively check if name exists in subtree, excluding a specific node."""
        if node != exclude_node and node.name == name:
            return True
        
        for child in node.children:
            if self._name_exists_in_subtree(child, name, exclude_node):
                return True
        
        return False
    
    def _notify_node_renamed(self, old_name, new_name):
        """Notify parent components that a node was renamed."""
        # This will be called by the parent UI to refresh the tree view
        # We'll store the callback function when the panel is created
        if hasattr(self, 'on_node_renamed') and self.on_node_renamed:
            self.on_node_renamed(self.current_node, old_name, new_name)
    
    def set_node_renamed_callback(self, callback):
        """Set callback function to notify when node is renamed."""
        self.on_node_renamed = callback
    
    def set_action_recorder_callback(self, callback):
        """Set callback function to record actions for undo/redo."""
        self.record_action = callback
    
    def set_action_complete_callback(self, callback):
        """Set callback function to complete action recording for undo/redo."""
        self.complete_action = callback
    
    def set_content_changed_callback(self, callback):
        """Set callback function to notify when content changes."""
        self.content_changed_callback = callback
    
    def _clear_content(self):
        """Clear the current node content and set it to None."""
        if not self.current_node or not self.is_editing:
            return
        
        result = messagebox.askyesno(
            "Clear Content", 
            "Are you sure you want to clear all content? This will set the content to None.\n\n"
            "This action can be undone by clicking Cancel without saving."
        )
        
        if result:
            # Set content to None
            self.current_node.set_content(None)
            
            # Refresh the display
            self._update_content()
    
    def _create_new_content(self):
        """Create new content of a specific type."""
        if not self.current_node or not self.is_editing:
            return
        
        # First clear existing content
        self.current_node.set_content(None)
        
        # Show dialog to choose content type
        dialog = CreateContentTypeDialog(self.content_container)
        
        if dialog.result:
            content_type = dialog.result
            
            if content_type == "text":
                # Create empty text content
                self.current_node.set_content("")
            elif content_type == "dict":
                # Create dictionary with sample data to enable table display
                self.current_node.set_content({"key": "value"})
            elif content_type == "list_of_dict":
                # Create list with sample dictionary to enable table display
                self.current_node.set_content([{"key": "value"}])
            elif content_type == "null":
                # Keep content as None (already set above)
                pass
            
            # Refresh the display
            self._update_content()
    
    def _add_item(self):
        """Add new item based on content type."""
        if not self.current_node or not self.is_editing:
            return
        
        if isinstance(self.current_node.content, dict):
            self._add_dict_item()
        elif isinstance(self.current_node.content, list):
            self._add_list_item()
        else:
            messagebox.showwarning("Warning", "Can only add items to dictionaries and lists.")
    
    def _remove_item(self):
        """Remove selected item."""
        if not self.current_node or not self.is_editing:
            return
        
        if self.content_display_mode == "table" and hasattr(self, 'content_table'):
            selection = self.content_table.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an item to remove.")
                return
            
            if isinstance(self.current_node.content, dict):
                self._remove_dict_item(selection[0])
            elif isinstance(self.current_node.content, list):
                self._remove_list_item(selection[0])
        else:
            messagebox.showwarning("Warning", "Item removal is only available in table mode.")
    
    def _add_dict_item(self):
        """Add new key-value pair to dictionary."""
        dialog = AddDictItemDialog(self.content_container)
        if dialog.result:
            key, value = dialog.result
            try:
                # Try to parse value as JSON first
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    # If not valid JSON, store as string
                    parsed_value = value
                
                self.current_node.content[key] = parsed_value
                self._update_content()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add item:\n{str(e)}")
    
    def _add_list_item(self):
        """Add new item to list."""
        if isinstance(self.current_node.content, list) and \
           len(self.current_node.content) > 0 and \
           isinstance(self.current_node.content[0], dict):
            # Adding to list of dictionaries
            dialog = AddListItemDialog(self.content_container, self.current_node.content)
            if dialog.result:
                self.current_node.content.append(dialog.result)
                self._update_content()
        else:
            # Simple list item
            dialog = AddSimpleItemDialog(self.content_container)
            if dialog.result is not None:
                self.current_node.content.append(dialog.result)
                self._update_content()
    
    def _remove_dict_item(self, item_id):
        """Remove dictionary item."""
        key = self.content_table.item(item_id, 'text')
        if key in self.current_node.content:
            del self.current_node.content[key]
            self._update_content()
    
    def _remove_list_item(self, item_id):
        """Remove list item."""
        try:
            index = int(self.content_table.item(item_id, 'text'))
            if 0 <= index < len(self.current_node.content):
                del self.current_node.content[index]
                self._update_content()
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", f"Failed to remove item:\n{str(e)}")
    
    def _on_table_double_click(self, event):
        """Handle double-click on table for editing."""
        if not self.is_editing:
            return
        
        # Get the item under the mouse cursor for editing
        row = self.content_table.identify_row(event.y)
        column = self.content_table.identify_column(event.x)
        
        if not row:
            return
        
        if isinstance(self.current_node.content, dict):
            self._edit_dict_item(row, column)
        elif isinstance(self.current_node.content, list):
            self._edit_list_item(row, column)

    def _edit_dict_item(self, row, column):
        """Edit dictionary item."""
        key = self.content_table.item(row, 'text')
        if column == '#1':  # Value column
            current_value = self.current_node.content.get(key, "")
            dialog = EditValueDialog(self.content_container, str(current_value))
            if dialog.result is not None:
                try:
                    # Try to parse as JSON
                    try:
                        parsed_value = json.loads(dialog.result)
                    except json.JSONDecodeError:
                        parsed_value = dialog.result
                    
                    self.current_node.content[key] = parsed_value
                    self._update_content()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update value:\n{str(e)}")
        elif column == '#0':  # Key column
            dialog = EditValueDialog(self.content_container, key, "Edit Key")
            if dialog.result is not None and dialog.result != key:
                # Rename key
                value = self.current_node.content.pop(key)
                self.current_node.content[dialog.result] = value
                self._update_content()

    def _edit_list_item(self, row, column):
        """Edit list item."""
        try:
            index = int(self.content_table.item(row, 'text'))
            if isinstance(self.current_node.content[index], dict):
                # Get column name
                columns = ['#0'] + list(self.content_table['columns'])
                if column == '#0':
                    return  # Can't edit index
                
                col_index = int(column.replace('#', '')) - 1
                if col_index < len(self.content_table['columns']):
                    col_name = self.content_table['columns'][col_index]
                    current_value = self.current_node.content[index].get(col_name, "")
                    
                    dialog = EditValueDialog(self.content_container, str(current_value))
                    if dialog.result is not None:
                        try:
                            # Try to parse as JSON
                            try:
                                parsed_value = json.loads(dialog.result)
                            except json.JSONDecodeError:
                                parsed_value = dialog.result
                            
                            self.current_node.content[index][col_name] = parsed_value
                            self._update_content()
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to update value:\n{str(e)}")
        except (ValueError, IndexError, KeyError) as e:
            messagebox.showerror("Error", f"Failed to edit item:\n{str(e)}")
    
    def _edit_list_column_key(self, column):
        """Edit column key name for list of dictionaries."""
        if not isinstance(self.current_node.content, list) or not self.current_node.content:
            return
        
        col_index = int(column.replace('#', '')) - 1
        if col_index < len(self.content_table['columns']):
            old_key = self.content_table['columns'][col_index]
            
            dialog = EditValueDialog(self.content_container, old_key, "Edit Column Name")
            if dialog.result is not None and dialog.result != old_key:
                new_key = dialog.result
                
                # Rename the key in all dictionaries in the list
                for item in self.current_node.content:
                    if isinstance(item, dict) and old_key in item:
                        item[new_key] = item.pop(old_key)
                
                self._update_content()
    
    def _on_table_header_double_click(self, event):
        """Handle double-click on table header for column renaming."""
        if not self.is_editing or not isinstance(self.current_node.content, list):
            return
        
        # Check if click is on header
        region = self.content_table.identify_region(event.x, event.y)
        if region == "heading":
            column = self.content_table.identify_column(event.x)
            if column != '#0':  # Don't allow renaming the index column
                self._edit_list_column_key(column)
    
    def _on_table_right_click(self, event):
        """Handle right-click on table for both column operations and general edit operations."""
        # Check if click is on header for column-specific operations
        region = self.content_table.identify_region(event.x, event.y)
        if region == "heading" and self.is_editing and isinstance(self.current_node.content, list):
            column = self.content_table.identify_column(event.x)
            if column != '#0':  # Don't show menu for index column
                self._show_column_context_menu(event, column)
        else:
            # Show general content context menu
            self._show_content_context_menu(event)
    
    def _show_column_context_menu(self, event, column):
        """Show context menu for column operations."""
        context_menu = tk.Menu(self.content_container, tearoff=0)
        
        col_index = int(column.replace('#', '')) - 1
        col_name = self.content_table['columns'][col_index] if col_index < len(self.content_table['columns']) else ""
        
        context_menu.add_command(label=f"Rename Column '{col_name}'", 
                               command=lambda: self._edit_list_column_key(column))
        context_menu.add_separator()
        context_menu.add_command(label="Add New Column", 
                               command=self._add_new_column)
        context_menu.add_command(label=f"Delete Column '{col_name}'", 
                                 accelerator="Del",
                               command=lambda: self._delete_column(column))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _on_text_right_click(self, event):
        """Handle right-click on text widget for content operations."""
        self._show_content_context_menu(event)
    
    def _show_content_context_menu(self, event):
        """Show general content context menu with all edit operations."""
        if not self.current_node:
            return
        
        context_menu = tk.Menu(self.content_container, tearoff=0)
        
        # Edit Mode Toggle
        if self.is_editing:
            context_menu.add_command(label="Exit Edit Mode",
                                    accelerator="Ctrl+E",
                                    command=lambda: self._toggle_edit_mode_off())
            context_menu.add_separator()
            
            # Content-specific operations
            if isinstance(self.current_node.content, dict):
                context_menu.add_command(label="Add Dictionary Item", 
                                       command=self._add_dict_item)
                if self.content_display_mode == "table":
                    context_menu.add_command(label="Remove Selected Item", 
                                           command=self._remove_item)
            elif isinstance(self.current_node.content, list):
                context_menu.add_command(label="Add List Item", 
                                       command=self._add_list_item)
                if self.content_display_mode == "table":
                    context_menu.add_command(label="Remove Selected Item", 
                                           command=self._remove_item)
                    if isinstance(self.current_node.content, list) and \
                       len(self.current_node.content) > 0 and \
                       isinstance(self.current_node.content[0], dict):
                        context_menu.add_command(label="Add New Column", 
                                               command=self._add_new_column)
            
            context_menu.add_separator()
            
            # General edit operations
            context_menu.add_command(label="Clear Content", 
                                   command=self._clear_content)
            context_menu.add_command(label="Create New Content", 
                                   command=self._create_new_content)
            
            context_menu.add_separator()
            
            # Save/Cancel operations
            context_menu.add_command(label="Save Changes", 
                                   command=self._save_changes)
            context_menu.add_command(label="Cancel Changes", 
                                   command=self._cancel_changes)
        else:
            context_menu.add_command(label="Enter Edit Mode",
                                   accelerator="Ctrl+E", 
                                   command=lambda: self._toggle_edit_mode_on())
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _toggle_edit_mode_on(self):
        """Turn on edit mode."""
        self.edit_mode_var.set(True)
        self._toggle_edit_mode()
    
    def _toggle_edit_mode_off(self):
        """Turn off edit mode."""
        self.edit_mode_var.set(False)
        self._toggle_edit_mode()
    
    def _add_new_column(self):
        """Add a new column to the list of dictionaries."""
        if not isinstance(self.current_node.content, list):
            return
        
        dialog = EditValueDialog(self.content_container, "", "New Column Name")
        if dialog.result is not None and dialog.result.strip():
            new_column_name = dialog.result.strip()
            
            # Check if column already exists
            existing_keys = set()
            for item in self.current_node.content:
                if isinstance(item, dict):
                    existing_keys.update(item.keys())
            
            if new_column_name in existing_keys:
                messagebox.showerror("Error", f"Column '{new_column_name}' already exists!")
                return
            
            # Add the new column to all dictionaries with empty value
            for item in self.current_node.content:
                if isinstance(item, dict):
                    item[new_column_name] = ""
            
            self._update_content()
    
    def _delete_column(self, column):
        """Delete a column from the list of dictionaries."""
        if not isinstance(self.current_node.content, list):
            return
        
        # Check if there's only one column left
        if len(self.content_table['columns']) <= 1:
            messagebox.showwarning("Cannot Delete Column", 
                                 "Cannot delete the last remaining column. "
                                 "At least one column must remain in the table.")
            return
        
        col_index = int(column.replace('#', '')) - 1
        if col_index < len(self.content_table['columns']):
            col_name = self.content_table['columns'][col_index]
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", f"Delete column '{col_name}' and all its data?"):
                # Remove the key from all dictionaries
                for item in self.current_node.content:
                    if isinstance(item, dict) and col_name in item:
                        del item[col_name]
                
                self._update_content()
    
    def _create_content_text_widget(self):
        """Create text widget for content display."""
        self.content_text = scrolledtext.ScrolledText(
            self.content_container,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED
        )
        # Bind right-click for context menu
        self.content_text.bind('<Button-3>', self._on_text_right_click)
        self.content_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_content_table_widget(self):
        """Create table widget for content display."""
        # Create frame for table and scrollbar
        table_frame = ttk.Frame(self.content_container)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for table display
        self.content_table = ttk.Treeview(table_frame, show='tree headings')
        
        # Bind double-click for editing
        self.content_table.bind('<Double-1>', self._on_table_double_click)
        # Bind right-click for column operations
        self.content_table.bind('<Button-3>', self._on_table_right_click)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.content_table.yview)
        self.content_table.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.content_table.xview)
        self.content_table.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack components
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.content_table.pack(fill=tk.BOTH, expand=True)
    
    def _clear_content_container(self):
        """Clear all widgets from content container."""
        for widget in self.content_container.winfo_children():
            widget.destroy()
    
    def _create_children_tab(self):
        """Create the children tab."""
        children_frame = ttk.Frame(self.notebook)
        self.notebook.add(children_frame, text="Children")
        
        # Create treeview for children with detailed columns
        self.children_tree = ttk.Treeview(children_frame, 
                                        columns=('Content Type', 'Children Count', 'Node Width', 'Total Nodes'), 
                                        show='tree headings')
        self.children_tree.heading('#0', text='Child Name', anchor='w')
        self.children_tree.heading('Content Type', text='Content Type', anchor='w')
        self.children_tree.heading('Children Count', text='Children', anchor='center')
        self.children_tree.heading('Node Width', text='Width', anchor='center')
        self.children_tree.heading('Total Nodes', text='Total Nodes', anchor='center')
        
        # Configure column widths
        self.children_tree.column('#0', width=150, minwidth=100)
        self.children_tree.column('Content Type', width=100, minwidth=80)
        self.children_tree.column('Children Count', width=80, minwidth=60)
        self.children_tree.column('Node Width', width=80, minwidth=60)
        self.children_tree.column('Total Nodes', width=100, minwidth=80)
        
        # Add scrollbar for children treeview
        children_scrollbar = ttk.Scrollbar(children_frame, orient=tk.VERTICAL, command=self.children_tree.yview)
        self.children_tree.configure(yscrollcommand=children_scrollbar.set)
        
        # Pack children components
        children_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.children_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def display_node_info(self, node: TreeNode):
        """
        Display information about the selected node.
        
        Args:
            node: The TreeNode to display information about
        """
        # Check if we have unsaved changes when switching nodes
        if self.is_editing and self.current_node and self.current_node != node:
            if self._has_unsaved_changes():
                result = messagebox.askyesnocancel(
                    "Unsaved Changes", 
                    "You have unsaved changes. Do you want to save them before switching to another node?\n\n"
                    "Yes: Save changes and switch\n"
                    "No: Discard changes and switch\n"
                    "Cancel: Stay on current node"
                )
                
                if result is True:  # Yes - Save changes
                    self._save_changes()
                    if self.is_editing:  # If save failed, don't switch
                        return
                elif result is False:  # No - Discard changes
                    self._toggle_edit_mode_off()
                    self._revert_to_original()
                else:  # Cancel - Stay on current node
                    self._toggle_edit_mode_off()
                    return
        
        self.current_node = node
        self._update_overview()
        self._update_content()
        self._update_children()
    
    def _update_overview(self):
        """Update the overview tab with node information."""
        # Clear existing items
        for item in self.overview_table.get_children():
            self.overview_table.delete(item)
        
        if not self.current_node:
            return
        
        node = self.current_node
        
        # Build overview data as key-value pairs
        overview_data = [
            ("Node Name", node.name),
            ("Content Type", type(node.content).__name__),
            ("Number of Children", str(len(node.children))),
            ("Has Parent", "Yes" if node.parent else "No"),
        ]
        
        if node.parent:
            overview_data.append(("Parent Name", node.parent.name))
        
        overview_data.extend([
            ("Node Depth", str(node.max_depth())),
            ("Node Width", str(node.max_width())),
            ("Total Nodes in Subtree", str(node.count())),
        ])
        
        # Display path from root
        path = []
        current = node
        while current:
            path.insert(0, current.name)
            current = current.parent
        overview_data.append(("Path from Root", " → ".join(path)))
        
        # Populate the table and store the node name item ID
        self.node_name_item_id = None
        for property_name, value in overview_data:
            item_id = self.overview_table.insert('', tk.END, text=property_name, values=(value,))
            if property_name == "Node Name":
                self.node_name_item_id = item_id
    
    def _update_content(self):
        """Update the content tab with node content."""
        if not self.current_node:
            return
        
        node = self.current_node
        
        # Determine the best display method based on content type
        if node.content is None:
            self._display_content_as_text("No content")
        elif isinstance(node.content, dict):
            if self._is_dict_suitable_for_table(node.content):
                self._display_content_as_table(node.content)
            else:
                self._display_content_as_text(json.dumps(node.content, indent=2, ensure_ascii=False))
        elif isinstance(node.content, (list, tuple)) and len(node.content) > 0:
            if self._is_list_of_dicts_suitable_for_table(node.content):
                self._display_list_as_table(node.content)
            else:
                self._display_content_as_text(json.dumps(list(node.content), indent=2, ensure_ascii=False))
        else:
            self._display_content_as_text(str(node.content))
    
    def _is_dict_suitable_for_table(self, data):
        """Check if a dictionary is suitable for table display."""
        if not isinstance(data, dict) or len(data) == 0:
            return False
        return True
    
    def _is_list_of_dicts_suitable_for_table(self, data):
        """Check if a list of dictionaries is suitable for table display."""
        if not isinstance(data, (list, tuple)) or len(data) == 0:
            return False
        
        # Check if all items are dictionaries with similar structure
        if not all(isinstance(item, dict) for item in data):
            return False
        
        # Get all unique keys from all dictionaries
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        # Check if the structure is reasonable for table display
        return True
    
    def _display_content_as_text(self, content_str):
        """Display content as formatted text."""
        # Clear container and create text widget if needed
        if self.content_display_mode != "text":
            self._clear_content_container()
            self._create_content_text_widget()
            self.content_display_mode = "text"
        
        # Update text widget
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, content_str)
        
        # Only disable if not in edit mode
        if not self.is_editing:
            self.content_text.config(state=tk.DISABLED)
    
    def _display_content_as_table(self, data):
        """Display dictionary content as a table."""
        # Clear container and create table widget if needed
        if self.content_display_mode != "table":
            self._clear_content_container()
            self._create_content_table_widget()
            self.content_display_mode = "table"
        
        # Clear existing items
        for item in self.content_table.get_children():
            self.content_table.delete(item)
        
        # Configure columns for key-value display
        self.content_table.configure(columns=('Value',))
        self.content_table.heading('#0', text='Key', anchor='w')
        self.content_table.heading('Value', text='Value', anchor='w')
        self.content_table.column('#0', width=200, minwidth=150)
        self.content_table.column('Value', width=300, minwidth=200)
        
        # Populate table with dictionary data
        for key, value in data.items():
            # Format complex values
            if isinstance(value, (dict, list, tuple)):
                display_value = json.dumps(value, ensure_ascii=False)
                if len(display_value) > 100:
                    display_value = display_value[:100] + "..."
            else:
                display_value = str(value)
            
            self.content_table.insert('', tk.END, text=str(key), values=(display_value,))
    
    def _display_list_as_table(self, data):
        """Display list of dictionaries as a table."""
        # Clear container and create table widget if needed
        if self.content_display_mode != "table":
            self._clear_content_container()
            self._create_content_table_widget()
            self.content_display_mode = "table"
        
        # Clear existing items
        for item in self.content_table.get_children():
            self.content_table.delete(item)
        
        # Get all unique keys from all dictionaries
        all_keys = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        all_keys = sorted(list(all_keys))
        
        # Configure columns
        self.content_table.configure(columns=all_keys)
        self.content_table.heading('#0', text='Index', anchor='w')
        self.content_table.column('#0', width=60, minwidth=50)
        
        # Set up column headers and widths
        for key in all_keys:
            self.content_table.heading(key, text=str(key), anchor='w')
            self.content_table.column(key, width=120, minwidth=80)
        
        # Populate table with list data
        for index, item in enumerate(data):
            if isinstance(item, dict):
                values = []
                for key in all_keys:
                    value = item.get(key, "")
                    if isinstance(value, (dict, list, tuple)):
                        display_value = json.dumps(value, ensure_ascii=False)
                        if len(display_value) > 50:
                            display_value = display_value[:50] + "..."
                    else:
                        display_value = str(value)
                    values.append(display_value)
                
                self.content_table.insert('', tk.END, text=str(index), values=values)
    
    def _update_children(self):
        """Update the children tab with node's children information."""
        # Clear existing items
        for item in self.children_tree.get_children():
            self.children_tree.delete(item)
        
        if not self.current_node:
            return
        
        node = self.current_node
        
        # Add children to treeview with detailed information
        for child in node.children:
            # Get content type
            content_type = type(child.content).__name__
            
            # Get number of children
            children_count = len(child.children)
            
            # Get node width
            node_width = child.max_width()
            
            # Get total nodes in subtree
            total_nodes = child.count()
            
            # Insert row with all the information
            self.children_tree.insert('', tk.END, 
                                    text=child.name, 
                                    values=(content_type, str(children_count), str(node_width), str(total_nodes)))
    
    def clear_info(self):
        """Clear all information from the panel."""
        # Check for unsaved changes before clearing
        if self.is_editing and self.current_node and self._has_unsaved_changes():
            result = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them before clearing?\n\n"
                "Yes: Save changes\n"
                "No: Discard changes\n"
                "Cancel: Keep current content"
            )
            
            if result is True:  # Yes - Save changes
                self._save_changes()
            elif result is False:  # No - Discard changes
                self._revert_to_original()
            else:  # Cancel - Don't clear
                return
        
        # Reset edit mode
        if self.is_editing:
            self.edit_mode_var.set(False)
            self._toggle_edit_mode()
        
        self.current_node = None
        self.original_content = None
        
        # Clear overview table
        for item in self.overview_table.get_children():
            self.overview_table.delete(item)
        
        # Clear content display
        if self.content_display_mode == "text" and hasattr(self, 'content_text'):
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.config(state=tk.DISABLED)
        elif self.content_display_mode == "table" and hasattr(self, 'content_table'):
            for item in self.content_table.get_children():
                self.content_table.delete(item)
        
        # Clear children treeview
        for item in self.children_tree.get_children():
            self.children_tree.delete(item)


class FlexTreeUI:
    """
    Main UI class that combines the tree viewer and info viewer panels.
    
    This class creates a resizable window with a left panel (TreeViewerPanel)
    for displaying the tree structure and a right panel (InfoViewerPanel)
    for showing detailed information about selected nodes.
    """
    
    def __init__(self, tree: Optional[Tree] = None):
        """
        Initialize the FlexTree UI.
        
        Args:
            tree: Optional Tree object to load initially
        """
        if tree is None:
            # Automatically create a new tree with a default root node when none provided
            root = TreeNode("Root", None)
            self.tree = Tree(root)
        else:
            self.tree = tree
        # Initialize clipboard system
        self.clipboard = []  # List of TreeNode objects
        self.clipboard_mode = None  # 'cut' or 'copy'
        
        # Initialize NewNode counter for unique naming
        self.new_node_counter = 0
        
        # Initialize current file path for save/save as functionality
        self.current_file_path = None
        
        # Initialize unsaved changes tracking
        self.has_unsaved_changes = False
        
        # Initialize action memory system for undo/redo
        self.action_memory = ActionMemorySystem(max_steps=20)
        
        # Search system
        self.search_results = []
        self.current_search_index = -1
        self.search_dialog = None
        self.replace_dialog = None
        
        self._setup_ui()
        
        # Load initial tree if provided
        if self.tree:
            self.treeviewer.load_tree(self.tree)
    
    def _setup_ui(self):
        """Set up the main user interface."""
        # Create main window
        self.root = tk.Tk()
        # Set initial title
        self._update_window_title()
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        # Create main paned window for resizable panels
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tree viewer panel (left)
        clipboard_callbacks = {
            'cut': self._cut_node,
            'copy': self._copy_node,
            'paste': self._paste_node,
            'delete': self._delete_node,
            'insert': self._insert_new_node
        }
        self.treeviewer = TreeViewerPanel(
            self.main_paned, 
            on_node_select=self._on_node_selected,
            clipboard_callbacks=clipboard_callbacks
        )
        self.main_paned.add(self.treeviewer, weight=1)
        
        # Create info viewer panel (right)
        self.infoviewer = InfoViewerPanel(self.main_paned)
        self.infoviewer.set_node_renamed_callback(self._on_node_renamed)
        self.infoviewer.set_action_recorder_callback(self._record_action_state)
        self.infoviewer.set_action_complete_callback(self._complete_action_state)
        self.infoviewer.set_content_changed_callback(self._mark_as_changed)
        self.main_paned.add(self.infoviewer, weight=2)
        
        # Create menu bar
        self._create_menu()
        
        # Setup keyboard bindings for clipboard
        self._setup_clipboard_bindings()
        
        # Create status bar
        self._create_status_bar()
        
        # Set initial pane positions
        self.root.after(100, self._set_initial_pane_position)
        
        # Setup window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Initialize action status
        self._update_action_status()
    
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self._new_json_file)
        file_menu.add_separator()
        file_menu.add_command(label="Open JSON...", accelerator="Ctrl+O", command=self._load_json_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self._save_json_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self._save_as_json_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self._undo_action)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self._redo_action)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=self._cut_node)
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=self._copy_node)
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=self._paste_node)
        edit_menu.add_separator()
        edit_menu.add_command(label="Insert New Node", accelerator="Ctrl+I", command=self._insert_new_node)
        edit_menu.add_command(label="Delete", accelerator="Del", command=self._delete_node)
        edit_menu.add_separator()
        edit_menu.add_command(label="Rename Node", accelerator="Ctrl+R", command=self._rename_node)
        edit_menu.add_command(label="Toggle Edit Mode", accelerator="Ctrl+E", command=self._toggle_edit_mode)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Find...", accelerator="Ctrl+F", command=self._open_search_dialog)
        view_menu.add_command(label="Find and Replace...", accelerator="Ctrl+H", command=self._open_replace_dialog)
        view_menu.add_separator()
        view_menu.add_command(label="Expand All", command=self.treeviewer._expand_all)
        view_menu.add_command(label="Collapse All", command=self.treeviewer._collapse_all)
        view_menu.add_separator()
        view_menu.add_command(label="Reset Panel Sizes", command=self._reset_panel_sizes)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_status_bar(self):
        """Create a status bar to show clipboard information."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.clipboard_label = ttk.Label(self.status_bar, text="")
        self.clipboard_label.pack(side=tk.RIGHT)
    
    def _update_clipboard_status(self):
        """Update the clipboard status in the status bar."""
        if self.clipboard:
            node_name = self.clipboard[0].name
            mode_text = "Cut" if self.clipboard_mode == 'cut' else "Copied"
            self.clipboard_label.config(text=f"{mode_text}: '{node_name}'")
        else:
            self.clipboard_label.config(text="")
    
    def _set_initial_pane_position(self):
        """Set the initial position of the paned window."""
        # Set left panel to about 1/3 of the width
        window_width = self.root.winfo_width()
        left_width = window_width // 3
        self.main_paned.sashpos(0, left_width)
    
    def _on_node_selected(self, node: TreeNode):
        """
        Handle node selection from the tree viewer.
        
        Args:
            node: The selected TreeNode
        """
        self.infoviewer.display_node_info(node)
    
    def _on_node_renamed(self, node: TreeNode, old_name: str, new_name: str):
        """
        Handle node renaming from the info viewer.
        
        Args:
            node: The renamed TreeNode
            old_name: The previous name
            new_name: The new name
        """
        # Refresh the tree view to show the new name
        self.treeviewer._populate_treeview()
        
        # Find and select the renamed node in the tree view
        self._select_node_in_tree(node)
    
    def _select_node_in_tree(self, target_node: TreeNode):
        """Select a specific node in the tree view."""
        def find_item_by_node(item_id=""):
            # Get children of the current item (root if item_id is empty)
            children = self.treeviewer.treeview.get_children(item_id)
            
            for child_id in children:
                # Check if this item corresponds to our target node
                if child_id in self.treeviewer.node_map:
                    node = self.treeviewer.node_map[child_id]
                    if node == target_node:
                        # Found the node, select it
                        self.treeviewer.treeview.selection_set(child_id)
                        self.treeviewer.treeview.focus(child_id)
                        self.treeviewer.treeview.see(child_id)
                        return True
                
                # Recursively search in children
                if find_item_by_node(child_id):
                    return True
            
            return False
        
        # Start the search from the root
        find_item_by_node()
    
    def _new_json_file(self):
        """Create a new JSON file with a default root node."""
        # Check for unsaved changes first
        if not self._check_unsaved_changes():
            return
        
        try:
            # Create a new tree with a default root node
            root = TreeNode("Root", None)
            new_tree = Tree(root)
            
            # Reset the NewNode counter
            self.new_node_counter = 0
            
            # Clear current file path (new file hasn't been saved yet)
            self.current_file_path = None
            
            # Mark as not having unsaved changes (new empty file)
            self.has_unsaved_changes = False
            
            # Load the new tree
            self.load_tree(new_tree)
            
            # Update window title
            self._update_window_title()
            
            # Clear clipboard
            self.clipboard = []
            self.clipboard_mode = None
            self._update_clipboard_status()
            
            # Clear action history
            self.action_memory.clear_history()
            self._update_action_status()

            #messagebox.showinfo("New File", "New JSON file created with default root node.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new file:\n{str(e)}")
    
    def _load_json_file(self):
        """Load a tree from a JSON file."""
        # Check for unsaved changes first
        if not self._check_unsaved_changes():
            return
            
        filename = filedialog.askopenfilename(
            title="Load Tree from JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                tree = Tree.load_json(filename)
                # Reset the NewNode counter when loading a file
                self.new_node_counter = 0
                # Set the current file path
                self.current_file_path = filename
                # Mark as saved (just loaded from file)
                self.has_unsaved_changes = False
                self.load_tree(tree)
                # Update window title to show current file
                self._update_window_title()
                #messagebox.showinfo("Success", f"Tree loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load JSON file:\n{str(e)}")
    
    def _save_json_file(self):
        """Save the current tree. If no current file path, prompt for one."""
        if not self.tree:
            messagebox.showwarning("Warning", "No tree to save")
            return
        
        # If we have a current file path, save directly to it
        if self.current_file_path:
            try:
                self.tree.save_json(self.current_file_path)
                self._mark_as_saved()
                #messagebox.showinfo("Success", f"Tree saved to {self.current_file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save JSON file:\n{str(e)}")
        else:
            # No current file path, behave like "Save As"
            self._save_as_json_file()
    
    def _save_as_json_file(self):
        """Save the current tree to a new JSON file (always prompts for filename)."""
        if not self.tree:
            messagebox.showwarning("Warning", "No tree to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Tree to JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.tree.save_json(filename)
                # Update current file path
                self.current_file_path = filename
                # Mark as saved
                self._mark_as_saved()
                # Update window title to show current file
                self._update_window_title()
                #messagebox.showinfo("Success", f"Tree saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save JSON file:\n{str(e)}")
    
    def _update_window_title(self):
        """Update the window title to reflect the current file and unsaved changes."""
        unsaved_indicator = "*" if self.has_unsaved_changes else ""
        
        if self.current_file_path:
            import os
            filename = os.path.basename(self.current_file_path)
            self.root.title(f"FlexTree JSON UI - {filename}{unsaved_indicator}")
        else:
            self.root.title(f"FlexTree JSON UI - Untitled{unsaved_indicator}")
    
    def _mark_as_changed(self):
        """Mark the document as having unsaved changes."""
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self._update_window_title()
    
    def _mark_as_saved(self):
        """Mark the document as saved (no unsaved changes)."""
        if self.has_unsaved_changes:
            self.has_unsaved_changes = False
            self._update_window_title()
    
    def _check_unsaved_changes(self) -> bool:
        """
        Check for unsaved changes and prompt user to save.
        
        Returns:
            True if it's safe to continue (no changes or user chose to discard)
            False if user wants to cancel the operation
        """
        if not self.has_unsaved_changes:
            return True
        
        # Check if there are unsaved changes in the info viewer as well
        info_has_changes = (hasattr(self.infoviewer, '_has_unsaved_changes') and 
                           self.infoviewer._has_unsaved_changes())
        
        if self.has_unsaved_changes or info_has_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before continuing?",
                default="yes"
            )
            
            if result is True:  # Yes - save first
                self._save_json_file()
                # Check if save was successful (user didn't cancel save dialog)
                return not self.has_unsaved_changes
            elif result is False:  # No - discard changes
                return True
            else:  # Cancel
                return False
        
        return True
    
    def _on_closing(self):
        """Handle window closing event."""
        if self._check_unsaved_changes():
            self.root.destroy()
    
    def _reset_panel_sizes(self):
        """Reset panel sizes to default proportions."""
        self._set_initial_pane_position()
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """FlexTree JSON UI

A graphical interface for viewing and exploring tree data structures.

Features:
• Interactive tree navigation
• Detailed node information
• Resizable panels
• JSON import/export
• Statistics and content viewing

Created with FlexTree library."""
        
        messagebox.showinfo("About FlexTree JSON UI", about_text)
    
    def load_tree(self, tree: Tree):
        """
        Load a new tree into the UI.
        
        Args:
            tree: The Tree object to load
        """
        self.tree = tree
        # Reset NewNode counter when loading a new tree
        self.new_node_counter = 0
        # Clear action history when loading new tree
        self.action_memory.clear_history()
        self.treeviewer.load_tree(tree)
        self.infoviewer.clear_info()
        # Update status to reflect cleared history
        self._update_action_status()
    
    def _setup_clipboard_bindings(self):
        """Setup keyboard bindings for clipboard and file operations."""
        # File operations
        self.root.bind('<Control-n>', lambda e: self._new_json_file())
        self.root.bind('<Control-N>', lambda e: self._new_json_file())
        self.root.bind('<Control-o>', lambda e: self._load_json_file())
        self.root.bind('<Control-O>', lambda e: self._load_json_file())
        self.root.bind('<Control-s>', lambda e: self._save_json_file())
        self.root.bind('<Control-S>', lambda e: self._save_json_file())
        self.root.bind('<Control-Shift-s>', lambda e: self._save_as_json_file())
        self.root.bind('<Control-Shift-S>', lambda e: self._save_as_json_file())
        
        # Undo/Redo operations
        self.root.bind('<Control-z>', lambda e: self._undo_action())
        self.root.bind('<Control-Z>', lambda e: self._undo_action())
        self.root.bind('<Control-y>', lambda e: self._redo_action())
        self.root.bind('<Control-Y>', lambda e: self._redo_action())
        
        # Edit operations
        self.root.bind('<Control-r>', lambda e: self._rename_node())
        self.root.bind('<Control-R>', lambda e: self._rename_node())
        self.root.bind('<F2>', lambda e: self._rename_node())
        self.root.bind('<Control-e>', lambda e: self._toggle_edit_mode())
        self.root.bind('<Control-E>', lambda e: self._toggle_edit_mode())
        
        # Clipboard operations
        self.root.bind('<Control-x>', lambda e: self._cut_node())
        self.root.bind('<Control-X>', lambda e: self._cut_node())
        self.root.bind('<Control-c>', lambda e: self._copy_node())
        self.root.bind('<Control-C>', lambda e: self._copy_node())
        self.root.bind('<Control-v>', lambda e: self._paste_node())
        self.root.bind('<Control-V>', lambda e: self._paste_node())
        self.root.bind('<Control-i>', lambda e: self._insert_new_node())
        self.root.bind('<Control-I>', lambda e: self._insert_new_node())
        
        # Search and replace operations
        self.root.bind('<Control-f>', lambda e: self._open_search_dialog())
        self.root.bind('<Control-F>', lambda e: self._open_search_dialog())
        self.root.bind('<Control-h>', lambda e: self._open_replace_dialog())
        self.root.bind('<Control-H>', lambda e: self._open_replace_dialog())
        self.root.bind('<Escape>', lambda e: self._close_search_dialogs())
        
        self.root.bind('<Delete>', lambda e: self._delete_node())
    
    def _get_selected_node(self) -> Optional[TreeNode]:
        """Get the currently selected node from the tree viewer."""
        selection = self.treeviewer.treeview.selection()
        if selection:
            item_id = selection[0]
            return self.treeviewer.node_map.get(item_id)
        return None
    
    def _get_selected_nodes(self) -> Optional[List[TreeNode]]:
        """Get the currently selected nodes from the tree viewer."""
        selection = self.treeviewer.treeview.selection()
        if selection:
            return [self.treeviewer.node_map.get(item_id) for item_id in selection]
        return None
    
    def _deep_copy_node(self, node: TreeNode) -> TreeNode:
        """Create a deep copy of a TreeNode and all its children."""
        # Create new node with copied content
        new_node = TreeNode(node.name, copy.deepcopy(node.content))
        
        # Recursively copy all children
        for child in node.children:
            new_node.add_child(self._deep_copy_node(child))
        
        return new_node
    
    def _cut_node(self):
        """Cut the selected node(s) to clipboard."""
        selected_nodes = self._get_selected_nodes()
        if not selected_nodes:
            messagebox.showwarning("No Selection", "Please select a node to cut.")
            return

        if any(node == self.tree.root for node in selected_nodes):
            messagebox.showwarning("Cannot Cut Root", "Cannot cut the root node.")
            return
        
        # Record action state before performing cut
        action_data = {
            'node_names': [node.name for node in selected_nodes],
            'parent_names': [node.parent.name if node.parent else None for node in selected_nodes]
        }
        self._record_action_state('cut', action_data)
        
        # Store the original node for cutting (we'll remove it after successful cut)
        self.clipboard = [self._deep_copy_node(selected_node) for selected_node in selected_nodes]
        self.clipboard_mode = 'cut'
        self._original_cut_nodes = selected_nodes  # Keep reference to original for removal

        self._update_clipboard_status()
        
        # Complete the action recording
        self._complete_action_state()
        
        #messagebox.showinfo("Cut", f"Node '{selected_node.name}' has been cut to clipboard.")
    
    def _copy_node(self):
        """Copy the selected node(s) to clipboard."""
        selected_nodes = self._get_selected_nodes()
        if not selected_nodes:
            messagebox.showwarning("No Selection", "Please select a node to copy.")
            return
        
        # Record action state before performing copy (for undo purposes)
        action_data = {
            'node_names': [node.name for node in selected_nodes]
        }
        self._record_action_state('copy', action_data)
        
        # Create deep copy and store in clipboard
        self.clipboard = [self._deep_copy_node(selected_node) for selected_node in selected_nodes]
        self.clipboard_mode = 'copy'
        
        self._update_clipboard_status()
        
        # Complete the action recording
        self._complete_action_state()
        
        #messagebox.showinfo("Copy", f"Node '{selected_node.name}' has been copied to clipboard.")
    
    def _paste_node(self):
        """Paste node(s) from clipboard to selected location."""
        if not self.clipboard:
            messagebox.showwarning("Empty Clipboard", "Clipboard is empty. Nothing to paste.")
            return
        
        selected_node = self._get_selected_node()
        if not selected_node:
            messagebox.showwarning("No Selection", "Please select a target node to paste into.")
            return
        
        # Record action state before performing paste
        action_data = {
            'target_node_name': selected_node.name,
            'clipboard_node_names': [node.name for node in self.clipboard],
            'clipboard_mode': self.clipboard_mode
        }
        self._record_action_state('paste', action_data)
        
        try:        
            # If this was a cut operation, remove the original node
            if self.clipboard_mode == 'cut' and hasattr(self, '_original_cut_nodes'):
                for original_node in self._original_cut_nodes:
                    if original_node.parent:
                        original_node.parent.remove_child(original_node)
                # Clear the cut reference since we've completed the cut operation
                delattr(self, '_original_cut_nodes')

            pasted_nodes = []
            for clipboard_node in self.clipboard:
                # Create a new copy each time we paste
                new_node = self._deep_copy_node(clipboard_node)
                # Ensure unique names for the pasted subtree (avoid collisions with existing tree
                # and also among nodes being pasted).
                _assigned_names = set()
                def _ensure_unique_names(node):
                    base = node.name
                    candidate = base
                    if candidate in _assigned_names or self._name_exists_in_tree(candidate):
                        counter = 1
                        while True:
                            candidate = f"{base} ({counter})"
                            if candidate not in _assigned_names and not self._name_exists_in_tree(candidate):
                                break
                            counter += 1
                    node.name = candidate
                    _assigned_names.add(candidate)
                    for ch in node.children:
                        _ensure_unique_names(ch)
                _ensure_unique_names(new_node)
                # Add to target node
                selected_node.add_child(new_node)
                pasted_nodes.append(new_node.name)


            # Refresh the tree display while preserving expansion state
            self.treeviewer.load_tree(self.tree, preserve_expansion=True)
            
            # Show success message
            pasted_names = "', '".join(pasted_nodes)
            #messagebox.showinfo("Paste", f"Node(s) '{pasted_names}' pasted successfully.")
            
            # For cut operations, clear clipboard after successful paste
            if self.clipboard_mode == 'cut':
                self.clipboard = []
                self.clipboard_mode = None
                self._update_clipboard_status()
            
            # Complete the action recording
            self._complete_action_state()
                
        except Exception as e:
            messagebox.showerror("Paste Error", f"Failed to paste node(s):\n{str(e)}")
    
    def _delete_node(self):
        """Delete the selected node."""
        selected_nodes = self._get_selected_nodes()
        if not selected_nodes:
            messagebox.showwarning("No Selection", "Please select a node to delete.")
            return

        if any(node == self.tree.root for node in selected_nodes):
            messagebox.showwarning("Cannot Delete Root", "Cannot delete the root node.")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete node(s) {', '.join(node.name for node in selected_nodes)} and all their children?\n\n"
            "This action can be undone with Ctrl+Z."
        )
        
        if result:
            # Record action state before performing delete
            action_data = {
                'node_names': [node.name for node in selected_nodes],
                'parent_names': [node.parent.name if node.parent else None for node in selected_nodes]
            }
            self._record_action_state('delete', action_data)
            
            try:
                # Remove from parent
                for selected_node in selected_nodes:
                    if selected_node.parent:
                        selected_node.parent.remove_child(selected_node)

                # Clear selection and refresh tree while preserving expansion state
                self.treeviewer.load_tree(self.tree, preserve_expansion=True)
                self.infoviewer.clear_info()
                
                # Complete the action recording
                self._complete_action_state()
                
                #messagebox.showinfo("Deleted", f"Node '{selected_node.name}' has been deleted.")
                
            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete node:\n{str(e)}")
    
    def _insert_new_node(self):
        """Insert a new child node with the name 'NewNode' or 'NewNode_i'."""
        selected_node = self._get_selected_node()
        if not selected_node:
            messagebox.showwarning("No Selection", "Please select a parent node to insert new child into.")
            return
        
        # Record action state before performing insert
        action_data = {
            'parent_node_name': selected_node.name
        }
        self._record_action_state('insert', action_data)
        
        try:
            # Generate unique name starting with "NewNode"
            new_name = self._get_unique_new_node_name()
            
            # Create new node with None content
            new_node = TreeNode(new_name, None)
            
            # Add to selected node as child
            selected_node.add_child(new_node)
            
            # Refresh the tree display while preserving expansion state
            self.treeviewer.load_tree(self.tree, preserve_expansion=True)
            
            # Ensure parent is expanded to show the new node
            self._ensure_node_parent_expanded(selected_node.name)
            
            # Select the parent node in the tree viewer (auto-select parent after insert)
            self._select_node_by_name(selected_node.name)
            
            # Complete the action recording
            self._complete_action_state()
            
            #messagebox.showinfo("Node Created", f"New node '{new_name}' created successfully.")
            
        except Exception as e:
            messagebox.showerror("Insert Error", f"Failed to create new node:\n{str(e)}")
    
    def _get_unique_new_node_name(self) -> str:
        """Generate a unique name for new nodes: NewNode, NewNode_1, NewNode_2, etc."""
        base_name = "NewNode"
        
        # If counter is 0, try base name first
        if self.new_node_counter == 0:
            if not self._name_exists_in_tree(base_name):
                self.new_node_counter = 1  # Next node will be NewNode_1
                return base_name
        
        # Use counter-based naming
        while True:
            if self.new_node_counter == 0:
                candidate_name = base_name
            else:
                candidate_name = f"{base_name}_{self.new_node_counter}"
                
            if not self._name_exists_in_tree(candidate_name):
                self.new_node_counter += 1
                return candidate_name
            
            self.new_node_counter += 1
    
    def _ensure_node_parent_expanded(self, parent_name: str):
        """Ensure that the specified parent node is expanded to show its children."""
        try:
            def find_and_expand_item(item_id, target_name):
                node = self.treeviewer.node_map.get(item_id)
                if node and node.name == target_name:
                    self.treeviewer.treeview.item(item_id, open=True)
                    return True
                
                for child_id in self.treeviewer.treeview.get_children(item_id):
                    if find_and_expand_item(child_id, target_name):
                        return True
                return False
            
            # Search through all top-level items
            for item_id in self.treeviewer.treeview.get_children():
                if find_and_expand_item(item_id, parent_name):
                    break
                    
        except Exception as e:
            # If expansion fails, it's not critical - just log it
            print(f"Could not expand parent node '{parent_name}': {e}")

    def _select_node_by_name(self, name: str):
        """Select a node in the tree viewer by its name."""
        try:
            # Find the treeview item corresponding to the node name
            def find_item_by_name(item_id, target_name):
                node = self.treeviewer.node_map.get(item_id)
                if node and node.name == target_name:
                    return item_id
                
                for child_id in self.treeviewer.treeview.get_children(item_id):
                    result = find_item_by_name(child_id, target_name)
                    if result:
                        return result
                return None
            
            # Search through all top-level items
            for item_id in self.treeviewer.treeview.get_children():
                found_item = find_item_by_name(item_id, name)
                if found_item:
                    self.treeviewer.treeview.selection_set(found_item)
                    self.treeviewer.treeview.focus(found_item)
                    # Ensure the item is visible
                    self.treeviewer.treeview.see(found_item)
                    break
                    
        except Exception as e:
            # If selection fails, it's not critical - just log it
            print(f"Could not select node '{name}': {e}")
    
    def _get_unique_name(self, base_name: str, target_parent: TreeNode) -> str:
        """Generate a unique name by appending (1), (2), etc. if needed."""
        # Check if base name is unique in entire tree
        if not self._name_exists_in_tree(base_name):
            return base_name
        
        # Try with numbers
        counter = 1
        while True:
            candidate_name = f"{base_name} ({counter})"
            if not self._name_exists_in_tree(candidate_name):
                return candidate_name
            counter += 1
    
    def _name_exists_in_tree(self, name: str) -> bool:
        """Check if a name already exists anywhere in the tree."""
        return self._name_exists_in_subtree(self.tree.root, name)
    
    def _name_exists_in_subtree(self, node: TreeNode, name: str) -> bool:
        """Recursively check if name exists in subtree."""
        if node.name == name:
            return True
        
        for child in node.children:
            if self._name_exists_in_subtree(child, name):
                return True
        
        return False
    
    def _deep_copy_tree(self, tree: Tree) -> Tree:
        """Create a deep copy of the entire tree."""
        return tree.deepcopy()
    
    def _record_action_state(self, action_type: str, action_data: Optional[Dict[str, Any]] = None):
        """Record the current state before performing an action."""
        # Get current tree state
        tree_state_before = self._deep_copy_tree(self.tree)
        
        # Get selected node name
        selected_node = self._get_selected_node()
        selected_node_name = selected_node.name if selected_node else None
        
        # Get current expansion state
        expansion_state = self.treeviewer._capture_expansion_state()
        
        # Record the action
        self.action_memory.record_action(
            action_type=action_type,
            tree_state_before=tree_state_before,
            selected_node_name=selected_node_name,
            expansion_state=expansion_state,
            action_data=action_data
        )
        
        # Update status bar
        self._update_action_status()
    
    def _complete_action_state(self):
        """Complete the last recorded action by capturing the 'after' state."""
        # Get current tree state after the action
        tree_state_after = self._deep_copy_tree(self.tree)
        
        # Get selected node name after the action
        selected_node = self._get_selected_node()
        selected_node_name_after = selected_node.name if selected_node else None
        
        # Get current expansion state after the action
        expansion_state_after = self.treeviewer._capture_expansion_state()
        
        # Complete the action record
        self.action_memory.complete_action(
            tree_state_after=tree_state_after,
            selected_node_name_after=selected_node_name_after,
            expansion_state_after=expansion_state_after
        )
        
        # Update status bar
        self._update_action_status()
        
        # Mark as changed since an action was completed
        self._mark_as_changed()
    
    def _undo_action(self):
        """Undo the last action."""
        if not self.action_memory.can_undo():
            # messagebox.showinfo("Undo", "No actions to undo.")
            return
        
        try:
            # Get the action to undo
            action = self.action_memory.get_undo_action()
            if not action:
                return
            
            # Restore the tree state from before the action
            self.tree = action['tree_state_before']
            
            # Refresh the tree display
            self.treeviewer.load_tree(self.tree)
            
            # Restore expansion and selection state
            if action['expansion_state']:
                self.treeviewer._restore_expansion_state(action['expansion_state'])
            
            # Clear info panel and reselect node if available
            if action['selected_node_name']:
                self._select_node_by_name(action['selected_node_name'])
            else:
                self.infoviewer.clear_info()
            
            # Update status
            self._update_action_status()
            
            # Mark as changed (even undoing counts as a change from the saved state)
            self._mark_as_changed()
            
            # Clear clipboard if it contained nodes that no longer exist
            self._validate_clipboard()
            
        except Exception as e:
            messagebox.showerror("Undo Error", f"Failed to undo action:\n{str(e)}")
    
    def _redo_action(self):
        """Redo the next action."""
        if not self.action_memory.can_redo():
            # messagebox.showinfo("Redo", "No actions to redo.")
            return
        
        try:
            # Get the action to redo
            action = self.action_memory.get_redo_action()
            if not action:
                return
            
            # Re-execute the action based on its type and stored data
            self._execute_redo_action(action)
            
            # Update status
            self._update_action_status()
            
            # Mark as changed (redoing counts as a change from the saved state)
            self._mark_as_changed()
            
        except Exception as e:
            messagebox.showerror("Redo Error", f"Failed to redo action:\n{str(e)}")
    
    def _execute_redo_action(self, action: Dict[str, Any]):
        """Execute a redo action by restoring the 'after' state."""
        try:
            # Check if we have the after state stored
            if action.get('tree_state_after') is None:
                messagebox.showwarning("Redo Error", "Cannot redo: action state incomplete.")
                return
            
            # Restore the tree state to what it was after the action
            self.tree = action['tree_state_after']
            
            # Refresh the tree display
            self.treeviewer.load_tree(self.tree)
            
            # Restore expansion and selection state to after the action
            if action.get('expansion_state_after'):
                self.treeviewer._restore_expansion_state(action['expansion_state_after'])
            
            # Clear info panel and reselect node if available
            if action.get('selected_node_name_after'):
                self._select_node_by_name(action['selected_node_name_after'])
            else:
                self.infoviewer.clear_info()
            
            # Clear clipboard if it contained nodes that no longer exist
            self._validate_clipboard()
            
        except Exception as e:
            messagebox.showerror("Redo Error", f"Failed to execute redo:\n{str(e)}")
    
    def _update_action_status(self):
        """Update the status bar with current undo/redo information."""
        if hasattr(self, 'status_label'):
            undo_available = "Yes" if self.action_memory.can_undo() else "No"
            redo_available = "Yes" if self.action_memory.can_redo() else "No"
            self.status_label.config(text=f"Undo: {undo_available} | Redo: {redo_available}")
    
    def _validate_clipboard(self):
        """Validate that clipboard nodes still exist in the tree."""
        if not self.clipboard:
            return
        
        # Check if any clipboard nodes still exist in the tree
        valid_clipboard = []
        for clip_node in self.clipboard:
            if self._node_exists_in_tree(clip_node.name):
                valid_clipboard.append(clip_node)
        
        # Update clipboard
        self.clipboard = valid_clipboard
        if not self.clipboard:
            self.clipboard_mode = None
        
        self._update_clipboard_status()
    
    def _node_exists_in_tree(self, name: str) -> bool:
        """Check if a node with the given name exists in the current tree."""
        return self._name_exists_in_tree(name)
    
    def _rename_node(self):
        """Rename the currently selected node."""
        selected_node = self._get_selected_node()
        if not selected_node:
            messagebox.showwarning("No Selection", "Please select a node to rename.")
            return
        
        # Use the existing EditNodeNameDialog
        dialog = EditNodeNameDialog(self.root, selected_node.name)
        
        if dialog.result and dialog.result != selected_node.name:
            new_name = dialog.result.strip()
            
            # Validate the new name
            if not new_name:
                messagebox.showerror("Error", "Node name cannot be empty.")
                return
            
            # Check if name is unique in the tree
            if not self._name_exists_in_tree(new_name):
                try:
                    # Record action for undo/redo
                    action_data = {'old_name': selected_node.name, 'new_name': new_name}
                    self._record_action_state('rename', action_data)
                    
                    # Update the node name
                    old_name = selected_node.name
                    selected_node.name = new_name
                    
                    # Refresh the tree display while preserving expansion state
                    self.treeviewer.load_tree(self.tree, preserve_expansion=True)
                    
                    # Select the renamed node
                    self._select_node_by_name(new_name)
                    
                    # Complete the action recording
                    self._complete_action_state()
                    
                    messagebox.showinfo("Success", f"Node renamed from '{old_name}' to '{new_name}'")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to rename node:\n{str(e)}")
            else:
                messagebox.showerror("Error", f"Name '{new_name}' already exists in the tree. Please choose a unique name.")
    
    def _toggle_edit_mode(self):
        """Toggle edit mode for the current node in the info viewer."""
        if self.infoviewer.current_node:
            # Delegate to the info viewer's toggle edit mode
            current_state = self.infoviewer.edit_mode_var.get()
            self.infoviewer.edit_mode_var.set(not current_state)
            self.infoviewer._toggle_edit_mode()
        else:
            messagebox.showwarning("No Selection", "Please select a node to edit its content.")
    
    def _open_search_dialog(self):
        """Open the search dialog."""
        if self.search_dialog and hasattr(self.search_dialog, 'dialog') and self.search_dialog.dialog.winfo_exists():
            # If dialog exists, bring it to front
            self.search_dialog.dialog.lift()
            self.search_dialog.dialog.focus()
            return
            
        self.search_dialog = SearchDialog(
            self.root, 
            self._perform_search,
            navigate_callback=self._navigate_to_search_result,
            find_next_callback=self._find_next
        )
        
    def _open_replace_dialog(self):
        """Open the find and replace dialog."""
        if self.replace_dialog and hasattr(self.replace_dialog, 'dialog') and self.replace_dialog.dialog.winfo_exists():
            # If dialog exists, bring it to front
            self.replace_dialog.dialog.lift()
            self.replace_dialog.dialog.focus()
            return
            
        self.replace_dialog = ReplaceDialog(
            self.root, 
            self._perform_search, 
            self._perform_replace,
            navigate_callback=self._navigate_to_search_result,
            find_next_callback=self._find_next
        )
    
    def _close_search_dialogs(self):
        """Close any open search dialogs."""
        if self.search_dialog and hasattr(self.search_dialog, 'dialog') and self.search_dialog.dialog.winfo_exists():
            self.search_dialog.dialog.destroy()
        if self.replace_dialog and hasattr(self.replace_dialog, 'dialog') and self.replace_dialog.dialog.winfo_exists():
            self.replace_dialog.dialog.destroy()
    
    def _perform_search(self, search_term, options):
        """Perform search across the tree and return results."""
        results = []
        
        if not self.tree or not self.tree.root:
            return results
        
        # Prepare search term based on case sensitivity
        if options['case_sensitive']:
            search_func = lambda text: search_term in text
            exact_search = search_term
        else:
            search_func = lambda text: search_term.lower() in text.lower()
            exact_search = search_term.lower()
        
        # Recursive search function
        def search_node(node):
            node_results = []
            
            # Search in node name
            if options['search_names']:
                node_name = node.name if options['case_sensitive'] else node.name.lower()
                
                if options['whole_words']:
                    # Use word boundary matching
                    import re
                    pattern = r'\b' + re.escape(exact_search) + r'\b'
                    flags = 0 if options['case_sensitive'] else re.IGNORECASE
                    if re.search(pattern, node.name, flags):
                        node_results.append({
                            'node': node,
                            'type': 'name',
                            'match_text': search_term,
                            'full_text': node.name
                        })
                else:
                    if search_func(node.name):
                        node_results.append({
                            'node': node,
                            'type': 'name',
                            'match_text': search_term,
                            'full_text': node.name
                        })
            
            # Search in node content
            if options['search_content'] and node.content is not None:
                content_str = str(node.content)
                content_search = content_str if options['case_sensitive'] else content_str.lower()
                
                if options['whole_words']:
                    # Use word boundary matching for content
                    import re
                    pattern = r'\b' + re.escape(exact_search) + r'\b'
                    flags = 0 if options['case_sensitive'] else re.IGNORECASE
                    if re.search(pattern, content_str, flags):
                        node_results.append({
                            'node': node,
                            'type': 'content',
                            'match_text': search_term,
                            'full_text': content_str
                        })
                else:
                    if search_func(content_str):
                        node_results.append({
                            'node': node,
                            'type': 'content',
                            'match_text': search_term,
                            'full_text': content_str
                        })
            
            # Search in children
            for child in node.children:
                node_results.extend(search_node(child))
                
            return node_results
        
        # Perform search starting from root
        self.search_results = search_node(self.tree.root)
        self.current_search_index = -1
        
        return self.search_results
    
    def _perform_replace(self, result, find_text, replace_text, options):
        """Perform replace operation on a search result."""
        try:
            node = result['node']
            result_type = result['type']
            
            # Record action for undo
            self._record_action_state("replace", {
                'node_name': node.name,
                'type': result_type,
                'find_text': find_text,
                'replace_text': replace_text
            })
            
            if result_type == 'name':
                # Replace in node name
                old_name = node.name
                if options['whole_words']:
                    import re
                    pattern = r'\b' + re.escape(find_text) + r'\b'
                    flags = 0 if options['case_sensitive'] else re.IGNORECASE
                    new_name = re.sub(pattern, replace_text, old_name, flags=flags)
                else:
                    if options['case_sensitive']:
                        new_name = old_name.replace(find_text, replace_text)
                    else:
                        # Case insensitive replacement
                        import re
                        pattern = re.escape(find_text)
                        flags = re.IGNORECASE
                        new_name = re.sub(pattern, replace_text, old_name, flags=flags)
                
                if new_name != old_name:
                    # Validate name uniqueness
                    if not self._is_name_unique_for_rename(node, new_name):
                        messagebox.showerror("Replace Error", f"Name '{new_name}' already exists in the tree.")
                        return False
                    
                    node.name = new_name
                    # Refresh tree display
                    self.treeviewer.load_tree(self.tree, preserve_expansion=True)
                    # Update info panel if this node is selected
                    selected_node = self._get_selected_node()
                    if selected_node and selected_node.name == new_name:
                        self.infoviewer.display_node_info(selected_node)
            
            elif result_type == 'content':
                # Replace in node content
                if node.content is not None:
                    # Determine if original content is JSON-structured (dict/list/tuple)
                    is_json_struct = False
                    json_text = None
                    parsed_json = None

                    if isinstance(node.content, (dict, list, tuple)):
                        is_json_struct = True
                        json_text = json.dumps(node.content, ensure_ascii=False)
                    elif isinstance(node.content, str):
                        # If it's a string, check whether it contains valid JSON
                        try:
                            parsed_json = json.loads(node.content)
                            is_json_struct = True
                            json_text = json.dumps(parsed_json, ensure_ascii=False)
                        except Exception:
                            # not JSON, treat as plain string below
                            is_json_struct = False
                            json_text = None

                    # Perform replacement either on JSON text (if structured) or on plain text
                    if is_json_struct and json_text is not None:
                        old_content = json_text
                        try:
                            if options['whole_words']:
                                import re
                                pattern = r'\b' + re.escape(find_text) + r'\b'
                                flags = 0 if options['case_sensitive'] else re.IGNORECASE
                                new_content_str = re.sub(pattern, replace_text, old_content, flags=flags)
                            else:
                                if options['case_sensitive']:
                                    new_content_str = old_content.replace(find_text, replace_text)
                                else:
                                    import re
                                    pattern = re.escape(find_text)
                                    flags = re.IGNORECASE
                                    new_content_str = re.sub(pattern, replace_text, old_content, flags=flags)

                            if new_content_str != old_content:
                                # Try to parse back to JSON to preserve structure
                                try:
                                    new_parsed = json.loads(new_content_str)
                                    node.content = new_parsed
                                except Exception:
                                    # Replacement would break JSON structure -> abort replace
                                    messagebox.showerror(
                                        "Replace Error",
                                        "Replacement would produce invalid JSON. Operation aborted to preserve JSON format."
                                    )
                                    return False
                        except Exception as e:
                            messagebox.showerror("Replace Error", f"Failed to perform replacement on JSON content:\n{e}")
                            return False

                    else:
                        # Non-JSON content: fall back to previous behavior operating on string representation
                        old_content = str(node.content)
                        if options['whole_words']:
                            import re
                            pattern = r'\b' + re.escape(find_text) + r'\b'
                            flags = 0 if options['case_sensitive'] else re.IGNORECASE
                            new_content_str = re.sub(pattern, replace_text, old_content, flags=flags)
                        else:
                            if options['case_sensitive']:
                                new_content_str = old_content.replace(find_text, replace_text)
                            else:
                                import re
                                pattern = re.escape(find_text)
                                flags = re.IGNORECASE
                                new_content_str = re.sub(pattern, replace_text, old_content, flags=flags)

                        if new_content_str != old_content:
                            # Try to preserve numeric types where sensible
                            try:
                                if isinstance(node.content, str):
                                    node.content = new_content_str
                                elif isinstance(node.content, (int, float)):
                                    if '.' in new_content_str:
                                        node.content = float(new_content_str)
                                    else:
                                        node.content = int(new_content_str)
                                else:
                                    node.content = new_content_str
                            except ValueError:
                                node.content = new_content_str

                    # Update info panel if this node is selected
                    selected_node = self._get_selected_node()
                    if selected_node == node:
                        self.infoviewer.display_node_info(selected_node)
            
            self._complete_action_state()
            return True
            
        except Exception as e:
            messagebox.showerror("Replace Error", f"Error performing replace: {str(e)}")
            return False
    
    def _is_name_unique_for_rename(self, node, new_name):
        """Check if a new name is unique when renaming a node (excluding the node itself)."""
        if not self.tree or not self.tree.root:
            return True
            
        def check_subtree(current_node):
            if current_node != node and current_node.name == new_name:
                return False
            for child in current_node.children:
                if not check_subtree(child):
                    return False
            return True
            
        return check_subtree(self.tree.root)
    
    def _navigate_to_search_result(self, result):
        """Navigate to and highlight a search result."""
        node = result['node']
        result_type = result['type']
        
        # Select the node in tree viewer
        self._select_node_in_tree(node)
        
        # Navigate to appropriate tab and highlight
        if result_type == 'content':
            # Switch to content tab
            self.infoviewer.notebook.select(1)  # Content tab is index 1
            
            # Delay highlighting to ensure widget is ready after tab switch
            self.root.after(10, self._delayed_highlight_content, result['match_text'])
        else:
            # For name matches, switch to overview tab
            self.infoviewer.notebook.select(0)  # Overview tab is index 0
    
    def _delayed_highlight_content(self, search_term):
        """Highlight content with a delay to ensure widget is ready."""
        try:
            # Check if content is displayed as text
            if (hasattr(self.infoviewer, 'content_text') and 
                self.infoviewer.content_text and 
                self.infoviewer.content_display_mode == "text"):
                self._highlight_text_in_widget(self.infoviewer.content_text, search_term)
            
            # Check if content is displayed as table
            elif (hasattr(self.infoviewer, 'content_table') and 
                  self.infoviewer.content_table and 
                  self.infoviewer.content_display_mode == "table"):
                self._highlight_text_in_widget(self.infoviewer.content_table, search_term)
        
        except Exception as e:
            print(f"Error in delayed highlight: {e}")
    
    def _highlight_text_in_widget(self, widget, search_term):
        """Highlight search term in a text widget or auto-select row in a table widget."""
        try:
            # Do nothing if no search term
            if not search_term:
                return

            # Guard: widget may have been destroyed; ensure it exists
            if not getattr(widget, "winfo_exists", lambda: False)():
                return

            # Check if widget is a Treeview (table) or Text widget
            if hasattr(widget, 'get_children'):  # This is a Treeview widget
                self._handle_table_search(widget, search_term)
            elif hasattr(widget, 'search'):  # This is a Text widget
                self._handle_text_search(widget, search_term)

        except Exception as e:
            # Avoid crashing due to widget being destroyed; log for debugging
            print(f"Error highlighting/selecting in widget: {e}")
    
    def _handle_text_search(self, text_widget, search_term):
        """Handle search highlighting in text widgets."""
        try:
            # Guard: ensure widget still exists and supports search
            if not text_widget.winfo_exists() or not hasattr(text_widget, "search"):
                return

            # Clear any existing highlights (only if widget still exists)
            if text_widget.winfo_exists():
                text_widget.tag_remove('search_highlight', '1.0', tk.END)
                # Configure highlight tag
                text_widget.tag_config('search_highlight', background='yellow', foreground='black')
            else:
                return

            # Search for all occurrences, checking existence between operations
            start_pos = '1.0'
            while True:
                if not text_widget.winfo_exists():
                    break

                pos = text_widget.search(search_term, start_pos, tk.END)
                if not pos:
                    break

                # Calculate end position
                end_pos = f"{pos}+{len(search_term)}c"

                if not text_widget.winfo_exists():
                    break

                # Add highlight tag
                text_widget.tag_add('search_highlight', pos, end_pos)

                # Move to next position
                start_pos = end_pos

            # Scroll to first occurrence if found and widget still exists
            if text_widget.winfo_exists():
                first_pos = text_widget.search(search_term, '1.0', tk.END)
                if first_pos:
                    text_widget.see(first_pos)

        except Exception as e:
            print(f"Error highlighting text: {e}")
    
    def _handle_table_search(self, table_widget, search_term):
        """Handle search and auto-selection in table widgets (Treeview)."""
        try:
            # Guard: ensure widget still exists
            if not table_widget.winfo_exists():
                return

            # Clear any existing selection
            table_widget.selection_remove(*table_widget.selection())

            # Search through all table items
            found_item = None
            search_term_lower = search_term.lower()
            
            for item_id in table_widget.get_children():
                if not table_widget.winfo_exists():
                    break
                
                # Check item text (first column)
                item_text = table_widget.item(item_id, 'text')
                if search_term_lower in str(item_text).lower():
                    found_item = item_id
                    break
                
                # Check item values (other columns)
                item_values = table_widget.item(item_id, 'values')
                if item_values:
                    for value in item_values:
                        if search_term_lower in str(value).lower():
                            found_item = item_id
                            break
                    
                    if found_item:
                        break

            # Select and scroll to the found item
            if found_item and table_widget.winfo_exists():
                table_widget.selection_set(found_item)
                table_widget.focus(found_item)
                table_widget.see(found_item)

        except Exception as e:
            print(f"Error selecting table row: {e}")
    
    def _find_next(self):
        """Find next search result."""
        if not self.search_results:
            return
            
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        result = self.search_results[self.current_search_index]
        self._navigate_to_search_result(result)
        
        # Update search dialog if open
        if self.search_dialog and hasattr(self.search_dialog, 'dialog') and self.search_dialog.dialog.winfo_exists():
            self.search_dialog.current_index = self.current_search_index
            self.search_dialog.results_listbox.selection_clear(0, tk.END)
            self.search_dialog.results_listbox.selection_set(self.current_search_index)
            self.search_dialog.results_listbox.see(self.current_search_index)
    
    def _find_previous(self):
        """Find previous search result."""
        if not self.search_results:
            return
            
        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        result = self.search_results[self.current_search_index]
        self._navigate_to_search_result(result)
        
        # Update search dialog if open
        if self.search_dialog and hasattr(self.search_dialog, 'dialog') and self.search_dialog.dialog.winfo_exists():
            self.search_dialog.current_index = self.current_search_index
            self.search_dialog.results_listbox.selection_clear(0, tk.END)
            self.search_dialog.results_listbox.selection_set(self.current_search_index)
            self.search_dialog.results_listbox.see(self.current_search_index)

    def run(self):
        """Start the UI application main loop."""
        self.root.mainloop()

class EditNodeNameDialog:
    """Dialog for editing a node name with validation."""
    
    def __init__(self, parent, current_name):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Rename Node")
        self.dialog.geometry("400x180")
        self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create and pack widgets
        ttk.Label(self.dialog, text="Enter new node name:", font=('Arial', 10)).pack(pady=(15, 5))
        
        # Info label
        info_label = ttk.Label(self.dialog, text="Note: Node names must be unique within the tree.", 
                              font=('Arial', 8), foreground='gray')
        info_label.pack(pady=(0, 10))
        
        self.entry = ttk.Entry(self.dialog, width=40, font=('Arial', 10))
        self.entry.pack(pady=5, padx=20, fill=tk.X)
        self.entry.insert(0, current_name)
        self.entry.select_range(0, tk.END)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.entry.bind('<Return>', lambda e: self._ok_clicked())
        self.entry.focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _ok_clicked(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Node name cannot be empty.")
            return
        self.result = name
        self.dialog.destroy()
    
    def _cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


class EditValueDialog:
    """Dialog for editing a single value."""
    
    def __init__(self, parent, current_value, title="Edit Value"):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create and pack widgets
        ttk.Label(self.dialog, text="Enter new value:").pack(pady=10)
        
        self.entry = ttk.Entry(self.dialog, width=50)
        self.entry.pack(pady=5, padx=20, fill=tk.X)
        self.entry.insert(0, current_value)
        self.entry.select_range(0, tk.END)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.entry.bind('<Return>', lambda e: self._ok_clicked())
        self.entry.focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _ok_clicked(self):
        self.result = self.entry.get()
        self.dialog.destroy()
    
    def _cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


class AddDictItemDialog:
    """Dialog for adding a new key-value pair to a dictionary."""
    
    def __init__(self, parent):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Item")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create and pack widgets
        ttk.Label(self.dialog, text="Key:").pack(pady=(10, 5))
        self.key_entry = ttk.Entry(self.dialog, width=50)
        self.key_entry.pack(pady=5, padx=20, fill=tk.X)
        
        ttk.Label(self.dialog, text="Value (JSON format or plain text):").pack(pady=(10, 5))
        self.value_entry = ttk.Entry(self.dialog, width=50)
        self.value_entry.pack(pady=5, padx=20, fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.value_entry.bind('<Return>', lambda e: self._ok_clicked())
        self.key_entry.focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _ok_clicked(self):
        key = self.key_entry.get().strip()
        value = self.value_entry.get()
        
        if not key:
            messagebox.showwarning("Warning", "Key cannot be empty.")
            return
        
        self.result = (key, value)
        self.dialog.destroy()
    
    def _cancel_clicked(self):
        self.result = None
        self.dialog.destroy()

class AddListItemDialog:
    """Dialog for adding a new item to a list of dictionaries."""
    
    def __init__(self, parent, existing_list):
        self.result = None
        self.existing_list = existing_list
        
        # Get all unique keys from existing items
        self.all_keys = set()
        for item in existing_list:
            if isinstance(item, dict):
                self.all_keys.update(item.keys())
        self.all_keys = sorted(list(self.all_keys))
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New List Item")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create scrollable frame
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create entry fields for each key
        ttk.Label(scrollable_frame, text="Enter values for new item:", font=('Arial', 10, 'bold')).pack(pady=10)
        
        self.entries = {}
        for key in self.all_keys:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=20, pady=2)
            
            ttk.Label(frame, text=f"{key}:", width=15).pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=40)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            self.entries[key] = entry
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Focus first entry
        if self.entries:
            next(iter(self.entries.values())).focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _ok_clicked(self):
        new_item = {}
        for key, entry in self.entries.items():
            value = entry.get()
            if value:  # Only add non-empty values
                try:
                    # Try to parse as JSON
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    # If not valid JSON, store as string
                    parsed_value = value
                new_item[key] = parsed_value
        
        self.result = new_item
        self.dialog.destroy()
    
    def _cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


class CreateContentTypeDialog:
    """Dialog for choosing the type of new content to create."""
    
    def __init__(self, parent):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Content")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create and pack widgets
        title_label = ttk.Label(self.dialog, text="Choose Content Type", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(20, 15))
        
        # Radio button variable
        self.content_type_var = tk.StringVar(value="text")
        
        # Create radio buttons with descriptions
        options_frame = ttk.Frame(self.dialog)
        options_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Text option
        text_frame = ttk.Frame(options_frame)
        text_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(text_frame, text="Text Content", variable=self.content_type_var, 
                       value="text").pack(anchor=tk.W)
        ttk.Label(text_frame, text="   Simple text or string content", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        # Dictionary option
        dict_frame = ttk.Frame(options_frame)
        dict_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(dict_frame, text="Dictionary", variable=self.content_type_var, 
                       value="dict").pack(anchor=tk.W)
        ttk.Label(dict_frame, text="   Key-value pairs (JSON object)", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        # List of dictionaries option
        list_dict_frame = ttk.Frame(options_frame)
        list_dict_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(list_dict_frame, text="List of Dictionaries", variable=self.content_type_var, 
                       value="list_of_dict").pack(anchor=tk.W)
        ttk.Label(list_dict_frame, text="   Array of objects (table-like data)", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        # Null option
        null_frame = ttk.Frame(options_frame)
        null_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(null_frame, text="Null Content", variable=self.content_type_var, 
                       value="null").pack(anchor=tk.W)
        ttk.Label(null_frame, text="   No content (None/null value)", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Focus the dialog
        self.dialog.focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _ok_clicked(self):
        self.result = self.content_type_var.get()
        self.dialog.destroy()
    
    def _cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


class AddSimpleItemDialog:
    """Dialog for adding a simple item to a list."""
    
    def __init__(self, parent):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Item")
        self.dialog.geometry("400x150")
        self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create and pack widgets
        ttk.Label(self.dialog, text="Enter new item value (JSON format or plain text):").pack(pady=10)
        
        self.entry = ttk.Entry(self.dialog, width=50)
        self.entry.pack(pady=5, padx=20, fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.entry.bind('<Return>', lambda e: self._ok_clicked())
        self.entry.focus()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def _ok_clicked(self):
        value = self.entry.get()
        try:
            # Try to parse as JSON
            self.result = json.loads(value)
        except json.JSONDecodeError:
            # If not valid JSON, store as string
            self.result = value
        self.dialog.destroy()
    
    def _cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


class SearchDialog:
    """Dialog for searching nodes and content with various options."""
    
    def __init__(self, parent, search_callback, navigate_callback=None, find_next_callback=None):
        self.parent = parent
        self.search_callback = search_callback
        self.navigate_callback = navigate_callback
        self.find_next_callback = find_next_callback
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Find")
        self.dialog.geometry("400x300")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self._setup_ui()
        
        # Focus and bind keys
        self.search_entry.focus()
        self.dialog.bind('<Return>', lambda e: self._search())
        self.dialog.bind('<Escape>', lambda e: self._close())
        
    def _setup_ui(self):
        """Setup the search dialog UI."""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search term
        ttk.Label(main_frame, text="Find what:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.search_entry = ttk.Entry(main_frame, width=40)
        self.search_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=(0, 5))
        
        # Search options frame
        options_frame = ttk.LabelFrame(main_frame, text="Search Options")
        options_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Search scope
        self.search_names = tk.BooleanVar(value=True)
        self.search_content = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Search node names", variable=self.search_names).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Search content", variable=self.search_content).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Match options
        self.case_sensitive = tk.BooleanVar(value=False)
        self.whole_words = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Match whole words", variable=self.whole_words).grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Results display
        results_frame = ttk.LabelFrame(main_frame, text="Search Results")
        results_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        
        # Results info
        self.results_label = ttk.Label(results_frame, text="No search performed yet")
        self.results_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        # Results listbox
        listbox_frame = ttk.Frame(results_frame)
        listbox_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)
        
        self.results_listbox = tk.Listbox(listbox_frame)
        results_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_listbox.grid(row=0, column=0, sticky='nsew')
        results_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Bind listbox selection
        self.results_listbox.bind('<<ListboxSelect>>', self._on_result_select)
        self.results_listbox.bind('<Double-Button-1>', self._on_result_double_click)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=10)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        buttons_frame.grid_columnconfigure(3, weight=1)
        
        ttk.Button(buttons_frame, text="Find All", command=self._search).grid(row=0, column=0, padx=2, sticky='ew')
        ttk.Button(buttons_frame, text="Find Next", command=self._find_next).grid(row=0, column=1, padx=2, sticky='ew')
        ttk.Button(buttons_frame, text="Find Previous", command=self._find_previous).grid(row=0, column=2, padx=2, sticky='ew')
        ttk.Button(buttons_frame, text="Close", command=self._close).grid(row=0, column=3, padx=2, sticky='ew')
        # Bind F3 / Shift+F3 for quick navigation
        self.dialog.bind('<F3>', lambda e: self._find_next())
        self.dialog.bind('<Shift-F3>', lambda e: self._find_previous())

        # Configure grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        
        # Store search results
        self.search_results = []
        self.current_index = -1
        
    def _search(self):
        """Perform search and display results."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.results_label.config(text="Please enter a search term")
            return
            
        options = {
            'search_names': self.search_names.get(),
            'search_content': self.search_content.get(),
            'case_sensitive': self.case_sensitive.get(),
            'whole_words': self.whole_words.get()
        }
        
        if not options['search_names'] and not options['search_content']:
            self.results_label.config(text="Please select at least one search scope (names or content)")
            return
            
        # Call the search callback
        self.search_results = self.search_callback(search_term, options)
        self.current_index = -1
        
        # Display results
        self.results_listbox.delete(0, tk.END)
        
        if not self.search_results:
            self.results_label.config(text="No matches found")
        else:
            self.results_label.config(text=f"Found {len(self.search_results)} matches")
            for i, result in enumerate(self.search_results):
                node_path = self._get_node_path(result['node'])
                if result['type'] == 'name':
                    display_text = f"[Name] {node_path}"
                else:
                    display_text = f"[Content] {node_path}"
                self.results_listbox.insert(tk.END, display_text)
    
    def _get_node_path(self, node):
        """Get the full path to a node."""
        path = []
        current = node
        while current:
            path.append(current.name)
            current = current.parent
        return " > ".join(reversed(path))
    
    def _on_result_select(self, event):
        """Handle result selection."""
        selection = self.results_listbox.curselection()
        if selection:
            self.current_index = selection[0]
    
    def _on_result_double_click(self, event):
        """Handle double-click on result to navigate."""
        selection = self.results_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self._navigate_to_current()
    
    def _find_next(self):
        """Navigate to next search result."""
        if not self.search_results:
            return
            
        self.current_index = (self.current_index + 1) % len(self.search_results)
        self.results_listbox.selection_clear(0, tk.END)
        self.results_listbox.selection_set(self.current_index)
        self.results_listbox.see(self.current_index)
        self._navigate_to_current()
        
        # Also trigger the main UI's find next method if available
        if self.find_next_callback:
            self.find_next_callback()
    
    def _find_previous(self):
        """Navigate to previous search result."""
        if not self.search_results:
            return
            
        self.current_index = (self.current_index - 1) % len(self.search_results)
        self.results_listbox.selection_clear(0, tk.END)
        self.results_listbox.selection_set(self.current_index)
        self.results_listbox.see(self.current_index)
        self._navigate_to_current()
    
    def _navigate_to_current(self):
        """Navigate to the current search result."""
        if 0 <= self.current_index < len(self.search_results):
            result = self.search_results[self.current_index]
            # Use the navigate callback if provided, otherwise fall back to parent method
            if self.navigate_callback:
                self.navigate_callback(result)
            elif hasattr(self.parent, '_navigate_to_search_result'):
                self.parent._navigate_to_search_result(result)
    
    def _close(self):
        """Close the search dialog."""
        self.dialog.destroy()


class ReplaceDialog:
    """Dialog for find and replace functionality."""
    
    def __init__(self, parent, search_callback, replace_callback, navigate_callback=None, find_next_callback=None):
        self.parent = parent
        self.search_callback = search_callback
        self.replace_callback = replace_callback
        self.navigate_callback = navigate_callback
        self.find_next_callback = find_next_callback
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Find and Replace")
        self.dialog.geometry("450x400")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"450x400+{x}+{y}")
        
        self._setup_ui()
        
        # Focus and bind keys
        self.find_entry.focus()
        self.dialog.bind('<Return>', lambda e: self._search())
        self.dialog.bind('<Escape>', lambda e: self._close())
        
    def _setup_ui(self):
        """Setup the replace dialog UI."""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Find and replace entries
        ttk.Label(main_frame, text="Find what:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.find_entry = ttk.Entry(main_frame, width=40)
        self.find_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=(0, 5))
        
        ttk.Label(main_frame, text="Replace with:").grid(row=1, column=0, sticky='w', pady=(0, 10))
        self.replace_entry = ttk.Entry(main_frame, width=40)
        self.replace_entry.grid(row=1, column=1, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Search options frame (same as search dialog)
        options_frame = ttk.LabelFrame(main_frame, text="Search Options")
        options_frame.grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Search scope
        self.search_names = tk.BooleanVar(value=True)
        self.search_content = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Search node names", variable=self.search_names).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Search content", variable=self.search_content).grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Match options
        self.case_sensitive = tk.BooleanVar(value=False)
        self.whole_words = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Match whole words", variable=self.whole_words).grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Results display (same as search dialog but with replace buttons)
        results_frame = ttk.LabelFrame(main_frame, text="Search Results")
        results_frame.grid(row=3, column=0, columnspan=3, sticky='nsew', pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        
        # Results info
        self.results_label = ttk.Label(results_frame, text="No search performed yet")
        self.results_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        # Results listbox
        listbox_frame = ttk.Frame(results_frame)
        listbox_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)
        
        self.results_listbox = tk.Listbox(listbox_frame)
        results_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_listbox.grid(row=0, column=0, sticky='nsew')
        results_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Bind listbox selection
        self.results_listbox.bind('<<ListboxSelect>>', self._on_result_select)
        self.results_listbox.bind('<Double-Button-1>', self._on_result_double_click)
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=10)
        
        # First row of buttons
        buttons_frame1 = ttk.Frame(buttons_frame)
        buttons_frame1.pack(fill=tk.X, pady=(0, 5))
        buttons_frame1.grid_columnconfigure(0, weight=1)
        buttons_frame1.grid_columnconfigure(1, weight=1)
        buttons_frame1.grid_columnconfigure(2, weight=1)
        
        ttk.Button(buttons_frame1, text="Find All", command=self._search).grid(row=0, column=0, padx=2, sticky='ew')
        ttk.Button(buttons_frame1, text="Find Next", command=self._find_next).grid(row=0, column=1, padx=2, sticky='ew')
        ttk.Button(buttons_frame1, text="Find Previous", command=self._find_previous).grid(row=0, column=2, padx=2, sticky='ew')

        # Bind F3 / Shift+F3 for quick navigation
        self.dialog.bind('<F3>', lambda e: self._find_next())
        self.dialog.bind('<Shift-F3>', lambda e: self._find_previous())


        # Second row of buttons
        buttons_frame2 = ttk.Frame(buttons_frame)
        buttons_frame2.pack(fill=tk.X, pady=(0, 5))
        buttons_frame2.grid_columnconfigure(0, weight=1)
        buttons_frame2.grid_columnconfigure(1, weight=1)
        buttons_frame2.grid_columnconfigure(2, weight=1)
        
        ttk.Button(buttons_frame2, text="Replace", command=self._replace_current).grid(row=0, column=0, padx=2, sticky='ew')
        ttk.Button(buttons_frame2, text="Replace All", command=self._replace_all).grid(row=0, column=1, padx=2, sticky='ew')
        ttk.Button(buttons_frame2, text="Close", command=self._close).grid(row=0, column=2, padx=2, sticky='ew')
        
        # Configure grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        
        # Store search results
        self.search_results = []
        self.current_index = -1
        
    def _search(self):
        """Perform search and display results."""
        search_term = self.find_entry.get().strip()
        if not search_term:
            self.results_label.config(text="Please enter a search term")
            return
            
        options = {
            'search_names': self.search_names.get(),
            'search_content': self.search_content.get(),
            'case_sensitive': self.case_sensitive.get(),
            'whole_words': self.whole_words.get()
        }
        
        if not options['search_names'] and not options['search_content']:
            self.results_label.config(text="Please select at least one search scope (names or content)")
            return
            
        # Call the search callback
        self.search_results = self.search_callback(search_term, options)
        self.current_index = -1
        
        # Display results
        self.results_listbox.delete(0, tk.END)
        
        if not self.search_results:
            self.results_label.config(text="No matches found")
        else:
            self.results_label.config(text=f"Found {len(self.search_results)} matches")
            for i, result in enumerate(self.search_results):
                node_path = self._get_node_path(result['node'])
                if result['type'] == 'name':
                    display_text = f"[Name] {node_path}"
                else:
                    display_text = f"[Content] {node_path}"
                self.results_listbox.insert(tk.END, display_text)
    
    def _get_node_path(self, node):
        """Get the full path to a node."""
        path = []
        current = node
        while current:
            path.append(current.name)
            current = current.parent
        return " > ".join(reversed(path))
    
    def _on_result_select(self, event):
        """Handle result selection."""
        selection = self.results_listbox.curselection()
        if selection:
            self.current_index = selection[0]
    
    def _on_result_double_click(self, event):
        """Handle double-click on result to navigate."""
        selection = self.results_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self._navigate_to_current()
    
    def _find_next(self):
        """Navigate to next search result."""
        if not self.search_results:
            return
            
        self.current_index = (self.current_index + 1) % len(self.search_results)
        self.results_listbox.selection_clear(0, tk.END)
        self.results_listbox.selection_set(self.current_index)
        self.results_listbox.see(self.current_index)
        self._navigate_to_current()
    
    def _find_previous(self):
        """Navigate to previous search result."""
        if not self.search_results:
            return
            
        self.current_index = (self.current_index - 1) % len(self.search_results)
        self.results_listbox.selection_clear(0, tk.END)
        self.results_listbox.selection_set(self.current_index)
        self.results_listbox.see(self.current_index)
        self._navigate_to_current()
        
        # Also trigger the main UI's find next method if available
        if self.find_next_callback:
            self.find_next_callback()
    
    def _navigate_to_current(self):
        """Navigate to the current search result."""
        if 0 <= self.current_index < len(self.search_results):
            result = self.search_results[self.current_index]
            # Use the navigate callback if provided, otherwise fall back to parent method
            if self.navigate_callback:
                self.navigate_callback(result)
            elif hasattr(self.parent, '_navigate_to_search_result'):
                self.parent._navigate_to_search_result(result)
    
    def _replace_current(self):
        """Replace the current selected result."""
        if 0 <= self.current_index < len(self.search_results):
            find_text = self.find_entry.get()
            replace_text = self.replace_entry.get()
            result = self.search_results[self.current_index]
            
            options = {
                'case_sensitive': self.case_sensitive.get(),
                'whole_words': self.whole_words.get()
            }
            
            success = self.replace_callback(result, find_text, replace_text, options)
            if success:
                # Remove this result from the list and refresh display
                self.search_results.pop(self.current_index)
                self.results_listbox.delete(self.current_index)
                
                # Adjust current index
                if self.current_index >= len(self.search_results):
                    self.current_index = len(self.search_results) - 1
                
                # Update results count
                if self.search_results:
                    self.results_label.config(text=f"Found {len(self.search_results)} matches")
                    if self.current_index >= 0:
                        self.results_listbox.selection_set(self.current_index)
                else:
                    self.results_label.config(text="No matches remaining")
    
    def _replace_all(self):
        """Replace all search results."""
        if not self.search_results:
            return
            
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        options = {
            'case_sensitive': self.case_sensitive.get(),
            'whole_words': self.whole_words.get()
        }
        
        replaced_count = 0
        # Work backwards to avoid index issues
        for i in range(len(self.search_results) - 1, -1, -1):
            result = self.search_results[i]
            success = self.replace_callback(result, find_text, replace_text, options)
            if success:
                replaced_count += 1
        
        # Clear results and update display
        self.search_results.clear()
        self.results_listbox.delete(0, tk.END)
        self.current_index = -1
        self.results_label.config(text=f"Replaced {replaced_count} matches")
    
    def _close(self):
        """Close the replace dialog."""
        self.dialog.destroy()


def main():
    """Main function to run the FlexTree UI application."""
    # Create and run UI
    ui = FlexTreeUI(None)
    ui.run()


if __name__ == "__main__":
    main()