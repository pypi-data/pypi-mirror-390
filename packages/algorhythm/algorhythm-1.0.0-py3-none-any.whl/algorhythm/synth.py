#synth.py

"""
Real-time audio synthesis and playback engine with recording capabilities.

This module provides a polyphonic audio synthesis system using sounddevice for
real-time playback. Configuration is done through the initialize() function,
allowing users to customize audio parameters before starting the engine.

Key Features:
    - Multiple synthesis types (sine, square, saw, triangle, pulse, noise, FM)
    - Real-time audio processing with threading support
    - ADSR envelope generation
    - Low-pass filtering and LFO modulation
    - Audio recording to WAV files
    - Polyphonic playback with automatic voice management
    - Fully configurable audio parameters

Dependencies:
    sounddevice: Audio I/O operations
    numpy: Signal processing and array operations
    scipy: WAV file writing (for recording)
    threading: Thread-safe audio callback management

Configuration:
    All audio parameters can be configured via the initialize() function:
    
    - sample_rate (int): Audio sample rate in Hz (default: 44100)
    - blocksize (int): Audio buffer size in samples (default: 4096)
    - master_volume (float): Global volume control 0.0-1.0 (default: 0.15)
    - channels (int): Output channels, 1=mono, 2=stereo (default: 2)
    - use_fade_window (bool): Enable fade-out to prevent clicks (default: True)
    - fade_length (float): Fade-out duration in seconds (default: 0.03)
    - dtype (str): Audio data type (default: 'float32')

Constants:
    SYNTHS (dict): Dictionary of available synthesis functions.
                   Keys: 'sine', 'square', 'saw', 'triangle', 'pulse',
                         'noise', 'fm'

Classes:
    AudioConfig: Internal configuration container (not for direct use)
    ActiveNote: Container for active audio notes (internal use)

Functions:
    Configuration:
        initialize(**config): Set up audio engine with custom parameters
        get_config(): Retrieve current configuration settings
    
    Waveform Generators:
        sine_wave, square_wave, saw_wave, triangle_wave, pulse_wave,
        white_noise, fm_sine_wave
    
    Audio Effects:
        lpf: Low-pass filter
        adsr_envelope: Attack-Decay-Sustain-Release envelope
        lfo_mod: Low-frequency oscillator modulation
        fade_out_window: Smooth fade-out to prevent clicks
    
    Playback:
        add_note: Add a note to the playback queue
    
    Recording:
        enable_recording: Start recording audio output
        disable_recording: Stop recording
        save_recording: Save recorded audio to WAV file

Quick Start:
    >>> import audio_engine
    >>> 
    >>> # Initialize with defaults
    >>> stream = audio_engine.initialize()
    >>> stream.start()
    >>> 
    >>> # Play a note
    >>> audio_engine.add_note(440, 1.0, 0.5, audio_engine.SYNTHS['sine'])
    >>> 
    >>> # Or customize settings
    >>> stream = audio_engine.initialize(
    ...     sample_rate=48000,
    ...     blocksize=2048,
    ...     master_volume=0.2
    ... )
    >>> stream.start()

Advanced Usage:
    >>> # Configure for low latency
    >>> stream = initialize(blocksize=512, sample_rate=48000)
    >>> stream.start()
    >>> 
    >>> # Play note with effects
    >>> add_note(220, 2.0, 0.6, SYNTHS['saw'],
    ...          lpf_cutoff=1500,
    ...          env_params={'attack': 0.1, 'decay': 0.2, 
    ...                      'sustain': 0.7, 'release': 0.5})
    >>> 
    >>> # Record audio
    >>> enable_recording()
    >>> # ... play notes ...
    >>> disable_recording()
    >>> save_recording('output.wav')
    >>> 
    >>> # Check current settings
    >>> config = get_config()
    >>> print(f"Sample rate: {config['sample_rate']} Hz")
    >>> 
    >>> stream.stop()
    >>> stream.close()

Notes:
    - All parameters can be changed by calling initialize() again with new values
    - The audio stream must be stopped before re-initializing
    - Thread-safe for concurrent note playback
    - Uses real-time audio callback; keep processing minimal in custom generators
"""

import sounddevice as sd
import threading
import numpy as np
from typing import Optional, Callable, Dict, Any


# ============================================================================
# Engine Configuration
# ============================================================================

class AudioConfig:
    """
    Audio engine configuration container.
    
    Stores all configurable parameters for the audio engine. Modified by
    the initialize() function. Users should not modify these directly;
    instead, pass parameters to initialize().
    
    Attributes:
        sample_rate (int): Audio sample rate in Hz.
        blocksize (int): Audio buffer size in samples.
        master_volume (float): Global volume control (0.0 to 1.0).
        use_fade_window (bool): Enable fade-out on note endings.
        fade_length (float): Fade-out duration in seconds.
        channels (int): Number of audio channels (1=mono, 2=stereo).
        dtype (str): Audio data type for sounddevice.
    """
    def __init__(self):
        # Audio parameters
        self.sample_rate: int = 44100
        self.blocksize: int = 4096
        self.channels: int = 2
        self.dtype: str = 'float32'
        
        # Processing parameters
        self.master_volume: float = 0.15
        self.use_fade_window: bool = True
        self.fade_length: float = 0.03
        
        # Internal state
        self.active_notes: list = []
        self.lock: threading.Lock = threading.Lock()
        self.recording_enabled: bool = False
        self.recorded_blocks: list = []

# Global configuration instance
_config = AudioConfig()


def initialize(
    sample_rate: int = 44100,
    blocksize: int = 4096,
    master_volume: float = 0.15,
    channels: int = 2,
    use_fade_window: bool = True,
    fade_length: float = 0.03,
    dtype: str = 'float32'
) -> sd.OutputStream:
    """
    Initialize the audio engine with custom settings.
    
    Sets up the audio engine with the specified configuration and returns
    a configured audio stream. Call stream.start() to begin playback.
    This function should be called once at the beginning of your program.
    
    Args:
        sample_rate (int, optional): Audio sample rate in Hz. Higher rates
                                      provide better quality but more CPU load.
                                      Common values: 44100 (CD), 48000 (pro),
                                      96000 (high-end). Defaults to 44100.
        blocksize (int, optional): Audio buffer size in samples. Lower values
                                    reduce latency but increase CPU load and
                                    risk of dropouts. Must be power of 2.
                                    Common values: 512 (low latency), 2048
                                    (balanced), 4096 (safe). Defaults to 4096.
        master_volume (float, optional): Global output volume (0.0 to 1.0).
                                          0.0 = silence, 1.0 = maximum.
                                          Defaults to 0.15 (15%).
        channels (int, optional): Number of output channels. 1 = mono,
                                   2 = stereo. Defaults to 2.
        use_fade_window (bool, optional): Apply fade-out to prevent clicks
                                           when notes end. Defaults to True.
        fade_length (float, optional): Duration of fade-out in seconds.
                                        Only used if use_fade_window=True.
                                        Defaults to 0.03 (30ms).
        dtype (str, optional): Audio data type. Options: 'float32', 'int16',
                                'int32'. Defaults to 'float32' (recommended).
    
    Returns:
        sounddevice.OutputStream: Configured audio stream. Call .start() to
                                   begin playback, .stop() to pause, and
                                   .close() when done.
    
    Raises:
        ValueError: If parameters are out of valid ranges.
        sd.PortAudioError: If audio device cannot be opened.
    
    Example:
        >>> # Simple initialization with defaults
        >>> stream = initialize()
        >>> stream.start()
        >>> 
        >>> # Low-latency configuration
        >>> stream = initialize(blocksize=512, sample_rate=48000)
        >>> stream.start()
        >>> 
        >>> # High-quality configuration
        >>> stream = initialize(sample_rate=96000, master_volume=0.2)
        >>> stream.start()
    
    Note:
        Changing configuration after initialization requires stopping the
        stream, calling initialize() again, and restarting.
    """
    # Validate parameters
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    if blocksize <= 0 or (blocksize & (blocksize - 1)) != 0:
        raise ValueError("blocksize must be a positive power of 2")
    if not 0.0 <= master_volume <= 1.0:
        raise ValueError("master_volume must be between 0.0 and 1.0")
    if channels not in [1, 2]:
        raise ValueError("channels must be 1 (mono) or 2 (stereo)")
    if fade_length < 0:
        raise ValueError("fade_length must be non-negative")
    
    # Update global configuration
    _config.sample_rate = sample_rate
    _config.blocksize = blocksize
    _config.master_volume = master_volume
    _config.channels = channels
    _config.use_fade_window = use_fade_window
    _config.fade_length = fade_length
    _config.dtype = dtype
    
    # Reset state
    _config.active_notes = []
    _config.recording_enabled = False
    _config.recorded_blocks = []
    
    # Create and return stream
    return sd.OutputStream(
        channels=_config.channels,
        samplerate=_config.sample_rate,
        callback=_audio_callback,
        blocksize=_config.blocksize,
        dtype=_config.dtype
    )


def get_config() -> Dict[str, Any]:
    """
    Get current audio engine configuration.
    
    Returns a dictionary containing all current configuration parameters.
    Useful for debugging or displaying current settings to users.
    
    Returns:
        dict: Dictionary with configuration parameters:
            - sample_rate (int): Current sample rate in Hz
            - blocksize (int): Current buffer size in samples
            - master_volume (float): Current master volume (0.0-1.0)
            - channels (int): Number of channels (1 or 2)
            - use_fade_window (bool): Fade-out enabled status
            - fade_length (float): Fade-out duration in seconds
            - active_notes_count (int): Number of currently playing notes
    
    Example:
        >>> config = get_config()
        >>> print(f"Sample rate: {config['sample_rate']} Hz")
        Sample rate: 44100 Hz
        >>> print(f"Playing {config['active_notes_count']} notes")
        Playing 3 notes
    """
    with _config.lock:
        return {
            'sample_rate': _config.sample_rate,
            'blocksize': _config.blocksize,
            'master_volume': _config.master_volume,
            'channels': _config.channels,
            'use_fade_window': _config.use_fade_window,
            'fade_length': _config.fade_length,
            'active_notes_count': len(_config.active_notes)
        }


# ============================================================================
# Recording Management
# ============================================================================

def enable_recording():
    """
    Enable audio recording.
    
    Clears any previously recorded audio and begins capturing all audio
    output from the audio callback. Recorded audio is stored in memory
    until save_recording() is called.
    
    Thread-safe: Can be called while audio is playing.
    
    Example:
        >>> enable_recording()
        >>> # Play some notes...
        >>> disable_recording()
        >>> save_recording('my_recording.wav')
    """
    with _config.lock:
        _config.recording_enabled = True
        _config.recorded_blocks = []


def disable_recording():
    """
    Stop audio recording.
    
    Stops capturing audio output but preserves the recorded data in memory.
    Use save_recording() to write the captured audio to a file.
    
    Thread-safe: Can be called while audio is playing.
    
    Example:
        >>> enable_recording()
        >>> # Play some notes...
        >>> disable_recording()
        >>> save_recording('output.wav')
    """
    with _config.lock:
        _config.recording_enabled = False


def save_recording(filename: str, samplerate: Optional[int] = None):
    """
    Save recorded audio to a WAV file.
    
    Writes all audio captured between enable_recording() and 
    disable_recording() calls to a stereo WAV file. If no audio
    was recorded, this function does nothing.
    
    Args:
        filename (str): Output file path (e.g., 'recording.wav').
        samplerate (int, optional): Sample rate in Hz. If None, uses
                                     current engine sample rate.
                                     Defaults to None.
    
    Returns:
        None
    
    Side Effects:
        Creates/overwrites a WAV file at the specified path.
        Requires scipy.io.wavfile to be installed.
    
    Example:
        >>> enable_recording()
        >>> add_note(440, 1.0, 0.5, SYNTHS['sine'])
        >>> disable_recording()
        >>> save_recording('a440.wav')
    """
    if _config.recorded_blocks:
        from scipy.io.wavfile import write
        audio = np.concatenate(_config.recorded_blocks)
        rate = samplerate if samplerate is not None else _config.sample_rate
        write(filename, rate, audio)


# ============================================================================
# Waveform Generators
# ============================================================================

def sine_wave(freq: float, duration: float, amplitude: float) -> np.ndarray:
    """
    Generate a pure sine wave.
    
    Creates a sinusoidal waveform, the most fundamental sound wave with
    a smooth, pure tone containing only the fundamental frequency.
    
    Args:
        freq (float): Frequency in Hz (e.g., 440.0 for A4).
        duration (float): Length of the wave in seconds.
        amplitude (float): Peak amplitude (0.0 to 1.0 recommended).
    
    Returns:
        numpy.ndarray: 1D array of audio samples.
    
    Example:
        >>> wave = sine_wave(440.0, 1.0, 0.5)
        >>> len(wave)
        44100
    """
    t = np.linspace(0, duration, int(_config.sample_rate * duration), False)
    return amplitude * np.sin(2 * np.pi * freq * t)


def square_wave(freq: float, duration: float, amplitude: float) -> np.ndarray:
    """
    Generate a square wave.
    
    Creates a waveform that alternates between positive and negative peak
    values, producing a hollow, clarinet-like sound. Rich in odd harmonics.
    
    Args:
        freq (float): Frequency in Hz.
        duration (float): Length of the wave in seconds.
        amplitude (float): Peak amplitude (0.0 to 1.0 recommended).
    
    Returns:
        numpy.ndarray: 1D array of audio samples.
    
    Example:
        >>> wave = square_wave(220.0, 0.5, 0.3)
    """
    t = np.linspace(0, duration, int(_config.sample_rate * duration), False)
    return amplitude * np.sign(np.sin(2 * np.pi * freq * t))


def saw_wave(freq: float, duration: float, amplitude: float) -> np.ndarray:
    """
    Generate a sawtooth wave.
    
    Creates a waveform that ramps linearly from -1 to 1, producing a
    bright, buzzy sound. Rich in both even and odd harmonics.
    
    Args:
        freq (float): Frequency in Hz.
        duration (float): Length of the wave in seconds.
        amplitude (float): Peak amplitude (0.0 to 1.0 recommended).
    
    Returns:
        numpy.ndarray: 1D array of audio samples.
    """
    t = np.linspace(0, duration, int(_config.sample_rate * duration), False)
    return amplitude * (2 * (t * freq % 1) - 1)


def triangle_wave(freq: float, duration: float, amplitude: float) -> np.ndarray:
    """
    Generate a triangle wave.
    
    Creates a waveform that ramps linearly up and down, producing a
    softer, mellower sound than square or saw waves.
    
    Args:
        freq (float): Frequency in Hz.
        duration (float): Length of the wave in seconds.
        amplitude (float): Peak amplitude (0.0 to 1.0 recommended).
    
    Returns:
        numpy.ndarray: 1D array of audio samples.
    """
    t = np.linspace(0, duration, int(_config.sample_rate * duration), False)
    return amplitude * (2 * np.abs(2 * ((t * freq) % 1) - 1) - 1)


def pulse_wave(freq: float, duration: float, amplitude: float, duty: float = 0.5) -> np.ndarray:
    """
    Generate a pulse wave with variable duty cycle.
    
    Creates a rectangular waveform where the duty cycle controls the
    ratio of high to low portions. 50% duty cycle produces a square wave.
    
    Args:
        freq (float): Frequency in Hz.
        duration (float): Length of the wave in seconds.
        amplitude (float): Peak amplitude (0.0 to 1.0 recommended).
        duty (float, optional): Duty cycle (0.0 to 1.0). Defaults to 0.5.
    
    Returns:
        numpy.ndarray: 1D array of audio samples.
    """
    t = np.linspace(0, duration, int(_config.sample_rate * duration), False)
    waveform = np.where((t * freq) % 1 < duty, 1, -1)
    return amplitude * waveform


def white_noise(duration: float, amplitude: float) -> np.ndarray:
    """
    Generate white noise.
    
    Creates random noise with equal power at all frequencies. Useful
    for percussion sounds, wind effects, or adding texture.
    
    Args:
        duration (float): Length of the noise in seconds.
        amplitude (float): Peak amplitude (0.0 to 1.0 recommended).
    
    Returns:
        numpy.ndarray: 1D array of random audio samples.
    """
    return amplitude * np.random.uniform(-1, 1, int(_config.sample_rate * duration))


def fm_sine_wave(freq: float, duration: float, amplitude: float, 
                 mod_freq: float = 2.0, mod_index: float = 2.0) -> np.ndarray:
    """
    Generate a frequency-modulated (FM) sine wave.
    
    Creates a complex, evolving tone by modulating the frequency of a
    carrier sine wave with another sine wave (modulator).
    
    Args:
        freq (float): Carrier frequency in Hz.
        duration (float): Length of the wave in seconds.
        amplitude (float): Peak amplitude (0.0 to 1.0 recommended).
        mod_freq (float, optional): Modulator frequency in Hz. Defaults to 2.0.
        mod_index (float, optional): Modulation depth. Defaults to 2.0.
    
    Returns:
        numpy.ndarray: 1D array of audio samples.
    """
    t = np.linspace(0, duration, int(_config.sample_rate * duration), False)
    modulator = mod_index * np.sin(2 * np.pi * mod_freq * t)
    return amplitude * np.sin(2 * np.pi * freq * t + modulator)


# Dictionary of available synthesis functions
SYNTHS = {
    'sine': sine_wave,
    'square': square_wave,
    'saw': saw_wave,
    'triangle': triangle_wave,
    'pulse': lambda freq, duration, amplitude: pulse_wave(freq, duration, amplitude, duty=0.2),
    'noise': lambda freq, duration, amplitude: white_noise(duration, amplitude),
    'fm': lambda freq, duration, amplitude: fm_sine_wave(freq, duration, amplitude, mod_freq=2.0, mod_index=2.0),
}


# ============================================================================
# Audio Effects and Processing
# ============================================================================

def lpf(wave: np.ndarray, cutoff: float, sample_rate: Optional[int] = None) -> np.ndarray:
    """
    Apply a simple low-pass filter to an audio signal.
    
    Implements a first-order recursive low-pass filter (single-pole IIR).
    Attenuates frequencies above the cutoff frequency.
    
    Args:
        wave (numpy.ndarray): Input audio signal (1D array).
        cutoff (float): Cutoff frequency in Hz.
        sample_rate (int, optional): Sample rate in Hz. If None, uses
                                      current engine sample rate.
    
    Returns:
        numpy.ndarray: Filtered audio signal.
    """
    sr = sample_rate if sample_rate is not None else _config.sample_rate
    RC = 1.0 / (cutoff * 2 * np.pi)
    dt = 1.0 / sr
    alpha = dt / (RC + dt)
    filtered = np.zeros_like(wave)
    filtered[0] = wave[0]
    for i in range(1, len(wave)):
        filtered[i] = filtered[i-1] + alpha * (wave[i] - filtered[i-1])
    return filtered


def adsr_envelope(wave: np.ndarray, attack: float = 0.01, decay: float = 0.05, 
                  sustain: float = 0.7, release: float = 0.1, 
                  sample_rate: Optional[int] = None) -> np.ndarray:
    """
    Apply an ADSR (Attack-Decay-Sustain-Release) envelope to an audio signal.
    
    Shapes the amplitude of a sound over time with four stages:
    Attack → Decay → Sustain → Release
    
    Args:
        wave (numpy.ndarray): Input audio signal (1D array).
        attack (float, optional): Attack time in seconds. Defaults to 0.01.
        decay (float, optional): Decay time in seconds. Defaults to 0.05.
        sustain (float, optional): Sustain level (0.0-1.0). Defaults to 0.7.
        release (float, optional): Release time in seconds. Defaults to 0.1.
        sample_rate (int, optional): Sample rate in Hz. If None, uses
                                      current engine sample rate.
    
    Returns:
        numpy.ndarray: Audio signal with envelope applied.
    """
    sr = sample_rate if sample_rate is not None else _config.sample_rate
    N = len(wave)
    attack_samples = int(attack * sr)
    decay_samples = int(decay * sr)
    release_samples = int(release * sr)
    sustain_samples = N - (attack_samples + decay_samples + release_samples)
    
    if sustain_samples < 0:
        sustain_samples = 0
        release_samples = N - (attack_samples + decay_samples)
    
    envelope = np.concatenate([
        np.linspace(0, 1, attack_samples, False),
        np.linspace(1, sustain, decay_samples, False),
        np.full(sustain_samples, sustain),
        np.linspace(sustain, 0, release_samples, False)
    ])
    
    envelope = envelope[:N]
    return wave * envelope


def lfo_mod(wave: np.ndarray, lfo_freq: float = 5, lfo_depth: float = 0.1,
            sample_rate: Optional[int] = None) -> np.ndarray:
    """
    Apply Low-Frequency Oscillator (LFO) amplitude modulation.
    
    Modulates the amplitude with a slow sine wave, creating tremolo.
    
    Args:
        wave (numpy.ndarray): Input audio signal (1D array).
        lfo_freq (float, optional): LFO frequency in Hz. Defaults to 5.
        lfo_depth (float, optional): Modulation depth (0.0-1.0). Defaults to 0.1.
        sample_rate (int, optional): Sample rate in Hz. If None, uses
                                      current engine sample rate.
    
    Returns:
        numpy.ndarray: Modulated audio signal.
    """
    sr = sample_rate if sample_rate is not None else _config.sample_rate
    t = np.arange(len(wave)) / sr
    modulation = 1 + lfo_depth * np.sin(2 * np.pi * lfo_freq * t)
    return wave * modulation


def fade_out_window(wave: np.ndarray, length: Optional[float] = None,
                    sample_rate: Optional[int] = None) -> np.ndarray:
    """
    Apply a fade-out window to prevent clicks at the end of a sound.
    
    Args:
        wave (numpy.ndarray): Input audio signal (1D array).
        length (float, optional): Fade duration in seconds. If None, uses
                                   _config.fade_length.
        sample_rate (int, optional): Sample rate in Hz. If None, uses
                                      current engine sample rate.
    
    Returns:
        numpy.ndarray: Audio signal with fade-out applied.
    """
    sr = sample_rate if sample_rate is not None else _config.sample_rate
    fade_len = length if length is not None else _config.fade_length
    fade_samples = int(fade_len * sr)
    
    if fade_samples > len(wave):
        fade_samples = len(wave)
    
    window = np.ones(len(wave))
    if fade_samples > 1:
        window[-fade_samples:] = np.linspace(1, 0, fade_samples)
    
    return wave * window


# ============================================================================
# Playback Management
# ============================================================================

class ActiveNote:
    """
    Container for an active audio note being played.
    
    Tracks the playback position within a pre-generated waveform buffer.
    
    Attributes:
        wave (numpy.ndarray): Complete audio waveform for this note.
        position (int): Current playback position (sample index).
    """
    def __init__(self, wave: np.ndarray):
        self.wave = wave
        self.position = 0


def add_note(freq: float, duration: float, amplitude: float, synth_func: Callable,
             lpf_cutoff: Optional[float] = None, env_params: Optional[Dict] = None,
             lfo_params: Optional[Dict] = None):
    """
    Generate and queue a note for playback.
    
    Creates a complete audio waveform with optional effects and adds it
    to the active playback queue. Thread-safe.
    
    Args:
        freq (float): Fundamental frequency in Hz.
        duration (float): Note length in seconds.
        amplitude (float): Base amplitude (0.0 to 1.0 recommended).
        synth_func (callable): Waveform generator function from SYNTHS dict.
        lpf_cutoff (float, optional): Low-pass filter cutoff in Hz. None = no filtering.
        env_params (dict, optional): ADSR envelope parameters.
        lfo_params (dict, optional): LFO parameters.
    
    Returns:
        None
    
    Example:
        >>> add_note(440, 1.0, 0.5, SYNTHS['sine'])
        >>> add_note(220, 2.0, 0.6, SYNTHS['saw'],
        ...          lpf_cutoff=1000,
        ...          env_params={'attack': 0.1, 'decay': 0.2, 'sustain': 0.7, 'release': 0.5})
    """
    wave = synth_func(freq, duration, amplitude)
    
    if lfo_params:
        wave = lfo_mod(wave, **lfo_params)
    
    if lpf_cutoff:
        wave = lpf(wave, lpf_cutoff)
    
    if env_params:
        wave = adsr_envelope(wave, **env_params)
    
    if _config.use_fade_window:
        wave = fade_out_window(wave)
    
    with _config.lock:
        _config.active_notes.append(ActiveNote(wave))


def _audio_callback(outdata, frames, time, status):
    """
    Audio stream callback function (internal).
    
    Called automatically by sounddevice. Do not call directly.
    """
    out_block = np.zeros(frames, dtype=np.float32)
    
    with _config.lock:
        for note in _config.active_notes[:]:
            end_pos = note.position + frames
            out_samples = note.wave[note.position:end_pos]
            out_block[:len(out_samples)] += out_samples
            note.position += frames
            if note.position >= len(note.wave):
                _config.active_notes.remove(note)
    
    out_block *= _config.master_volume
    out_block = np.clip(out_block, -1.0, 1.0)
    
    # Handle mono/stereo
    if _config.channels == 2:
        outdata[:, 0] = out_block
        outdata[:, 1] = out_block
    else:
        outdata[:, 0] = out_block
    
    if _config.recording_enabled:
        if _config.channels == 2:
            recorded = np.column_stack((out_block, out_block))
        else:
            recorded = out_block.reshape(-1, 1)
        _config.recorded_blocks.append(recorded.astype(np.float32))


