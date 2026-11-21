import pandas as pd
import plotly.express as px

def read_dataframe(file):
    """Lee un archivo Excel o CSV y devuelve un DataFrame"""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            return None
        return df
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return None

def generate_summary(df):
    """Genera un resumen en texto del DataFrame para la IA"""
    summary = f"El archivo tiene {df.shape[0]} filas y {df.shape[1]} columnas.\n"
    summary += "Columnas y tipos de datos:\n"
    for col in df.columns:
        summary += f"- {col} ({df[col].dtype})\n"
    
    summary += "\nPrimeras 5 filas de datos:\n"
    summary += df.head(5).to_string()
    return summary

def generate_chart(df, x_col, y_col, chart_type="bar"):
    """Genera una gráfica interactiva"""
    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} por {x_col}")
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, title=f"Tendencia de {y_col}")
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col, title=f"Distribución de {y_col}")
        return fig
    except Exception as e:
        return None