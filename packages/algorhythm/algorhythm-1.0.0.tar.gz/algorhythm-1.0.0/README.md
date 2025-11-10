# Algorhythm

*A Python audio synthesis and music composition library for real-time polyphonic sound generation*

Algorhythm is a powerful yet intuitive library for creating music programmatically using Python. It combines real-time audio synthesis, pattern sequencing, and music theory utilities to enable everything from simple melodies to complex generative compositions.

## Features

- **Real-time Audio Synthesis**: Multiple waveform generators (sine, square, saw, triangle, pulse, white noise, FM synthesis)
- **Polyphonic Playback**: Play multiple notes and layers simultaneously
- **Audio Effects**: Built-in ADSR envelopes, low-pass filtering, and LFO modulation
- **Pattern Sequencing**: Create and layer looping musical patterns with independent timing
- **Music Theory Tools**: Generate chords and note frequencies with equal temperament tuning
- **Audio Recording**: Capture your compositions to WAV files
- **Configurable Engine**: Customize sample rate, buffer size, and audio parameters
- **Thread-safe**: Designed for concurrent operation and live performance

## Installation

Install Algorhythm via pip:
```pip install algorhythm```

### Dependencies

- `numpy`: Signal processing and array operations
- `sounddevice`: Real-time audio I/O
- `scipy`: WAV file writing (for recording)

If you need to install the dependencies manually:
```pip install numpy sounddevice scipy``` 

## Quick Start

### Basic Audio Synthesis

```
from algorhythm.synth import initialize, add_note, SYNTHS

# Initialize audio engine with default settings
stream = initialize()
stream.start()

# Play a single note (A4 = 440Hz)
add_note(freq=440, duration=1.0, amplitude=0.5, synth_func=SYNTHS['sine'])

# Wait for playback to finish
import time
time.sleep(2)

# Cleanup
stream.stop()
stream.close()
```
---

### Custom Configuration
```
# Configure for low latency or high quality
stream = initialize(
    sample_rate=48000,      # Higher quality
    blocksize=512,          # Lower latency
    master_volume=0.2,      # Adjust overall volume
    channels=2              # Stereo output
)
stream.start()
```
---

### Playing Chords:
```
from algorhythm.chords_library import chord_notes

# Generate a C major chord in the 4th octave
c_major = chord_notes('C', 'major', 4)

# Play all notes in the chord
for note_name, octave, frequency in c_major:
    add_note(frequency, 2.0, 0.3, SYNTHS['sine'])
```
---

### Pattern Sequencing:
```
from algorhythm.patternlayer import PatternLayer

# Create an arpeggio pattern
arpeggio = PatternLayer(
    name="Arpeggio",
    pattern=[261.63, 329.63, 392.00],  # C, E, G (C major triad)
    intervals=[0.5, 0.5, 0.5],         # Play every 0.5 seconds
    durations=[0.4, 0.4, 0.4],         # Each note lasts 0.4 seconds
    amplitudes=[0.3, 0.3, 0.3],        # Constant volume
    synth='sine'
)

# Start the pattern (loops continuously)
arpeggio.start()

# Stop when done
time.sleep(5)
arpeggio.stop()
```

## Audio Effects

### ADSR Envelope:
```
# Create a note with attack, decay, sustain, and release
add_note(
    freq=440,
    duration=2.0,
    amplitude=0.6,
    synth_func=SYNTHS['saw'],
    env_params={
        'attack': 0.1,    # Fade in over 0.1 seconds
        'decay': 0.2,     # Decay to sustain level over 0.2 seconds
        'sustain': 0.7,   # Hold at 70% amplitude
        'release': 0.5    # Fade out over 0.5 seconds
    }
)
```
---

### Low-Pass Filter:
```
# Add filtering to remove harsh high frequencies
add_note(
    freq=440,
    duration=2.0,
    amplitude=0.6,
    synth_func=SYNTHS['square'],
    lpf_cutoff=1000  # Cut frequencies above 1000Hz
)
```
---

### LFO Modulation (Tremolo):
```
# Add vibrato/tremolo effect
add_note(
    freq=440,
    duration=3.0,
    amplitude=0.5,
    synth_func=SYNTHS['sine'],
    lfo_params={
        'lfo_freq': 5,      # Modulate 5 times per second
        'lfo_depth': 0.3    # 30% amplitude variation
    }
)
```
## Recording Audio

```
from algorhythm.synth import enable_recording, disable_recording, save_recording

# Start recording
enable_recording()

# Play your composition
add_note(440, 1.0, 0.5, SYNTHS['sine'])
time.sleep(2)

# Stop and save
disable_recording()
save_recording('output.wav')
```

## Available Synth Types

The `SYNTHS` dictionary provides quick access to the core waveforms and modulation types used in Algorhythm. Each type has a distinct sound character:

| Key         | Description                                       |
|-------------|---------------------------------------------------|
| `sine`      | Pure sine wave – smooth, fundamental tone         |
| `square`    | Square wave – hollow, clarinet-like               |
| `saw`       | Sawtooth wave – bright, buzzy                     |
| `triangle`  | Triangle wave – mellow, soft                      |
| `pulse`     | Pulse wave (20% duty cycle) – thin, nasal         |
| `noise`     | White noise – broadband random texture            |
| `fm`        | FM synthesis – bell-like, metallic                |

- **Sine**: The simplest and purest tone; contains only the fundamental frequency.
- **Square**: Hollow and reedy, rich in odd harmonics.
- **Saw**: Buzzy and bright, rich in both odd and even harmonics.
- **Triangle**: Softer and clearer than square, a gentle harmonic spectrum.
- **Pulse**: A variant of square with a thinner, more nasal sound due to a narrow duty cycle.
- **Noise**: Contains all frequencies, perfect for percussive or atmospheric sounds.
- **FM**: Frequency-modulated sine; produces complex, metallic, or bell-like timbres.

You can use any of these keys with the `SYNTHS` dictionary to select the desired waveform for synthesis.

## Advanced Example: Multi-Layer Composition
```
import threading
from algorhythm.synth import initialize, SYNTHS, enable_recording, disable_recording, save_recording
from algorhythm.patternlayer import PatternLayer

# Initialize
stream = initialize(master_volume=0.15)
stream.start()
enable_recording()

# Bass layer
bass = PatternLayer(
    name="Bass",
    pattern=[110, 110, 165, 110],  # A2, A2, E3, A2
    intervals=[0.5] * 4,
    durations=[0.3] * 4,
    amplitudes=[0.5, 0.3, 0.4, 0.3],
    synth='saw',
    lpf_cutoff=800,
    env_params={'attack': 0.01, 'decay': 0.1, 'sustain': 0.3, 'release': 0.2}
)

# Melody layer
melody = PatternLayer(
    name="Melody",
    pattern=[440, 494, 523, 494],  # A4, B4, C5, B4
    intervals=[0.25] * 4,
    durations=[0.2] * 4,
    amplitudes=[0.2] * 4,
    synth='sine'
)

# Start layers with timing
bass.start()
threading.Timer(2.0, melody.start).start()

# Play for 10 seconds
time.sleep(10)

# Cleanup
bass.stop()
melody.stop()
disable_recording()
save_recording('composition.wav')
stream.stop()
stream.close()
```

## Music Theory Utilities

### Generate Chords:
```
from algorhythm.chords_library import chord_notes, chord_inversion, list_chords

# Available chord types: 'major', 'minor', 'maj7', 'min7', 'dom7', 'sus2', 'sus4'

# Get chord notes with frequencies
em_chord = chord_notes('E', 'minor', 4)
# Returns: [('E', 4, 329.63), ('G', 4, 392.00), ('B', 4, 493.88)]

# Create inversions
first_inversion = chord_inversion(em_chord, 1)  # G in bass
second_inversion = chord_inversion(em_chord, 2) # B in bass

# List all chord types for a root
all_c_chords = list_chords('C', 4)
```

---

### Calculate Note Frequencies:
```
from algorhythm.chords_library import get_frequency

# Get frequency for any note and octave
a4_freq = get_frequency('A', 4)  # 440.0 Hz
c4_freq = get_frequency('C', 4)  # 261.63 Hz
```

## API Reference

### synth.py

- `initialize(**config)`: Configure and create audio stream
- `get_config()`: Get current engine configuration
- `add_note(freq, duration, amplitude, synth_func, **effects)`: Queue a note for playback
- `enable_recording()`: Start capturing audio output
- `disable_recording()`: Stop recording
- `save_recording(filename)`: Save recorded audio to WAV file

### patternlayer.py

- `PatternLayer.__init__(...)`: Create a pattern sequencer
- `PatternLayer.start()`: Begin playing the pattern
- `PatternLayer.stop()`: Stop playback
- `PatternLayer.update_pattern(**params)`: Modify pattern parameters in real-time

### chords_library.py

- `get_frequency(note, octave)`: Calculate frequency for a note
- `chord_notes(root_note, chord_type, octave)`: Generate chord note frequencies
- `chord_inversion(notes, inversion)`: Reorder notes for inversions
- `list_chords(root_note, octave)`: Get all chord types for a root

---

## Configuration Options

```
initialize(
    sample_rate=44100,        # Audio sample rate (Hz)
    blocksize=4096,           # Buffer size (samples)
    master_volume=0.15,       # Global volume (0.0-1.0)
    channels=2,               # 1=mono, 2=stereo
    use_fade_window=True,     # Adds fade to all notes
    fade_length=0.03,         # Fade duration (seconds)
    dtype='float32'           # Audio data type
)
```


---

## Requirements

- Python 3.7+
- NumPy >= 1.20.0
- sounddevice >= 0.4.0
- scipy >= 1.7.0

---

## License

MIT License – See LICENSE file for details

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Credits

Created by Niamh Callinan Keenan  
Created for algorithmic music composition and generative audio art.

---

**Happy composing! 🎵**
