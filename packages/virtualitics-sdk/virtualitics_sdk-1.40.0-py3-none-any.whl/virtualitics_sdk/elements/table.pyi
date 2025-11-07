import openpyxl
import pandas
from _typeshed import Incomplete
from abc import ABC
from enum import Enum
from predict_backend.validation.type_validation import validate_types
from typing import Any, Callable, Coroutine
from virtualitics_sdk.assets.dataset import Dataset as Dataset
from virtualitics_sdk.elements.element import Element as Element, ElementType as ElementType
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface

logger: Incomplete
PREDICT_SUCCESS_TEXT_COLOR: str
PREDICT_SUCCESS_CELL_COLOR: str
PREDICT_ERROR_TEXT_COLOR: str
PREDICT_ERROR_CELL_COLOR: str
PREDICT_WARNING_TEXT_COLOR: str
PREDICT_WARNING_CELL_COLOR: str
PREDICT_DEFAULT_TEXT_COLOR: str
PREDICT_DEFAULT_CELL_COLOR: str

class RowActionType(Enum):
    UPDATE: str
    REDIRECT: str
    UPDATE_REDIRECT: str

class RowAction(ABC):
    title: Incomplete
    description: Incomplete
    action_type: Incomplete
    def __init__(self, title: str, description: str, type: RowActionType) -> None: ...
    def to_json(self): ...

class Table(Element):
    '''A Table element.

    :param content: A DataFrame, Pandas series, or Dataset. Dataframes that have  column with the reserved keyword `id` as their name are not supported and will raise an Exception.
    :param downloadable: Whether this table should be downloaded, defaults to False.
    :param filters_active: Whether the filters are active on this table, defaults to False.
    :param title: The title of the element, defaults to \'\'.
    :param description: The element\'s description, defaults to \'\'.
    :param show_title: Whether to show the title on the page when rendered, defaults to True.
    :param show_description: Whether to show the description to the page when rendered, defaults to True.
    :param cell_colors: Dataframe of cell colors as hex strings. Columns should exist inside source dataset, defaults to None, joined to in content dataframe by index. See code example below for usage.
    :param text_colors: Dataframe of text colors as hex strings. Columns should exist inside source dataset, defaults to None, joined to in content dataframe by index. See code example below for usage.
    :param column_descriptions: Descriptions of the column of the inputs. These can be set for specific columns and must not be set for every column, defaults to None.
    :param searchable: Toggles the ability to search table values, defaults to True.
    :param missing_values: Set to true if this table contains missing values and you want to flag this to the user.
    :param notes: The popover description that shows upon hovering over a particular row. Each index in the list maps to the corresponding row. Defaults to None.
    :param links: The link to redirect to when hovering over a particular row. Each index in the list maps to the corresponding row. Defaults to None.
    :param show_filter: Whether to show the filter on the page when rendered, defaults to False.
    :param max_table_rows_to_display: Defaults to 2500 rows, this is the number of rows that will be sent to the frontend, however
           the entire table is downloadable from the frontend regardless of this limit. Browsers with more resources may be able to handle
           much larger limits than this default value.
    :param xlsx_config: dictionary of configurable parameters for tables that are backed by an xlsx object
    :param editable: should this table be editable by the user from the frontend. This defaults to true.
    :param max_table_row_height: The maximum height of the table rows. Defaults to 300 characters.
    :param markdown_columns: Controls which columns render their content as markdown. If None or an empty list ([]), no columns will render as markdown. If set to True, all columns will render as markdown. If set to a list of column names, only the specified columns will render as markdown, while others will render as plain text
    :param missing_value_text:  A string used to replace missing values (e.g., None, NaN, or NaT) in the table when rendered. Defaults to None, meaning missing values will remain as-is.
    :param editable_columns: Controls which columns are editable. If None, False, or an empty list ([]), no columns will be editable. If set to True, all columns will be editable. If set to a list of column names, only the specified columns will be editable. Defaults to True. You must turn this to False if editable is also False if you wish to disable table edits.
    :param row_actions: A list of `RowAction`s that will be attached to the first rows of the table, as determined by the `max_table_rows_to_display` parameter. Defaults to None.
    :param column_formatters: A dictionary of key: Column Name and value: Python format string, that optionally formats the specified numeric columns on the frontend. As an example, \'{total_spending: "$ {:,.2f}"}\' would format the total_spending column as currency, while sorting as an float. Defaults to None.
    :param on_edit_update: Updater function. Allows to execute a function when the table content\'s get changed.
                           Takes a StoreInterface and the Table itself, defaults to None.
                        
    :raises NotImplementedError: When table is created with invalid type.

    **EXAMPLE:**

       .. code-block:: python

           # Imports
           from virtualitics_sdk import Table, PREDICT_ERROR_TEXT_COLOR
           . . .
           . . .
           # Example usage
           class ExampleStep(Step):
             def run(self, flow_metadata):
               . . .
               point_per_cluster = 5 # Number of rows we want cell/text color to apply to
               cell_colors = pandas.DataFrame({"Y Feature": ["#39cd63"] * point_per_cluster})
               text_colors = pandas.DataFrame({"X Feature": ["#ee2310"] * point_per_cluster})
               table = Table(example_dataset,
                       title="Example Table",
                       description="This is a table showing cells/text color",
                       downloadable=True,
                       cell_colors=cell_colors,
                       text_colors=text_colors)

    The above Table will be displayed as:

       .. image:: ../images/table_color_ex.png
          :align: center
    '''
    persistence: Incomplete
    cell_color_persistence: Incomplete
    text_color_persistence: Incomplete
    row_action_function_persistence: Incomplete
    on_edit_update_fn_persistence: bool
    buttons: Incomplete
    @validate_types
    def __init__(self, content: pandas.DataFrame | Dataset | openpyxl.Workbook, downloadable: bool = False, filters_active: bool = False, title: str = '', description: str = '', show_title: bool = True, show_description: bool = True, cell_colors: pandas.DataFrame | None = None, text_colors: pandas.DataFrame | None = None, column_descriptions: dict[str, str] | None = None, searchable: bool = True, missing_values: bool = False, notes: list[str] | None = None, links: list[str] | None = None, show_filter: bool = False, max_table_rows_to_display: int = 2500, xlsx_config: dict | None = None, editable: bool = True, max_table_row_height: int = 300, markdown_columns: list[str] | bool | None = None, missing_value_text: str | None = None, editable_columns: list[str] | bool | None = True, row_actions: list[RowAction] | None = None, column_formatters: dict[str, str] | None = None, on_edit_update: Callable[[StoreInterface, Table], Coroutine[Any, Any, None]] | None = None, **kwargs) -> None: ...
    def to_json(self) -> dict: ...
    def extract_context(self) -> dict: ...
    def get_dtypes(self, _df: pandas.DataFrame) -> dict: ...
    def get_df(self) -> pandas.DataFrame:
        """Returns the Table Element's persisted data as a pandas.Dataframe.
        """

class UpdateRowAction(RowAction):
    updater: Incomplete
    update_name: Incomplete
    def __init__(self, title: str, description: str, updater: Callable[[StoreInterface, list[int]], str | None]) -> None:
        """An Update Row Action allows you to update a page based on that contents in a row

        :param title: The title of the update. Shown when the user is selecting a specific Row action
        :param description: The description of the update. Shown on-hover or in specific modals
        :param updater: The updater function. It takes a StoreInterface and a list of integers which represent
        the selected row indices
        """

class RedirectRowAction(RowAction):
    redirects: Incomplete
    new_tab: Incomplete
    def __init__(self, title: str, description: str, redirect_func: Callable[[int], str | None], new_tab: bool = False) -> None:
        """An Update Row Action allows you to update a page based on that contents in a row

        :param title: The title of the update. Shown when the user is selecting a specific Row action
        :param description: The description of the update. Shown on-hover or in specific modals
        :param redirect_func: The redirect function. It takes an integer representing the row idx being called
        the selected row indices
        """

class UpdateRedirectRowAction(RowAction):
    updater: Incomplete
    update_name: Incomplete
    redirects: Incomplete
    new_tab: Incomplete
    def __init__(self, title: str, description: str, updater: Callable[[StoreInterface, list[int]], str | None], redirect_func: Callable[[int], str | None], new_tab: bool = False) -> None:
        """An Update Row Action allows you to update a page based on that contents in a row

        :param title: The title of the update. Shown when the user is selecting a specific Row action
        :param description: The description of the update. Shown on-hover or in specific modals
        :param updater: The updater function. It takes a StoreInterface and a list of integers which represent
        the selected row indices
        """
