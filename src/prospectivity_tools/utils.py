def df_more_info(dataframe):
    """
    Generate a detailed description of the columns in a DataFrame.

    Args:
        dataframe (pd.DataFrame): The DataFrame to describe.

    Returns:
        str: A formatted string describing the DataFrame's columns.
    """
    output = []

    for col in dataframe.columns:
        output.append(f"Column: {col}")
        output.append(
            f"  Missing: {dataframe[col].isnull().sum()} ({dataframe[col].isnull().mean():.1%})"
        )
        if dataframe[col].dtype == "object":
            # if fewer than 5 unique values, describe them as a count of each value
            if dataframe[col].nunique() <= 5:
                value_counts = dataframe[col].value_counts()
                output.append(f"  Value counts:\n{value_counts}\n")
            else:
                output.append(f"  Unique values: {dataframe[col].nunique()}")
                # 10 random examples, each on their own indented line
                examples = dataframe[col].sample(10, random_state=42).tolist()
                output.append("  Examples:")
                for example in examples:
                    output.append(f"    - {example}")

        elif dataframe[col].dtype in ["int64", "float64", "float32", "int32"]:
            output.append(
                f"  Min: {dataframe[col].min()}, Max: {dataframe[col].max()}, "
                f"  Mean: {dataframe[col].mean()}"
            )
        else:
            output.append(f"  Data type: {dataframe[col].dtype}")
        output.append("\n")

    # Join the output list into a single string and return it
    return "\n".join(output)
