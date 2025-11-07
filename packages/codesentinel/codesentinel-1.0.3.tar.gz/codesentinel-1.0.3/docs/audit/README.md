# Audit Results & Scripts

Performance testing, auditing, and benchmarking tools and results.

## Folders

### scripts/

Audit and testing scripts:

- `audit_global_overhead.py` - Measure global system overhead
- `audit_integrity_overhead.py` - Measure file integrity system performance
- `fault_test_integrity.py` - Test file integrity under various fault conditions

### results/

Stored audit results:

- `audit_global_overhead_results.json` - Global overhead test results
- `audit_integrity_overhead_results.json` - Integrity system performance results
- `audit_integrity_fault_test_results.json` - Fault tolerance test results

## Running Audits

```bash
python scripts/audit_integrity_overhead.py
python scripts/fault_test_integrity.py
```

Results are stored in `results/` folder with timestamps.

---

**Compliance**: T2-2 (Performance standards) + T3-7 (Build artifact management)
