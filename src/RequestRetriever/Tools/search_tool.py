"""Fast, dependency-light incident search (BM25 + token coverage + character n-grams).
The Excel workbook is loaded once and all document features are precomputed.
"""
from collections import Counter
from pathlib import Path
import math
import re
import pandas as pd

DEFAULT_EXCEL = Path(__file__).resolve().parents[3] / "data" / "IncidentResolution.xlsx"
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "for", "from",
    "has", "have", "in", "is", "it", "of", "on", "or", "our", "the", "to", "was",
    "were", "when", "while", "with", "unable", "user", "issue", "issues", "error",
    "errors", "problem", "problems", "please", "not", "appearing", "showing",
}
LABELS = ("Problem Statement", "Impact", "RCA", "Resolution", "Defect")


def _tokens(value: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", str(value).lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def _ngrams(tokens: list[str], n: int = 3) -> frozenset[str]:
    text = " ".join(tokens)
    if not text:
        return frozenset()
    if len(text) < n:
        return frozenset((text,))
    return frozenset(text[i:i+n] for i in range(len(text)-n+1))


def _parse_resolution(value: str) -> dict[str, str]:
    result = {label: "Not provided in the knowledge base" for label in LABELS}
    raw = str(value or "")
    pattern = re.compile(r"(?:^|\n)\s*(Problem Statement|Impact|RCA|Resolution|Defect(?:\s*ID)?)\s*:\s*", re.I)
    matches = list(pattern.finditer(raw))
    for i, match in enumerate(matches):
        key = match.group(1).lower().replace(" ", "")
        label = "Defect" if key.startswith("defect") else next(x for x in LABELS if x.lower().replace(" ", "") == key)
        end = matches[i+1].start() if i+1 < len(matches) else len(raw)
        value = raw[match.end():end].strip()
        if value:
            result[label] = value
    return result


class IncidentSearch:
    def __init__(self, excel_file: str | Path = DEFAULT_EXCEL):
        self.excel_file = Path(excel_file)
        if not self.excel_file.is_file():
            raise FileNotFoundError(f"Knowledge-base Excel file not found: {self.excel_file}")
        frame = pd.read_excel(self.excel_file, sheet_name="Resolution_Comments", usecols=["Issue", "Resolution"])
        self.records = []
        for row_number, row in frame.iterrows():
            issue = "" if pd.isna(row["Issue"]) else str(row["Issue"]).strip()
            raw = "" if pd.isna(row["Resolution"]) else str(row["Resolution"]).strip()
            if not issue:
                continue
            fields = _parse_resolution(raw)
            search_text = " ".join((issue, fields["Problem Statement"], fields["Impact"], fields["RCA"]))
            tokens = _tokens(search_text)
            self.records.append({
                "row_number": int(row_number) + 2, "issue": issue,
                "problem_statement": fields["Problem Statement"], "impact": fields["Impact"],
                "rca": fields["RCA"], "resolution": fields["Resolution"],
                "defect_id": fields["Defect"], "_tokens": tokens,
                "_tf": Counter(tokens), "_token_set": set(tokens), "_chars": _ngrams(tokens),
                "_issue_tokens": set(_tokens(issue)),
            })
        if not self.records:
            raise ValueError("No usable incident rows were found in the Excel knowledge base.")
        self.doc_count = len(self.records)
        self.avgdl = sum(len(r["_tokens"]) for r in self.records) / self.doc_count
        self.doc_freq = Counter()
        for record in self.records:
            self.doc_freq.update(record["_token_set"])

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        q_tokens = _tokens(query)
        if not q_tokens:
            # Short queries such as "issue" contain only stop words; retain useful raw tokens.
            q_tokens = re.findall(r"[a-z0-9]+", str(query).lower())
        if not q_tokens:
            return []
        q_set = set(q_tokens)
        q_chars = _ngrams(q_tokens)
        q_phrase = " ".join(q_tokens)
        ranked = []
        k1, b = 1.5, 0.75
        for record in self.records:
            tf = record["_tf"]
            dl = len(record["_tokens"])
            bm25 = 0.0
            for term in q_set:
                freq = tf.get(term, 0)
                if not freq:
                    continue
                df = self.doc_freq.get(term, 0)
                idf = math.log(1 + (self.doc_count - df + 0.5) / (df + 0.5))
                denom = freq + k1 * (1 - b + b * dl / max(self.avgdl, 1))
                bm25 += idf * freq * (k1 + 1) / denom
            coverage = len(q_set & record["_token_set"]) / max(len(q_set), 1)
            char_score = len(q_chars & record["_chars"]) / max(len(q_chars | record["_chars"]), 1)
            issue_coverage = len(q_set & record["_issue_tokens"]) / max(len(q_set), 1)
            # Normalized and bounded; issue-title matches receive a small boost.
            bm25_norm = bm25 / (bm25 + 2.5) if bm25 else 0.0
            score = 0.45 * coverage + 0.30 * bm25_norm + 0.15 * char_score + 0.10 * issue_coverage
            item = {k: v for k, v in record.items() if not k.startswith("_")}
            item["retrieval_score"] = round(min(score, 1.0), 4)
            ranked.append(item)
        ranked.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return ranked[:max(1, min(int(top_k), len(ranked)))]
