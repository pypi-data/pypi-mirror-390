"""
Collection of output formatting methods: nccmp.
"""

from prettytable import PrettyTable

from ipsl_ncdiff.model.dataset import split_variable_name


def format_nccmp(diffs) -> str:
    """
    Fromat the statistics of value differences in the same format as the `nccmp` tool.
    URL: https://gitlab.com/remikz/nccmp

    Note: some of the values might differ, especially the std/var,
          because a different backand is used here, namely numpy.
          However, the majorty of statistics should be the same!
    """
    table = PrettyTable()
    table.border = False
    table.field_names = [
        "Variable",
        "Group",
        "Count",
        "Sum",
        "AbsSum",
        "Min",
        "Max",
        "Range",
        "Mean",
        "StdDev",
    ]
    # Align left those columns
    table.align["Variable"] = "l"
    table.align["Group"] = "l"
    # Aligh right the rest of columns
    for field in table.field_names[2:]:
        table.align[field] = "r"
    # Setup proper float formatting (it's actually the default nccmp for floats: %g)
    for field in table.field_names[3:]:
        table.custom_format[field] = lambda _, v: f"{v:g}"
    # Add row-by-row
    for var_report in diffs.variables:
        full_name = var_report.name
        # Use pathlib to figure out groups and variable names
        group, name = split_variable_name(full_name)
        if var_report.value:
            dvals = var_report.value
            table.add_row(
                [
                    name,
                    group,
                    dvals["count_not_equal"],
                    dvals["sum_diff"],
                    dvals["abs_sum_diff"],
                    dvals["min_diff"],
                    dvals["max_diff"],
                    dvals["range_diff"],
                    dvals["mean_diff"],
                    dvals["std_diff"],
                ]
            )
    return table.get_string()
