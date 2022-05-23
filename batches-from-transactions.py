import numpy as np
import pandas as pd
import glob



def read_transactions(name='transactions'):
    try:
        path = './userdata_transactions/{}.csv'.format(name)
        df = pd.read_csv(path,header=0)
        df.columns = df.columns.str.lower()
        
        # rename transaction date column to date
        df = df.rename(columns={'transaction date': 'date'})
        
        # Reset index, remove duplicate index if one is made
        df.reset_index(inplace=True)
        df.drop(['index'], axis=1, inplace=True)
        
    except ValueError:
        path = './userdata_transactions/{}.xlsx'.format(name)
        df = pd.read_excel(path,header=0)
        
        #make column titles lowercase
        df.columns = df.columns.str.lower()
        
        # for excel make new column 'date' expressing transaction date as simplified date rather than date-time
        df['date'] = df['transaction date'].dt.floor('d')
        df.drop('transaction date', axis=1, inplace=True)
        # Reset index, remove duplicate index if one is made
        df.reset_index(inplace=True)
        df.drop(['index'], axis=1, inplace=True)
        
    else:
        return df


def batch_calculations(x):
    ledger = x.to_dict('records')
    index_dict = {}

    # next, we will create a log of former batches before overwriting latest batch in index_dict
    #former_batches = {}

    for i in range(0,len(ledger)):

        # TEMP VARS
        # --- assign short names temporary use during for each line of iteration

        symbol = ledger[i]['symbol']
        side = ledger[i]['side']
        quantity = ledger[i]['qty']
        cost_basis = ledger[i]['cost basis']
        amount = ledger[i]['amount']
        date = ledger[i]['date']


        # INDEX DICTIONARY - CONDITIONAL CALCULATIONS TO DETERMINE NEW LEDGER ENTRIES 

        # new stock
        if symbol not in index_dict:     # new ticker

            index_dict[symbol] = {}

            index_dict[symbol]['current_status'] = 'Active'

            index_dict[symbol]['batch_number'] = 1
            index_dict[symbol]['batch_lot'] = 1
            index_dict[symbol]['batch_dateopen'] = date
            index_dict[symbol]['batch_dateclosed'] = 'n/a'

            index_dict[symbol]['qty_buys'] = quantity
            index_dict[symbol]['qty_sells'] = 0
            index_dict[symbol]['qty_net'] = quantity

            index_dict[symbol]['amount_buys'] = amount
            index_dict[symbol]['amount_sells'] = 0
            index_dict[symbol]['amount_net'] = amount

            index_dict[symbol]['CB_batch'] = cost_basis
            index_dict[symbol]['CB_effective'] = cost_basis

            index_dict[symbol]['SB_avg'] = 0

            index_dict[symbol]['p&l_batch'] = 0
            index_dict[symbol]['p&l_ticker'] = 0


            ledger[i]['current_status'] = 'Active'
            ledger[i]['batch_number'] = 1
            ledger[i]['batch_dateopen'] = index_dict[symbol]['batch_dateopen']
            ledger[i]['batch_dateclosed'] = index_dict[symbol]['batch_dateclosed']
            ledger[i]['batch_lot'] = 1
            ledger[i]['qty_buys'] = quantity
            ledger[i]['qty_sells'] = 0
            ledger[i]['qty_net'] = quantity
            ledger[i]['amount_buys'] = amount
            ledger[i]['amount_sells'] = 0
            ledger[i]['amount_net'] = amount
            ledger[i]['CB_batch'] = cost_basis
            ledger[i]['CB_effective'] = cost_basis
            ledger[i]['SB_avg'] = 0
            ledger[i]['p&l_batch'] = 0
            ledger[i]['p&l_ticker'] = 0



        # new purchase
        elif symbol in index_dict and side == 'buy':           # known ticker, new purchase

            # when latest batch before now had been closed / fully sold: 
            if round(index_dict[symbol]['qty_net'],4) == 0 and index_dict[symbol]['current_status'] == 'Inactive':      

                index_dict[symbol]['current_status'] = 'Active'
                index_dict[symbol]['batch_number'] += 1
                index_dict[symbol]['batch_lot'] = 1
                index_dict[symbol]['batch_dateopen'] = date
                index_dict[symbol]['batch_dateclosed'] = 'n/a'
                index_dict[symbol]['qty_buys'] = quantity
                index_dict[symbol]['qty_sells'] = 0
                index_dict[symbol]['qty_net'] = quantity
                index_dict[symbol]['amount_net'] = amount
                index_dict[symbol]['amount_sells'] = 0
                index_dict[symbol]['amount_buys'] = amount  

                index_dict[symbol]['CB_batch'] = cost_basis
                index_dict[symbol]['CB_effective'] = cost_basis
                index_dict[symbol]['SB_avg'] = 0
                index_dict[symbol]['p&l_batch'] = 0

                #update ledger
                ledger[i]['current_status']     = index_dict[symbol]['current_status']
                ledger[i]['batch_number']       = index_dict[symbol]['batch_number']
                ledger[i]['batch_dateopen'] = index_dict[symbol]['batch_dateopen']
                ledger[i]['batch_dateclosed'] = index_dict[symbol]['batch_dateclosed']
                ledger[i]['batch_lot']          = index_dict[symbol]['batch_lot']
                ledger[i]['qty_buys']           = index_dict[symbol]['qty_buys']
                ledger[i]['qty_sells']          = index_dict[symbol]['qty_sells']
                ledger[i]['qty_net']            = index_dict[symbol]['qty_net']
                ledger[i]['amount_net']         = index_dict[symbol]['amount_net']
                ledger[i]['amount_sells']       = index_dict[symbol]['amount_sells']
                ledger[i]['amount_buys']        = index_dict[symbol]['amount_buys']
                ledger[i]['CB_batch']           = index_dict[symbol]['CB_batch']
                ledger[i]['CB_effective']       = index_dict[symbol]['CB_effective']
                ledger[i]['SB_avg']             = index_dict[symbol]['SB_avg']
                ledger[i]['p&l_batch']          = index_dict[symbol]['p&l_batch']
                ledger[i]['p&l ticker']         = index_dict[symbol]['p&l_ticker']
                ledger[i]['p&l_line']           = 0

            # when batch is an existing batch:
            else:    
                # adjust the cost basis
                qty_prior = index_dict[symbol]['qty_net']
                CB_prior = index_dict[symbol]['CB_batch']
                qty_line = quantity
                CB_line = cost_basis

                CB_f = ((qty_prior * CB_prior) + (qty_line * CB_line)) / (qty_prior + qty_line)

                # update index dict values
                index_dict[symbol]['batch_lot'] += 1
                index_dict[symbol]['qty_net'] += quantity
                index_dict[symbol]['qty_buys'] += quantity
                index_dict[symbol]['amount_net'] += amount
                index_dict[symbol]['amount_buys'] += amount
                index_dict[symbol]['CB_batch'] = CB_f
                index_dict[symbol]['CB_effective'] = (index_dict[symbol]['amount_net']) / (index_dict[symbol]['qty_net'])

                #update ledger
                ledger[i]['current_status']     = index_dict[symbol]['current_status']
                ledger[i]['batch_number']       = index_dict[symbol]['batch_number']
                ledger[i]['batch_lot']          = index_dict[symbol]['batch_lot']
                ledger[i]['batch_dateopen'] = index_dict[symbol]['batch_dateopen']
                ledger[i]['batch_dateclosed'] = index_dict[symbol]['batch_dateclosed']
                ledger[i]['qty_buys']           = index_dict[symbol]['qty_buys']
                ledger[i]['qty_sells']          = index_dict[symbol]['qty_sells']
                ledger[i]['qty_net']            = index_dict[symbol]['qty_net']
                ledger[i]['amount_net']         = index_dict[symbol]['amount_net']
                ledger[i]['amount_sells']       = index_dict[symbol]['amount_sells']
                ledger[i]['amount_buys']        = index_dict[symbol]['amount_buys']
                ledger[i]['CB_batch']           = index_dict[symbol]['CB_batch']
                ledger[i]['CB_effective']       = index_dict[symbol]['CB_effective']
                ledger[i]['SB_avg']             = index_dict[symbol]['SB_avg']
                ledger[i]['p&l_batch']          = index_dict[symbol]['p&l_batch']
                ledger[i]['p&l ticker']         = index_dict[symbol]['p&l_ticker']
                ledger[i]['p&l_line']           = 0


        # add known ticker, SELL
        elif symbol in index_dict and side == 'sell':

            # sell portion of batch
            if round(index_dict[symbol]['qty_net'],4) > round(quantity,4):

                # adjust batch avg sell basis
                qty_prior = index_dict[symbol]['qty_sells']
                SB_prior = index_dict[symbol]['SB_avg']
                qty_line = quantity
                SB_line = cost_basis

                SB_f = ((qty_prior * SB_prior) + (qty_line * SB_line)) / (qty_prior + qty_line)

                # update index dict values
                index_dict[symbol]['qty_net'] -= quantity
                index_dict[symbol]['qty_sells'] += quantity

                index_dict[symbol]['amount_net'] -= amount
                index_dict[symbol]['amount_sells'] += amount

                index_dict[symbol]['CB_effective'] = (index_dict[symbol]['amount_net']) / (index_dict[symbol]['qty_net'])

                index_dict[symbol]['SB_avg'] = SB_f

                pnl_line = quantity * (cost_basis - index_dict[symbol]['CB_batch'])

                index_dict[symbol]['p&l_batch'] += pnl_line
                index_dict[symbol]['p&l_ticker'] += pnl_line

                #update ledger
                ledger[i]['current_status']     = index_dict[symbol]['current_status']
                ledger[i]['batch_number']       = index_dict[symbol]['batch_number']
                ledger[i]['batch_lot']          = index_dict[symbol]['batch_lot']
                ledger[i]['batch_dateopen'] = index_dict[symbol]['batch_dateopen']
                ledger[i]['batch_dateclosed'] = index_dict[symbol]['batch_dateclosed']
                ledger[i]['qty_buys']           = index_dict[symbol]['qty_buys']
                ledger[i]['qty_sells']          = index_dict[symbol]['qty_sells']
                ledger[i]['qty_net']            = index_dict[symbol]['qty_net']
                ledger[i]['amount_net']         = index_dict[symbol]['amount_net']
                ledger[i]['amount_sells']       = index_dict[symbol]['amount_sells']
                ledger[i]['amount_buys']        = index_dict[symbol]['amount_buys']
                ledger[i]['CB_batch']           = index_dict[symbol]['CB_batch']
                ledger[i]['CB_effective']       = index_dict[symbol]['CB_effective']
                ledger[i]['SB_avg']             = index_dict[symbol]['SB_avg']
                ledger[i]['p&l_batch']          = index_dict[symbol]['p&l_batch']
                ledger[i]['p&l ticker']         = index_dict[symbol]['p&l_ticker']
                ledger[i]['p&l_line']           = pnl_line

            # sell remainder of batch
            elif round(index_dict[symbol]['qty_net'],4) == round(quantity,4):  

                # calculate new avg sell basis
                qty_prior = index_dict[symbol]['qty_sells']
                SB_prior = index_dict[symbol]['SB_avg']
                qty_line = quantity
                SB_line = cost_basis

                SB_f = ((qty_prior * SB_prior) + (qty_line * SB_line)) / (qty_prior + qty_line)


                # update index dict values
                index_dict[symbol]['qty_net'] -= quantity
                index_dict[symbol]['qty_sells'] += quantity

                index_dict[symbol]['amount_net'] -= amount
                index_dict[symbol]['amount_sells'] += amount

                #index_dict[symbol]['CB_effective'] = (index_dict[symbol]['amount_net']) / (index_dict[symbol]['qty_net'])

                index_dict[symbol]['SB_avg'] = SB_f

                pnl_line = quantity * (cost_basis - index_dict[symbol]['CB_batch'])

                index_dict[symbol]['p&l_batch'] += pnl_line
                index_dict[symbol]['p&l_ticker'] += pnl_line

                # close the current batch
                index_dict[symbol]['current_status'] = 'Inactive'
                index_dict[symbol]['batch_dateclosed'] = date

                #update ledger
                ledger[i]['current_status']     = index_dict[symbol]['current_status']
                ledger[i]['batch_number']       = index_dict[symbol]['batch_number']
                ledger[i]['batch_lot']          = index_dict[symbol]['batch_lot']
                ledger[i]['batch_dateopen'] = index_dict[symbol]['batch_dateopen']
                ledger[i]['batch_dateclosed'] = index_dict[symbol]['batch_dateclosed']
                ledger[i]['qty_buys']           = index_dict[symbol]['qty_buys']
                ledger[i]['qty_sells']          = index_dict[symbol]['qty_sells']
                ledger[i]['qty_net']            = index_dict[symbol]['qty_net']
                ledger[i]['amount_net']         = index_dict[symbol]['amount_net']
                ledger[i]['amount_sells']       = index_dict[symbol]['amount_sells']
                ledger[i]['amount_buys']        = index_dict[symbol]['amount_buys']
                ledger[i]['CB_batch']           = index_dict[symbol]['CB_batch']
                ledger[i]['CB_effective']       = index_dict[symbol]['CB_effective']
                ledger[i]['SB_avg']             = index_dict[symbol]['SB_avg']
                ledger[i]['p&l_batch']          = index_dict[symbol]['p&l_batch']
                ledger[i]['p&l ticker']         = index_dict[symbol]['p&l_ticker']
                ledger[i]['p&l_line']           = pnl_line
    
    dfx = pd.DataFrame.from_dict(index_dict)
    output_df = dfx.transpose()
    output_df.reset_index(inplace=True)
    output_df.rename(columns={'index':'symbol'},inplace=True)
    output_df.sort_values(by=['current_status', 'symbol'],inplace=True)
    output_df.reset_index(drop=True,inplace=True)

    annotated_ledger = pd.DataFrame.from_dict(ledger)
    
    return output_df,annotated_ledger

def output_to_csv(dataframe,filename):
    #filename='portfolio-batches'
    dataframe.to_csv('./{}.csv'.format(filename))
    print("Job complete! File written to ./{}.csv".format(filename))

if __name__ == "__main__":
    df = read_transactions()
    output_df,annotated_ledger = batch_calculations(df)
    output_to_csv(output_df,'portfolio-batches')
    
    output_to_csv(annotated_ledger,'annotated-ledger')
    
else:
    pass