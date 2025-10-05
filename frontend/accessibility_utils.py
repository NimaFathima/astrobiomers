"""
Accessibility utilities and ARIA label helpers
Provides functions to enhance accessibility across the application
"""

# Common ARIA labels for space biology research platform
ARIA_LABELS = {
    # Navigation
    "nav_home": "Navigate to home page",
    "nav_research": "Navigate to research papers page",
    "nav_knowledge_graph": "Navigate to interactive knowledge graph",
    "nav_ai_assistant": "Navigate to AI assistant chat",
    "nav_trends": "Navigate to research trends analysis",
    
    # Search
    "search_input": "Enter search query for papers or topics",
    "search_button": "Submit search query",
    "search_results": "Search results list",
    
    # Knowledge Graph
    "kg_canvas": "Interactive knowledge graph visualization. Use arrow keys to navigate nodes.",
    "kg_node": "Graph node representing entity or paper. Click to view details.",
    "kg_edge": "Graph edge representing relationship. Click to view supporting evidence.",
    "kg_zoom_in": "Zoom in to knowledge graph",
    "kg_zoom_out": "Zoom out from knowledge graph",
    "kg_reset": "Reset knowledge graph view",
    
    # AI Assistant
    "chat_input": "Type your question about space biology research",
    "chat_send": "Send question to AI assistant",
    "chat_message": "Chat message",
    "chat_examples": "Example questions you can ask",
    
    # Trends
    "timeline_chart": "Publication timeline chart showing papers per year",
    "emerging_topics_chart": "Bar chart of emerging research topics",
    "authors_table": "Table of top authors by publication count",
    
    # Evidence Modal
    "evidence_modal": "Evidence supporting this relationship",
    "evidence_papers": "List of research papers providing evidence",
    "evidence_close": "Close evidence modal",
    
    # General UI
    "loading": "Loading content, please wait",
    "error": "Error message",
    "close": "Close dialog or modal",
    "expand": "Expand section",
    "collapse": "Collapse section",
}


def get_aria_label(key: str, default: str = "") -> str:
    """
    Get ARIA label for a specific UI element
    
    Args:
        key: Key for the ARIA label
        default: Default label if key not found
        
    Returns:
        ARIA label string
    """
    return ARIA_LABELS.get(key, default)


# Keyboard shortcuts
KEYBOARD_SHORTCUTS = {
    "search": "/",
    "help": "?",
    "close_modal": "Escape",
    "submit_form": "Enter",
    "navigate_next": "Tab",
    "navigate_prev": "Shift+Tab",
}


def get_keyboard_shortcut(action: str) -> str:
    """Get keyboard shortcut for an action"""
    return KEYBOARD_SHORTCUTS.get(action, "")


# Screen reader announcements
def announce_for_sr(message: str) -> dict:
    """
    Create announcement for screen readers
    
    Args:
        message: Message to announce
        
    Returns:
        Dictionary with ARIA live region properties
    """
    return {
        "role": "status",
        "aria-live": "polite",
        "aria-atomic": "true",
        "message": message
    }
