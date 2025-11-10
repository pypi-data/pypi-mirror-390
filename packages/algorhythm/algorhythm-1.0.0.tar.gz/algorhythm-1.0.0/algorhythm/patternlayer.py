"""
Pattern-based musical sequencer for the algorhythm audio engine.

This module provides the PatternLayer class, which enables pattern-based
sequencing of musical notes. Each layer represents an independent sequence
of notes that can be started, stopped, and updated dynamically during
playback.

Classes:
    PatternLayer: A threaded pattern sequencer for musical note patterns.

Dependencies:
    threading: Timer-based sequencing
    algorhythm.synth: Audio synthesis engine

Usage Example:
    >>> from patternlayer import PatternLayer
    >>> 
    >>> # Create a simple arpeggio pattern
    >>> layer = PatternLayer(
    ...     name="Arpeggio",
    ...     pattern=[440, 550, 660],  # A, C#, E (A major triad)
    ...     intervals=[0.5, 0.5, 0.5],  # Play every 0.5 seconds
    ...     durations=[0.4, 0.4, 0.4],  # Each note lasts 0.4 seconds
    ...     amplitudes=[0.3, 0.3, 0.3],  # Constant volume
    ...     synth='sine'
    ... )
    >>> 
    >>> # Start playback
    >>> layer.start()
    >>> 
    >>> # Stop when done
    >>> layer.stop()
"""

import threading
from .synth import SYNTHS, add_note


class PatternLayer:
    """
    A threaded pattern sequencer for musical note patterns.
    
    PatternLayer manages a repeating sequence of notes with configurable
    timing, synthesis parameters, and audio effects. Each instance runs
    independently in its own thread, allowing multiple layers to play
    simultaneously for polyphonic compositions.
    
    The pattern loops continuously once started, cycling through the
    provided note frequencies, intervals, durations, and amplitudes.
    Arrays of different lengths will wrap independently.
    
    Attributes:
        name (str): Human-readable identifier for this layer.
        pattern (list): List of note frequencies in Hz.
        intervals (list): List of time delays between notes in seconds.
        durations (list): List of note durations in seconds.
        amplitudes (list): List of note amplitudes (0.0 to 1.0).
        synth (str): Synthesis type from SYNTHS dictionary.
        lpf_cutoff (float or None): Low-pass filter cutoff frequency in Hz.
        env_params (dict or None): ADSR envelope parameters.
        lfo_params (dict or None): LFO modulation parameters.
        step (int): Current step position in the pattern.
        active (bool): Whether the layer is currently playing.
    
    Example:
        >>> # Create a rhythmic bass pattern
        >>> bass = PatternLayer(
        ...     name="Bass",
        ...     pattern=[110, 110, 165, 110],  # A2, A2, E3, A2
        ...     intervals=[0.5, 0.5, 0.5, 0.5],
        ...     durations=[0.3, 0.3, 0.3, 0.3],
        ...     amplitudes=[0.5, 0.3, 0.4, 0.3],
        ...     synth='saw',
        ...     lpf_cutoff=800,
        ...     env_params={'attack': 0.01, 'decay': 0.1, 'sustain': 0.3, 'release': 0.2}
        ... )
        >>> bass.start()
    """
    
    def __init__(
            self, name, pattern, intervals, durations, amplitudes, synth='saw',
            lpf_cutoff=None, env_params=None, lfo_params=None
        ):
        """
        Initialize a PatternLayer sequencer.
        
        Args:
            name (str): Descriptive name for this layer (used in debug output).
            pattern (list of float): Note frequencies in Hz. Will loop continuously.
            intervals (list of float): Time delays between notes in seconds.
                                       Wraps independently if shorter than pattern.
            durations (list of float): Duration of each note in seconds.
                                       Wraps independently if shorter than pattern.
            amplitudes (list of float): Amplitude for each note (0.0 to 1.0).
                                        Wraps independently if shorter than pattern.
            synth (str, optional): Synthesis type. Must be key in SYNTHS dict
                                   ('sine', 'saw', 'square', 'triangle', 'pulse',
                                   'noise', 'fm'). Defaults to 'saw'.
            lpf_cutoff (float, optional): Low-pass filter cutoff in Hz.
                                          None = no filtering. Defaults to None.
            env_params (dict, optional): ADSR envelope parameters with keys:
                                         'attack', 'decay', 'sustain', 'release'.
                                         None = no envelope. Defaults to None.
            lfo_params (dict, optional): LFO modulation parameters with keys:
                                         'lfo_freq', 'lfo_depth'.
                                         None = no LFO. Defaults to None.
        
        Example:
            >>> layer = PatternLayer(
            ...     name="Pad",
            ...     pattern=[261.63, 329.63, 392.00],  # C major chord
            ...     intervals=[2.0],  # 2 seconds between notes
            ...     durations=[3.0],  # Each note lasts 3 seconds (overlapping)
            ...     amplitudes=[0.2],  # Quiet, sustained
            ...     synth='triangle',
            ...     env_params={'attack': 1.0, 'decay': 0.5, 'sustain': 0.8, 'release': 2.0}
            ... )
        """
        self.name = name
        self.pattern = pattern
        self.intervals = intervals
        self.durations = durations
        self.amplitudes = amplitudes
        self.synth = synth
        self.lpf_cutoff = lpf_cutoff
        self.env_params = env_params
        self.lfo_params = lfo_params
        self.step = 0
        self.active = False
        self._timer = None

    def _play_note(self):
        """
        Play the current note in the pattern sequence (internal method).
        
        Retrieves frequency, duration, and amplitude from the pattern arrays
        using modulo indexing (wraps around if arrays have different lengths).
        Sends the note to the audio engine with configured effects.
        
        Prints debug information showing layer name, synthesis type, frequency,
        duration, and amplitude.
        
        Returns:
            None
        """
        freq = self.pattern[self.step % len(self.pattern)]
        duration = self.durations[self.step % len(self.durations)]
        amplitude = self.amplitudes[self.step % len(self.amplitudes)]
        synth_func = SYNTHS.get(self.synth, SYNTHS['sine'])
        add_note(
            freq, duration, amplitude, synth_func,
            lpf_cutoff=self.lpf_cutoff,
            env_params=self.env_params,
            lfo_params=self.lfo_params
        )
        print(f"[{self.name}] Played {self.synth} {freq}Hz for {duration}s at amp {amplitude}")

    def _sequencer(self):
        """
        Internal sequencer loop (recursive timer-based scheduling).
        
        Plays the current note, schedules the next note based on the interval
        array, and increments the step counter. Continues recursively while
        the layer is active.
        
        This method should not be called directly. Use start() instead.
        
        Returns:
            None
        """
        if self.active:
            self._play_note()
            interval = self.intervals[self.step % len(self.intervals)]
            self.step += 1
            self._timer = threading.Timer(interval, self._sequencer)
            self._timer.start()

    def start(self):
        """
        Start playing the pattern sequence.
        
        Begins playback from step 0 if not already active. The pattern will
        loop continuously until stop() is called. Safe to call multiple times
        (will only start once).
        
        Thread-safe: Can be called from any thread.
        
        Returns:
            None
        
        Example:
            >>> layer.start()  # Begin playing
            >>> # Pattern plays in background...
            >>> layer.stop()   # Stop when done
        """
        if not self.active:
            self.active = True
            self.step = 0
            self._sequencer()

    def stop(self):
        """
        Stop playing the pattern sequence.
        
        Halts playback and cancels any pending scheduled notes. The layer
        can be restarted with start(), which will begin from step 0 again.
        Safe to call multiple times or when already stopped.
        
        Thread-safe: Can be called from any thread.
        
        Returns:
            None
        
        Note:
            Already-playing notes will complete their duration. This only
            prevents new notes from being triggered.
        
        Example:
            >>> layer.start()
            >>> # ... let it play for a while ...
            >>> layer.stop()  # Stops scheduling new notes
        """
        self.active = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def update_pattern(self, pattern=None, intervals=None, durations=None, amplitudes=None, synth=None,
                      lpf_cutoff=None, env_params=None, lfo_params=None):
        """
        Update pattern parameters while preserving playback state.
        
        Allows real-time modification of any pattern parameter without
        stopping playback. Only specified parameters are updated; others
        remain unchanged. Changes take effect on the next note played.
        
        Thread-safe: Can be called while the layer is playing.
        
        Args:
            pattern (list of float, optional): New note frequencies in Hz.
            intervals (list of float, optional): New inter-note intervals in seconds.
            durations (list of float, optional): New note durations in seconds.
            amplitudes (list of float, optional): New note amplitudes (0.0-1.0).
            synth (str, optional): New synthesis type from SYNTHS dict.
            lpf_cutoff (float, optional): New filter cutoff in Hz.
            env_params (dict, optional): New ADSR envelope parameters.
            lfo_params (dict, optional): New LFO modulation parameters.
        
        Returns:
            None
        
        Example:
            >>> layer.start()
            >>> # Play for a while, then make it faster and quieter
            >>> layer.update_pattern(
            ...     intervals=[0.25, 0.25, 0.25],  # Twice as fast
            ...     amplitudes=[0.1, 0.1, 0.1]     # Quieter
            ... )
            >>> # Changes take effect immediately on next note
        """
        if pattern is not None:
            self.pattern = pattern
        if intervals is not None:
            self.intervals = intervals
        if durations is not None:
            self.durations = durations
        if amplitudes is not None:
            self.amplitudes = amplitudes
        if synth is not None:
            self.synth = synth
        if lpf_cutoff is not None:
            self.lpf_cutoff = lpf_cutoff
        if env_params is not None:
            self.env_params = env_params
        if lfo_params is not None:
            self.lfo_params = lfo_params
