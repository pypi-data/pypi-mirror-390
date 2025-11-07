# Copyright (c) 2025, Zhendong Peng (pzd17@tsinghua.org.cn)
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

from itertools import groupby
from typing import Any, Dict, List, Union

import torch
import torchaudio.functional as F
from lhotse.supervision import AlignmentItem
from tgt import io
from tgt.core import Interval, IntervalTier, TextGrid

io.unicode = str


def forced_align(log_probs: torch.Tensor, targets: torch.Tensor, blank: int = 0) -> List[AlignmentItem]:
    """
    Perform CTC alignment on the given log probabilities and targets.

    Args:
        log_probs (torch.Tensor): Log probabilities of CTC emission output. Tensor of shape (T, C), where T is the input length, and C is the number of characters in the alphabet including blank.
        targets (torch.Tensor): Target sequence. Tensor of shape (L,), where L is the target length.
        blank (int): The index of the blank symbol in CTC emission. Default is 0.
    Returns:
        List[AlignmentItem]: A list of AlignmentItem objects representing the alignments.
    """
    log_probs, targets = log_probs.unsqueeze(0).cpu(), targets.unsqueeze(0).cpu()
    alignments, scores = F.forced_align(log_probs, targets, blank=blank)
    alignments, scores = alignments[0], scores[0]

    items = []
    # use enumerate to keep track of the original indices, then group by token value
    for token, group in groupby(enumerate(alignments), key=lambda item: item[1]):
        if token == blank:
            continue
        group = list(group)
        start = group[0][0]
        duration = len(group)
        score = scores[start : start + duration].sum().item()
        items.append(AlignmentItem(token.item(), start, duration, score))
    return items


def save_text_grid(
    alignments: List[Union[AlignmentItem, Dict[str, Any], Interval]], save_path: str, format: str = "short"
):
    """
    Saves the given alignments to a TextGrid file.

    Args:
        alignments (List[Union[AlignmentItem, Dict[str, Any], Interval]]): A list of alignments to be saved.
            Each alignment can be an AlignmentItem, a dictionary, or an Interval object.
        save_path (str): The file path where the TextGrid will be saved.
        format (str): The format of the TextGrid file. Default is "short".
    """
    tier = IntervalTier()
    for alignment in alignments:
        if isinstance(alignment, Interval):
            start_time = alignment.start_time
            end_time = alignment.end_time
            text = alignment.text
        elif isinstance(alignment, AlignmentItem):
            start_time = alignment.start
            end_time = alignment.end
            text = alignment.symbol
        else:
            start_time = alignment.get("start_time", alignment.get("start", 0))
            end_time = alignment.get("end_time", alignment.get("end", start_time + alignment.get("duration", 0)))
            text = alignment.get("text", alignment.get("symbol", ""))
        interval = Interval(round(start_time, 3), round(end_time, 3), text)
        tier.add_interval(interval)

    text_grid = TextGrid()
    text_grid.add_tier(tier)
    io.write_to_file(text_grid, save_path, format)
