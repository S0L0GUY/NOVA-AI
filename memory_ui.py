"""Memory Dashboard UI - Live view and management of AI memories."""

from datetime import datetime

import streamlit as st
from classes.memory import MemoryManager, MemoryType

st.set_page_config(page_title="Memory Dashboard", layout="wide")
st.title("🧠 AI Memory Dashboard")


# Initialize memory manager
@st.cache_resource
def get_memory_manager():
    return MemoryManager()


manager = get_memory_manager()

# Sidebar navigation
st.sidebar.title("Navigation")
tab = st.sidebar.radio(
    "Select View",
    ["Overview", "Short-Term Memories", "Long-Term Memories", "Quick Notes", "Search", "Statistics"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Add New Memory")
add_form = st.sidebar.form("add_memory")
mem_type = add_form.selectbox(
    "Memory Type",
    ["short_term", "long_term", "quick_note"],
)
mem_content = add_form.text_area("Content", height=100)
mem_tags = add_form.text_input("Tags (comma-separated)")
if mem_type == "long_term":
    mem_importance = add_form.slider("Importance", 1, 5, 1)
else:
    mem_importance = 1

if add_form.form_submit_button("➕ Save Memory"):
    tags = [t.strip() for t in mem_tags.split(",") if t.strip()]
    memory_type_map = {
        "short_term": MemoryType.SHORT_TERM,
        "long_term": MemoryType.LONG_TERM,
        "quick_note": MemoryType.QUICK_NOTE,
    }
    mem_id = manager.store_memory(mem_content, memory_type_map[mem_type], tags, mem_importance)
    st.sidebar.success(f"✅ Memory saved (ID: {mem_id})")
    st.rerun()


def display_memory(memory, col=None):
    """Display a single memory card."""
    container = col if col else st
    with container.container(border=True):
        row1, row2 = st.columns([3, 1])
        with row1:
            st.subheader(f"#{memory['id']} - {memory['type'].replace('_', ' ').title()}")
        with row2:
            if memory.get("importance"):
                st.caption(f"⭐ {'★' * memory['importance']}")

        st.write(memory["content"])

        if memory["tags"]:
            tag_str = " ".join([f"🏷️ {tag}" for tag in memory["tags"]])
            st.caption(tag_str)

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.caption(f"Created: {datetime.fromisoformat(memory['created_at']).strftime('%Y-%m-%d %H:%M')}")
        with col2:
            st.caption(f"Updated: {datetime.fromisoformat(memory['updated_at']).strftime('%Y-%m-%d %H:%M')}")
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{memory['id']}"):
                if manager.delete_memory(memory["id"]):
                    st.success("Deleted!")
                    st.rerun()


# Main content area
def render_memory_grid(memories, empty_message):
    """Render memories in a two-column responsive grid."""
    if memories:
        col1, col2 = st.columns(2)
        for idx, memory in enumerate(memories):
            with (col1 if idx % 2 == 0 else col2):
                display_memory(memory)
    else:
        st.info(empty_message)


def render_overview():
    st.header("Memory Overview")

    stats = manager.get_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Memories", stats["total"])
    with col2:
        st.metric("Short-Term", stats["by_type"].get("short_term", 0))
    with col3:
        st.metric("Long-Term", stats["by_type"].get("long_term", 0))
    with col4:
        st.metric("Quick Notes", stats["by_type"].get("quick_note", 0))

    st.markdown("---")
    st.subheader("📋 Recent Memories")

    all_memories = manager.fetch_all_memories()
    if all_memories:
        for memory in all_memories[:10]:  # Show 10 most recent
            display_memory(memory)
    else:
        st.info("No memories yet. Start by adding one!")


def render_short_term():
    st.header("📗 Short-Term Memories (1-7 days)")
    memories = manager.fetch_memories(MemoryType.SHORT_TERM)
    render_memory_grid(memories, "No short-term memories")


def render_long_term():
    st.header("📕 Long-Term Memories (Persistent)")
    memories = manager.fetch_memories(MemoryType.LONG_TERM, order_by="importance DESC, updated_at DESC")
    render_memory_grid(memories, "No long-term memories")


def render_quick_notes():
    st.header("📙 Quick Notes (1-3 days)")
    memories = manager.fetch_memories(MemoryType.QUICK_NOTE)
    render_memory_grid(memories, "No quick notes")


def render_search():
    st.header("🔍 Search Memories")
    query = st.text_input("Search by content or tags")

    if query:
        results = manager.search_memories(query)
        st.subheader(f"Found {len(results)} result(s)")

        if results:
            for memory in results:
                display_memory(memory)
        else:
            st.warning("No memories found matching your search")


def render_statistics():
    st.header("📊 Memory Statistics")

    stats = manager.get_stats()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Memories", stats["total"])
        st.metric("Short-Term Memories", stats["by_type"].get("short_term", 0))

    with col2:
        st.metric("Long-Term Memories", stats["by_type"].get("long_term", 0))
        st.metric("Quick Notes", stats["by_type"].get("quick_note", 0))

    st.markdown("---")
    st.subheader("📈 Memory Breakdown")

    all_memories = manager.fetch_all_memories()
    if all_memories:
        memory_data = {
            "Type": [m["type"] for m in all_memories],
            "Importance": [m.get("importance", 1) for m in all_memories],
        }

        import pandas as pd

        df = pd.DataFrame(memory_data)
        st.write(df.value_counts("Type"))

        st.markdown("---")
        st.subheader("📝 All Memories (JSON Export)")
        st.json(all_memories)


TAB_RENDERERS = {
    "Overview": render_overview,
    "Short-Term Memories": render_short_term,
    "Long-Term Memories": render_long_term,
    "Quick Notes": render_quick_notes,
    "Search": render_search,
    "Statistics": render_statistics,
}

render_tab = TAB_RENDERERS.get(tab)
if render_tab:
    render_tab()
else:
    st.error("Unknown view selected.")
