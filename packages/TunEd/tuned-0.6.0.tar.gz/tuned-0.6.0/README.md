# TunEd

## Description

**TunEd** is a command-line tuning tool.

## Dependencies

- Python >= 3.12
- sounddevice >= 0.4.6
- numpy >= 1.26.4
- scypy >= 1.16.1
- librosa >= 0.11.0
- aubio >= 0.4.9

**TunEd** use **sounddevice** library to stream audio from your computer's microphone.

**sounddevice** need install of **PortAudio**.

- For Debian / Ubuntu Linux:

```bash
~$ apt-get install portaudio19-dev python-all-dev
```

## Installation

Using pip:

```bash
~ $ pip install tuned
```

With source:

```bash
~ $ git clone https://framagit.org/drd/tuned.git
```

Install requirements:

```bash
~ $ pip install -r requirements_dev.txt
```

To create a python package, go to inside tuned directory:

```bash
~ $ cd tuned
```

Build the package in an isolated environment, generating a source-distribution and wheel in the directory dist/ (<https://build.pypa.io/en/stable/>):

```bash
~$ python -m build
```

To install it:

```bash
~ $ pip install ./dist/tuned-0.3.0-py3-none-any.whl
```

## Usage

Launch TunEd with standard tuning frequency (@440㎐):

```bash
~$ tuned
```

### Global Parameters

- **`--frequency <int>`** / **`-f <int>`**: Sets the reference frequency for A4 (e.g., 442). Default: `440`.
- **`--mod <mode>`** / **`-m <mode>`**: Chooses the detection mode.
- **`--verbose`** / **`-v`**: Increases the amount of information displayed.

### Detection Modes

#### Note detection (default)

Detects a single note and displays its tuning accuracy.

```bash
~$ tuned -m note
```
- **`--monitoring`**: Activates audio monitoring (routes the input sound to the output).

#### Chord detection

Identifies the played chord and details its component notes.

```bash
~$ tuned -m chord
```
- **`--monitoring`**: Activates audio monitoring (routes the input sound to the output).
- **`--no-harmonics-identification`** / **`-nohi`**: Disables the identification of harmonics in chord analysis. This can improve performance but may reduce accuracy for complex chords.

#### Metronome

A visual metronome that displays the beat.

```bash
~$ tuned -m metronome
```

- **`--bpm <int>`**: Sets the beats per minute. Default: `60`.
- **`--time-signature <n/d>`** / **`-ts <n/d>`**: Sets the time signature (e.g., '4/4', '3/8'). Default: `4/4`.

### Verbosity Levels (`-v`)

You can stack the `-v` flag to display more information.

- **(no flag)**: Basic display for the selected mode.
- **`-v`**: **Precision**: Shows the tuning offset in cents.
- **`-vv`**: **Frequency**: Adds the frequency of the detected note(s) in Hz.
- **`-vvv`**: **Signal Level**: Adds the signal strength in dB.
- **`-vvvv`**: **Execution Time**: Adds the processing time for each analysis loop.

## Authors

- **drd** - <drd.ltt000@gmail.com> - Main developper

## License

TunEd is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

TunEd is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
