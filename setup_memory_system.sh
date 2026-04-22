#!/bin/bash
# Memory system setup and UI launcher

echo "🧠 NOVA AI - Memory System Setup"
echo "=================================="

# Check if streamlit is installed
if ! python -m pip show streamlit > /dev/null 2>&1; then
    echo "📦 Installing Streamlit..."
    python -m pip install streamlit pandas
fi

echo ""
echo "✅ Memory system is ready!"
echo ""
echo "Available commands:"
echo "  1. Start Memory Dashboard UI:"
echo "     streamlit run memory_ui.py"
echo ""
echo "  2. Access memory via AI tools in nova.py:"
echo "     - save_short_term_memory(content, tags)"
echo "     - save_long_term_memory(content, tags, importance)"
echo "     - save_quick_note(content, tags)"
echo "     - fetch_all_memories()"
echo "     - search_memories(query)"
echo "     - update_memory(memory_id, ...)"
echo "     - delete_memory(memory_id)"
echo ""
echo "📊 Memory system features:"
echo "  - Short-term: Session-specific, 1-7 days"
echo "  - Long-term: Persistent, indefinite"
echo "  - Quick Notes: Reminders, 1-3 days"
echo "  - Full-text search support"
echo "  - Importance levels (1-5) for long-term"
echo "  - Tag organization"
echo "  - SQLite backend (memories.db)"
