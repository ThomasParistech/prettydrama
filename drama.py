#!/usr/bin/python3
"""Drama."""
from dataclasses import dataclass


import re




@dataclass
class Scene:
    """aaaaaaaaaa"""
    dialogues: list[tuple[str, str]]  # List of (character, dialogue) tuples

    @staticmethod
    def from_lines(lines: list[str]) -> 'Scene':
        """Load a Scene from text lines."""
        return Scene(dialogues=split_character_lines(lines))


@dataclass
class Act:
    """A container for multiple scenes (WordSpeakerMap objects)."""
    scenes: list[Scene]

    @staticmethod
    def from_lines(lines: list[str]) -> 'Act':
        """Load an Act from text lines."""
        return Act(scenes=[Scene.from_lines(scene_lines)
                           for scene_lines in split_lines_into_blocks(lines, "*scene*")])


@dataclass
class Drama:
    """The complete play, containing a sequence of Acts."""
    title: str
    acts: list[Act]

    @staticmethod
    def from_file(drama_txt: str) -> 'Drama':
        """Load a Drama from a text file."""
        with open(drama_txt, "r") as file:
            lines = [line.strip() for line in file]
            return Drama.from_lines(lines)

    @staticmethod
    def from_lines(lines: list[str]) -> 'Drama':
        """Load a Drama from text lines. First line is title."""
        title = lines[0] if lines else ""
        remaining = lines[1:]
        return Drama(
            title=title,
            acts=[Act.from_lines(act_lines)
                  for act_lines in split_lines_into_blocks(remaining, "=act=")]
        )

    def print(self) -> None:
        """Print the Drama structure."""
        for act_index, act in enumerate(self.acts, start=1):
            print(f"Act {act_index}:")
            for scene_index, scene in enumerate(act.scenes, start=1):
                print(f"  Scene {scene_index}:")
                for character, dialogue in scene.dialogues:
                    print(f"    {character}: {dialogue}")


def split_lines_into_blocks(lines: list[str],
                            keyword: str) -> list[list[str]]:
    """Split a list of lines into blocks whenever a line contains a given keyword."""
    blocks: list[list[str]] = []
    current_block: list[str] = []

    keyword_lower = keyword.lower()
    for line in lines:
        if keyword_lower in line.lower():
            if current_block:
                blocks.append(current_block)
                current_block = []
        else:
            current_block.append(line)

    if current_block:
        blocks.append(current_block)

    return blocks


def split_character_lines(lines: list[str]) -> list[tuple[str, str]]:
    """Split lines into (character, lines) tuples."""
    result: list[tuple[str, str]] = []
    current_character = None
    current_lines: list[str] = []

    for line in lines:
        match = re.match(r"<([^>]+)>", line)
        if match:
            if current_character is not None:
                result.append((current_character, "\n".join(current_lines)))
            current_character = match.group(1)
            current_lines = [line[match.end():].strip()]
        else:
            if current_character is not None:
                current_lines.append(line)

    if current_character is not None:
        result.append((current_character, "\n".join(current_lines)))

    return result
