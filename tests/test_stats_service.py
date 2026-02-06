from stats_service import compute_comparison_stats, map_outcome_bucket


def test_map_outcome_bucket_basic_cases():
    assert map_outcome_bucket("Dismissed") == "dismissed_or_nolle"
    assert map_outcome_bucket("Nolle Prosequi") == "dismissed_or_nolle"
    assert map_outcome_bucket("Guilty") == "convicted"
    assert map_outcome_bucket(None) == "other_or_unknown"


def test_compute_comparison_stats_single_outcome():
    rows = [
        {
            "charge_disposition": "Dismissed",
            "disposition_date": "2023-01-01",
            "arraignment_date": "2022-12-01",
        }
    ]

    stats = compute_comparison_stats(
        rows,
        user_stage_id="POST_ARRAIGNMENT_PRETRIAL",
        offense_category=None,
        charge_class=None,
    )

    assert stats["sample_size"] == 1
    assert stats["outcomes_counts"]["dismissed_or_nolle"] == 1
    assert stats["outcomes_pct"]["dismissed_or_nolle"] == 100.0


def test_compute_comparison_stats_empty_input():
    stats = compute_comparison_stats(
        [],
        user_stage_id="POST_ARRAIGNMENT_PRETRIAL",
        offense_category=None,
        charge_class=None,
    )

    assert stats["sample_size"] == 0
    assert stats["outcomes_pct"] == {}
