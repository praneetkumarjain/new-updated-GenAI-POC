
import openai
import os, json
import config
import pandas as pd
from sqlalchemy import create_engine
from chat_response import OpenAiBackend
from openai import AzureOpenAI
import time
qnaObj = OpenAiBackend()
connection_str = f"mssql+pymssql://{config.username}:{config.password}@{config.server}:1433/{config.database}"
def ask_file(question_to_ask):
    task = f''' Based on the user question select the file which might contain the data the below
    description is in format filename: it contains column [<COLUMN_NAMES>]
    return only filename without any extra details
    Agent_Capacity_Expansion_Plan.csv: it contains columns ['Year', 'Total']
    Agent_Gross_refining_margin_GRM.csv: it contains columns ['Refinery', 'Unit', "January'23", "February'23", "March'23", "April'23", "May'23", "June'23", "July'23", "August'23", "Spetember'23"]
    Agent_Product_Demand_Growth_percentage.csv: it contains columns ['Product', '2028']
    Agent_Refinery_Throughput_2023.csv: it contains columns ['Refinery', "July'23 (Mb/d)"]
    Agent_Refinery_Utilisation_2023.csv: it contains columns ['Refinery', 'Type', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'Year']
    Capacity_Expansion_Plan.csv: it contains columns ['Year', 'Capacity Expansion Plan (mb/d)', 'labels']
    Gross_refining_margin.csv: it contains columns ['Refinery GRM ($/b)', "January'23", "February'23", "March'23", "April'23", "May'23", "June'23", "July'23", "August'23", "Spetember'23", 'labels']
    Gross_refining_margins_vs_benchmark.csv: it contains columns ['Refinery', 'Refinery Gross Margin ($/b)', 'labels']
    Gross_refining_margin_Plan_vs_Actual.csv: it contains columns ['Refinery', 'Planned GRM ($/b)', 'Actual GRM ($/b)', 'labels']
    Overall_Feedstock_Diet.csv: it contains columns ['Feedstock Item', 'Volume (%)', 'labels']
    Product_Volume_Plan_vs_Actual.csv: it contains columns ['Product', 'Business Plan Volume (MBBL)', 'Actual Volume (MBBL)', 'labels']
    R4_Refinery_Feedstock_Diet_Plan_vs_Actual.csv: it contains columns ['Feedstock Diet', 'Plan (%)', 'Actual (%)', 'labels']
    R4_refinery_Gross_Margin_Variance.csv: it contains columns ['Product', 'R4 GRM variance ($Million)', 'labels']
    R4_Refinery_Product_Volume_Plan_vs_Actual.csv: it contains columns ['Product', 'Plan Volume (KBBL)', 'Actual Volume (KBBL)', 'labels']
    R4_Refinery_Utilisation_Plan_vs_Actual.csv: it contains columns ['Month', 'Plan Utilisation %', 'Actual Utilisation %', 'labels']
    Refinery_throughput_2023.csv: it contains columns ['title', 'x_label', 'y_label', 'Refinery', 'July_2023']
    Refinery_Throughput_Plan_Vs_Actual.csv: it contains columns ['Refinery', 'Actual Throughput (MBD)', 'Business Plan Throughput (MBD)', 'labels']
    Refinery_Utilization_2023.csv: it contains columns ['title', 'x_label', 'y_label', 'Refinery', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'Overall_Year']
    scope_2028.csv: it contains columns ['Scope 1 and Scope 2 emissions']
    Energy_Efficiency_Index.csv : it contains columns ['Months','Energy_Efficiency_Index', 'ABC_Peer1', 'DEF_Peer2', 'Benchmark', 'labels']
    Levels_waterconsumption_waterdischarge_refineries.csv : it contains columns ['Refinery', 'Water_withdrawn', 'Water_discharged', 'labels']
    Last6months_waterconsumption_discharge_R4refinery.csv : it contains columns ['Months','Actual_Water_Withdrawn', 'Actual_Water_Discharged', 'Allowance_Limit_Water_Withdrawn', 'Allowance_Limit_Water_Discharged', 'labels']
    Water_Consumption_Breakup.csv : it contains columns ['Process_Consumption', 'percentage', 'labels']  
    Daily_Report_Data.csv: it contains columns ['Refinery','Production Plan (bbl)','Production Actual (bbl)','Asset Utilization Plan (%)','Asset Utilization Actual (%)','Water Consumed Allowable limit (ton)','Water consumed Actual (ton)','Power Consumed Plan (MKWh)','Power Consumed Actual (MKWh)','Flaring Allowable limit (cum)','Flaring Actual (cum)','Lost Work Case (LWC) Nos','Hydrocarbon(HC)/Highly toxic material (HTM) leakNos']
    Production_plan_vs_actual.csv: it contains columns ['Production_Vol_Plan_vs_actual','Plan_Volume_KBBL','labels']
    Product_wise_breakup_percentage.csv: it contains columns ['Product', 'Product_breakup_percentage', 'labels']
    procurement_kpi_status.csv: it contains columns ['KPI','Target','Actual','Status','Highlights']
    OnTime_Delivery.csv: it contains columns ['Month','OnTimeDelivery','labels']
    Defect_Rate.csv: it contains columns ['Month','DefectRate','labels']
    Order_Fulfillment.csv: it contains columns ['Month','OrderFulfillmentPercent','labels']
    Daily_report_procurement.csv: it contains columns ['Section', 'Details']
    Refinery_Capacity.csv: it contains columns ['Region', 'Year_2023','Year_2030','Percentage Change','labels']
    Projected_Demand_Vs_Capacity_Expansion_for_2030.csv: it contains columns ['Product', 'US','Middle_East','China','Internal Refinery','labels']
    Refinery_Utilization_2024.csv: it contains columns [ 'Month', 'Internal_Refinery','US','Asia', 'labels']
    '''
    client = AzureOpenAI(
                            azure_endpoint=config.azure_endpoint,
                            api_key=config.api_key,  
                            api_version=config.openai_api_version
                        )
    response = client.chat.completions.create(
        model=config.model_name,
        messages=[ 
            {"role": "system", "content": task},
            {"role": "user", "content": question_to_ask}
        ]
    )
    res = response.choices[0].message.content
    return res
#changed this original code to newcode below this parahgraph
def convert_csv_HighchartsJson(df, new_df, file_name, chart_type="line"): 
    x_label = df.loc[0, 'labels']
    y_label = df.loc[1, 'labels']
    chart_title = file_name.replace('.csv', ' ')
 
    series_names = new_df.columns[1:]
    x_axis = new_df.columns[0]
 
    highcharts_data = {
        "data": {
            "xlabel": x_label,
            "ylabel": y_label,
            "title": chart_title,
            "type": chart_type,
            "xAxis": new_df[x_axis].tolist(),
            "series": []
        }
    }
 
    for series_name in series_names:
        series_data = {
            "name": series_name,
            "data": [float(x) for x in new_df[series_name].tolist()]
        }
        highcharts_data["data"]["series"].append(series_data)
 
    return highcharts_data
def convert_csv_HighchartsJson(df, new_df, file_name, chart_type="line"):
    x_label = df.loc[0, 'labels']
    y_label = df.loc[1, 'labels']
    chart_title = file_name.replace('.csv', ' ')
 
    series_names = new_df.columns[1:]
    x_axis = new_df.columns[0]
 
    highcharts_data = {
        "data": {
            "xlabel": x_label,
            "ylabel": y_label,
            "title": chart_title,
            "type": chart_type,
            "xAxis": new_df[x_axis].tolist(),
            "series": []
        }
    }

    for series_name in series_names:
        series_data = {
            "name": series_name,
            "data": []
        }
        
        # Loop through each value in the series
        for value in new_df[series_name]:
            try:
                # Try converting to float
                series_data["data"].append(float(value))
            except ValueError:
                # In case of non-numeric value, append None (can be handled by Highcharts)
                series_data["data"].append(None)

        highcharts_data["data"]["series"].append(series_data)
 
    return highcharts_data
### Original Code ###
def convert_csv_HighchartsJson_old(df, new_df, file_name, chart_type="line"):
    x_label = df.loc[0, 'labels']
    y_label = df.loc[1, 'labels']
    chart_title = file_name.replace('.csv', ' ')
 
    series_names = new_df.columns[1:]
    x_axis = new_df.columns[0]
 
    highcharts_data = {
        "data": {
            "xlabel": x_label,
            "ylabel": y_label,
            "title": chart_title,
            "type": chart_type,
            "xAxis": new_df[x_axis].tolist(),
            "series": []
        }
    }

    for series_name in series_names:
        series_data = {
            "name": series_name,
            "data": [float(x) for x in new_df[series_name].tolist()]
        }
        highcharts_data["data"]["series"].append(series_data)
 
    return highcharts_data
### Updated Code with Error Handling ###
def convert_csv_HighchartsJson(df, new_df, file_name, chart_type="line"):
    x_label = df.loc[0, 'labels']
    y_label = df.loc[1, 'labels']
    chart_title = file_name.replace('.csv', ' ')
 
    series_names = new_df.columns[1:]
    x_axis = new_df.columns[0]
 
    highcharts_data = {
        "data": {
            "xlabel": x_label,
            "ylabel": y_label,
            "title": chart_title,
            "type": chart_type,
            "xAxis": new_df[x_axis].tolist(),
            "series": []
        }
    }

    for series_name in series_names:
        series_data = {
            "name": series_name,
            "data": []
        }
        
        # Loop through each value in the series
        for value in new_df[series_name]:
            try:
                # Try converting to float
                series_data["data"].append(float(value))
            except ValueError:
                # In case of non-numeric value, append None (can be handled by Highcharts)
                series_data["data"].append(None)

        highcharts_data["data"]["series"].append(series_data)
 
    return highcharts_data
###updated code ends here###

def generate_table_json(df):
    categories = df.iloc[:, 0].tolist()
    data = []
    
    for col in df.columns[1:]:
        series = {
            "name": col,
            "data": df[col].tolist()
        }
        data.append(series)
    table_json = {
        "KPI_Name": categories,
        "data": data
    }
    
    return table_json
def get_chat_response_json_withtitle(text):
    plot_words = ['plot', 'draw', 'display', "sketch", "outline", "render", "illustrate", "graph", "visualize", "chart"]
    multi_plot_keywords = ['kpi status', 'key kpi status']
    
    # Handle Daily Report Data
    if "daily report data" in text.lower():
        filename = "Daily_Report_Data.csv"
        tablename = filename[:-4].replace(' ', '_')
        engine = create_engine(connection_str)
        conn = engine.connect()
        
        # Read the data from SQL table
        df = pd.read_sql_table(tablename, conn)
        # Prepare JSON data for the daily report
        categories = df['Refinery'].tolist()
        data = []
        for col in df.columns[1:]:
            series = {
                "name": col,
                "data": df[col].tolist()
            }
            data.append(series)
        daily_report_json = {
            "Refinery_name": categories,
            "data": data,
            "summary": [
                "For R4 refinery, charge gas compressor vibration issue leading to downtime of 16 hrs",
                "For R4 refinery, HE3 (Heat Exchanger) unplanned cleaning due to significant reduction in heat load"
            ]
        }
        return daily_report_json
    #daily procurement
    if "daily report for procurement" in text.lower():
        filename = "Daily_report_procurement.csv"
        tablename = filename[:-4].replace(' ', '_')  # Table name is based on the file name
        engine = create_engine(connection_str)
        conn = engine.connect()

    # Read the data from SQL table
        df = pd.read_sql_table(tablename, conn)

    # Group by 'Section' and aggregate the 'Details' into a list for each section
        grouped_df = df.groupby('Section')['Details'].apply(list).reset_index()

    # Define the custom order of the sections (SQL-like order)
        custom_order = [
            "Executive Summary",
            "Purchase Orders",
            "Supplier Management",
            "Inventory Management",
            "Contracts Management",
            "Expenditure Tracking",
            "Delivery and Logistics",
            "Compliance and Risk Management",
            "Savings and Efficiencies",
            "Action Items and Next Steps",
            "Miscellaneous Updates"
        ]

    # Create a mapping of each section to its index in the custom order list
        section_order = {section: idx for idx, section in enumerate(custom_order)}

    # Sort the grouped DataFrame based on the custom order
        grouped_df['Order'] = grouped_df['Section'].map(section_order)
        grouped_df = grouped_df.sort_values(by='Order').drop(columns=['Order'])

    # Initialize the response list
        report_data = []

    # Iterate over each row in the sorted DataFrame and create the desired output format
        for _, row in grouped_df.iterrows():
            section_dict = {
                'heading': row['Section'],
                'value': row['Details']
            }
            report_data.append(section_dict)

    # Return the structured JSON response containing all sections
        response = {
            "type": "json",
            "data": report_data
        }

        return response
    #daily procurement report
    if "daily report procurement" in text.lower():
        filename = "Daily_report_procurement.csv"
        tablename = filename[:-4].replace(' ', '_')  # Table name is based on the file name
        engine = create_engine(connection_str)
        conn = engine.connect()

    # Read the data from SQL table
        df = pd.read_sql_table(tablename, conn)

    # Group by 'Section' and aggregate the 'Details' into a list for each section
        grouped_df = df.groupby('Section')['Details'].apply(list).reset_index()

    # Initialize the response list
        report_data = []

    # Iterate over each row in the grouped DataFrame and create the desired output format
        for _, row in grouped_df.iterrows():
            section_dict = {
                'heading': row['Section'],
                'value': row['Details']
            }
            report_data.append(section_dict)

    # Return the structured JSON response containing all sections
        response = {
            "type": "json",
            "data": report_data
        }

        return response
    
    # Existing logic for procurement kpi status handling
    if "procurement kpi status" in text.lower():
        filename = "procurement_kpi_status.csv"
        tablename = filename[:-4].replace(' ', '_')
        engine = create_engine(connection_str)
        conn = engine.connect()
        
        # Read the data from SQL table
        df = pd.read_sql_table(tablename, conn)
        # Prepare JSON data for procurement KPI status
        kpi_categories = df['KPI'].tolist()
        kpi_data = []
        for col in df.columns[1:]:
            series = {
                "name": col,
                "data": df[col].tolist()
            }
            kpi_data.append(series)
        procurement_kpi_json = {
            "KPI_Name": kpi_categories,
            "data": kpi_data
        }
        return procurement_kpi_json
    # Multi-plot response (4 graphs)
    if any(keyword in text.lower() for keyword in multi_plot_keywords):
        # Define the files and chart types
        filenames = [
            "Gross_refining_margins_vs_benchmark.csv",
            "Production_plan_vs_actual.csv",
            "Overall_Feedstock_Diet.csv",
            "Product_wise_breakup_percentage.csv"
        ]
        chart_types = ["column", "column", "pie", "pie"]  # Chart types for each file
        all_graphs_data = {
            'title': 'Key Performance Indicators are as follows:',  # Adding the title here
            'type': 'multi-plot', 
            'data': []
        }
        for idx, filename in enumerate(filenames):
            tablename = filename[:-4].replace(' ', '_')
            engine = create_engine(connection_str)
            conn = engine.connect()
           
            # Read data from CSV files
            df = pd.read_sql_table(tablename, conn)
            df1 = df.drop(['labels'], axis=1)
            # Default benchmark value for all column charts (adjust as needed)
            benchmark_value = {'benchmarkValue': 'NA', 'benchmarkName': 'NA'}
            # For specific files (like Gross_refining_margins_vs_benchmark.csv), add benchmark values
            if filename == "Gross_refining_margins_vs_benchmark.csv":
                benchmark_value = {'benchmarkValue': '4.9', 'benchmarkName': 'Asia Benchmark'}  # Example benchmark value
            elif filename == "Production_plan_vs_actual.csv":
                benchmark_value = {'benchmarkValue': 'NA', 'benchmarkName': 'NA'}  # Placeholder, can be customized
            # Determine the chart type (dynamic chart handling)
            chart_type = chart_types[idx]
            data = convert_csv_HighchartsJson(df, df1, filename, chart_type=chart_type)
            all_graphs_data['data'].append({
                'chart': data,
                'type': chart_type,  # Specify the chart type in the response
                'benchmark': benchmark_value  # Add benchmark data
            })
            # Add table data if needed
            table_data = generate_table_json(df1)
            all_graphs_data['data'][-1]['table'] = table_data
        return all_graphs_data  # Removed print statement here
    
    # New functionality for plotting 3 types of graphs for vendor performance
    if "plot performance of vendor" in text.lower():
        filenames_performance = [
            "OnTime_Delivery.csv",
            "Defect_Rate.csv",
            "Order_Fulfillment.csv"
        ]
    
        # Define the chart types for each file
        chart_types = {
            "OnTime_Delivery.csv": "line",
            "Defect_Rate.csv": "column",
            "Order_Fulfillment.csv": "line"
        }
    
        performance_data = {
            'title': 'Comprehensive Analysis of Vendor Performance Metrics for M/s ABL Ltd: On-Time Delivery, Defect Rate, and Order Fulfillment Trends',
            'type': 'multi-plot',
            'data': []
        }
    
        for filename in filenames_performance:
            tablename = filename[:-4].replace(' ', '_')
            engine = create_engine(connection_str)
            conn = engine.connect()
        
            # Read data from SQL tables
            df = pd.read_sql_table(tablename, conn)
            df1 = df.drop(['labels'], axis=1)
        
            # Determine the chart type for the current file
            chart_type = chart_types[filename]
        
            # Convert data to Highcharts JSON format
            data = convert_csv_HighchartsJson(df, df1, filename, chart_type=chart_type)
        
            performance_data['data'].append({
                'chart': data,
                'type': chart_type  # Specify the chart type in the response
            })
        
            # Add table data if needed
            table_data = generate_table_json(df1)
            performance_data['data'][-1]['table'] = table_data
    
        return performance_data
    
    # Standard question answering functionality
    for catch_word in plot_words:
        if catch_word in text.lower():
            filename = ask_file(text)
            tablename = filename[:-4].replace(' ', '_')
                    
            engine = create_engine(connection_str)
            conn = engine.connect()
            df = pd.read_sql_table(tablename, conn)
            df1 = df.drop(['labels'], axis=1)
            chart_type = "line"  # Default to line for single plot
            data = convert_csv_HighchartsJson(df, df1, filename, chart_type=chart_type)
            response = {
                'type': 'plot',
                'data': data
            }
            #if df1.shape[1] > 2 or sum(1 for number in list(df1[df1.columns[1]]) if number <= 0) < len(list(df1[df1.columns[1]])):
            if df1.shape[1] > 2 or sum(1 for number in list(df1[df1.columns[1]]) if float(number) >= 0)<len(list(df1[df1.columns[1]])):
                piechart_flag = 0 # Disable pie chart on the UI
            else:
                piechart_flag = 1 # Show pie chart
                
                 
            if filename == "Gross_refining_margins_vs_benchmark.csv":
                benchmark_value = {'benchmarkValue': '4.9', 'benchmarkName': 'Asia Benchmark'}
            else:
                benchmark_value = {'benchmarkValue': 'NA', 'benchmarkName': 'NA'}
            response['data']['ydata'] = benchmark_value
            response['data']['piechart'] = piechart_flag
            # Add table data to the response
            table_data = generate_table_json(df1)
            response['table'] = table_data
            return response  # Removed print statement here
              
    answer = qnaObj.ask_question(text)
    response = {
                'type': 'string',
                'data': answer
                }
    return response
