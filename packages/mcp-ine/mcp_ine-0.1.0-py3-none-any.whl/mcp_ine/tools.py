from typing import Optional, List, Dict, Any
from .common import mcp, ine_request, logger, INE_DEFAULT_PERIODS

@mcp.tool()
def List_Operations(filter_text: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available INE statistical operations
    
    Args:
        filter_text: Optional filter by code or name (e.g., 'IPC', 'población')
    
    Returns:
        List of operations with Id, Codigo, Nombre, and Url
    """
    try:
        operations = ine_request("OPERACIONES_DISPONIBLES")
        
        if isinstance(operations, dict) and "error" in operations:
            return [operations]
        
        # Apply filter if provided
        if filter_text:
            filter_lower = filter_text.lower()
            operations = [
                op for op in operations
                if filter_lower in op.get('Codigo', '').lower() or 
                   filter_lower in op.get('Nombre', '').lower()
            ]
        
        logger.info(f"Retrieved {len(operations)} operations")
        return operations
    except Exception as e:
        logger.error(f"Error in List_Operations: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def Get_Operation_Tables(operation_code: str) -> List[Dict[str, Any]]:
    """Get available tables for a statistical operation
    
    Args:
        operation_code: Operation code (e.g., 'IPC', 'IPI', 'EPA')
    
    Returns:
        List of tables with Id, Nombre, Codigo, FK_Periodicidad, etc.
    """
    try:
        tables = ine_request("TABLAS_OPERACION", operation_code)
        
        if isinstance(tables, dict) and "error" in tables:
            return [tables]
        
        logger.info(f"Retrieved {len(tables)} tables for operation {operation_code}")
        return tables
    except Exception as e:
        logger.error(f"Error in Get_Operation_Tables: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def Get_Table_Data(
    table_id: int,
    last_periods: Optional[int] = None,
    period_type: Optional[str] = None,
    date_range: Optional[str] = None,
    detail_level: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get data from a specific table
    
    Args:
        table_id: Table ID (e.g., 50902 for national CPI)
        last_periods: Last N periods to retrieve
        period_type: 'A' (annual), 'M' (monthly), 'AM' (both)
        date_range: Date range 'YYYYMMDD:YYYYMMDD' (e.g., '20240101:20241231')
        detail_level: Detail level 0-3 (default: 1)
    
    Returns:
        List of series with COD, Nombre, FK_Unidad, FK_Escala, and Data array
    """
    try:
        params = {}
        if last_periods:
            params['nult'] = last_periods
        if period_type:
            params['tip'] = period_type
        if date_range:
            params['date'] = date_range
        if detail_level is not None:
            params['det'] = detail_level
        
        data = ine_request("DATOS_TABLA", str(table_id), params)
        
        if isinstance(data, dict) and "error" in data:
            return [data]
        
        logger.info(f"Retrieved {len(data)} series from table {table_id}")
        return data
    except Exception as e:
        logger.error(f"Error in Get_Table_Data: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def Get_Series_Data(
    series_code: str,
    last_periods: Optional[int] = None,
    period_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get data from a specific time series
    
    Args:
        series_code: Series code (e.g., 'IPC251856' for annual CPI variation)
        last_periods: Last N periods to retrieve
        period_type: 'A' (annual), 'M' (monthly), 'AM' (both)
    
    Returns:
        Series object with COD, Nombre, FK_Unidad, FK_Escala, and Data array
    """
    try:
        params = {}
        if last_periods:
            params['nult'] = last_periods
        if period_type:
            params['tip'] = period_type
        
        data = ine_request("DATOS_SERIE", series_code, params)
        
        if isinstance(data, dict) and "error" in data:
            return data
        
        logger.info(f"Retrieved series {series_code}")
        return data
    except Exception as e:
        logger.error(f"Error in Get_Series_Data: {e}")
        return {"error": str(e)}


@mcp.tool()
def Get_Table_Variables(table_id: int) -> List[Dict[str, Any]]:
    """Get available variables for a table
    
    Args:
        table_id: Table ID
    
    Returns:
        List of variables with Id and Nombre
    """
    try:
        variables = ine_request("VARIABLES_TABLA", str(table_id))
        
        if isinstance(variables, dict) and "error" in variables:
            return [variables]
        
        logger.info(f"Retrieved {len(variables)} variables for table {table_id}")
        return variables
    except Exception as e:
        logger.error(f"Error in Get_Table_Variables: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def Get_Variable_Values(variable_id: int, table_id: int) -> List[Dict[str, Any]]:
    """Get possible values for a variable in a table
    
    Args:
        variable_id: Variable ID
        table_id: Table ID
    
    Returns:
        List of values with Id, FK_Variable, Nombre, and Codigo
    """
    try:
        values = ine_request("VALORES_VARIABLE", f"{variable_id}/{table_id}")
        
        if isinstance(values, dict) and "error" in values:
            return [values]
        
        logger.info(f"Retrieved {len(values)} values for variable {variable_id} in table {table_id}")
        return values
    except Exception as e:
        logger.error(f"Error in Get_Variable_Values: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def Search_Data(
    query: str,
    operation_filter: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search for data across operations and tables
    
    Args:
        query: Search term (e.g., 'inflación', 'paro', 'población')
        operation_filter: Optional operation code to filter (e.g., 'IPC')
        max_results: Maximum number of results to return
    
    Returns:
        List of matching operations and tables
    """
    try:
        results = []
        query_lower = query.lower()
        
        # Search in operations
        operations = ine_request("OPERACIONES_DISPONIBLES")
        if not isinstance(operations, dict) or "error" not in operations:
            for op in operations:
                if query_lower in op.get('Nombre', '').lower() or \
                   query_lower in op.get('Codigo', '').lower():
                    results.append({
                        "type": "operation",
                        "code": op.get('Codigo'),
                        "name": op.get('Nombre'),
                        "id": op.get('Id')
                    })
                    if len(results) >= max_results:
                        break
        
        # If operation filter specified, search in its tables
        if operation_filter and len(results) < max_results:
            tables = ine_request("TABLAS_OPERACION", operation_filter)
            if not isinstance(tables, dict) or "error" not in tables:
                for table in tables:
                    if query_lower in table.get('Nombre', '').lower():
                        results.append({
                            "type": "table",
                            "id": table.get('Id'),
                            "name": table.get('Nombre'),
                            "code": table.get('Codigo'),
                            "operation": operation_filter
                        })
                        if len(results) >= max_results:
                            break
        
        logger.info(f"Search '{query}' returned {len(results)} results")
        return results[:max_results]
    except Exception as e:
        logger.error(f"Error in Search_Data: {e}")
        return [{"error": str(e)}]


@mcp.tool()
def Get_Latest_Data(
    operation_code: str,
    table_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get the most recent data from an operation
    
    Args:
        operation_code: Operation code (e.g., 'IPC', 'EPA')
        table_filter: Optional table name filter
    
    Returns:
        Latest data with table info and most recent values
    """
    try:
        # Get tables for the operation
        tables = ine_request("TABLAS_OPERACION", operation_code)
        
        if isinstance(tables, dict) and "error" in tables:
            return [tables]
        
        if not tables:
            return [{"error": f"No tables found for operation {operation_code}"}]
        
        # Filter tables if requested
        if table_filter:
            filter_lower = table_filter.lower()
            tables = [t for t in tables if filter_lower in t.get('Nombre', '').lower() or str(t.get('Id')) == table_filter]
        
        if not tables:
            return [{"error": f"No tables match filter '{table_filter}'"}]
        
        # Get latest data from first matching table
        table = tables[0]
        table_id = table.get('Id')
        
        # Request only the most recent period
        data = ine_request("DATOS_TABLA", str(table_id), {'nult': 1})
        
        if isinstance(data, dict) and "error" in data:
            return [data]
        
        results = []
        
        # Extract latest values from series that have data
        for series in data[:10]:  # Limit to first 10 series
            if series.get('Data') and len(series['Data']) > 0:
                latest_point = series['Data'][-1] if isinstance(series['Data'], list) else series['Data']
                results.append({
                    "operation": operation_code,
                    "table_id": table_id,
                    "table_name": table.get('Nombre'),
                    "series_code": series.get('COD'),
                    "series_name": series.get('Nombre'),
                    "value": latest_point.get('Valor') if isinstance(latest_point, dict) else latest_point,
                    "date": latest_point.get('Fecha') if isinstance(latest_point, dict) else None,
                    "year": latest_point.get('Anyo') if isinstance(latest_point, dict) else None
                })
        
        logger.info(f"Retrieved latest data for {operation_code}")
        return results
    except Exception as e:
        logger.error(f"Error in Get_Latest_Data: {e}")
        return [{"error": str(e)}]
