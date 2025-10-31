"""
Strategic Injection Point Identifier

Identifies optimal points for human injection during the humanization workflow,
provides contextual guidance, and manages user input collection.
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class InjectionPoint:
    """Represents a strategic human injection point."""
    section: str
    priority: int  # 1-5, 5 = highest priority
    position: int  # Character position in text
    context_before: str
    context_after: str
    guidance_prompt: str
    skip_available: bool = True


class InjectionPointIdentifier:
    """
    Identifies and manages strategic human injection points in academic text.

    Targets key sections where human expertise adds the most value:
    - Introduction (domain context, novelty claims)
    - Results (data interpretation, statistical nuances)
    - Discussion (implications, limitations, multiple interpretations)
    - Conclusion (future directions, broader impact)
    """

    # Section patterns for academic papers
    SECTION_PATTERNS = {
        "abstract": r"(?i)\n\s*abstract\s*\n",
        "introduction": r"(?i)\n\s*(?:1\.|I\.)?\s*introduction\s*\n",
        "methods": r"(?i)\n\s*(?:2\.|II\.)?\s*(?:methods?|methodology|materials?\s+and\s+methods?)\s*\n",
        "results": r"(?i)\n\s*(?:3\.|III\.)?\s*results?\s*\n",
        "discussion": r"(?i)\n\s*(?:4\.|IV\.)?\s*discussion\s*\n",
        "conclusion": r"(?i)\n\s*(?:5\.|V\.)?\s*conclusions?\s*\n",
        "references": r"(?i)\n\s*(?:references|bibliography)\s*\n"
    }

    def __init__(self, max_injection_points: int = 5, context_chars: int = 300):
        """
        Initialize injection point identifier.

        Args:
            max_injection_points: Maximum number of injection points
            context_chars: Characters to show before/after injection point
        """
        self.max_injection_points = max_injection_points
        self.context_chars = context_chars

    def identify_sections(self, text: str) -> Dict[str, int]:
        """
        Identify section boundaries in academic text.

        Args:
            text: Academic paper text

        Returns:
            Dictionary of section names to starting positions
        """
        sections = {}

        for section_name, pattern in self.SECTION_PATTERNS.items():
            match = re.search(pattern, text)
            if match:
                sections[section_name] = match.start()

        return sections

    def calculate_priority(
        self,
        section: str,
        position: int,
        text_length: int,
        detection_score: float
    ) -> int:
        """
        Calculate priority score for injection point.

        Args:
            section: Section name
            position: Position in text
            text_length: Total text length
            detection_score: Current detection score

        Returns:
            Priority score 1-5 (5 = highest)
        """
        base_priority = {
            "introduction": 4,  # High - sets context and novelty
            "results": 5,  # Highest - critical data interpretation
            "discussion": 5,  # Highest - multiple valid perspectives
            "conclusion": 3,  # Medium - future directions
            "methods": 2,  # Low - usually formulaic
            "abstract": 2,  # Low - summary of other sections
        }.get(section, 1)

        # Boost priority if detection score is high
        if detection_score > 70:
            base_priority = min(5, base_priority + 1)

        # Boost priority for middle sections (most content)
        relative_position = position / text_length
        if 0.3 <= relative_position <= 0.7:
            base_priority = min(5, base_priority + 1)

        return base_priority

    def generate_guidance_prompt(
        self,
        section: str,
        context_before: str,
        context_after: str
    ) -> str:
        """
        Generate contextual guidance prompt for human input.

        Args:
            section: Section name
            context_before: Text before injection point
            context_after: Text after injection point

        Returns:
            Guidance prompt
        """
        section_guidance = {
            "introduction": (
                "Review the **Introduction** section below. Please provide:\n"
                "1. Domain-specific context or terminology clarifications\n"
                "2. Suggestions to strengthen the novelty/contribution claims\n"
                "3. Any factual corrections or nuanced interpretations\n\n"
                "**Your input will be integrated to enhance authenticity and accuracy.**"
            ),
            "results": (
                "Review the **Results** section below. Please provide:\n"
                "1. Alternative interpretations of the data/findings\n"
                "2. Statistical or methodological nuances to highlight\n"
                "3. Suggestions for clearer data presentation\n\n"
                "**Your expertise helps capture scientific subtleties.**"
            ),
            "discussion": (
                "Review the **Discussion** section below. Please provide:\n"
                "1. Additional implications or broader context\n"
                "2. Limitations or caveats to acknowledge\n"
                "3. Connections to related work or alternative viewpoints\n\n"
                "**Your insights add depth and scholarly perspective.**"
            ),
            "conclusion": (
                "Review the **Conclusion** section below. Please provide:\n"
                "1. Future research directions to suggest\n"
                "2. Broader impact or practical applications\n"
                "3. Final thoughts on significance or relevance\n\n"
                "**Your input strengthens the closing message.**"
            ),
        }

        base_prompt = section_guidance.get(
            section,
            "Review the text below and provide any improvements, clarifications, or additions:"
        )

        return f"{base_prompt}\n\n{'='*60}\n**CONTEXT:**\n{context_before}\n\n[INJECTION POINT HERE]\n\n{context_after}\n{'='*60}"

    def extract_context(
        self,
        text: str,
        position: int,
        context_chars: int
    ) -> Tuple[str, str]:
        """
        Extract context before and after injection point.

        Args:
            text: Full text
            position: Injection point position
            context_chars: Characters to extract on each side

        Returns:
            Tuple of (context_before, context_after)
        """
        start = max(0, position - context_chars)
        end = min(len(text), position + context_chars)

        context_before = text[start:position].strip()
        context_after = text[position:end].strip()

        # Add ellipsis if truncated
        if start > 0:
            context_before = "..." + context_before
        if end < len(text):
            context_after = context_after + "..."

        return context_before, context_after

    def identify_injection_points(
        self,
        text: str,
        detection_score: float = 50.0
    ) -> List[InjectionPoint]:
        """
        Identify strategic injection points in text.

        Args:
            text: Academic paper text
            detection_score: Current detection score

        Returns:
            List of injection points sorted by priority
        """
        sections = self.identify_sections(text)

        if not sections:
            # No sections identified, create single injection point in middle
            middle_pos = len(text) // 2
            context_before, context_after = self.extract_context(
                text, middle_pos, self.context_chars
            )

            return [InjectionPoint(
                section="main_body",
                priority=3,
                position=middle_pos,
                context_before=context_before,
                context_after=context_after,
                guidance_prompt=self.generate_guidance_prompt(
                    "main_body", context_before, context_after
                )
            )]

        # Create injection points for key sections
        injection_points = []
        text_length = len(text)

        # Priority sections for injection
        priority_sections = [
            "results",
            "discussion",
            "introduction",
            "conclusion"
        ]

        for section in priority_sections:
            if section not in sections:
                continue

            position = sections[section]

            # Calculate priority
            priority = self.calculate_priority(
                section, position, text_length, detection_score
            )

            # Extract context
            context_before, context_after = self.extract_context(
                text, position, self.context_chars
            )

            # Generate guidance
            guidance = self.generate_guidance_prompt(
                section, context_before, context_after
            )

            injection_points.append(InjectionPoint(
                section=section,
                priority=priority,
                position=position,
                context_before=context_before,
                context_after=context_after,
                guidance_prompt=guidance
            ))

            # Stop if reached max injection points
            if len(injection_points) >= self.max_injection_points:
                break

        # If discussion appears twice, add second discussion point
        if len(injection_points) < self.max_injection_points:
            discussion_match = list(re.finditer(
                self.SECTION_PATTERNS["discussion"],
                text
            ))
            if len(discussion_match) > 1:
                position = discussion_match[1].start()
                priority = self.calculate_priority(
                    "discussion", position, text_length, detection_score
                )
                context_before, context_after = self.extract_context(
                    text, position, self.context_chars
                )
                guidance = self.generate_guidance_prompt(
                    "discussion", context_before, context_after
                )

                injection_points.append(InjectionPoint(
                    section="discussion_2",
                    priority=priority,
                    position=position,
                    context_before=context_before,
                    context_after=context_after,
                    guidance_prompt=guidance
                ))

        # Sort by priority (highest first)
        injection_points.sort(key=lambda p: p.priority, reverse=True)

        return injection_points[:self.max_injection_points]

    def format_for_user(self, injection_point: InjectionPoint) -> str:
        """
        Format injection point for user display.

        Args:
            injection_point: Injection point to format

        Returns:
            Formatted string for display
        """
        return f"""
{'='*80}
HUMAN INJECTION POINT - {injection_point.section.upper()}
Priority: {'★' * injection_point.priority} ({injection_point.priority}/5)
{'='*80}

{injection_point.guidance_prompt}

{'='*80}
OPTIONS:
1. Provide your input/suggestions (type your response)
2. Skip this injection point (type 'skip')
3. Skip all remaining injection points (type 'skip-all')
{'='*80}
"""

    def integrate_user_input(
        self,
        text: str,
        injection_point: InjectionPoint,
        user_input: str
    ) -> str:
        """
        Integrate user input into text at injection point.

        Args:
            text: Original text
            injection_point: Injection point
            user_input: User's input

        Returns:
            Text with integrated user input
        """
        if not user_input or user_input.strip().lower() in ['skip', 'skip-all']:
            return text

        # Insert user input at injection point
        position = injection_point.position

        # Find end of current paragraph/section
        next_newline = text.find('\n\n', position)
        if next_newline == -1:
            next_newline = len(text)

        # Integrate user input
        integrated_text = (
            text[:next_newline] +
            f"\n\n{user_input.strip()}\n\n" +
            text[next_newline:]
        )

        return integrated_text

    def to_dict(self, injection_points: List[InjectionPoint]) -> List[Dict]:
        """
        Convert injection points to dictionary format.

        Args:
            injection_points: List of injection points

        Returns:
            List of dictionaries
        """
        return [asdict(ip) for ip in injection_points]


# Example usage
if __name__ == "__main__":
    sample_text = """
    Abstract
    This paper presents a novel approach to machine learning...

    Introduction
    Machine learning has revolutionized many fields. However, several challenges remain...

    Methods
    We used a dataset of 10,000 samples collected from...

    Results
    Our experiments showed significant improvements with p < 0.001...

    Discussion
    These results indicate that our approach is effective. However, several limitations...

    Discussion
    Additionally, we observe that the model performs better on...

    Conclusion
    In conclusion, we have demonstrated a new method that...
    """

    identifier = InjectionPointIdentifier(max_injection_points=5)
    injection_points = identifier.identify_injection_points(
        sample_text,
        detection_score=65.0
    )

    print(f"Identified {len(injection_points)} injection points:\n")
    for i, point in enumerate(injection_points, 1):
        print(f"{i}. {point.section.upper()} (Priority: {point.priority}/5)")
        print(f"   Position: {point.position}")
        print()

    # Show formatted prompt for first injection point
    if injection_points:
        print(identifier.format_for_user(injection_points[0]))
