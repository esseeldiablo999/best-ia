from duckduckgo_search import DDGS

def search_web(query, max_results=3):
    """Busca en internet y devuelve los resultados"""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            if not results:
                return "No se encontraron resultados en la web."
            
            text = "Resultados de la búsqueda en internet:\n\n"
            for i, res in enumerate(results, 1):
                text += f"{i}. {res['title']}\n{res['body']}\nFuente: {res['href']}\n\n"
            return text
    except Exception as e:
        return f"Error al buscar en internet: {str(e)}"