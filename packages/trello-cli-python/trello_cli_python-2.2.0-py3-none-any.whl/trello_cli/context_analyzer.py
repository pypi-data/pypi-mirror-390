"""
Context analyzer for card movements - Uses Claude AI to understand card context
and provide intelligent analysis about what's happening
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


def _build_card_context(card) -> Dict[str, Any]:
    """
    Extract comprehensive context from a card for analysis.
    Includes title, description, checklist progress, labels, due dates, etc.
    """
    context = {
        "title": card.name,
        "description": card.desc if hasattr(card, 'desc') else "",
        "card_id": card.id,
        "url": card.url if hasattr(card, 'url') else "",
    }

    # Due date
    if hasattr(card, 'due') and card.due:
        try:
            due_date = card.due
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date)
            context["due_date"] = due_date.strftime("%Y-%m-%d")
            # Check if overdue
            if due_date < datetime.now():
                context["overdue"] = True
        except:
            pass

    # Labels
    if hasattr(card, 'labels') and card.labels:
        context["labels"] = [
            {
                "name": label.name if hasattr(label, 'name') else label.get('name', ''),
                "color": label.color if hasattr(label, 'color') else label.get('color', '')
            }
            for label in card.labels
        ]

    # Checklist progress
    if hasattr(card, 'checklists') and card.checklists:
        checklists = []
        for checklist in card.checklists:
            # Handle both dict and object formats
            if isinstance(checklist, dict):
                checklist_name = checklist.get('name', '')
                items = checklist.get('items', [])
            else:
                checklist_name = checklist.name if hasattr(checklist, 'name') else ''
                items = checklist.items if hasattr(checklist, 'items') else []

            if items:
                completed = 0
                for item in items:
                    if isinstance(item, dict):
                        state = item.get('state', '')
                    else:
                        state = item.state if hasattr(item, 'state') else ''
                    if state == 'complete':
                        completed += 1

                checklists.append({
                    "name": checklist_name,
                    "total": len(items),
                    "completed": completed,
                    "percentage": int((completed / len(items) * 100)) if items else 0
                })

        if checklists:
            context["checklists"] = checklists

    # Comment count
    if hasattr(card, 'comments'):
        context["comment_count"] = len(card.comments) if card.comments else 0

    return context


def analyze_card_movement(card, source_list_name: str, target_list_name: str) -> str:
    """
    Analyze a card movement and provide intelligent context.
    Uses Claude AI if API key is available, otherwise provides basic analysis.
    """
    context = _build_card_context(card)

    # Try to use Claude AI if available
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key.strip():
        return _get_claude_analysis(context, source_list_name, target_list_name, api_key)
    else:
        return _get_basic_analysis(context, source_list_name, target_list_name)


def _get_basic_analysis(context: Dict[str, Any], source_list: str, target_list: str) -> str:
    """
    Provide basic context analysis without Claude AI.
    """
    analysis = f"\n📊 CONTEXT ANALYSIS\n"
    analysis += f"{'─' * 60}\n"

    # Summarize what's in the card
    if context.get("description"):
        desc_preview = context["description"][:100] + "..." if len(context["description"]) > 100 else context["description"]
        analysis += f"📝 Description: {desc_preview}\n"

    # Labels context
    if context.get("labels"):
        label_str = ", ".join([f"{label['name']}" for label in context["labels"]])
        analysis += f"🏷️  Labels: {label_str}\n"

    # Due date context
    if context.get("due_date"):
        status = "🔴 OVERDUE" if context.get("overdue") else "📅 Due"
        analysis += f"{status}: {context['due_date']}\n"

    # Checklist progress
    if context.get("checklists"):
        analysis += f"\n✓ Checklist Progress:\n"
        for checklist in context["checklists"]:
            progress_bar = "█" * (checklist["percentage"] // 10) + "░" * (10 - checklist["percentage"] // 10)
            analysis += f"  • {checklist['name']}: [{progress_bar}] {checklist['completed']}/{checklist['total']}\n"

    # Transition analysis
    analysis += f"\n🔄 Movement: {source_list} → {target_list}\n"
    analysis += f"{'─' * 60}\n"

    return analysis


def _get_claude_analysis(context: Dict[str, Any], source_list: str, target_list: str, api_key: str) -> str:
    """
    Use Claude AI to provide intelligent contextual analysis of the card movement.
    """
    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        # Build prompt for Claude to understand the context
        prompt = f"""You are a agile coach AI analyzing a Trello card movement. Provide a brief, insightful analysis.

CARD DETAILS:
Title: {context['title']}
Description: {context.get('description', 'No description')}
Labels: {', '.join([l.get('name', l.get('color', '')) for l in context.get('labels', [])]) or 'None'}
Due Date: {context.get('due_date', 'No due date')}
Checklist Progress: {json.dumps(context.get('checklists', []))}

MOVEMENT:
From: {source_list}
To: {target_list}

Provide a 2-3 sentence analysis about:
1. What this card is about (based on title and description)
2. Why this movement is significant
3. Any concerns based on the context (e.g., overdue items, incomplete checklists)

Be conversational and insightful. Keep it concise."""

        message = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        analysis_text = message.content[0].text if message.content else ""

        # Format the response with visual indicators
        return f"\n💡 CLAUDE AI ANALYSIS\n{'─' * 60}\n{analysis_text}\n{'─' * 60}\n"

    except Exception as e:
        # Fallback to basic analysis if Claude fails
        import traceback
        # Uncomment for debugging: print(f"Claude API error: {e}\n{traceback.format_exc()}")
        return _get_basic_analysis(context, source_list, target_list)


def get_movement_opinion(card, source_list_name: str, target_list_name: str) -> str:
    """
    Main entry point: Get contextual opinion about a card movement.
    """
    return analyze_card_movement(card, source_list_name, target_list_name)
