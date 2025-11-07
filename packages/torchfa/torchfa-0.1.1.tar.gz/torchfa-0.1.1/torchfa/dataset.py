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

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from g2p_mix import G2pMix
from lhotse import CutSet, MonoCut, MultiCut, Recording, SupervisionSegment, validate
from lhotse.cut.data import DataCut
from lhotse.dataset import SimpleCutSampler, UnsupervisedDataset
from lhotse.dataset.collation import collate_audio
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)


class Dataset(UnsupervisedDataset):
    """
    A variant of UnsupervisedDataset that provides waveform samples instead of features.
    The output is a tensor of shape (C, T), with C being the number of channels and T the number of audio samples.
    In this implementation, there will always be a single channel.

    Returns:

    .. code-block::

        {
            'audio': (B x NumSamples) float tensor
            'audio_lens': (B, ) int tensor
        }
    """

    def __init__(self, cuts: CutSet, batch_size: int, sampling_rate: int, num_workers: int = 0) -> None:
        super().__init__()
        self.cuts = cuts
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.sampling_rate = sampling_rate

        self.g2per = G2pMix(tn=True)

    @staticmethod
    def build_cuts(wav_paths: List[Union[Path, str]], texts: List[str]) -> CutSet:
        """
        Builds a CutSet from a list of audio file paths and their corresponding transcripts.
        Args:
            wav_paths (List[Union[Path, str]]): A list of audio file paths.
            texts (List[str]): A list of corresponding transcripts.
        Returns:
            CutSet: A CutSet containing audio cuts with their supervisions.
        """
        cuts = []
        for wav_path, text in zip(wav_paths, texts):
            rec = Recording.from_file(wav_path)
            sup = SupervisionSegment(
                id=rec.id,
                recording_id=rec.id,
                start=0,
                duration=rec.duration,
                text=text,
            )
            cuts.append(
                (MonoCut if rec.num_channels == 1 else MultiCut)(
                    id=rec.id,
                    start=0,
                    duration=rec.duration,
                    channel=rec.channel_ids,
                    recording=rec,
                    supervisions=[sup],
                )
            )
        return CutSet.from_cuts(cuts)

    def process_cut(self, cut: DataCut) -> DataCut:
        """
        Processes a cut by ensuring it is mono, resampling it to the target sampling rate, and trimming it to the supervisions.
        Args:
            cut (DataCut): The cut to process.
        Returns:
            DataCut: The processed cut.
        """
        if cut.num_channels > 1:
            logger.warning(f"Select the first channel from {cut.num_channels} channels of {cut.id}.")
            # to_mono(mono_downmix=True) will create a new cut (start=0) without supervisions.
            cut = cut.to_mono()[0]
        if cut.sampling_rate != self.sampling_rate:
            logger.warning(f"Resample {cut.id} from {cut.sampling_rate} to {self.sampling_rate}.")
            cut = cut.resample(self.sampling_rate)
        return cut.trim_to_supervisions()[0]

    def g2p(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Converts text to phonemes and words using G2P.
        Args:
            text (str): The input text to convert.
        Returns:
            Tuple[List[str], List[str]]: A tuple containing two lists:
                - A list of phonemes (characters).
                - A list of words.
        """
        chars = []
        words = []
        for item in self.g2per.g2p(text):
            if item["lang"] == "ZH":
                chars.append("".join(item["phones"])[:-1])
                words.append(item["word"])
            elif item["lang"] == "EN":
                chars.append(item["word"].lower())
                words.append(item["word"])
            else:
                chars.append("'")
                words.append(item["word"])
        return chars, words

    def __getitem__(self, cuts: CutSet) -> Dict[str, Any]:
        """
        Processes a batch of cuts and returns a dictionary containing audio data, lengths, characters, and words.
        Args:
            cuts (CutSet): A CutSet containing the cuts to process.
        Returns:
            Dict[str, Any]: A dictionary with the following keys:
                - 'cuts': The processed cuts.
                - 'audio': A tensor of audio samples.
                - 'audio_lens': A tensor of audio lengths.
                - 'chars': A list of phonemes (characters).
                - 'words': A list of words.
        """
        self._validate(cuts)

        audio, audio_lens = collate_audio(cuts.map(self.process_cut))
        chars, words = zip(*[self.g2p(cut.supervisions[0].text) for cut in cuts])
        return {
            "cuts": cuts,
            "audio": audio,
            "audio_lens": audio_lens,
            "chars": chars,
            "words": words,
        }

    def _validate(self, cuts: CutSet) -> None:
        validate(cuts)
        for cut in cuts:
            assert cut.has_recording
            assert len(cut.supervisions) == 1, f"{cut.id} has more than one supervision: {len(cut.supervisions)}."
            # Timestamps of the supervision are relative to the cut
            assert cut.supervisions[0].start >= 0
            assert round(cut.supervisions[0].end, 3) <= round(cut.duration, 3)

    @property
    def dataloader(self) -> DataLoader:
        return DataLoader(
            self,
            sampler=SimpleCutSampler(self.cuts, max_cuts=self.batch_size),
            batch_size=None,
            num_workers=self.num_workers,
        )
