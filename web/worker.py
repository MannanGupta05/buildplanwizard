import os
import sys
import time
import traceback
from datetime import datetime

# Handle both relative and absolute imports
try:
    from .database import (
        claim_next_analysis_job,
        get_connection,
        mark_analysis_job_completed,
        mark_analysis_job_failed,
        set_map_analysis_status,
        update_map_analysis,
    )
    from .analysis import analyze_map_with_ai
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from database import (
        claim_next_analysis_job,
        get_connection,
        mark_analysis_job_completed,
        mark_analysis_job_failed,
        set_map_analysis_status,
        update_map_analysis,
    )
    from analysis import analyze_map_with_ai


def safe_print(message):
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        safe_message = message.encode("ascii", "replace").decode("ascii")
        print(safe_message, flush=True)
    except Exception as exc:
        print(f"Print error: {str(exc)}", flush=True)


def build_report(filename, overall_status, results):
    report = f"Map Analysis Report for {filename}\n"
    report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"Overall Status: {overall_status.upper()}\n"
    report += "\n"

    if results and any(k != "error" for k in results.keys()):
        report += "RULE COMPLIANCE SUMMARY:\n"
        report += "=" * 55 + "\n"

        rule_mapping = {
            "Habitable Room": "Habitable Room (Bedroom & Drawing Room)",
            "Bathroom": "Bathroom",
            "Store": "Store Room",
        }

        rule_counter = 1
        for rule, result in results.items():
            if rule == "error":
                continue

            clean_rule_name = rule_mapping.get(rule, rule)
            if result.get("passed"):
                status_symbol = "PASS"
            else:
                status_symbol = "FAIL"

            report += f"{rule_counter:2d}. {clean_rule_name:<40}  {status_symbol}\n"
            rule_counter += 1

        report += "=" * 55 + "\n"

    return report


def process_analysis_job(job_id, map_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT image, filename, file_type FROM maps WHERE id = %s", (map_id,))
    map_data = c.fetchone()
    conn.close()

    if not map_data:
        error_report = "Analysis Error: Map data not found\nPlease try uploading again or contact support."
        update_map_analysis(map_id, error_report, "error")
        mark_analysis_job_failed(job_id, "Map data not found")
        return

    file_data, filename, file_type = map_data
    safe_print(f"Starting analysis job_id={job_id} map_id={map_id} filename={filename}")

    try:
        set_map_analysis_status(map_id, "processing")
        results, overall_status, raw_validation, validation_text = analyze_map_with_ai(file_data, filename, file_type)

        if overall_status == "error" or "error" in results:
            error_message = results.get("error", {}).get("message", "Unknown error occurred")
            error_report = f"Analysis Error: {error_message}\nPlease try uploading again or contact support."
            update_map_analysis(map_id, error_report, "error")
            mark_analysis_job_failed(job_id, error_message)
            safe_print(f"Analysis failed for map_id={map_id}: {error_message}")
            return

        report = build_report(filename, overall_status, results)
        update_map_analysis(map_id, report, overall_status)
        mark_analysis_job_completed(job_id)
        safe_print(f"Analysis completed for map_id={map_id} with status={overall_status}")

    except Exception as exc:
        traceback.print_exc()
        error_message = str(exc)
        error_report = f"Analysis Error: {error_message}\nPlease try uploading again or contact support."
        try:
            update_map_analysis(map_id, error_report, "error")
        except Exception:
            traceback.print_exc()
        mark_analysis_job_failed(job_id, error_message)
        safe_print(f"Unhandled worker error for map_id={map_id}: {error_message}")


def run_worker_loop():
    poll_interval = int(os.environ.get("ANALYSIS_JOB_POLL_SECONDS", "3"))
    safe_print(f"Analysis worker started. Poll interval: {poll_interval}s")

    while True:
        try:
            claimed_job = claim_next_analysis_job()
            if not claimed_job:
                time.sleep(poll_interval)
                continue

            job_id, map_id = claimed_job
            process_analysis_job(job_id, map_id)
        except Exception as exc:
            traceback.print_exc()
            safe_print(f"Worker loop error: {str(exc)}")
            time.sleep(poll_interval)


if __name__ == "__main__":
    run_worker_loop()
