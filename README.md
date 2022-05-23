# stock-portfolio-batches-from-transactions

* __The primary purpose__ of this script is to assign ___Batch Numbers___ and batch-specific calculations (e.g. batch ___adjusted-cost basis___) for a stock portfolio based on its full transaction history. 
* Determination of the adjusted cost basis can become surprisingly tedious if the same batch has been partially reduced in size before later adding more shares at a different cost. This is further complicated when numerous different batches are present for the same instrument at different times. Despite the growing number of retail investors and traders, spreadsheet software is hardly up to this task (without resorting to VBA, manual entry of surrogate lookup keys, etc.). 
* While simple in principle, but tedious in practice - this script helps you avoid complexities in retroactively calculating batch metrics and realized gains/losses from a portfolio's transaction history across separate batches of one instrument or across separate allocation adjustments within a single batches (or both). __If you often rebalance, you certainly fit the use case of this script.__
* This script iterates through a stock portfolio's transaction history (*.csv,*.xlsx), and using chronological running tallies to derive __status, batch number, batch-average cost basis, and realized gains (_per batch_ & _per instrument_)__.

# Usage
* In `./userdata_transactions/`, provide a CSV file titled `transactions.csv`. 
  * the CSV file should be sorted chronologically (oldest at top) 
  * the _transactions_ file should be acceptable also as `*.xlsx`, but this is not tested in current version of script (previously, yes).
* Run `batches-from-transactions.py` to launch the script, which constructs pandas dataframes combs through the transactions records.
* A file is automatically output called `"portfolio-batches.csv"`. The report contain data for each ticker found in the trading history (Sorted by active/inactive, then by ticker symbol alphabetically.
  * Batch numbers and batch-specific calculations (e.g. cost basis) are performed for the current/latest batch. Older batch history is currently not written to the file. 
  * P&L values are also provided _per instrument_ (cumulative totals per each ticker across all batches), as well as _per batch_. Since P&L values are based on REALIZED gains/losses (not the current price of the security)  gains appear in the current Active batches only if a portion of it has been sold. 
