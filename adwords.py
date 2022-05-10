# Import statements
import math
import sys
import pandas as pd
import numpy as np
import random as rd
import collections
rd.seed(0)


# Constants that are used in the code
GREEDY = "greedy"
MSVV = "msvv"
BALANCE = "balance"
ITERATIONS = 100

# To check if there are any bidders with remaining budget to bid
def adv_budget_empty(adv_bids,bidders_budget):
    for adv in adv_bids:
        if adv_bids[adv] <= bidders_budget[adv]:
            return False
    return True

# To calculate psi value for each bidder based on spent fraction
def calculate_psi(frac_x):
    return (1-math.exp(frac_x-1))

# Greedy algorithm which checks only the max bid value
def greedyAlgorithm(bidders_budget,queries_bids,query_lines):

    current_iteration = 0
    revenue = []
    # To run for 100 iterations
    while current_iteration <= ITERATIONS:
        copy_bidders_budget = bidders_budget.copy()
        rev = 0
        if current_iteration !=0:
            rd.shuffle(query_lines)
        # finding the best bidder for each query
        for query in query_lines:
            adv_bids = queries_bids[query]
            
            if adv_budget_empty(adv_bids,copy_bidders_budget):
                continue
            
            max_bid_value = -math.inf
            max_bidder = None
            for bid in adv_bids:
                if adv_bids[bid] <= copy_bidders_budget[bid]:
                    if adv_bids[bid] > max_bid_value:
                        max_bid_value = adv_bids[bid]
                        max_bidder = bid
                    elif max_bid_value == adv_bids[bid]:
                        if bid < max_bidder:
                            max_bidder = bid

            rev = rev+max_bid_value
            copy_bidders_budget[max_bidder] = copy_bidders_budget[max_bidder]-max_bid_value
        
        revenue.append(rev)
        # print the first value
        if current_iteration==0:
            print(round(rev,2))
            revenue[0] = 0
        current_iteration = current_iteration+1
    # finding average revenue
    avg_revenue = sum(revenue)/100

    return avg_revenue

# Balance algorithm which checks the remaining balance of each bidder
def balanceAlgorithm(bidders_budget,queries_bids,query_lines):

    avg_revenue = 0
    current_iteration = 0
    # To run for 100 iterations
    while current_iteration <= ITERATIONS:
        if current_iteration !=0:
            rd.shuffle(query_lines)
        
        revenue = 0
        copy_bidders_budget = bidders_budget.copy()
        # finding the best bidder for each query
        for query in query_lines:
            adv_bids = queries_bids[query]
            
            if adv_budget_empty(adv_bids,copy_bidders_budget):
                continue

            max_bidder = list(adv_bids.keys())[0]
            # finding the best bidder based on remaining budget
            for bid in adv_bids:
                
                if  adv_bids[bid] <= copy_bidders_budget[bid]:
                    if copy_bidders_budget[bid] > copy_bidders_budget[max_bidder]:
                        max_bidder = bid
                    
                    elif copy_bidders_budget[bid] == copy_bidders_budget[max_bidder]:
                        if bid < max_bidder:
                            max_bidder = bid
            
            max_bid_value = adv_bids[max_bidder]

            revenue = revenue+max_bid_value
            copy_bidders_budget[max_bidder] = copy_bidders_budget[max_bidder]-max_bid_value
        # print the first value
        if current_iteration==0:
            print(round(revenue,2))
            revenue = 0
        current_iteration = current_iteration+1
        avg_revenue = avg_revenue + revenue
    # finding average revenue
    avg_revenue = avg_revenue/100

    return avg_revenue

# MSVV algorithm which checks on bidValue*psiValue
def msvvAlgorithm(bidders_budget,queries_bids,query_lines):
    current_iteration = 0
    avg_revenue = 0
    # To run for 100 iterations
    while current_iteration <= ITERATIONS:
        copy_bidders_budget = bidders_budget.copy()
        revenue = 0
        if current_iteration !=0:
            rd.shuffle(query_lines)
        adv_frac_spent = collections.defaultdict(float)
        # finding the best bidder for each query
        for query in query_lines:
            adv_bids = queries_bids[query]
            adv_psi_bids = {}
            if adv_budget_empty(adv_bids,copy_bidders_budget):
                continue
            # find bidder with maximum psi*bid value
            for bid in adv_bids:

                if bid not in adv_frac_spent:
                    adv_psi_bids[bid] = adv_bids[bid]*calculate_psi(0.0)
                else:
                    adv_psi_bids[bid] = adv_bids[bid]*calculate_psi(adv_frac_spent[bid])
            
            max_psi_bidder = None
            max_psi_value = -math.inf
            max_bid_value = 0
            for bid in adv_psi_bids:
                
                if adv_bids[bid] < copy_bidders_budget[bid]:
                    if max_psi_value < adv_psi_bids[bid]:
                        max_psi_value = adv_psi_bids[bid]
                        max_psi_bidder = bid
                        max_bid_value = adv_bids[bid]
                    
                    elif max_psi_value == adv_psi_bids[bid]:
                        if bid < max_psi_bidder:
                            max_psi_bidder = bid
                            max_bid_value = adv_bids[bid]
            
            revenue = revenue+max_bid_value
            copy_bidders_budget[max_psi_bidder] = copy_bidders_budget[max_psi_bidder]-max_bid_value
            adv_frac_spent[max_psi_bidder] = (adv_frac_spent[max_psi_bidder]*bidders_budget[max_psi_bidder]+max_bid_value)/bidders_budget[max_psi_bidder]
        # print the first value
        if current_iteration==0:
            print(round(revenue,2))
            revenue = 0
        current_iteration = current_iteration+1
        avg_revenue = avg_revenue + revenue
    # finding average revenue
    avg_revenue = avg_revenue/100

    return avg_revenue
    pass

# Main function to call the corresponding algorithm
def main(algorithmName):
    # Reading queries.txt
    with open('queries.txt') as file:
        file_read_lines = file.readlines()
    
    query_lines = []
    for line in file_read_lines:
        query_lines.append(line.strip())
    # Reading bidder_dataset.csv
    bidders_df = pd.read_csv("bidder_dataset.csv")
    
    bidders_budget = collections.defaultdict(int)
    queries_bids = {}
    for i in range(len(bidders_df)):
        bidder_row = bidders_df.iloc[i]
        bidder_id = bidder_row['Advertiser']

        if bidder_id not in bidders_budget:
            bidders_budget[bidder_id] = bidder_row['Budget']

        query = bidder_row['Keyword']
        
        if query not in queries_bids:
            queries_bids[query] = {}
        
        queries_bids[query][bidder_id] = bidder_row['Bid Value']

    avg_revenue = 0
    optimal = sum(bidders_budget.values())

    # If algorithm is greedy
    if algorithmName == GREEDY:
        avg_revenue = greedyAlgorithm(bidders_budget.copy(),queries_bids,query_lines)
    # If algorithm is mssv
    elif algorithmName == MSVV:
        avg_revenue = msvvAlgorithm(bidders_budget.copy(),queries_bids,query_lines)
    # If algorithm is balance
    elif algorithmName == BALANCE:
        avg_revenue = balanceAlgorithm(bidders_budget.copy(),queries_bids,query_lines)
        
    else:
        print("Undefined Algorithm")
        exit()
    
    competetive_ratio = avg_revenue/optimal
    print(round(competetive_ratio,2))
    return

# Two arguments are required to run this file
# Please provide the algorithm name: greedy or mssv or balance
if __name__=="__main__":
    if len(sys.argv) == 2:
        algorithmName = sys.argv[1]
    else:
        print("Wrong number of arguments")
        exit()

    main(algorithmName)

#After runnig each algorithm, following are the values:

#command                          # revenue        # competetive ratio
# python adwords.py greedy        # 16731.4        # 0.94
# python adwords.py msvv          # 17671.0        # 0.99
# python adwords.py balance       # 12320.2        # 0.69