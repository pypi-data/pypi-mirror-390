# QA Test Scenarios - End-to-End User Journeys

This document provides test scenarios for validating `llmtxt` CLI behavior across common usage patterns. These represent the 80/20 of CLI states and workflows that should be validated before release.

**Purpose**: Execute these scenarios to verify the CLI works correctly across different states, flag combinations, and user workflows.

**Test Environment Setup**:
- Ollama installed and running: `ollama serve &`
- Lightweight model pulled: `ollama pull gemma3:270m` (lightweight, fast for testing)
- Environment variables configured:
  ```bash
  export OPENAI_BASE_URL="http://localhost:11434/v1"
  export OPENAI_API_KEY="ollama-dummy-key"
  ```
- Clean test environment with fresh cache
- Test URLs should be stable documentation sites (typer.tiangolo.com is recommended - ~25 pages)
- **Why Ollama**: Zero API costs, same code paths as production, fast local execution

## Test Scenario 1: Fresh Install - Default Behavior

**Test ID**: `TS-001`
**Priority**: Critical
**State**: Clean environment (no cache, no previous runs)

**Preconditions**:
- Ollama is running with gemma3:270m model
- Environment variables set:
  ```bash
  export OPENAI_BASE_URL="http://localhost:11434/v1"
  export OPENAI_API_KEY="ollama-dummy-key"
  ```
- No existing cache directory (`.llmsbrieftxt_cache/`)
- No existing output directory (`~/.claude/docs/`)
- `llmtxt` command is available in PATH

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 10 --depth 1`
2. Observe console output for progress indicators
3. Wait for completion

**Expected Results**:
- ✅ Command exits with status code 0
- ✅ Output file created at `~/.claude/docs/typer.tiangolo.com.txt`
- ✅ Cache directory created at `.llmsbrieftxt_cache/`
- ✅ Cache file `summaries.json` contains entries for processed URLs
- ✅ Output file contains structured entries with "Title:", "Keywords:", "Summary:" format
- ✅ Console shows progress (e.g., "Processing X URLs...", "Cached: 0 | New: X")
- ✅ No error messages or warnings (unless some URLs fail, which is acceptable)

**Verification Commands**:
```bash
# Check exit code
echo $?  # Should be 0

# Verify output exists and has content
test -f ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS" || echo "FAIL"
wc -l ~/.claude/docs/typer.tiangolo.com.txt  # Should have 40+ lines (4 lines per entry × ~10 entries)

# Verify cache exists
test -f .llmsbrieftxt_cache/summaries.json && echo "PASS" || echo "FAIL"
cat .llmsbrieftxt_cache/summaries.json | jq 'length'  # Should show ~10 cached entries

# Verify output structure
grep -c "^Title:" ~/.claude/docs/typer.tiangolo.com.txt  # Should be ~10 (number of URLs processed)
grep -c "^Keywords:" ~/.claude/docs/typer.tiangolo.com.txt  # Should match Title count
grep -c "^Summary:" ~/.claude/docs/typer.tiangolo.com.txt  # Should match Title count
```

**Cleanup**:
```bash
rm -rf ~/.claude/docs/typer.tiangolo.com.txt
rm -rf .llmsbrieftxt_cache/
```

---

## Test Scenario 2: Preview Mode - No API Calls

**Test ID**: `TS-002`
**Priority**: High
**State**: Clean or existing cache (should not matter)

**Preconditions**:
- Ollama environment configured (but won't be used for preview)
- `llmtxt` command is available

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --show-urls --depth 1`
2. Observe console output
3. Check that command completes quickly (< 10 seconds)

**Expected Results**:
- ✅ Command exits with status code 0
- ✅ Console displays "Found X URLs to process"
- ✅ Console displays estimated cost (e.g., "Estimated cost: $0.XX")
- ✅ Console lists discovered URLs
- ✅ NO output file is created
- ✅ NO API calls are made (verify by checking for new cache entries or time taken)
- ✅ NO cache modifications (if cache existed before)

**Verification Commands**:
```bash
# Check exit code
echo $?  # Should be 0

# Verify NO output file created
test ! -f ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS" || echo "FAIL"

# Capture and verify output format
llmtxt https://typer.tiangolo.com --show-urls --depth 1 2>&1 | tee output.txt
grep -q "Found [0-9]* URLs" output.txt && echo "PASS" || echo "FAIL"
grep -q "Estimated cost:" output.txt && echo "PASS" || echo "FAIL"
grep -q "https://typer.tiangolo.com" output.txt && echo "PASS" || echo "FAIL"
```

**Cleanup**:
```bash
rm -f output.txt
```

---

## Test Scenario 3: Limited Scope - Depth and Max-URLs Constraints

**Test ID**: `TS-003`
**Priority**: High
**State**: Clean environment

**Preconditions**:
- Ollama environment configured
- Clean cache state

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --model gemma3:270m --depth 1 --max-urls 8`
2. Wait for completion
3. Verify constraints were respected

**Expected Results**:
- ✅ Command exits with status code 0
- ✅ Output file created at `~/.claude/docs/typer.tiangolo.com.txt`
- ✅ Number of entries ≤ 8 (respects max-urls)
- ✅ URLs are at most 1 link away from starting URL (respects depth)
- ✅ Console shows processing status with correct counts

**Verification Commands**:
```bash
# Count entries in output
ENTRY_COUNT=$(grep -c "^Title:" ~/.claude/docs/typer.tiangolo.com.txt)
test $ENTRY_COUNT -le 8 && echo "PASS: max-urls respected" || echo "FAIL: too many entries"

# Verify depth constraint (URLs should not be deeply nested)
# This is harder to verify programmatically, so inspect manually
cat ~/.claude/docs/typer.tiangolo.com.txt | grep "^Title:"

# Check cache has correct number of entries
CACHE_COUNT=$(cat .llmsbrieftxt_cache/summaries.json | jq 'length')
test $CACHE_COUNT -le 8 && echo "PASS" || echo "FAIL"
```

**Cleanup**:
```bash
rm -rf ~/.claude/docs/typer.tiangolo.com.txt
rm -rf .llmsbrieftxt_cache/
```

---

## Test Scenario 4A: Cache-Only Mode - No API Calls

**Test ID**: `TS-004A`
**Priority**: High
**State**: Existing cache from previous run

**Preconditions**:
- Run initial generation: `llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 10 --depth 1`
- Cache exists at `.llmsbrieftxt_cache/summaries.json`
- Note the cache entry count (should be ~10)

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --use-cache-only --output /tmp/cached-output.txt`
2. Observe completion time (should be very fast, < 5 seconds)
3. Verify output was generated from cache only

**Expected Results**:
- ✅ Command exits with status code 0
- ✅ Output file created at `/tmp/cached-output.txt`
- ✅ Output contains same entries as original run
- ✅ Console shows "Cached: X | New: 0" (no new summaries generated)
- ✅ Completion time is very fast (no API calls)
- ✅ Cache file is NOT modified (check timestamp)

**Verification Commands**:
```bash
# Verify output exists
test -f /tmp/cached-output.txt && echo "PASS" || echo "FAIL"

# Compare entry count
ORIGINAL_COUNT=$(grep -c "^Title:" ~/.claude/docs/typer.tiangolo.com.txt)
CACHED_COUNT=$(grep -c "^Title:" /tmp/cached-output.txt)
test $ORIGINAL_COUNT -eq $CACHED_COUNT && echo "PASS: same entry count" || echo "FAIL"

# Verify cache timestamp didn't change
ls -l .llmsbrieftxt_cache/summaries.json
```

**Cleanup**:
```bash
rm -f /tmp/cached-output.txt
```

---

## Test Scenario 4B: Force Refresh - Ignore Cache

**Test ID**: `TS-004B`
**Priority**: Medium
**State**: Existing cache from previous run

**Preconditions**:
- Ollama environment configured
- Cache exists from previous run
- Note cache modification time

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --model gemma3:270m --force-refresh --max-urls 10 --depth 1`
2. Wait for completion
3. Verify cache was updated

**Expected Results**:
- ✅ Command exits with status code 0
- ✅ Output file created/updated at `~/.claude/docs/typer.tiangolo.com.txt`
- ✅ Console shows "Cached: 0 | New: X" (all new summaries)
- ✅ Cache file timestamp is updated
- ✅ Cache file contents are replaced with fresh data
- ✅ Takes full time (API calls were made)

**Verification Commands**:
```bash
# Check cache was modified
stat .llmsbrieftxt_cache/summaries.json | grep Modify

# Verify all entries were regenerated (cache should have new timestamps)
cat .llmsbrieftxt_cache/summaries.json | jq '.[].timestamp' 2>/dev/null
```

**Cleanup**:
```bash
rm -rf ~/.claude/docs/typer.tiangolo.com.txt
rm -rf .llmsbrieftxt_cache/
```

---

## Test Scenario 5: Custom Paths - Output and Cache Directories

**Test ID**: `TS-005`
**Priority**: High
**State**: Clean environment

**Preconditions**:
- Ollama environment configured
- Create test directory: `mkdir -p /tmp/test-llmtxt/{output,cache}`

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --model gemma3:270m --output /tmp/test-llmtxt/output/custom.txt --cache-dir /tmp/test-llmtxt/cache --max-urls 8 --depth 1`
2. Verify custom paths are used
3. Verify default paths are NOT used

**Expected Results**:
- ✅ Command exits with status code 0
- ✅ Output file created at `/tmp/test-llmtxt/output/custom.txt` (NOT at ~/.claude/docs/)
- ✅ Cache created at `/tmp/test-llmtxt/cache/summaries.json` (NOT at .llmsbrieftxt_cache/)
- ✅ Default directories are empty or non-existent
- ✅ Output file has valid content

**Verification Commands**:
```bash
# Verify custom output location
test -f /tmp/test-llmtxt/output/custom.txt && echo "PASS: custom output" || echo "FAIL"
test ! -f ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS: no default output" || echo "FAIL"

# Verify custom cache location
test -f /tmp/test-llmtxt/cache/summaries.json && echo "PASS: custom cache" || echo "FAIL"
test ! -d .llmsbrieftxt_cache && echo "PASS: no default cache" || echo "FAIL"

# Verify content
grep -q "^Title:" /tmp/test-llmtxt/output/custom.txt && echo "PASS" || echo "FAIL"
```

**Cleanup**:
```bash
rm -rf /tmp/test-llmtxt/
```

---

## Test Scenario 6: Output Format - Searchability

**Test ID**: `TS-006`
**Priority**: High
**State**: Generated output file exists

**Preconditions**:
- Ollama environment configured
- Run: `llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 15 --depth 2`
- Output file exists at `~/.claude/docs/typer.tiangolo.com.txt`

**Test Steps**:
1. Search for known terms in output file
2. Verify structured format allows effective searching
3. Test with ripgrep and grep

**Expected Results**:
- ✅ Can search by Title: `grep "^Title:" file`
- ✅ Can search by Keywords: `grep "^Keywords:" file`
- ✅ Can search by Summary: `grep "^Summary:" file`
- ✅ Can search for URLs in titles
- ✅ Each entry has consistent structure
- ✅ Entries are separated by blank lines for readability

**Verification Commands**:
```bash
FILE=~/.claude/docs/typer.tiangolo.com.txt

# Test structured field searches
grep "^Title:" $FILE | head -3
grep "^Keywords:" $FILE | head -3
grep "^Summary:" $FILE | head -3

# Verify each Title has corresponding Keywords and Summary
TITLE_COUNT=$(grep -c "^Title:" $FILE)
KEYWORD_COUNT=$(grep -c "^Keywords:" $FILE)
SUMMARY_COUNT=$(grep -c "^Summary:" $FILE)

test $TITLE_COUNT -eq $KEYWORD_COUNT && test $TITLE_COUNT -eq $SUMMARY_COUNT && \
  echo "PASS: consistent structure" || echo "FAIL: inconsistent structure"

# Test case-insensitive search for Typer-specific terms
rg -i "argument|option|command|cli" $FILE && echo "PASS: ripgrep search works" || echo "FAIL"

# Test URL extraction from titles
grep "^Title:.*https://" $FILE && echo "PASS: URLs in titles" || echo "FAIL"
```

**Cleanup**:
```bash
rm -rf ~/.claude/docs/typer.tiangolo.com.txt
rm -rf .llmsbrieftxt_cache/
```

---

## Test Scenario 7: Partial Failures - Failed URLs Handling

**Test ID**: `TS-007`
**Priority**: Critical
**State**: Clean environment

**Preconditions**:
- Ollama environment configured
- Use a site known to have some broken links OR manually test with non-existent URLs

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 20 --depth 2`
   (Note: some URLs may fail during crawl or extraction)
2. Wait for completion
3. Check for failed_urls.txt file

**Expected Results**:
- ✅ Command exits with status code 0 (NOT failure code)
- ✅ Output file is still created with successful URLs
- ✅ `failed_urls.txt` created in same directory as output (if any failures occurred)
- ✅ `failed_urls.txt` lists URLs that failed with reasons
- ✅ Console shows warnings/errors for failed URLs but continues processing
- ✅ Successful URLs are cached and included in output

**Verification Commands**:
```bash
# Verify output was generated despite failures
test -f ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS: output created" || echo "FAIL"

# Check for failed URLs file (may or may not exist)
if [ -f ~/.claude/docs/failed_urls.txt ]; then
  echo "INFO: Some URLs failed"
  cat ~/.claude/docs/failed_urls.txt
  # Verify it has content
  test -s ~/.claude/docs/failed_urls.txt && echo "PASS: failed URLs logged" || echo "FAIL: empty"
else
  echo "INFO: All URLs succeeded (no failed_urls.txt)"
fi

# Verify successful URLs are in output
ENTRY_COUNT=$(grep -c "^Title:" ~/.claude/docs/typer.tiangolo.com.txt)
test $ENTRY_COUNT -gt 0 && echo "PASS: at least some URLs succeeded" || echo "FAIL: no entries"

# Verify successful URLs are cached
CACHE_COUNT=$(cat .llmsbrieftxt_cache/summaries.json | jq 'length')
test $CACHE_COUNT -gt 0 && echo "PASS: successful URLs cached" || echo "FAIL"
```

**Cleanup**:
```bash
rm -rf ~/.claude/docs/typer.tiangolo.com.txt
rm -rf ~/.claude/docs/failed_urls.txt
rm -rf .llmsbrieftxt_cache/
```

---

## Test Scenario 8: Alternative Model - Different Ollama Model

**Test ID**: `TS-008`
**Priority**: Medium
**State**: Clean environment

**Preconditions**:
- Ollama environment configured
- Alternative model pulled: `ollama pull phi3:mini` (2.3GB, larger model for quality comparison)
- Verify model available: `ollama list | grep phi3`

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --model phi3:mini --max-urls 10 --depth 1`
2. Verify generation completes successfully
3. Compare output quality with gemma3:270m (optional)

**Expected Results**:
- ✅ Command exits with status code 0
- ✅ Output file created at `~/.claude/docs/typer.tiangolo.com.txt`
- ✅ Summaries are generated with phi3 model
- ✅ No API costs incurred
- ✅ Cache is populated
- ✅ Output has correct format (Title, Keywords, Summary)
- ✅ Quality may be noticeably better than gemma3:270m

**Verification Commands**:
```bash
# Verify output exists
test -f ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS: output created" || echo "FAIL"

# Verify structure
grep -q "^Title:" ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS: has titles" || echo "FAIL"
grep -q "^Keywords:" ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS: has keywords" || echo "FAIL"
grep -q "^Summary:" ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS: has summaries" || echo "FAIL"

# Count entries
ENTRY_COUNT=$(grep -c "^Title:" ~/.claude/docs/typer.tiangolo.com.txt)
test $ENTRY_COUNT -gt 0 && echo "PASS: $ENTRY_COUNT entries" || echo "FAIL"

# Compare summary quality (manual inspection)
head -30 ~/.claude/docs/typer.tiangolo.com.txt
```

**Cleanup**:
```bash
rm -rf ~/.claude/docs/typer.tiangolo.com.txt
rm -rf .llmsbrieftxt_cache/
```

---

## Test Scenario 9: Depth Configuration - Crawl Boundary Validation

**Test ID**: `TS-009`
**Priority**: High
**State**: Clean environment

**Preconditions**:
- Ollama environment configured
- Test with a site that has clear depth structure

**Test Steps**:
1. Run with depth 1: `llmtxt https://typer.tiangolo.com --depth 1 --show-urls`
2. Run with depth 2: `llmtxt https://typer.tiangolo.com --depth 2 --show-urls`
3. Compare URL counts - depth 2 should discover more URLs
4. Generate with depth 1: `llmtxt https://typer.tiangolo.com --model gemma3:270m --depth 1 --max-urls 10`
5. Verify only shallow URLs are processed

**Expected Results**:
- ✅ Higher depth values discover more URLs
- ✅ Depth 1: Only starting URL + direct links
- ✅ Depth 2: Includes links from depth 1 pages
- ✅ `--show-urls` correctly previews discovered URLs
- ✅ Generated output respects depth constraint
- ✅ URL counts increase with depth: depth1 < depth2 < depth3

**Verification Commands**:
```bash
# Preview and capture URL counts
DEPTH1_COUNT=$(llmtxt https://typer.tiangolo.com --depth 1 --show-urls 2>&1 | grep "Found" | grep -oP '\d+')
DEPTH2_COUNT=$(llmtxt https://typer.tiangolo.com --depth 2 --show-urls 2>&1 | grep "Found" | grep -oP '\d+')

echo "Depth 1 URLs: $DEPTH1_COUNT"
echo "Depth 2 URLs: $DEPTH2_COUNT"

# Depth 2 should find more URLs than depth 1
test $DEPTH2_COUNT -gt $DEPTH1_COUNT && echo "PASS: depth increases URL count" || echo "FAIL"

# Actually generate with depth 1
llmtxt https://typer.tiangolo.com --model gemma3:270m --depth 1 --max-urls 5

# Verify output
test -f ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS" || echo "FAIL"
```

**Cleanup**:
```bash
rm -rf ~/.claude/docs/typer.tiangolo.com.txt
rm -rf .llmsbrieftxt_cache/
```

---

## Test Scenario 10: Incremental Runs - Cache Reuse Across Sessions

**Test ID**: `TS-010`
**Priority**: High
**State**: Existing cache from previous run

**Preconditions**:
- Ollama environment configured
- First run completed: `llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 10 --depth 1`
- Cache exists with ~10 entries
- Note cache creation time

**Test Steps**:
1. Run again with higher max-urls: `llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 20 --depth 1`
2. Observe that cached entries are reused
3. Verify only new URLs are processed

**Expected Results**:
- ✅ Command exits with status code 0
- ✅ Console shows "Cached: 10 | New: X" (reuses existing cache)
- ✅ Only new URLs trigger API calls
- ✅ Total time is less than processing 20 URLs from scratch
- ✅ Output file contains entries from both cache and new generation
- ✅ Cache file is updated with new entries (not replaced)

**Verification Commands**:
```bash
# Check cache size increased
INITIAL_CACHE=$(cat .llmsbrieftxt_cache/summaries.json | jq 'length')
# Run with more URLs
llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 20 --depth 1 2>&1 | tee output.log
FINAL_CACHE=$(cat .llmsbrieftxt_cache/summaries.json | jq 'length')

echo "Initial cache: $INITIAL_CACHE"
echo "Final cache: $FINAL_CACHE"
test $FINAL_CACHE -gt $INITIAL_CACHE && echo "PASS: cache grew" || echo "FAIL"

# Verify "Cached:" appears in output
grep -q "Cached:" output.log && echo "PASS: cache reuse reported" || echo "FAIL"

# Verify output has more entries
ENTRY_COUNT=$(grep -c "^Title:" ~/.claude/docs/typer.tiangolo.com.txt)
test $ENTRY_COUNT -ge 10 && echo "PASS: has at least 10 entries" || echo "FAIL"
```

**Cleanup**:
```bash
rm -rf ~/.claude/docs/typer.tiangolo.com.txt
rm -rf .llmsbrieftxt_cache/
rm -f output.log
```

---

## Test Scenario 11: Error Handling - Ollama Not Running

**Test ID**: `TS-011`
**Priority**: Critical
**State**: Ollama service stopped

**Preconditions**:
- Ollama service is NOT running
- Stop Ollama: `pkill ollama` or `killall ollama`
- Environment variables still set (but service unavailable)

**Test Steps**:
1. Run: `llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 8`
2. Observe error message about connection failure

**Expected Results**:
- ✅ Command exits with non-zero status code
- ✅ Clear error message about connection failure or API endpoint
- ✅ No output file created
- ✅ No cache directory created (or minimal artifacts)
- ✅ Error mentions inability to connect to localhost:11434

**Verification Commands**:
```bash
# Ensure Ollama is stopped
pkill ollama 2>/dev/null || true
sleep 2

# Run and capture exit code
llmtxt https://typer.tiangolo.com --model gemma3:270m --max-urls 8 2>&1 | tee error.log
EXIT_CODE=$?

test $EXIT_CODE -ne 0 && echo "PASS: non-zero exit" || echo "FAIL: should have failed"
grep -qi "connection\|refused\|timeout\|11434" error.log && echo "PASS: connection error" || echo "FAIL"

# Verify no output
test ! -f ~/.claude/docs/typer.tiangolo.com.txt && echo "PASS: no output" || echo "FAIL"
```

**Cleanup**:
```bash
rm -f error.log
# Restart Ollama for subsequent tests
ollama serve > /dev/null 2>&1 &
sleep 2
```

---

## Test Scenario 12: Error Handling - Invalid Model Name

**Test ID**: `TS-012`
**Priority**: Medium
**State**: Clean environment

**Preconditions**:
- Ollama environment configured
- Model NOT pulled: `nonexistent-model-xyz`

**Test Steps**:
1. Run with non-existent model: `llmtxt https://typer.tiangolo.com --model nonexistent-model-xyz --max-urls 5 --depth 1`
2. Observe error about model not found

**Expected Results**:
- ✅ Command exits with non-zero status code
- ✅ Error message about model not found or not available
- ✅ No output file created (or minimal)
- ✅ Suggests checking available models or pulling model

**Verification Commands**:
```bash
# Run with invalid model
llmtxt https://typer.tiangolo.com --model nonexistent-model-xyz --max-urls 5 2>&1 | tee error.log
EXIT_CODE=$?

test $EXIT_CODE -ne 0 && echo "PASS: non-zero exit" || echo "FAIL: should have failed"
grep -qi "model\|not found\|available" error.log && echo "PASS: model error" || echo "FAIL"

# Verify minimal artifacts
# May have discovered URLs but not generated summaries
```

**Cleanup**:
```bash
rm -f error.log
rm -rf ~/.claude/docs/typer.tiangolo.com.txt 2>/dev/null
rm -rf .llmsbrieftxt_cache/ 2>/dev/null
```

---

## QA Checklist - Pre-Release Validation

Run all scenarios above and mark results:

- [ ] **TS-001**: Fresh install default behavior
- [ ] **TS-002**: Preview mode (--show-urls)
- [ ] **TS-003**: Depth and max-urls constraints
- [ ] **TS-004A**: Cache-only mode
- [ ] **TS-004B**: Force refresh
- [ ] **TS-005**: Custom output and cache paths
- [ ] **TS-006**: Output format searchability
- [ ] **TS-007**: Partial failure handling
- [ ] **TS-008**: Alternative model (phi3:mini)
- [ ] **TS-009**: Depth configuration
- [ ] **TS-010**: Incremental cache reuse
- [ ] **TS-011**: Ollama not running error
- [ ] **TS-012**: Invalid model name error

**Pass Criteria**: All critical (TS-001, 002, 004A, 005, 007, 011) and high priority tests pass.

---

## Test Execution Notes

**Recommended Test Order**:
1. Start with TS-001 (fresh install) to validate core functionality
2. Run TS-002 (preview) to ensure no-op mode works
3. Run cache tests (TS-004A, TS-004B, TS-010) in sequence to validate cache states
4. Run error handling tests (TS-007, TS-011) to ensure graceful failures
5. Run integration tests (TS-008, TS-012) if those environments available

**Test Environment**:
- Use typer.tiangolo.com as the standard test URL (~25 pages, stable documentation)
- Use `--max-urls 10 --depth 1` for faster test cycles
- Always clean up between tests to ensure isolated state
- Keep Ollama running in background: `ollama serve > /dev/null 2>&1 &`
- Monitor Ollama logs if needed: `tail -f ~/.ollama/logs/server.log`

**Automation**:
- Each test scenario can be scripted as a shell script
- Verification commands can be used in CI/CD pipelines
- Consider pytest framework for integration tests (see tests/integration/test_ollama_e2e.py)
- All tests run with zero API costs using local Ollama instance
