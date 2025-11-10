# chords_library.py

"""
A music theory library for generating chord notes and frequencies.

This module provides functionality to:
- Calculate frequencies for musical notes using equal temperament tuning
- Generate chord notes based on interval patterns
- Create chord inversions
- List all available chord types for a given root note

The module uses standard Western music notation with A4 = 440Hz as the reference.

Classes:
    None

Functions:
    get_frequency(note, octave): Calculate frequency for a note
    chord_notes(root_note, chord_type, octave): Generate notes for a chord
    chord_inversion(notes, inversion): Reorder chord notes for inversions
    list_chords(root_note, octave): Get all chord types for a root

Constants:
    NOTES: List of note names in chromatic scale
    A4_INDEX: Index of A4 in the note system
    A4_FREQ: Reference frequency (440Hz)
    CHORD_INTERVALS: Dictionary of chord interval patterns
"""

from math import pow


# Notes and their corresponding numbers in a chromatic scale
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Reference frequency for A4 (standard concert pitch)
A4_INDEX = NOTES.index('A') + 4 * 12  # A in the 4th octave
A4_FREQ = 440.0  # Hz


def get_frequency(note, octave):
    """
    Calculate the frequency of a musical note using equal temperament tuning.
    
    Uses the formula: f = 440 * 2^((n - n_A4) / 12)
    where n is the note index and n_A4 is A4's index.
    
    Args:
        note (str): Note name (e.g., 'C', 'F#', 'Bb'). Must be one of the 
                    notes in the NOTES list.
        octave (int): Octave number (typically 0-8, where 4 is middle octave).
    
    Returns:
        float: The frequency of the note in Hertz (Hz).
    
    Raises:
        ValueError: If note is not in NOTES list.
    
    Example:
        >>> get_frequency('A', 4)
        440.0
        >>> get_frequency('C', 4)
        261.6255653005986
    """
    n = NOTES.index(note) + octave * 12
    return A4_FREQ * pow(2, (n - A4_INDEX) / 12)


# Interval recipes for chord types (semitones from root)
# Each list represents the semitone intervals that define the chord
CHORD_INTERVALS = {
    'major':      [0, 4, 7],      # Root, major third, perfect fifth
    'minor':      [0, 3, 7],      # Root, minor third, perfect fifth
    'maj7':       [0, 4, 7, 11],  # Major triad + major seventh
    'min7':       [0, 3, 7, 10],  # Minor triad + minor seventh
    'dom7':       [0, 4, 7, 10],  # Major triad + minor seventh (dominant)
    'sus2':       [0, 2, 7],      # Root, major second, perfect fifth
    'sus4':       [0, 5, 7],      # Root, perfect fourth, perfect fifth
}


def chord_notes(root_note, chord_type, octave=4):
    """
    Generate the notes, octaves, and frequencies for a chord.
    
    Calculates all notes in a chord based on the root note, chord type,
    and starting octave. Handles octave transitions when intervals wrap
    around the 12-note chromatic scale.
    
    Args:
        root_note (str): The root note of the chord (e.g., 'C', 'F#', 'Bb').
                         Must be one of the notes in NOTES list.
        chord_type (str): Type of chord to generate. Must be one of the keys
                          in CHORD_INTERVALS ('major', 'minor', 'maj7', 
                          'min7', 'dom7', 'sus2', 'sus4').
        octave (int, optional): Starting octave for the root note. 
                                Defaults to 4 (middle octave).
    
    Returns:
        list of tuple: Each tuple contains (note_name, octave, frequency)
                       where note_name is str, octave is int, and 
                       frequency is float in Hz.
    
    Raises:
        ValueError: If chord_type is not supported or root_note is invalid.
    
    Example:
        >>> chord_notes('C', 'major', 4)
        [('C', 4, 261.63), ('E', 4, 329.63), ('G', 4, 392.00)]
        >>> chord_notes('A', 'min7', 3)
        [('A', 3, 220.0), ('C', 4, 261.63), ('E', 4, 329.63), ('G', 4, 392.00)]
    """
    intervals = CHORD_INTERVALS.get(chord_type, None)
    if intervals is None:
        raise ValueError(f"Chord type '{chord_type}' not supported.")
    
    root_index = NOTES.index(root_note)
    notes = []
    
    for i in intervals:
        # Calculate note index with modulo for wrapping around octave
        idx = (root_index + i) % 12
        # Calculate octave adjustment when wrapping
        note_octave = octave + ((root_index + i) // 12)
        notes.append((NOTES[idx], note_octave, get_frequency(NOTES[idx], note_octave)))
    
    return notes


def chord_inversion(notes, inversion=1):
    """
    Reorder chord notes to create an inversion.
    
    Chord inversions move the lowest note(s) up by an octave, changing
    the voicing while maintaining the same chord quality. 
    - Inversion 0: Root position (no change)
    - Inversion 1: First inversion (lowest note moved to top)
    - Inversion 2: Second inversion (two lowest notes moved to top)
    
    Args:
        notes (list): List of note tuples from chord_notes(), each containing
                      (note_name, octave, frequency).
        inversion (int, optional): Inversion number (0 = root position,
                                   1 = first inversion, etc.). Must be 
                                   between 0 and len(notes)-1. Defaults to 1.
    
    Returns:
        list: Reordered list of note tuples representing the inversion.
    
    Raises:
        ValueError: If inversion number is invalid for the chord size.
    
    Example:
        >>> c_major = chord_notes('C', 'major', 4)
        >>> chord_inversion(c_major, 0)  # Root position
        [('C', 4, 261.63), ('E', 4, 329.63), ('G', 4, 392.00)]
        >>> chord_inversion(c_major, 1)  # First inversion (E in bass)
        [('E', 4, 329.63), ('G', 4, 392.00), ('C', 4, 261.63)]
    """
    if inversion == 0:
        return notes
    elif inversion > 0 and inversion < len(notes):
        return notes[inversion:] + notes[:inversion]
    else:
        raise ValueError("Invalid inversion number")


def list_chords(root_note, octave=4):
    """
    Generate all available chord types for a given root note.
    
    Creates a dictionary mapping each chord type to its corresponding
    note list, useful for exploring chord options or building chord
    progression tools.
    
    Args:
        root_note (str): The root note for all chords (e.g., 'C', 'F#').
                         Must be one of the notes in NOTES list.
        octave (int, optional): Starting octave for the root note.
                                Defaults to 4 (middle octave).
    
    Returns:
        dict: Dictionary where keys are chord type names (str) and 
              values are lists of note tuples [(note, octave, freq), ...].
    
    Raises:
        ValueError: If root_note is not in NOTES list.
    
    Example:
        >>> all_c_chords = list_chords('C', 4)
        >>> all_c_chords.keys()
        dict_keys(['major', 'minor', 'maj7', 'min7', 'dom7', 'sus2', 'sus4'])
        >>> all_c_chords['major']
        [('C', 4, 261.63), ('E', 4, 329.63), ('G', 4, 392.00)]
    """
    all_chords = {}
    for chord_type in CHORD_INTERVALS.keys():
        notes = chord_notes(root_note, chord_type, octave)
        all_chords[chord_type] = notes
    return all_chords

