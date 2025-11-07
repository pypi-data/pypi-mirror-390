# torchfa

[![PyPI](https://img.shields.io/pypi/v/torchfa)](https://pypi.org/project/torchfa/)
[![License](https://img.shields.io/github/license/pengzhendong/torchfa)](LICENSE)

A Python package for performing forced alignment on audio files using Torchaudio's MMS model. This tool aligns audio with text transcripts to provide precise timing information for each word, making it useful for speech analysis, subtitling, and other applications requiring accurate speech-text synchronization.

## Features

- High-accuracy forced alignment using Torchaudio's MMS model
- Support for both Chinese and English text
- Batch processing capabilities for multiple audio files
- Output aligned segments in various formats including TextGrid

## Installation

```bash
pip install torchfa
```

## Usage

### Basic Usage

```python
from torchfa import TorchaudioForcedAligner

aligner = TorchaudioForcedAligner()

audio = "assets/clean_speech.wav"
transcript = "关服务高端产品仍处于供不应求的局面"
cut = aligner.align_audios(audio, transcript)

# Save aligned audio segments
cut.trim_to_alignments("word").save_audios("./")

# Print alignment results
for alignment in cut.supervisions[0].alignment["word"]:
    print(alignment)
```

Output:

```
AlignmentItem(symbol='关', start=0.02, duration=0.121, score=0.21)
AlignmentItem(symbol='服', start=0.241, duration=0.141, score=0.07)
AlignmentItem(symbol='务', start=0.502, duration=0.101, score=0.49)
AlignmentItem(symbol='高', start=0.724, duration=0.181, score=0.97)
AlignmentItem(symbol='端', start=0.945, duration=0.141, score=0.52)
AlignmentItem(symbol='产', start=1.126, duration=0.201, score=0.81)
AlignmentItem(symbol='品', start=1.367, duration=0.141, score=0.35)
AlignmentItem(symbol='仍', start=1.608, duration=0.201, score=0.89)
AlignmentItem(symbol='处', start=1.869, duration=0.121, score=0.72)
AlignmentItem(symbol='于', start=2.09, duration=0.06, score=0.96)
AlignmentItem(symbol='供', start=2.251, duration=0.161, score=0.95)
AlignmentItem(symbol='不', start=2.452, duration=0.06, score=0.69)
AlignmentItem(symbol='应', start=2.573, duration=0.161, score=0.63)
AlignmentItem(symbol='求', start=2.754, duration=0.141, score=0.95)
AlignmentItem(symbol='的', start=2.935, duration=0.08, score=0.99)
AlignmentItem(symbol='局', start=3.075, duration=0.101, score=0.98)
AlignmentItem(symbol='面', start=3.256, duration=0.221, score=0.94)
```

### Saving to TextGrid Format

```python
from torchfa import TorchaudioForcedAligner
from torchfa.utils import save_text_grid

aligner = TorchaudioForcedAligner()

audio = "assets/clean_speech.wav"
transcript = "关服务高端产品仍处于供不应求的局面"
cut = aligner.align_audios(audio, transcript)

# Save as TextGrid file
save_text_grid(cut.supervisions[0].alignment["word"], "output.TextGrid", "long")
```

### Batch Processing

```python
from torchfa import TorchaudioForcedAligner

aligner = TorchaudioForcedAligner(batch_size=4)  # Process 4 files at once

audio_paths = [
    "audio1.wav",
    "audio2.wav",
    "audio3.wav"
]
transcripts = [
    "This is the first transcript.",
    "This is the second transcript.",
    "This is the third transcript."
]

cuts = aligner.align_audios(audio_paths, transcripts)

for cut in cuts:
    for alignment in cut.supervisions[0].alignment["word"]:
        print(alignment)
```

## License

[MIT](LICENSE)
