__all__ = ["DatasetWriter"]
import io
import pandas as pd
from lt_utils.common import *
from uuid import uuid4
from lt_utils.misc_utils import get_current_time


class DatasetWriter:
    def __init__(
        self,
        base_path: str = "./datasets/",
        max_audios_per_file: int = 5000,
        min_speaker_samples: int = 16,
        compression: Optional[
            Literal["snappy", "gzip", "brotli", "lz4", "zstd"]
        ] = "gzip",
    ):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.max_audios = max_audios_per_file
        self.min_speaker_samples = min_speaker_samples
        # brotli and gzip are the best ones for compression
        self.compression = compression

        self.current_data = {
            "created": get_current_time(),
            "speakers": {},
            "duration": 0.0,
            "audios": 0,
            "num_speakers": 0,
        }

        self.session_total_audios = 0
        self.session_total_duration = 0.0

        self.file_index = self._get_next_file_index()

    def _get_next_file_index(self):
        existing = sorted(self.base_path.glob("tts-part-*.parquet"))
        if not existing:
            return 1
        last = existing[-1].stem.split("-")[-1]
        return int(last) + 1

    def __call__(
        self,
        audio: Union[PathLike, bytes],
        duration: float,
        speaker_id: Union[int, str],
        text: str,
        processed_text: Optional[str] = None,
        sample_rate: int = 24000,
        source: Optional[str] = None,
        score: float = None,
    ):
        if speaker_id not in self.current_data["speakers"]:
            self.current_data["speakers"][speaker_id] = {
                "data": [],
                "total": 0,
                "duration": 0.0,
            }

        audio_entry = {
            "text": text,
            "processed_text": processed_text,
            "audio": audio,
            "sample_rate": sample_rate,
            "duration": duration,
            "source": source,
            "score": score,
        }

        spk = self.current_data["speakers"][speaker_id]
        spk["data"].append(audio_entry)
        spk["total"] += 1
        spk["duration"] += duration

        self.current_data["audios"] += 1
        self.current_data["duration"] += duration
        self.current_data["num_speakers"] = len(self.current_data["speakers"])

        self.session_total_audios += 1
        self.session_total_duration += duration

        if self.current_data["audios"] >= self.max_audios:
            self.save()

    def save(self):
        if self.current_data["audios"] == 0:
            return

        file_path = self.base_path / f"tts-part-{self.file_index:05d}.parquet"

        flat_data = []
        for spk_id, spk_info in self.current_data["speakers"].items():
            for entry in spk_info["data"]:
                flat_data.append({"speaker_id": spk_id, **entry})

        df = pd.DataFrame(flat_data)
        df.to_parquet(file_path, compression=self.compression)

        self._warn_low_speakers()

        self.current_data = {
            "created": get_current_time(),
            "speakers": {},
            "duration": 0.0,
            "audios": 0,
            "num_speakers": 0,
        }
        self.file_index += 1

    def _warn_low_speakers(self):
        for spk_id, spk_info in self.current_data["speakers"].items():
            if spk_info["total"] < self.min_speaker_samples:
                print(f"Warning: Speaker {spk_id} has only {spk_info['total']} samples")

    def __repr__(self):
        return f"DatasetWriter(current_file=tts-part-{self.file_index:05d}.parquet, total_audios={self.session_total_audios}, total_duration={self.session_total_duration})"
