from typing import List

from .base_parser import BaseParser, ChunkRecord


class TextParser(BaseParser):
    def parse(self, file_path: str) -> List[ChunkRecord]:
        records = []
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            chunks = self.chunk_text(text)
            for chunk in chunks:
                record = ChunkRecord(
                    chunk=chunk,
                    source_path=file_path,
                    page=1
                )
                records.append(record)
        return records
