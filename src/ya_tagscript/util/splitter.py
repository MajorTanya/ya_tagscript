def split_at_substring_zero_depth(
    haystack: str,
    needle: str,
    *,
    max_split: int = -1,
) -> list[str]:
    if not needle:  # Handle empty needle case
        return [haystack]

    result: list[str] = []
    start_idx = 0
    depth = 0
    splits = 0
    needle_len = len(needle)  # Calculate length once
    haystack_len = len(haystack)  # Calculate length once

    for i in range(haystack_len):
        char = haystack[i]

        # Update nesting depth
        if char == "{":
            depth += 1
        elif char == "}" and depth > 0:  # Prevent negative depth
            depth -= 1

        # Check for needle at zero depth
        elif (
            depth == 0
            and (max_split < 0 or splits < max_split)
            and i + needle_len <= haystack_len  # Boundary check
            and haystack[i : i + needle_len] == needle
        ):
            result.append(haystack[start_idx:i])
            start_idx = i + needle_len
            splits += 1
            i += needle_len - 1  # Skip ahead, but -1 because the loop will increment i

    # Add the final segment
    result.append(haystack[start_idx:])
    return result
