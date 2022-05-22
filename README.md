# stock-portfolio-batches-from-transactions
This script iterates through spreadsheet data to derive batch numbers, batch-specific calculations, and active versus closed positions by ticker and batch number.  

# Usage
* In './userdata_transactions', provide a CSV file titled 'transactions.csv'. It may be XLSX, but this is not tested in current version of script (previous= yes).
  * the CSV file should be sorted chronologically (oldest at top) 
* Run 'batches-from-transactions.py' to construct pandas dataframes and iterate through the transactions records.
* A file is automatically output called "portfolio-batches.csv". These will contain data for every ticker in your trading history (active first)
  * P&L values are based on REALIZED gains/losses, not the current value. They are provided for the current batch only if you have sold a portion of it. Otherwise, P&L values are also provided in cumulative totals per each ticker (across all batches). 
  * Batch numbers and batch-specific calculations (e.g. cost basis) are performed for the current/latest batch. Older batch history is currently not written to the file. 
