# Native DataHub Write-Back Capture Runbook

## Acceptance condition

The recording must show the actual local DataHub UI, the exact accepted dataset, and the native description text containing the retained EvidenceBound receipt. An editorial recreation is not sufficient.

## Required visible sequence

1. Start from the DataHub home page at `http://localhost:9002`.
2. Search for `ORDER_ENTRY_DB.analytics.order_history`.
3. Open the exact dataset:
   `urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.ORDER_ENTRY_DB.analytics.order_history,PROD)`.
4. Keep the browser address bar and dataset identity visible long enough to establish provenance.
5. Open the dataset description.
6. Scroll slowly through the retained receipt and keep these fields readable:
   - verdict;
   - reason;
   - Proof Pack root;
   - schema digest;
   - lineage digest;
   - human approval required;
   - promotion authorization false.
7. Show both VERIFIED and BLOCKED receipts if both are retained.
8. End on the dataset identity and receipt without editing anything.

## Recording rules

- 1920×1080, 30 fps.
- Browser zoom 100%; do not crop the address bar or dataset name.
- No notifications, bookmarks, personal account data or secrets.
- No mouse circling, artificial zoom or subtitles over the receipt.
- Do not claim the read-only recording performed the write-back.
- Label the clip in the edit only as `RETAINED LIVE DATAHUB DESCRIPTION RECEIPT`.

## Fail-closed stop

Stop and do not use the clip if the dataset identity, receipt fields or write-back provenance cannot be read from the recording.
