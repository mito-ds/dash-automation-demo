# vanguard-performance-demo

[Watch the demo](https://www.loom.com/share/283d65b5c1f9444b8243ea29183a1778)

## Demo Instructions
1. Import `fund_info.csv`
2. Use custom imports to import fund performance.
   - Use a fake username and password.
   - Use the year 2022
4. Use `Vlookup` to add the `Fund Manager` to the `fund_info` dataframe
5. Use the `MonthName` formula to extract the month from the date in `fund_info`
6. Create a pivot tale
   - Rows: `Fund`, `Fund Manager`
   - Columns: `Month`
   - Values: `sum` of `MoM Return`
7. Add conditional formatting
   - <0, highlight in red
   - \>0, highlight in green
8. Generate Excel file
9. Open Excel file and show formatting

Take a break to talk about what we just did. Paint the scenario that since your manager found this report useful, they want to see the same report for historical data. 

1. Click on change imported data and update the `performance` data to look at 2021. Notice that the colors change dramatically
2. Redownload the Excel file
3. Highlight how quick it is to create this report now. 
