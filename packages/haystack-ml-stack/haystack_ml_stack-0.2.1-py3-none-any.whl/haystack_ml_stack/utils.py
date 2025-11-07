import pandas as pd
import numpy as np
import typing as _t


def stream_tags_cleanup(
    stream, user_favorite_tags: list[str], user_favorite_authors: list[str]
) -> dict:
    stream_tags = stream.get("haystackTags", [])
    is_favorite_tag = (
        any(stream_tag in user_favorite_tags for stream_tag in stream_tags)
        if user_favorite_tags is not None
        else False
    )
    is_favorite_author = (
        stream.get("author", None) in user_favorite_authors
        if user_favorite_authors is not None
        else False
    )
    return {
        "IS_FAVORITE_TAG": is_favorite_tag,
        "IS_FAVORITE_AUTHOR": is_favorite_author,
    }


def browsed_count_cleanups(
    stream,
    position_debiasing: _t.Literal["4_browsed", "all_browsed"] = "4_browsed",
) -> dict:
    position_alias_mapping = {
        "0": "1ST_POS",
        "1": "2ND_POS",
        "2": "3RD_POS",
        "3+": "REST_POS",
    }
    if position_debiasing == "4_browsed":
        suffix = "_UP_TO_4_BROWSED"
    elif position_debiasing == "all_browsed":
        suffix = ""
    else:
        raise ValueError(f"Unexpected position debiasing '{position_debiasing}'.")
    browsed_count_obj = stream.get("PSELECT#24H", {}).get(position_debiasing, {})
    total_selects = 0
    total_browsed = 0
    total_selects_and_watched = 0
    feats = {}
    for position in position_alias_mapping.keys():
        pos_counts = browsed_count_obj.get(position, {})
        total_browsed += pos_counts.get("total_browsed", 0)
        total_selects += pos_counts.get("total_selects", 0)
        total_selects_and_watched += pos_counts.get("total_selects_and_watched", 0)
    if position_debiasing == "4_browsed":
        suffix = "_UP_TO_4_BROWSED"
    elif position_debiasing == "all_browsed":
        suffix = ""
    else:
        raise ValueError("Should not be here.")
    feats[f"STREAM_24H_TOTAL_BROWSED{suffix}"] = total_browsed
    feats[f"STREAM_24H_TOTAL_SELECTS{suffix}"] = total_selects
    feats[f"STREAM_24H_TOTAL_SELECTS_AND_WATCHED{suffix}"] = total_selects_and_watched
    return feats


def device_split_browsed_count_cleanups(
    stream,
    device_type: _t.Literal["TV", "MOBILE"],
    position_debiasing: _t.Literal["4_browsed", "all_browsed"] = "4_browsed",
) -> dict:
    position_alias_mapping = {
        "0": "1ST_POS",
        "1": "2ND_POS",
        "2": "3RD_POS",
        "3+": "REST_POS",
    }
    if position_debiasing == "4_browsed":
        suffix = "_UP_TO_4_BROWSED"
    elif position_debiasing == "all_browsed":
        suffix = ""
    else:
        raise ValueError(f"Unexpected position debiasing '{position_debiasing}'.")

    _validate_device_type(device_type)

    browsed_count_obj = stream.get(f"PSELECT#24H#{device_type}", {}).get(
        position_debiasing, {}
    )
    total_selects = 0
    total_browsed = 0
    total_selects_and_watched = 0
    feats = {}
    for position, alias in position_alias_mapping.items():
        pos_counts = browsed_count_obj.get(position, {})
        total_browsed = pos_counts.get("total_browsed", 0)
        total_selects = pos_counts.get("total_selects", 0)
        total_selects_and_watched = pos_counts.get("total_selects_and_watched", 0)
        feats[f"STREAM_{alias}_{device_type}_24H_TOTAL_BROWSED{suffix}"] = total_browsed
        feats[f"STREAM_{alias}_{device_type}_24H_TOTAL_SELECTS{suffix}"] = total_selects
        feats[f"STREAM_{alias}_{device_type}_24H_TOTAL_SELECTS_AND_WATCHED{suffix}"] = (
            total_selects_and_watched
        )
    return feats


def watched_count_cleanups(stream, entry_contexts: list[str] = None) -> dict:
    if entry_contexts is None:
        entry_contexts = [
            "autoplay",
            "choose next",
            "ch swtch",
            "sel thumb",
            "launch first in session",
        ]
    _validate_pwatched_entry_context(entry_contexts)

    counts_obj = stream.get(f"PWATCHED#24H", {})
    feats = {}
    for entry_context in entry_contexts:
        attempts = counts_obj.get(entry_context, {}).get("attempts", 0)
        watched = counts_obj.get(entry_context, {}).get("watched", 0)
        context_key = entry_context if "launch" not in entry_context else "launch"
        context_key = context_key.upper().replace(" ", "_")
        feats[f"STREAM_{context_key}_24H_TOTAL_WATCHED"] = watched
        feats[f"STREAM_{context_key}_24H_TOTAL_ATTEMPTS"] = attempts
    return feats


def device_watched_count_cleanups(
    stream, device_type: str, entry_contexts: list[str] = None
) -> dict:
    if entry_contexts is None:
        entry_contexts = [
            "autoplay",
            "choose next",
            "ch swtch",
            "sel thumb",
            "launch first in session",
        ]

    _validate_pwatched_entry_context(entry_contexts)
    _validate_device_type(device_type)

    counts_obj = stream.get(f"PWATCHED#24H#{device_type}", {})
    feats = {}
    for entry_context in entry_contexts:
        attempts = counts_obj.get(entry_context, {}).get("attempts", 0)
        watched = counts_obj.get(entry_context, {}).get("watched", 0)
        context_key = entry_context if "launch" not in entry_context else "launch"
        context_key = context_key.upper().replace(" ", "_")
        feats["features"][f"STREAM_{context_key}_{device_type}_24H_TOTAL_WATCHED"] = (
            watched
        )
        feats["features"][f"STREAM_{context_key}_{device_type}_24H_TOTAL_ATTEMPTS"] = (
            attempts
        )
    return feats


def generic_beta_adjust_features(
    data: pd.DataFrame,
    prefix: str,
    pwatched_beta_params: dict,
    pselect_beta_params: dict,
    pslw_beta_params: dict,
    use_low_sample_flags: bool = False,
    low_sample_threshold: int = 3,
    use_attempt_features: bool = False,
    max_attempt_cap: int = 100,
    debiased_pselect: bool = True,
    use_logodds: bool = False,
) -> pd.DataFrame:
    pwatched_features = {}
    for context, (alpha, beta) in pwatched_beta_params.items():
        total_watched = data[f"{prefix}_{context}_TOTAL_WATCHED"].fillna(0)
        total_attempts = data[f"{prefix}_{context}_TOTAL_ATTEMPTS"].fillna(0)
        pwatched_features[f"{prefix}_{context}_ADJ_PWATCHED"] = (
            total_watched + alpha
        ) / (total_attempts + alpha + beta)
        if use_low_sample_flags:
            pwatched_features[f"{prefix}_{context}_LOW_SAMPLE"] = total_attempts.le(
                low_sample_threshold
            ).astype(int)
        if use_attempt_features:
            pwatched_features[f"{prefix}_{context}_ATTEMPTS"] = total_attempts.clip(
                upper=max_attempt_cap
            )

    pselect_features = {}
    debias_suffix = "_UP_TO_4_BROWSED" if debiased_pselect else ""
    for key, (alpha, beta) in pselect_beta_params.items():
        total_selects = data[f"{prefix}_{key}_TOTAL_SELECTS{debias_suffix}"].fillna(0)
        total_browsed = data[f"{prefix}_{key}_TOTAL_BROWSED{debias_suffix}"].fillna(0)
        pselect_features[f"{prefix}_{key}_ADJ_PSELECT{debias_suffix}"] = (
            total_selects + alpha
        ) / (total_selects + total_browsed + alpha + beta)
        if use_low_sample_flags:
            pselect_features[f"{prefix}_{key}_PSELECT_LOW_SAMPLE{debias_suffix}"] = (
                (total_selects + total_browsed).le(low_sample_threshold).astype(int)
            )
        if use_attempt_features:
            pselect_features[f"{prefix}_{key}_PSELECT_ATTEMPTS{debias_suffix}"] = (
                total_selects + total_browsed
            ).clip(upper=max_attempt_cap)
        total_slw = data[
            f"{prefix}_{key}_TOTAL_SELECTS_AND_WATCHED{debias_suffix}"
        ].fillna(0)
        pslw_alpha, pslw_beta = pslw_beta_params[key]
        pselect_features[f"{prefix}_{key}_ADJ_PSLW{debias_suffix}"] = (
            total_slw + pslw_alpha
        ) / (total_selects + total_browsed + pslw_alpha + pslw_beta)
        pselect_features[f"{prefix}_{key}_PSelNotW{debias_suffix}"] = (
            pselect_features[f"{prefix}_{key}_ADJ_PSELECT{debias_suffix}"]
            - pselect_features[f"{prefix}_{key}_ADJ_PSLW{debias_suffix}"]
        )

    adjusted_feats = pd.DataFrame({**pwatched_features, **pselect_features})
    if use_logodds:
        adjusted_feats = adjusted_feats.pipe(
            lambda x: x.assign(
                **x[
                    [
                        c
                        for c in x.columns
                        if "PSELECT" in c
                        or "PSLW" in c
                        or "PWATCHED" in c
                        or "PSelNotW" in c
                    ]
                ]
                .clip(lower=0.001)
                .pipe(prob_to_logodds)
            )
        )
    return adjusted_feats


def prob_to_logodds(prob: float) -> float:
    return np.log(prob) - np.log(1 - prob)


def scale_preds(
    preds: pd.Series,
    original_mean: float,
    original_std: float,
    target_mean: float,
    target_std: float,
) -> pd.Series:
    z_score = (preds - original_mean) / original_std
    return z_score * target_std + target_mean


def sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))


def generic_logistic_predict(
    data: pd.DataFrame, coeffs: pd.Series, intercept: float
) -> pd.Series:
    return ((data[coeffs.index] * coeffs).sum(axis=1) + intercept).pipe(sigmoid)


def _validate_device_type(device_type: str):
    if device_type not in ("TV", "MOBILE"):
        raise ValueError(f"Invalid device type '{device_type}")


def _validate_pwatched_entry_context(entry_contexts: list[str]):
    valid_contexts = [
        "autoplay",
        "choose next",
        "ch swtch",
        "sel thumb",
        "launch first in session",
    ]
    invalid_contexts = [c for c in entry_contexts if c not in valid_contexts]
    if invalid_contexts:
        raise ValueError(f"Invalid entry contexts found: {invalid_contexts}")
