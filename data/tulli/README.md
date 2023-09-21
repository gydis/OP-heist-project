**international_trade_country_NACE_breakdown.csv** has the following dimensions:
+ Time period, e.g. 202303 - March 2023
+ Country code, e.g. DE - Germany
+ Trade direction - Export: destination, Import: country of origin, country of consignment.
+ NACE Industry classigfication, e.g. A - agriculture. 

The values are value of trade and cumulative value from the beginning of the year.

You can find descriptions of country codes and NACE in .csv tables in util folder.

Command for loading Country-industry breakdown table:
```
df = pd.read_csv("international_trade_country_NACE_breakdown.csv", index_col=[0,1,2,3])
```
This way the data frame will have a multi-dimensional index

**tulli_international_trade_region_economy-sector.csv** dimensions:
+ Time period, same format (Records once a year)
+ Region of Finland
+ Direction - Import/Export (No consignment)

A lot of values, but some interesting ones: 
+ Cum. value from the beginning of the year
+ share of industrial/trade/other sectors in the trade. 
