def render_json_report(scan_results, summary_stats):
    from json import dumps
    results = {
        "summary": summary_stats,
        "tools": {k: v.__dict__ for k, v in scan_results.items()},
    }
    return dumps(results, indent=2)
