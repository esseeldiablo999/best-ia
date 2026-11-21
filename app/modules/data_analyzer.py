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
    resumen = f"El archivo tiene {df.shape[0]} filas y {df.shape[1]} columnas.\n"
    resumen += "Columnas y tipos de datos:\n"
    for col in df.columns:
        resumen += f"- {col} ({df[col].dtype})\n"
    
    resumen += "\nPrimeras 15 filas de datos:\n"
    resumen += df.head(15).to_string()
    
    # Agregar estadísticas descriptivas (Máximos, mínimos, promedios)
    try:
        resumen += "\n\nEstadísticas descriptivas de columnas numéricas (mínimo, máximo, promedio):\n"
        resumen += df.describe().to_string()
    except:
        pass

    # Agregar los 3 valores más altos de cada columna numérica para que la IA responda rápido
    columnas_numericas = df.select_dtypes(include=['number']).columns
    if len(columnas_numericas) > 0:
        resumen += "\n\nTop 3 valores más altos por columna:\n"
        for col in columnas_numericas:
            try:
                top_3 = df.nlargest(3, col)
                # Tomamos la primera columna (usualmente el ID o Nombre) y la columna numérica
                columnas_a_mostrar = [df.columns[0], col] if df.columns[0] != col else [col]
                resumen += f"\nTop en '{col}':\n{top_3[columnas_a_mostrar].to_string()}\n"
            except:
                pass

    return resumen

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