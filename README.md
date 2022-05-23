# stock-portfolio-batches-from-transactions

* __The primary purpose__ of this script is to assign ___Batch Numbers___ and batch-specific calculations (e.g. batch ___adjusted-cost basis___) for a stock portfolio based on its full transaction history. 
* While simple in principle, determination of a batch's adjusted cost basis can become a headache in some situations; in particular, when a batch has been partially reduced in size before later increasing the size of the position once again. For this reason, it can be surprisingly complex to review a full transaction history and calculate the realized gains of each transaction within a batch. __If you often rebalance, you certainly fit the use case of this script.__
* This script iterates through a stock portfolio's transaction history (*.csv,*.xlsx), and using chronological running tallies to derive __status, batch number, batch-average cost basis, and realized gains (_per batch_ & _per instrument_)__.

# Usage
* In `./userdata_transactions/`, provide a CSV file titled 'transactions.csv'. It may be XLSX, but this is not tested in current version of script (previous= yes).
  * the CSV file should be sorted chronologically (oldest at top) 
* Run 'batches-from-transactions.py' to construct pandas dataframes and iterate through the transactions records.
* A file is automatically output called "portfolio-batches.csv". These will contain data for every ticker in your trading history (active first)
  * P&L values are based on REALIZED gains/losses, not the current value. They are provided for the current batch only if you have sold a portion of it. Otherwise, P&L values are also provided in cumulative totals per each ticker (across all batches). 
  * Batch numbers and batch-specific calculations (e.g. cost basis) are performed for the current/latest batch. Older batch history is currently not written to the file. 
