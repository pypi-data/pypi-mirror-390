# Resolution-Independent Coordinate System Design

## Problem Statement

AI agents require consistent UI element coordinates across different screen resolutions. System prompts currently document element positions using absolute coordinates (e.g., `address_bar: (500, 90)`), which only work on specific screen resolutions (e.g., 1920×1080). When customers use different resolutions, these coordinates become invalid, causing automation failures.

## Challenges

**Why simple scaling doesn't work perfectly:**
- Browser UI elements (chrome, toolbars) have fixed/minimum sizes that don't scale linearly
- OS-level DPI/UI scaling affects positioning differently across platforms
- Window decorations vary by operating system
- Multi-monitor setups add complexity

**Rejected approaches:**
- **Image-based detection**: Too costly at current stage, requires storing/managing reference images
- **Absolute coordinates**: Not scalable across different resolutions
- **Vision-based solutions**: Too complex, reserved for future enhancement

## Chosen Solution: Normalized Coordinates

### Architecture

```
Agent System Prompt (Normalized Coords)
           ↓
calculate_screen_coordinates(normalized_x, normalized_y)
           ↓
PyAutoGUI move_mouse(absolute_x, absolute_y)
```

### Implementation

**Tool: `calculate_screen_coordinates`**

```python
def calculate_screen_coordinates(
    normalized_x: float,  # Range: 0.0 to 1.0
    normalized_y: float,  # Range: 0.0 to 1.0
) -> Dict[str, Any]:
    """Calculate absolute screen coordinates from normalized values."""
    screen_size = pyautogui.size()
    absolute_x = int(normalized_x * screen_size.width)
    absolute_y = int(normalized_y * screen_size.height)

    return {
        "status": "success",
        "x": absolute_x,
        "y": absolute_y,
        "screen_width": screen_size.width,
        "screen_height": screen_size.height
    }
```

**Location:** `realtimex-pyautogui-server` repository

**Dependency:** PyAutoGUI (already available in that server)

---

## Coordinate Conversion Formula

Convert existing absolute coordinates to normalized format:

```python
# Reference screen: 1920×1080
normalized_x = absolute_x / 1920
normalized_y = absolute_y / 1080

# Example:
# address_bar: (500, 90)
# → normalized: (0.260, 0.083)
```

**Calculation examples:**

| Element | Absolute (1920×1080) | Normalized | Calculation |
|---------|---------------------|------------|-------------|
| address_bar | (500, 90) | (0.260, 0.083) | (500/1920, 90/1080) |
| search_button | (960, 540) | (0.500, 0.500) | (960/1920, 540/1080) |
| settings_icon | (1824, 54) | (0.950, 0.050) | (1824/1920, 54/1080) |

---

## System Prompt Update

**Before (absolute - not scalable):**
```markdown
| Element | Coordinates | Description |
|---------|------------|-------------|
| address_bar | (500, 90) | Browser address bar |
```

**After (normalized - scalable):**
```markdown
| Element | Normalized Coords | Ref Screen | Description |
|---------|------------------|------------|-------------|
| address_bar | (0.260, 0.083) | 1920×1080 | Browser address bar |
| search_button | (0.500, 0.500) | Any | Center search button |

**Usage Pattern:**
1. Calculate absolute coordinates:
   coords = calculate_screen_coordinates(0.260, 0.083)
2. Move mouse to position:
   move_mouse(coords["x"], coords["y"])
3. Perform action:
   click_mouse()
```

---

## Agent Workflow

```python
# Step 1: Agent reads normalized coordinates from system prompt
element_coords = (0.260, 0.083)  # address_bar

# Step 2: Calculate absolute coordinates for current screen
result = calculate_screen_coordinates(0.260, 0.083)
# Returns: {"status": "success", "x": 665, "y": 119, "screen_width": 2560, ...}

# Step 3: Move mouse to calculated position
move_mouse(result["x"], result["y"])

# Step 4: Perform action
click_mouse()
```

---

## Advantages

✅ **Scalable**: Works across any screen resolution
✅ **Simple**: Single tool, minimal code
✅ **Cost-effective**: No image storage or processing
✅ **Maintainable**: Update coordinates in one place (system prompt)
✅ **Fast**: Simple math calculation, no I/O overhead
✅ **Deterministic**: Consistent behavior across environments

---

## Limitations & Mitigations

**Browser chrome fixed sizing:**
- **Issue**: Address bars/toolbars may have fixed pixel heights
- **Mitigation**: Test on target resolutions, adjust normalized values if needed
- **Future**: Add window-relative coordinate mode

**DPI scaling:**
- **Issue**: High-DPI displays may affect positioning
- **Mitigation**: PyAutoGUI handles this automatically on most platforms

**Multi-monitor setups:**
- **Issue**: Coordinates assume primary monitor
- **Mitigation**: Document limitation, consider monitor selection in future

---

## Implementation Checklist

### For realtimex-pyautogui-server:
- [ ] Add `calculate_screen_coordinates(normalized_x, normalized_y)` tool
- [ ] Add input validation (0.0 ≤ value ≤ 1.0)
- [ ] Add comprehensive error handling
- [ ] Update server documentation
- [ ] Add usage examples

### For Agent System Prompts:
- [ ] Convert all absolute coordinates to normalized format
- [ ] Update element coordinate tables
- [ ] Document usage pattern (calculate → move → click)
- [ ] Add coordinate conversion reference
- [ ] Include troubleshooting guidelines

### Testing:
- [ ] Test on 1920×1080 (reference resolution)
- [ ] Test on 2560×1440 (common high-res)
- [ ] Test on 1366×768 (common laptop)
- [ ] Test on macOS (different DPI handling)
- [ ] Validate browser UI element accuracy

---

## Future Enhancements

**Phase 2 - Window-Relative Mode:**
```python
calculate_window_coordinates(
    normalized_x,
    normalized_y,
    use_active_window=True  # Calculate relative to active window
)
```

**Phase 3 - Image-Based Detection:**
- Add visual element detection for critical UI elements
- Fallback mechanism when coordinates are inaccurate
- Reference image library for common browser elements

**Phase 4 - Adaptive Learning:**
- Track coordinate accuracy across resolutions
- Auto-adjust normalized values based on success rates
- Machine learning for optimal coordinate prediction

---

## References

- PyAutoGUI Documentation: https://pyautogui.readthedocs.io/
- Related Server: `realtimex-pyautogui-server` (examples/realtimex_pyautogui_server/)
- MCP Server: `realtimex-computer-use` (current package)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Author:** RTA
**Status:** Approved - Ready for Implementation