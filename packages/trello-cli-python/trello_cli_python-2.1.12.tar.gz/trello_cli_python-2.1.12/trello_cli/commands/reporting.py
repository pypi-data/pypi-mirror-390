"""
Reporting Commands - Real board insights with Claude AI
Commands: report, feedback, score

These extract daemon logic and present insights via Claude for pedagogical depth.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import os

# Claude SDK integration (optional - graceful degradation if not available)
try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False


class BoardReporter:
    """Extract and report on board state using daemon analysis logic."""

    def __init__(self, trello_client):
        self.trello = trello_client

    def get_board_report(self, board_id: str) -> str:
        """
        Generate comprehensive board report.
        Shows: duplicates, orphaned tasks, frozen progress, missing scope.
        """
        board = self.trello.get_board(board_id)
        lists = self.trello.get_lists(board_id)
        cards = []

        # Collect all cards
        for list_obj in lists:
            cards.extend(self.trello.get_cards(list_obj.id))

        # Analyze
        report = self._build_report(board, lists, cards)
        return report

    def _build_report(self, board, lists, cards) -> str:
        """Build structured report."""
        output = []
        output.append("")
        output.append("=" * 80)
        output.append(f"📊 BOARD REPORT: {board.name}")
        output.append("=" * 80)
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")

        # Section 1: Duplicates
        duplicates = self._find_duplicates(cards)
        output.append("🔍 DUPLICATED TASKS")
        output.append("-" * 80)
        if duplicates:
            for dup_group in duplicates:
                output.append(f"Found {len(dup_group)} similar tasks:")
                for card in dup_group:
                    output.append(f"  • {card.name} (in {card.list_id})")
            output.append("")
        else:
            output.append("✅ No duplicates found")
            output.append("")

        # Section 2: Orphaned tasks (no phase, no scope)
        orphaned = self._find_orphaned_tasks(cards)
        output.append("⚠️  ORPHANED TASKS (No phase/scope definition)")
        output.append("-" * 80)
        if orphaned:
            output.append(f"Found {len(orphaned)} tasks without context:")
            for card in orphaned[:10]:  # Show first 10
                output.append(f"  • {card.name}")
                if not card.description:
                    output.append(f"    └─ No description")
                if not self._has_checklist(card):
                    output.append(f"    └─ No subtasks")
            if len(orphaned) > 10:
                output.append(f"  ... and {len(orphaned) - 10} more")
            output.append("")
        else:
            output.append("✅ All tasks have proper scope")
            output.append("")

        # Section 3: Frozen progress (in same list too long)
        frozen = self._find_frozen_cards(cards)
        output.append("❄️  FROZEN PROGRESS (>7 days in same list)")
        output.append("-" * 80)
        if frozen:
            output.append(f"Found {len(frozen)} stalled tasks:")
            for card, days in frozen[:10]:
                output.append(f"  • {card.name} (stuck {days} days)")
            if len(frozen) > 10:
                output.append(f"  ... and {len(frozen) - 10} more")
            output.append("")
        else:
            output.append("✅ All tasks moving regularly")
            output.append("")

        # Section 4: Fake Done (FRAUD DETECTION)
        fake_done = self._find_fake_done(cards)
        output.append("🚫 FAKE COMPLETION (Fraud Detection)")
        output.append("-" * 80)
        if fake_done:
            output.append(f"CRÍTICO: {len(fake_done)} tarjetas en 'Done' con checklists incompletos:")
            for card, total, completed in fake_done[:10]:
                output.append(f"  • {card.name}")
                output.append(f"    └─ {completed}/{total} items completados ({completed*100//total}%)")
            if len(fake_done) > 10:
                output.append(f"  ... and {len(fake_done) - 10} more")
            output.append("")
        else:
            output.append("✅ No fake completion detected")
            output.append("")

        # Section 5: Missing PRs/Commits
        missing_evidence = self._find_missing_evidence(cards)
        output.append("📝 MISSING EXECUTION EVIDENCE")
        output.append("-" * 80)
        if missing_evidence:
            output.append(f"Found {len(missing_evidence)} tasks without PR/commit:")
            for card in missing_evidence[:10]:
                status = "In Progress" if "in_progress" in str(card.list_id).lower() else "Other"
                output.append(f"  • {card.name} ({status})")
                output.append(f"    └─ No PR/commit referenced in description")
            if len(missing_evidence) > 10:
                output.append(f"  ... and {len(missing_evidence) - 10} more")
            output.append("")
        else:
            output.append("✅ All tasks have execution evidence")
            output.append("")

        # Summary stats
        output.append("=" * 80)
        output.append("📈 SUMMARY")
        output.append("=" * 80)
        output.append(f"Total cards: {len(cards)}")
        output.append(f"Total lists: {len([l for l in self.trello.get_lists(board.id)])}")
        output.append(f"Duplicates: {sum(len(g) for g in duplicates)} cards")
        output.append(f"Orphaned: {len(orphaned)} cards")
        output.append(f"Frozen: {len(frozen)} cards")
        output.append(f"🚫 Fake Done: {len(fake_done)} cards (FRAUD)")
        output.append(f"Missing evidence: {len(missing_evidence)} cards")
        output.append("")
        output.append("=" * 80)

        return "\n".join(output)

    def get_board_feedback(self, board_id: str, use_claude: bool = True) -> str:
        """
        Qualitative feedback on board health.
        Uses Claude SDK if available for pedagogical depth, falls back to heuristics.
        """
        board = self.trello.get_board(board_id)
        lists = self.trello.get_lists(board_id)
        cards = []

        for list_obj in lists:
            cards.extend(self.trello.get_cards(list_obj.id))

        # Extract raw analysis
        score, issues = self._assess_board(cards)
        fake = self._find_fake_done(cards)
        orphaned = self._find_orphaned_tasks(cards)
        frozen = self._find_frozen_cards(cards)

        # Try to use Claude if available and requested
        if use_claude and CLAUDE_AVAILABLE:
            return self._get_claude_feedback(board, score, issues, fake, orphaned, frozen, cards)
        else:
            feedback = self._build_feedback(board, lists, cards)
            return feedback

    def _get_claude_feedback(self, board, score: int, issues: List[str], fake, orphaned, frozen, cards) -> str:
        """
        Use Claude SDK to generate intelligent, pedagogical feedback.
        Falls back gracefully if API key is missing or API fails.
        """
        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                return self._build_feedback_fallback(board, score, issues)

            client = Anthropic(api_key=api_key)

            # Build a detailed analysis prompt for Claude
            analysis = f"""
BOARD ANALYSIS: {board.name}

METRICS:
- Health Score: {score}/100
- Total Cards: {len(cards)}
- Fake Done (FRAUD): {len(fake)}
- Orphaned Tasks: {len(orphaned)}
- Frozen Tasks: {len(frozen)}

CRITICAL ISSUES:
{chr(10).join(f"- {issue}" for issue in issues)}

FAKE COMPLETIONS (items not done but card marked Done):
{chr(10).join(f"- {card.name}: {completed}/{total} items done ({completed*100//total}%)"
  for card, total, completed in fake[:5])}

ORPHANED TASKS (no description, no subtasks):
{chr(10).join(f"- {card.name}" for card in orphaned[:5])}

FROZEN TASKS (>7 days without movement):
{chr(10).join(f"- {card.name} ({days} days stuck)" for card, days in frozen[:5])}

Based on this analysis, provide:
1. Current state assessment (1 sentence)
2. Top 3 most critical problems (numbered, concise)
3. Specific next steps (3 actionable items)
4. One insight about the team's workflow

Format: Professional but conversational. No jargon. Assume this is for an AI user who understands code.
"""

            response = client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": analysis
                    }
                ]
            )

            feedback = response.content[0].text

            output = []
            output.append("")
            output.append("=" * 80)
            output.append("🧠 CLAUDE AI FEEDBACK")
            output.append("=" * 80)
            output.append("")
            output.append(feedback)
            output.append("")
            output.append("=" * 80)
            output.append("")

            return "\n".join(output)

        except Exception as e:
            # Graceful degradation: fall back to heuristic feedback
            return self._build_feedback_fallback(board, score, issues)

    def _build_feedback_fallback(self, board, score: int, issues: List[str]) -> str:
        """Fallback heuristic feedback if Claude is not available."""
        output = []
        output.append("")
        output.append("⚠️  Claude SDK not available (using heuristic feedback)")
        output.append("=" * 80)

        # Health status
        if score >= 80:
            status = "🟢 HEALTHY"
            assessment = "Board structure is solid. Tasks are well-defined."
        elif score >= 60:
            status = "🟡 FRAGILE"
            assessment = "Board has organization but needs attention in some areas."
        elif score >= 40:
            status = "🔴 CHAOTIC"
            assessment = "Board lacks structure. Risk of confusion and duplicated work."
        else:
            status = "🚫 BROKEN"
            assessment = "Board needs immediate reorganization."

        output.append(f"STATUS: {status}")
        output.append(f"HEALTH SCORE: {score}/100")
        output.append("")
        output.append(f"ASSESSMENT: {assessment}")
        output.append("")

        if issues:
            output.append("🚨 CRITICAL ISSUES:")
            output.append("-" * 80)
            for issue in issues:
                output.append(f"  • {issue}")
            output.append("")

        output.append("=" * 80)
        output.append("")

        return "\n".join(output)

    def _build_feedback(self, board, lists, cards) -> str:
        """Build pedagogical feedback."""
        output = []
        output.append("")
        output.append("🧠 BOARD ANALYSIS & FEEDBACK")
        output.append("=" * 80)
        output.append("")

        # Assess board health
        score, issues = self._assess_board(cards)

        # Health status
        if score >= 80:
            status = "🟢 HEALTHY"
            assessment = "Board structure is solid. Tasks are well-defined."
        elif score >= 60:
            status = "🟡 FRAGILE"
            assessment = "Board has organization but needs attention in some areas."
        elif score >= 40:
            status = "🔴 CHAOTIC"
            assessment = "Board lacks structure. Risk of confusion and duplicated work."
        else:
            status = "🚫 BROKEN"
            assessment = "Board needs immediate reorganization."

        output.append(f"STATUS: {status}")
        output.append(f"HEALTH SCORE: {score}/100")
        output.append("")
        output.append(f"ASSESSMENT: {assessment}")
        output.append("")

        # Issues
        if issues:
            output.append("🚨 CRITICAL ISSUES:")
            output.append("-" * 80)
            for issue in issues[:5]:
                output.append(f"  • {issue}")
            if len(issues) > 5:
                output.append(f"  ... and {len(issues) - 5} more issues")
            output.append("")

        # Suggestions
        suggestions = self._generate_suggestions(score, cards)
        if suggestions:
            output.append("💡 RECOMMENDED ACTIONS:")
            output.append("-" * 80)
            for i, suggestion in enumerate(suggestions[:3], 1):
                output.append(f"  {i}. {suggestion}")
            output.append("")

        output.append("=" * 80)
        output.append("")

        return "\n".join(output)

    def get_board_score(self, board_id: str) -> str:
        """
        Integrity score of board based on 5 axes (from daemon analyzer).
        0-100 scale.
        """
        board = self.trello.get_board(board_id)
        lists = self.trello.get_lists(board_id)
        cards = []

        for list_obj in lists:
            cards.extend(self.trello.get_cards(list_obj.id))

        score, breakdown = self._calculate_score(board, lists, cards)
        return self._format_score(score, breakdown)

    def _calculate_score(self, board, lists, cards) -> Tuple[int, Dict]:
        """
        Calculate score based on 5 axes:
        1. Structure (25%) - Lists organized, clear states
        2. Clarity (20%) - Cards have descriptions, scope defined
        3. Progress (20%) - Cards moving, not frozen
        4. Evidence (20%) - PRs, commits, deployments referenced
        5. Health (15%) - No duplicates, no orphans, no chaos
        """
        scores = {}

        # Axis 1: Structure
        structure_score = self._score_structure(lists, cards)
        scores["structure"] = (structure_score, 0.25)

        # Axis 2: Clarity
        clarity_score = self._score_clarity(cards)
        scores["clarity"] = (clarity_score, 0.20)

        # Axis 3: Progress
        progress_score = self._score_progress(cards)
        scores["progress"] = (progress_score, 0.20)

        # Axis 4: Evidence
        evidence_score = self._score_evidence(cards)
        scores["evidence"] = (evidence_score, 0.20)

        # Axis 5: Health
        health_score = self._score_health(cards)
        scores["health"] = (health_score, 0.15)

        # Calculate weighted score
        total_score = sum(score * weight for score, weight in scores.values())

        return int(total_score), scores

    def _format_score(self, score: int, breakdown: Dict) -> str:
        """Format score for display."""
        output = []
        output.append("")
        output.append("=" * 80)
        output.append("📊 BOARD INTEGRITY SCORE")
        output.append("=" * 80)
        output.append("")

        # Overall score
        if score >= 80:
            level = "EXCELLENT"
            icon = "🟢"
        elif score >= 60:
            level = "GOOD"
            icon = "🟡"
        elif score >= 40:
            level = "FAIR"
            icon = "🟠"
        else:
            level = "POOR"
            icon = "🔴"

        output.append(f"Overall Score: {score}/100 [{icon} {level}]")
        output.append("")

        # Breakdown
        output.append("Breakdown by Axis:")
        output.append("-" * 80)

        axis_names = {
            "structure": "Structure (Lists, States)",
            "clarity": "Clarity (Descriptions, Scope)",
            "progress": "Progress (Movement, No Frozen)",
            "evidence": "Evidence (PRs, Commits, Deploys)",
            "health": "Health (No Duplicates, No Orphans)",
        }

        for axis, name in axis_names.items():
            if axis in breakdown:
                score_val, weight = breakdown[axis]
                bar = "█" * (score_val // 10) + "░" * (10 - score_val // 10)
                output.append(f"  {name}")
                output.append(f"    {bar} {score_val}/100 ({weight*100:.0f}% weight)")

        output.append("")
        output.append("=" * 80)
        output.append("")

        return "\n".join(output)

    # Helper methods for analysis
    def _find_duplicates(self, cards) -> List[List]:
        """Find similar cards (simplified: same first words)."""
        groups = {}
        for card in cards:
            # Simple token matching
            tokens = card.name.lower().split()[:2]  # First 2 words
            key = " ".join(tokens)

            if len(key) > 5:  # Skip short names
                if key not in groups:
                    groups[key] = []
                groups[key].append(card)

        # Return only groups with 2+ cards
        return [group for group in groups.values() if len(group) >= 2]

    def _find_orphaned_tasks(self, cards) -> List:
        """Find tasks without description or subtasks."""
        orphaned = []
        for card in cards:
            has_desc = card.description and len(card.description) > 20
            has_checklist = self._has_checklist(card)

            if not has_desc and not has_checklist:
                orphaned.append(card)

        return orphaned

    def _get_checklist_progress(self, card) -> tuple:
        """
        Get checklist progress for a card.
        Returns: (total_items, completed_items, completion_rate)
        """
        total = 0
        completed = 0

        if hasattr(card, 'checklists') and card.checklists:
            for checklist in card.checklists:
                items = checklist.get('items', [])
                for item in items:
                    total += 1
                    if item.get('state') == 'complete':
                        completed += 1

        if total == 0:
            return 0, 0, 0.0

        return total, completed, completed / total

    def _find_frozen_cards(self, cards) -> List[Tuple]:
        """Find cards stuck in same list >7 days."""
        frozen = []
        now = datetime.now()
        threshold = now - timedelta(days=7)

        for card in cards:
            # Check if card was created/moved before threshold
            if hasattr(card, 'dateLastActivity') and card.dateLastActivity:
                try:
                    last_activity = datetime.fromisoformat(card.dateLastActivity)
                    days_frozen = (now - last_activity).days

                    if days_frozen > 7:
                        frozen.append((card, days_frozen))
                except (ValueError, TypeError):
                    # Skip cards with invalid date format
                    pass

        return sorted(frozen, key=lambda x: x[1], reverse=True)

    def _find_missing_evidence(self, cards) -> List:
        """Find cards without PR/commit/deployment reference."""
        missing = []
        for card in cards:
            desc = (card.description or "").lower()

            has_pr = "pr" in desc or "pull" in desc
            has_commit = "commit" in desc or "merge" in desc
            has_deploy = "deploy" in desc or "release" in desc

            if not (has_pr or has_commit or has_deploy):
                # Only cards in execution states
                if hasattr(card, 'idList') and "progress" in str(card.idList).lower():
                    missing.append(card)

        return missing

    def _find_fake_done(self, cards) -> List[Tuple]:
        """
        Find cards in 'Done' list but with incomplete checklists.
        Fraud detection: tarjeta marcada como Done pero items sin completar.
        Returns: [(card, total_items, completed_items)]
        """
        fake = []
        done_keywords = ["done", "complete", "finished"]

        for card in cards:
            list_name = getattr(card, 'list_id', '')
            if not any(kw in str(list_name).lower() for kw in done_keywords):
                continue

            total, completed, rate = self._get_checklist_progress(card)

            # Si tiene checklists y no están 100% completos = FRAUDE
            if total > 0 and completed < total:
                fake.append((card, total, completed))

        return fake

    def _has_checklist(self, card) -> bool:
        """Check if card has checklists."""
        return hasattr(card, 'checklists') and len(card.checklists) > 0

    def _assess_board(self, cards) -> Tuple[int, List[str]]:
        """Quick assessment of board health."""
        issues = []
        score = 100

        # Check FAKE DONE first (most critical)
        fake = self._find_fake_done(cards)
        if fake:
            score -= 40
            issues.append(
                f"🚫 FRAUD: {len(fake)} tasks marked Done but checklists incomplete"
            )

        # Check duplicates
        dups = self._find_duplicates(cards)
        if dups:
            score -= 20
            issues.append(
                f"Found {sum(len(g) for g in dups)} duplicate/similar tasks"
            )

        # Check orphaned
        orphaned = self._find_orphaned_tasks(cards)
        if len(orphaned) > len(cards) * 0.3:
            score -= 25
            issues.append(
                f"{len(orphaned)} tasks lack description/scope definition"
            )

        # Check frozen
        frozen = self._find_frozen_cards(cards)
        if len(frozen) > len(cards) * 0.2:
            score -= 20
            issues.append(f"{len(frozen)} tasks stuck in same list >7 days")

        # Check evidence
        missing = self._find_missing_evidence(cards)
        if len(missing) > len(cards) * 0.3:
            score -= 15
            issues.append(f"{len(missing)} active tasks missing PR/commit references")

        return max(0, score), issues

    def _generate_suggestions(self, score: int, cards) -> List[str]:
        """Generate actionable suggestions."""
        suggestions = []

        if score < 40:
            suggestions.append("Consolidate and clarify task definitions")
            suggestions.append("Map out phases (MVP, R1, R2)")
            suggestions.append("Add descriptions to all cards")

        elif score < 60:
            suggestions.append("Review orphaned tasks and add context")
            suggestions.append("Merge duplicate cards")
            suggestions.append("Set deadlines for stalled tasks")

        else:
            suggestions.append("Review and consolidate completed phases")
            suggestions.append("Plan next release cycle")
            suggestions.append("Document lessons learned")

        return suggestions

    # Scoring helper methods
    def _score_structure(self, lists, cards) -> int:
        """Score based on list organization."""
        score = 100

        # Check if have standard states
        list_names = [l.name.lower() for l in lists]
        has_todo = any("todo" in n or "backlog" in n for n in list_names)
        has_inprogress = any("progress" in n or "doing" in n for n in list_names)
        has_done = any("done" in n or "complete" in n for n in list_names)

        if not (has_todo and has_inprogress and has_done):
            score -= 30

        if len(lists) < 2:
            score -= 20

        if len(lists) > 15:
            score -= 15  # Too many lists

        return max(0, score)

    def _score_clarity(self, cards) -> int:
        """Score based on card clarity."""
        score = 100
        described = 0

        for card in cards:
            if card.description and len(card.description) > 20:
                described += 1

        clarity_rate = described / max(1, len(cards))

        if clarity_rate < 0.5:
            score -= 50
        elif clarity_rate < 0.8:
            score -= 20

        return max(0, score)

    def _score_progress(self, cards) -> int:
        """Score based on task progress (including checklist items)."""
        frozen = self._find_frozen_cards(cards)
        score = 100

        if len(frozen) > len(cards) * 0.5:
            score -= 50
        elif len(frozen) > len(cards) * 0.2:
            score -= 25

        # Penalizar tarjetas "casi hechas" (>50% pero <100% checklists)
        almost_done = 0
        for card in cards:
            total, completed, rate = self._get_checklist_progress(card)
            if total > 0 and 0.5 < rate < 1.0:
                almost_done += 1

        if almost_done > len(cards) * 0.3:
            score -= 15

        return max(0, score)

    def _score_evidence(self, cards) -> int:
        """Score based on execution evidence."""
        missing = self._find_missing_evidence(cards)
        score = 100

        evidence_rate = 1 - (len(missing) / max(1, len(cards)))

        if evidence_rate < 0.5:
            score -= 50
        elif evidence_rate < 0.8:
            score -= 20

        return max(0, score)

    def _score_health(self, cards) -> int:
        """Score based on health (duplicates, orphans)."""
        dups = self._find_duplicates(cards)
        orphaned = self._find_orphaned_tasks(cards)

        score = 100

        dup_count = sum(len(g) for g in dups)
        if dup_count > 0:
            score -= min(30, dup_count * 5)

        orphan_rate = len(orphaned) / max(1, len(cards))
        if orphan_rate > 0.3:
            score -= 30
        elif orphan_rate > 0.1:
            score -= 15

        return max(0, score)
