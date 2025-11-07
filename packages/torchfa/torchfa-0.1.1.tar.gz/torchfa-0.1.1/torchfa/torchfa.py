# Copyright (c) 2024, Zhendong Peng (pzd17@tsinghua.org.cn)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Union

import torch
from lhotse import CutSet
from lhotse.supervision import AlignmentItem
from torchaudio.pipelines import MMS_FA as bundle

from torchfa.dataset import Dataset


class TorchaudioForcedAligner:
    def __init__(self, batch_size: int = 1, device: str = "cpu"):
        self.batch_size = batch_size
        self.device = torch.device(device)
        self.model = bundle.get_model(with_star=False)
        self.model.to(self.device)

        self.sample_rate = bundle.sample_rate
        self.aligner = bundle.get_aligner()
        self.tokenizer = bundle.get_tokenizer()

    @property
    def labels(self):
        return bundle.get_labels()

    def align_cuts(self, cuts: CutSet):
        """
        Aligns the given cuts using the torchaudio forced aligner.

        Args:
            cuts (CutSet): A CutSet containing audio cuts to be aligned.
        Yields:
            CutSet: A CutSet with aligned supervisions.
        """
        dset = Dataset(cuts, batch_size=self.batch_size, sampling_rate=self.sample_rate)
        for batch in dset.dataloader:
            with torch.inference_mode():
                audio = batch["audio"].to(self.device)
                audio_lens = batch["audio_lens"].to(self.device)
                emissions, lengths = self.model(audio, audio_lens)

            for idx in range(audio.size(0)):
                cut = batch["cuts"][idx]
                words = batch["words"][idx]
                chars = self.tokenizer(batch["chars"][idx])
                ratio = audio_lens[idx] / lengths[idx] / self.sample_rate
                offset = cut.start + cut.supervisions[0].start

                # forced alignment
                alignments = []
                token_spans = self.aligner(emissions[idx][: lengths[idx]], chars)
                for word, spans in zip(words, token_spans):
                    start = spans[0].start
                    duration = spans[-1].end - start
                    start = round(float(ratio * start) + offset, 3)
                    duration = round(float(ratio * duration), 3)
                    score = round(sum(s.score * len(s) for s in spans) / sum(len(s) for s in spans), 2)
                    alignments.append(AlignmentItem(word, start, duration, score))

                supervision = cut.supervisions[0].with_alignment("word", alignments)
                cut.supervisions[0] = supervision
                yield cut

    def align_audios(self, audio_paths: Union[List[str], str], transcripts: Union[List[str], str]):
        """
        Aligns audio files with their corresponding transcripts.

        Args:
            audio_paths (Union[List[str], str]): A list of audio file paths or a single audio file path.
            transcripts (Union[List[str], str]): A list of corresponding transcripts or a single transcript.
        Returns:
            CutSet: A CutSet containing aligned audio cuts.
        """
        is_list = not isinstance(audio_paths, str)
        if not is_list:
            assert isinstance(transcripts, str)
            audio_paths = [audio_paths]
            transcripts = [transcripts]
        cuts = Dataset.build_cuts(audio_paths, transcripts)
        cuts = self.align_cuts(cuts)
        return list(cuts)[0] if not is_list else cuts
