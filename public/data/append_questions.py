#!/usr/bin/env python3
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR

TARGETS = {
    "People": "questions_people.json",
    "Process": "questions_process.json",
    "Business": "questions_business.json",
}


def usage() -> None:
    print(
        "Usage:\n"
        "  python3 public/data/append_questions.py            # summary of current banks\n"
        "  python3 public/data/append_questions.py <input.json>\n"
        "  python3 public/data/append_questions.py --summary-input <input.json>\n"
        "  python3 public/data/append_questions.py --report-duplicates <input.json>\n"
        "Input format: [{ group: string, questions: [...] }, ...]"
    )


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def validate_question(q):
    if not isinstance(q, dict):
        return "Question must be an object"
    if not isinstance(q.get("id"), int):
        return "Question id must be a number"
    if not isinstance(q.get("domain"), str) or not q.get("domain"):
        return "Question domain is required"
    if not isinstance(q.get("questionText"), str) or not q.get("questionText"):
        return "Question text is required"
    return None


def normalize_domain(domain: str):
    value = (domain or "").strip().lower()
    if value == "people":
        return "People"
    if value == "process":
        return "Process"
    if value == "business":
        return "Business"
    return None


def normalize_text(value: str) -> str:
    text = str(value or "").strip().lower()
    return " ".join(text.split())


def infer_question_type(q):
    q_type = q.get("type")
    if isinstance(q_type, str):
        q_type = q_type.strip().lower()
        q_type = "".join(ch for ch in q_type if ch.isalpha())
    else:
        q_type = None
    if not q_type:
        if "hotspot" in q:
            q_type = "hotspot"
        elif "dragdrop" in q:
            q_type = "dragdrop"
        elif "multiselect" in q:
            q_type = "multiselect"
        elif "fillin" in q:
            q_type = "fillin"
        else:
            q_type = "single"
    if q_type == "hot" or q_type == "hotspot":
        return "hotspot"
    if q_type == "dragdrop":
        return "dragdrop"
    if q_type == "multiselect":
        return "multiselect"
    if q_type == "fillin":
        return "fillin"
    return "single"


def summarize_bank(domain: str, questions):
    counts = {
        "single": 0,
        "multiselect": 0,
        "dragdrop": 0,
        "hotspot": 0,
        "fillin": 0,
    }
    for q in questions:
        q_type = infer_question_type(q)
        counts[q_type] = counts.get(q_type, 0) + 1
    return {"domain": domain, "total": len(questions), "counts": counts}


def summarize_grouped_input(payload):
    by_domain = {"People": [], "Process": [], "Business": []}
    group_breakdown = {}
    for group_index, group in enumerate(payload):
        group_name = group.get("group") if isinstance(group, dict) else None
        group_name = group_name if isinstance(group_name, str) and group_name.strip() else f"Group {group_index}"
        group_breakdown[group_name] = group_breakdown.get(group_name, {"total": 0, "types": {}})
        questions = group.get("questions") if isinstance(group, dict) else None
        questions = questions if isinstance(questions, list) else []
        for q in questions:
            group_breakdown[group_name]["total"] += 1
            domain = normalize_domain(q.get("domain"))
            if domain in by_domain:
                by_domain[domain].append(q)
            q_type = infer_question_type(q)
            group_breakdown[group_name]["types"][q_type] = (
                group_breakdown[group_name]["types"].get(q_type, 0) + 1
            )

    summaries = [summarize_bank(domain, items) for domain, items in by_domain.items()]
    total_all = sum(s["total"] for s in summaries)
    overall = {"single": 0, "multiselect": 0, "dragdrop": 0, "hotspot": 0, "fillin": 0}
    for s in summaries:
        for key, val in s["counts"].items():
            overall[key] = overall.get(key, 0) + val

    print("Input Summary")
    for s in summaries:
        c = s["counts"]
        print(
            f"- {s['domain']}: {s['total']} total | "
            f"single {c.get('single', 0)}, "
            f"multi {c.get('multiselect', 0)}, "
            f"drag {c.get('dragdrop', 0)}, "
            f"hotspot {c.get('hotspot', 0)}, "
            f"fill {c.get('fillin', 0)}"
        )
    print(
        f"- Overall: {total_all} total | "
        f"single {overall.get('single', 0)}, "
        f"multi {overall.get('multiselect', 0)}, "
        f"drag {overall.get('dragdrop', 0)}, "
        f"hotspot {overall.get('hotspot', 0)}, "
        f"fill {overall.get('fillin', 0)}"
    )
    print("\nGroup details")
    for name, stats in group_breakdown.items():
        t = stats["types"]
        print(
            f"- {name}: {stats['total']} total | "
            f"single {t.get('single', 0)}, "
            f"multi {t.get('multiselect', 0)}, "
            f"drag {t.get('dragdrop', 0)}, "
            f"hotspot {t.get('hotspot', 0)}, "
            f"fill {t.get('fillin', 0)}"
        )


def print_summary() -> int:
    summaries = []
    for domain, file_name in TARGETS.items():
        file_path = DATA_DIR / file_name
        if not file_path.exists():
            print(f"{file_name}: missing")
            continue
        data = read_json(file_path)
        if not isinstance(data, list):
            print(f"{file_name}: invalid (not an array)")
            continue
        summaries.append(summarize_bank(domain, data))

    if not summaries:
        print("No question banks found.")
        return 0

    total_all = sum(s["total"] for s in summaries)
    overall = {"single": 0, "multiselect": 0, "dragdrop": 0, "hotspot": 0, "fillin": 0}
    for s in summaries:
        for key, val in s["counts"].items():
            overall[key] = overall.get(key, 0) + val

    print("Question Bank Summary")
    for s in summaries:
        c = s["counts"]
        print(
            f"- {s['domain']}: {s['total']} total | "
            f"single {c.get('single', 0)}, "
            f"multi {c.get('multiselect', 0)}, "
            f"drag {c.get('dragdrop', 0)}, "
            f"hotspot {c.get('hotspot', 0)}, "
            f"fill {c.get('fillin', 0)}"
        )
    print(
        f"- Overall: {total_all} total | "
        f"single {overall.get('single', 0)}, "
        f"multi {overall.get('multiselect', 0)}, "
        f"drag {overall.get('dragdrop', 0)}, "
        f"hotspot {overall.get('hotspot', 0)}, "
        f"fill {overall.get('fillin', 0)}"
    )
    print("Note: group names are not stored in the bank files, so summary is by domain.")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        return print_summary()

    if sys.argv[1] in ("--summary-input", "--input-summary"):
        if len(sys.argv) < 3:
            usage()
            return 1
        input_path = (SCRIPT_DIR / sys.argv[2]).resolve()
        payload = read_json(input_path)
        if not isinstance(payload, list):
            raise ValueError("Input JSON must be an array of groups")
        summarize_grouped_input(payload)
        return 0

    report_duplicates = False
    if sys.argv[1] in ("--report-duplicates", "--report-dup"):
        if len(sys.argv) < 3:
            usage()
            return 1
        report_duplicates = True
        input_path = (SCRIPT_DIR / sys.argv[2]).resolve()
    else:
        input_path = (SCRIPT_DIR / sys.argv[1]).resolve()

    payload = read_json(input_path)

    if not isinstance(payload, list):
        raise ValueError("Input JSON must be an array of groups")

    buckets = {"People": [], "Process": [], "Business": []}
    group_stats = {}
    errors = []

    for group_index, group in enumerate(payload):
        questions = group.get("questions") if isinstance(group, dict) else None
        questions = questions if isinstance(questions, list) else []
        group_name = group.get("group") if isinstance(group, dict) else None
        group_name = group_name if isinstance(group_name, str) and group_name.strip() else f"Group {group_index}"
        if group_name not in group_stats:
            group_stats[group_name] = {"total": 0, "added": 0, "text_duplicates": 0}
        for idx, q in enumerate(questions):
            group_stats[group_name]["total"] += 1
            err = validate_question(q)
            if err:
                errors.append(f"Group {group_index}, question {idx}: {err}")
                continue
            domain = normalize_domain(q.get("domain"))
            if not domain:
                errors.append(
                    f"Group {group_index}, question {idx}: Unknown domain '{q.get('domain')}'"
                )
                continue
            buckets[domain].append(q)
            q["_group_name"] = group_name

    if errors:
        print("Validation errors:\n" + "\n".join(f"- {e}" for e in errors), file=sys.stderr)
        return 1

    added_counts = {}
    total_counts = {}
    reassigned_counts = {}
    text_duplicate_counts = {}
    duplicate_examples = []
    for domain, file_name in TARGETS.items():
        file_path = DATA_DIR / file_name
        existing = read_json(file_path)
        if not isinstance(existing, list):
            raise ValueError(f"{file_name} does not contain an array")

        existing_ids = {q.get("id") for q in existing}
        existing_texts = {normalize_text(q.get("questionText")) for q in existing if q.get("questionText")}
        incoming = buckets[domain]
        deduped = []
        duplicates = []
        reassigned = 0
        for q in incoming:
            q_text = normalize_text(q.get("questionText"))
            if q_text in existing_texts:
                duplicates.append(q)
                if report_duplicates:
                    # find a matching existing question (first match)
                    match = next(
                        (item for item in existing if normalize_text(item.get("questionText")) == q_text),
                        None,
                    )
                    if match:
                        duplicate_examples.append(
                            {
                                "domain": domain,
                                "input_id": q.get("id"),
                                "existing_id": match.get("id"),
                                "questionText": q.get("questionText"),
                            }
                        )
            else:
                if q.get("id") in existing_ids:
                    new_id = max(existing_ids) + 1 if existing_ids else 1
                    while new_id in existing_ids:
                        new_id += 1
                    q["id"] = new_id
                    reassigned += 1
                existing_ids.add(q.get("id"))
                existing_texts.add(q_text)
                deduped.append(q)
        for q in deduped:
            group_name = q.pop("_group_name", "Unknown")
            if group_name in group_stats:
                group_stats[group_name]["added"] += 1
        for q in duplicates:
            group_name = q.get("_group_name", "Unknown")
            if group_name in group_stats:
                group_stats[group_name]["text_duplicates"] += 1
        merged = existing + deduped

        write_json(file_path, merged)
        added_counts[domain] = len(deduped)
        total_counts[domain] = len(merged)
        reassigned_counts[domain] = reassigned
        text_duplicate_counts[domain] = len(duplicates)
        print(
            f"{file_name}: +{len(deduped)} new (skipped {len(duplicates)} text-duplicates, reassigned {reassigned} IDs)"
        )

    total_added = sum(added_counts.values())
    total_questions = sum(total_counts.values())
    print("\nSummary")
    for domain in ("People", "Process", "Business"):
        print(
            f"- {domain}: added {added_counts.get(domain, 0)}, "
            f"text-duplicates {text_duplicate_counts.get(domain, 0)}, "
            f"reassigned IDs {reassigned_counts.get(domain, 0)}, "
            f"total {total_counts.get(domain, 0)}"
        )
    print(f"- Total added: {total_added}")
    print(f"- Total questions: {total_questions}")

    print("\nGroup details")
    for name, stats in group_stats.items():
        print(
            f"- {name}: input {stats['total']}, added {stats['added']}, "
            f"text-duplicates {stats['text_duplicates']}"
        )

    if report_duplicates and duplicate_examples:
        print("\nDuplicate examples (by questionText)")
        for item in duplicate_examples[:20]:
            print(
                f"- {item['domain']}: input id {item['input_id']} "
                f"matches existing id {item['existing_id']} | {item['questionText']}"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
