"""Alpha360 TCN 结构（训练与推理共用）。"""

from __future__ import annotations

try:
    import torch
    import torch.nn as nn
except ImportError:  # pragma: no cover
    torch = None  # type: ignore
    nn = None  # type: ignore


class TCNScore(nn.Module if nn else object):  # type: ignore[misc]
    """6 通道 × seq_len 卷积 → 5 日 forward return 回归。"""

    def __init__(self, channels: int = 6, hidden: int = 32) -> None:
        if nn is None:
            raise ImportError("需要 torch: pip install -r requirements-ml.txt")
        super().__init__()
        self.conv1 = nn.Conv1d(channels, hidden, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(hidden, hidden, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = self.pool(x).squeeze(-1)
        return self.fc(x).squeeze(-1)
