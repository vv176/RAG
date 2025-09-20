# qa_chunker.py
# Robust parser for "Question ... / Answer ..." FAQ text files.

import re
from typing import List, Dict, Optional

# Matches a question header line, e.g.:
# "Ques. 1: What is ...", "Question 2 - ...", "Q: What is ..."
Q_HEADER_RE = re.compile(
    r"""^\s*
        (?:Q(?:ues(?:tion)?)?\.?)      # Q / Ques. / Question.
        \s*(?:No\.|\#)?\s*            # optional No. / #
        (?P<num>\d+)?                  # optional number
        \s*[:\-–]\s*                   # ':' or '-' after header
        (?P<q>.+?)\s*$                 # the question text (rest of line)
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Matches an answer header line, e.g.:
# "Ans: It is ...", "Answer - It is ..."
A_HEADER_RE = re.compile(
    r"""^\s*
        (?:Ans(?:wer)?\.?)             # Ans / Answer
        \s*[:\-–]\s*                   # ':' or '-'
        (?P<a>.*)\s*$                  # initial answer text (may continue next lines)
    """,
    re.IGNORECASE | re.VERBOSE,
)

def _normalize(text: str) -> str:
    """Trim outer whitespace and collapse internal runs of spaces on each line."""
    # Keep line breaks (answers often span lines); normalize spaces per line.
    lines = [re.sub(r"[ \t]+", " ", ln.strip()) for ln in text.strip().splitlines()]
    # Drop leading/trailing blank lines after normalization
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)

def parse_qa_pairs_from_text(text: str) -> List[Dict]:
    """
    Parse a FAQ text into Q/A chunks.
    Expected structure (tolerant):
      Ques. 1: <question...>
      Ans: <answer may span multiple lines>
      [blank line(s)]
      Ques. 2: ...
      Ans: ...
      ...
    Returns a list of dicts with: id, question_number (optional), question, answer, chunk_text.
    """
    lines = text.splitlines()
    chunks: List[Dict] = []

    state = "SEEK_Q"  # states: SEEK_Q -> IN_Q -> IN_A
    q_num: Optional[str] = None
    q_lines: List[str] = []
    a_lines: List[str] = []
    id_counter = 1

    def flush_chunk():
        nonlocal id_counter, q_num, q_lines, a_lines
        q = _normalize("\n".join(q_lines))
        a = _normalize("\n".join(a_lines))
        if q and a:
            chunk = {
                "id": id_counter,
                "question_number": q_num if q_num else None,
                "question": q,
                "answer": a,
                "chunk_text": f"Q: {q}\nA: {a}",
            }
            chunks.append(chunk)
            id_counter += 1
        # reset holders
        q_num = None
        q_lines = []
        a_lines = []

    for raw in lines:
        line = raw.rstrip("\n")

        if state == "SEEK_Q":
            m_q = Q_HEADER_RE.match(line)
            if m_q:
                q_num = m_q.group("num")
                q_first = m_q.group("q").strip()
                q_lines = [q_first] if q_first else []
                state = "IN_Q"
            else:
                # ignore any non-question garbage/header lines
                continue

        elif state == "IN_Q":
            m_a = A_HEADER_RE.match(line)
            if m_a:
                a_first = m_a.group("a").strip()
                a_lines = [a_first] if a_first else []
                state = "IN_A"
            else:
                # allow multi-line questions until an Answer header appears
                # but if another Q header appears (malformed doc), start a new Q
                m_q = Q_HEADER_RE.match(line)
                if m_q:
                    # orphan question with no answer -> skip/replace with new question
                    q_num = m_q.group("num")
                    q_first = m_q.group("q").strip()
                    q_lines = [q_first] if q_first else []
                    # still IN_Q
                else:
                    q_lines.append(line.strip())

        elif state == "IN_A":
            m_q = Q_HEADER_RE.match(line)
            if m_q:
                # finalize previous Q/A and start new question
                flush_chunk()
                q_num = m_q.group("num")
                q_first = m_q.group("q").strip()
                q_lines = [q_first] if q_first else []
                state = "IN_Q"
            else:
                m_a = A_HEADER_RE.match(line)
                if m_a and not a_lines:
                    # rare case: answer header split across lines—treat as continuation
                    a_first = m_a.group("a").strip()
                    if a_first:
                        a_lines.append(a_first)
                else:
                    a_lines.append(line.strip())

    # end for: flush any trailing Q/A
    if state == "IN_A":
        flush_chunk()

    return chunks

def parse_qa_file(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    return parse_qa_pairs_from_text(txt)


def _print_pretty(chunks: List[Dict]) -> None:
    for i, ch in enumerate(chunks, 1):
        qn = f"{ch['question_number']}. " if ch.get("question_number") else ""
        print(f"[{i}] {qn}{ch['question']}")
        print(f"    -> {ch['answer']}")
        if i != len(chunks):
            print()


def _print_json(chunks: List[Dict]) -> None:
    import json

    print(json.dumps(chunks, ensure_ascii=False, indent=2))


def main() -> None:
    path = "/Users/vivekanandvivek/RAG/data/FAQ.txt"
    chunks = parse_qa_file(path)
    for ch in chunks:
        print(f"Q: {ch['question']}")
        print(f"A: {ch['answer']}")
        print()


if __name__ == "__main__":
    main()
